#include <SPI.h>
#include <mcp_can.h>

MCP_CAN CAN0(10);  // CS 핀

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));

  if (CAN0.begin(MCP_ANY, CAN_1000KBPS, MCP_8MHZ) == CAN_OK)
    Serial.println("CAN Initialized");
  else
    Serial.println("CAN Init Failed");

  CAN0.setMode(MCP_NORMAL);
}

void loop() {
  // 무작위 데이터 생성
  uint16_t rpm = random(800, 13000);       // 엔진 RPM
  uint8_t tps = random(0, 100);            // 스로틀 포지션
  int8_t iat = random(-20, 60);            // 흡기 온도
  uint16_t speed = random(0, 250);         // 속도 (km/h)
  uint16_t clt1 = random(20, 130);         // 냉각수 온도 1
  uint16_t clt2 = random(20, 130);         // 냉각수 온도 2
  uint16_t eot_in = random(30, 150);       // 오일 온도 IN
  uint16_t eot_out = random(30, 150);      // 오일 온도 OUT
  char gear = "N12345"[random(0, 6)];      // 기어: N, 1~5단 중 무작위

  // 각 데이터를 전송할 수 있도록 여러 프레임으로 나눔

  // Frame 1: 엔진 상태 (RPM, TPS, IAT)
  byte data1[8];
  data1[0] = rpm & 0xFF;
  data1[1] = rpm >> 8;
  data1[2] = tps;
  data1[3] = iat;
  data1[4] = 0;  // reserved
  data1[5] = 0;
  data1[6] = 0;
  data1[7] = 0;
  CAN0.sendMsgBuf(0x600, 0, 8, data1);

  // Frame 2: 속도 및 기어
  byte data2[8];
  data2[0] = speed & 0xFF;
  data2[1] = speed >> 8;
  data2[2] = gear;  // ASCII 문자
  data2[3] = 0;
  data2[4] = 0;
  data2[5] = 0;
  data2[6] = 0;
  data2[7] = 0;
  CAN0.sendMsgBuf(0x601, 0, 8, data2);

  // Frame 3: 냉각수 온도 CLT1, CLT2
  byte data3[8];
  data3[0] = clt1 & 0xFF;
  data3[1] = clt1 >> 8;
  data3[2] = clt2 & 0xFF;
  data3[3] = clt2 >> 8;
  data3[4] = 0;
  data3[5] = 0;
  data3[6] = 0;
  data3[7] = 0;
  CAN0.sendMsgBuf(0x602, 0, 8, data3);

  // Frame 4: 오일 온도 EOT IN, OUT
  byte data4[8];
  data4[0] = eot_in & 0xFF;
  data4[1] = eot_in >> 8;
  data4[2] = eot_out & 0xFF;
  data4[3] = eot_out >> 8;
  data4[4] = 0;
  data4[5] = 0;
  data4[6] = 0;
  data4[7] = 0;
  CAN0.sendMsgBuf(0x603, 0, 8, data4);

  // 디버깅 출력
  Serial.print("RPM: "); Serial.print(rpm);
  Serial.print(" | TPS: "); Serial.print(tps);
  Serial.print(" | IAT: "); Serial.print(iat);
  Serial.print(" | SPD: "); Serial.print(speed);
  Serial.print(" | GEAR: "); Serial.print(gear);
  Serial.print(" | CLT1: "); Serial.print(clt1);
  Serial.print(" | CLT2: "); Serial.print(clt2);
  Serial.print(" | EOT_IN: "); Serial.print(eot_in);
  Serial.print(" | EOT_OUT: "); Serial.println(eot_out);

  delay(500);
}
