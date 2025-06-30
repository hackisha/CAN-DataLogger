import can
import struct
import csv
import threading
from datetime import datetime
import sys
import termios
import tty
import requests
import os

# Firebase 설정
FIREBASE_URL    = "https://emucanlogger-default-rtdb.firebaseio.com/logs"
FIREBASE_SECRET = ""

# CAN ID 정의
EMU_ID_600 = 0x600  # RPM, TPS, IAT, MAP
EMU_ID_601 = 0x601  # Speed, Gear
EMU_ID_602 = 0x602  # CLT1, CLT2
EMU_ID_603 = 0x603  # EOT_IN, EOT_OUT
EMU_ID_604 = 0x604  # Battery Voltage

# 로그 디렉터리 및 파일 생성
if not os.path.exists("./logs"):
    os.makedirs("./logs")
CSV_FILENAME = f"./logs/emu_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

exit_flag = False
latest_data = {}

# === 파서 함수들 ===
def parse_emu_600(data):
    # RPM, TPS(%), IAT(°C), MAP(kPa)
    return {
        "RPM":          struct.unpack_from('<H', data, 0)[0],
        "TPS_percent":  data[2] * 0.5,
        "IAT_C":        struct.unpack_from('b', data, 3)[0],
        "MAP_kPa":      struct.unpack_from('<H', data, 4)[0]
    } if len(data) == 8 else {}

def parse_emu_601(data):
    # Speed(km/h), Gear 문자
    speed = struct.unpack_from('<H', data, 0)[0]
    gear  = chr(data[2]) if 32 <= data[2] <= 126 else "?"
    return {"Speed_kmh": speed, "Gear": gear} if len(data) == 8 else {}

def parse_emu_602(data):
    # CLT1, CLT2 온도
    return {
        "CLT1_C": struct.unpack_from('<H', data, 0)[0],
        "CLT2_C": struct.unpack_from('<H', data, 2)[0]
    } if len(data) == 8 else {}

def parse_emu_603(data):
    # EOT_IN, EOT_OUT 온도
    return {
        "EOT_IN_C":  struct.unpack_from('<H', data, 0)[0],
        "EOT_OUT_C": struct.unpack_from('<H', data, 2)[0]
    } if len(data) == 8 else {}

def parse_emu_604(data):
    # 배터리 전압
    return {"Battery_V": struct.unpack_from('<H', data, 2)[0] * 0.027} if len(data) == 8 else {}

# Firebase에 업로드
def upload_to_firebase(data):
    key = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    url = f"{FIREBASE_URL}/{key}.json?auth={FIREBASE_SECRET}"
    try:
        res = requests.put(url, json=data)
        print("Firebase 업로드 성공" if res.status_code == 200 else f"Firebase 실패 ({res.status_code})")
    except Exception as e:
        print("Firebase 오류:", e)

# 's' 키 누르면 종료 플래그 설정
def keypress_listener():
    global exit_flag
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        print("s 키를 누르면 종료됩니다.")
        while True:
            if sys.stdin.read(1).lower() == 's':
                exit_flag = True
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main():
    global exit_flag
    print(f"CSV 저장: {CSV_FILENAME}")
    print(f"Firebase 경로: {FIREBASE_URL}\n")

    # deprecation warning 제거
    bus = can.interface.Bus(channel='can0', interface='socketcan')
    threading.Thread(target=keypress_listener, daemon=True).start()

    with open(CSV_FILENAME, 'w', newline='') as csvfile:
        fieldnames = [
            "Timestamp","RPM","TPS_percent","IAT_C","MAP_kPa","Battery_V",
            "Speed_kmh","Gear","CLT1_C","CLT2_C","EOT_IN_C","EOT_OUT_C"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while not exit_flag:
            msg = bus.recv(timeout=0.1)
            if not msg:
                continue

            # ID에 맞춰 적절히 파싱
            parsers = {
                EMU_ID_600: parse_emu_600,
                EMU_ID_601: parse_emu_601,
                EMU_ID_602: parse_emu_602,
                EMU_ID_603: parse_emu_603,
                EMU_ID_604: parse_emu_604,
            }
            parsed = parsers.get(msg.arbitration_id, lambda d: {})(msg.data)
            if not parsed:
                continue

            latest_data.update(parsed)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            latest_data["Timestamp"] = ts
            writer.writerow(latest_data)

            # 값이 숫자일 때만 포맷 적용
            def fmt(v, f): return f"{v:{f}}" if isinstance(v,(int,float)) else f"{v}"

            print(
                f"[{ts}] | RPM:{fmt(latest_data.get('RPM','-'),'5')} | "
                f"TPS:{fmt(latest_data.get('TPS_percent','-'),'5.1f')}% | "
                f"IAT:{fmt(latest_data.get('IAT_C','-'),'4')}°C | "
                f"MAP:{fmt(latest_data.get('MAP_kPa','-'),'4')}kPa | "
                f"Batt:{fmt(latest_data.get('Battery_V','-'),'5.2f')}V | "
                f"SPD:{fmt(latest_data.get('Speed_kmh','-'),'5')}km/h | "
                f"Gear:{latest_data.get('Gear','-'):>2} | "
                f"CLT1:{fmt(latest_data.get('CLT1_C','-'),'3')}°C | "
                f"CLT2:{fmt(latest_data.get('CLT2_C','-'),'3')}°C | "
                f"EOT_IN:{fmt(latest_data.get('EOT_IN_C','-'),'4')}°C | "
                f"EOT_OUT:{fmt(latest_data.get('EOT_OUT_C','-'),'4')}°C"
            )

            # 0x600 프레임만 Firebase에 업로드
            if msg.arbitration_id == EMU_ID_600:
                upload_to_firebase(latest_data)

    bus.shutdown()  # 정상 종료
    print(f"\n로깅 종료. 파일: '{CSV_FILENAME}'")

if __name__ == "__main__":
    main()
