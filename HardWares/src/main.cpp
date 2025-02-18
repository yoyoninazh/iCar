#include <Arduino.h>

const int laserPin = 3;  // 激光连接的引脚
const int delayTime = 200;  // 延时时间

void toggleLaser(bool state);  // 声明 toggleLaser 函数

void setup() {
  pinMode(laserPin, OUTPUT);  // 设置激光引脚为输出
  Serial.begin(9600);  // 初始化串口
}

void loop() {
  toggleLaser(true);
  delay(delayTime);  // 延时 0.2 秒

  toggleLaser(false);
  delay(delayTime);  // 延时 0.2 秒
}

void toggleLaser(bool state) {
  digitalWrite(laserPin, state ? HIGH : LOW);  // 根据状态打开或关闭激光
  Serial.println(state ? "Laser ON" : "Laser OFF");
}