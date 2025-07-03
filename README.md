# CAN-DataLogger
## 구성
- EMU BLACK
- 라즈베리파이 B3 +
- CAN to USB


## WSL 에서 USB to CAN 연결
**powershell**
``` powershell
usbipd list //현재 연결된 장치 확인
```
![image](https://github.com/user-attachments/assets/14f866a0-5d8c-4209-a59e-9be43a8ebf99)

``` bash
usbipd bind --busid [wsl에 연결할 장치의 BUSID ex)1-3 ] //성공시 STATE가 Shared로 되어야 함

usbipd attach --wsl --busid [연결할 장치의 BUSID]
```

---
## can-utils (https://github.com/linux-can/can-utils)
**LINUX**
``` bash
sudo ifconfig can0 down
sudo ip link set can0 type can bitrate 1000000 //비트레이트는 사용할 CAN BUS에 맞게 설정
sudo ifconfig can0 up

candump can0 //성공 시 can메시지가 넘어오는 것을 볼 수 있음
```
---
## WEB UI
### Main Dashboard
![image](https://github.com/user-attachments/assets/2db50bff-2fe6-4b85-9293-2717f42b307e)

### sensor_gragh(CLT IN, CLT OUT 추가예정)
![image](https://github.com/user-attachments/assets/b23ef203-c98f-4a2e-9498-21b9d3120dbd)
