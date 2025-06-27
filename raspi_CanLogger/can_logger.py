import can
import struct
import csv
import threading
from datetime import datetime
import sys
import select

# EMU CAN 메시지의 기본 CAN ID
EMU_BASE_ID = 0x600

# 현재 시간 기준으로 로그 파일 이름 생성
CSV_FILENAME = f"emu_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# 종료 플래그
exit_flag = False

def parse_emu_600(data):
    """
    EMU Black의 0x600 CAN 프레임을 파싱하여 RPM, MAP, TPS, IAT, Battery 값을 추출
    """
    if len(data) != 8:
        return None

    # Little endian으로 디코딩m(EMU에서 설정에 따라 변경해줘야함 아마도)
    rpm     = struct.unpack_from('<H', data, 0)[0]
    map_kpa = struct.unpack_from('<H', data, 2)[0]
    tps     = data[4]
    iat     = struct.unpack_from('b', data, 5)[0]
    batt    = data[6] / 10.0

    return {
        "RPM": rpm,
        "MAP_kPa": map_kpa,
        "TPS_percent": tps,
        "IAT_C": iat,
        "Battery_V": round(batt, 1)
    }

def keyboard_listener():
    """
    사용자로부터 's' 키 입력을 감지하여 프로그램 종료 플래그 설정
    """
    global exit_flag
    print("Press 's' then Enter to stop logging and save the file.")
    while True:
        # 입력이 있을 때만 처리
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.readline().strip()
            if key.lower() == 's':
                exit_flag = True
                break

def main():
    global exit_flag

    bus = can.interface.Bus(channel='can0', bustype='socketcan')
    print(f"Logging EMU CAN data to '{CSV_FILENAME}'...\n")

    # 키보드 입력을 백그라운드로 감지하는 스레드 시작
    thread = threading.Thread(target=keyboard_listener, daemon=True)
    thread.start()

    with open(CSV_FILENAME, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "Timestamp", "RPM", "MAP_kPa", "TPS_percent", "IAT_C", "Battery_V"
        ])
        writer.writeheader()

        # 수신 루프
        while not exit_flag:
            msg = bus.recv(timeout=0.1)
            if msg is None:
                continue
            if msg.arbitration_id == EMU_BASE_ID:
                parsed = parse_emu_600(msg.data)
                if parsed:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    parsed["Timestamp"] = timestamp
                    writer.writerow(parsed)
                    print(
                        f"[{timestamp}]  "
                        f"RPM: {parsed['RPM']:>5}   "
                        f"MAP: {parsed['MAP_kPa']:>3} kPa   "
                        f"TPS: {parsed['TPS_percent']:>3}%   "
                        f"IAT: {parsed['IAT_C']:>4}°C   "
                        f"Batt: {parsed['Battery_V']:.1f} V"
                    )

    print(f"\nLogging stopped. File saved as '{CSV_FILENAME}'.")

if __name__ == "__main__":
    main()

