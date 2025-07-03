# CAN-DataLogger
## 구성
- EMU BLACK
- 라즈베리파이 B3 +
- CAN to USB

## OVERVIEW

## WSL 에서 USB to CAN 연결
**powershell**
### 하드웨어 구성

``` powershell
usbipd list //현재 연결된 장치 확인
```
![image](https://github.com/user-attachments/assets/14f866a0-5d8c-4209-a59e-9be43a8ebf99)
![ECU-CAN-RASPI](https://github.com/user-attachments/assets/559677cb-8672-4a76-9522-492ca7da93d2)

``` bash
usbipd bind --busid [wsl에 연결할 장치의 BUSID ex)1-3 ] //성공시 STATE가 Shared로 되어야 함
- ECUMaster EMU BLACK  
- Raspberry Pi 3B+  
- USB-to-CAN 모듈  
- (테스트용) Arduino UNO R3 + MCP2515 CAN 모듈  

usbipd attach --wsl --busid [연결할 장치의 BUSID]
```
### 소프트웨어 구성

- Linux 기반의 **SocketCAN 인터페이스**를 사용하여 CAN 통신을 처리  
- `can-utils`는 SocketCAN 위에서 CAN 데이터를 수동으로 송수신할 수 있는 CLI 도구  
- Python의 `py-can` 라이브러리는 SocketCAN을 통해 CAN 데이터를 실시간으로 송수신 및 처리

## can-utils (https://github.com/linux-can/can-utils)
## Getting Start
만약 Rasberry Pi가 아닌 WSL에서 실행 시 아래와 같이 세팅
``` powershell
//powershell

usbipd list //현재 연결된 장치 확인
usbipd bind --busid <BUSID> //성공시 STATE가 Shared로 되어야 함
usbipd attach --wsl --busid <BUSID>
```

**LINUX**
### CAN 인터페이스 설정
Linux에서 ```can-utils```를 사용해 CAN0 인터페이스 초기화
``` bash
sudo apt-get update
sudo apt-get install can-utils
@@ -32,10 +39,17 @@ sudo ifconfig can0 up

candump can0 //성공 시 can메시지가 넘어오는 것을 볼 수 있음
```
### 로깅 스크립트 실행
``` bash
cd emu_logger_firebase
sudo python3 emu_logger_firebase.py
```

## WEB UI
### Main Dashboard
### 대시보드
```dashboard.html```
![image](https://github.com/user-attachments/assets/2db50bff-2fe6-4b85-9293-2717f42b307e)

### sensor_gragh(CLT IN, CLT OUT 추가예정)
### 센서그래프(수정 중)
```sensor_gragh.html```
![image](https://github.com/user-attachments/assets/b23ef203-c98f-4a2e-9498-21b9d3120dbd)
