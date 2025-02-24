#include <Arduino.h>

// 定义引脚
const int CLK_PIN = 2;  // CLK输出引脚连接到D2
const int DT_PIN = 3;   // DT输出引脚连接到D3
const int SW_PIN = 4;   // SW引脚连接到D4

// 全局变量
int counter = 0;          // 计数器
int currentStateCLK;      // CLK引脚当前状态
int lastStateCLK;         // CLK引脚上一状态
int btnState;             // 按钮状态
unsigned long lastButtonPress = 0;  // 上次按钮按下时间，用于消抖

void setup() {
  // 配置引脚
  pinMode(CLK_PIN, INPUT);
  pinMode(DT_PIN, INPUT);
  pinMode(SW_PIN, INPUT_PULLUP);  // 启用内部上拉电阻
  
  // 初始化串口通信
  Serial.begin(9600);
  Serial.println("旋转编码器测试程序");
  
  // 读取CLK引脚的初始状态
  lastStateCLK = digitalRead(CLK_PIN);
}

void loop() {
  // 读取当前CLK引脚状态
  currentStateCLK = digitalRead(CLK_PIN);

  // 如果CLK引脚状态发生变化，说明发生了旋转
  if (currentStateCLK != lastStateCLK) {
    // 如果DT引脚状态与CLK不同，说明是顺时针旋转
    if (digitalRead(DT_PIN) != currentStateCLK) {
      counter++;
      Serial.print("顺时针旋转 | 计数: ");
    } else {
      counter--;
      Serial.print("逆时针旋转 | 计数: ");
    }
    Serial.println(counter);
  }
  
  // 保存CLK引脚状态，供下次循环使用
  lastStateCLK = currentStateCLK;

  // 读取按钮状态
  btnState = digitalRead(SW_PIN);
  
  // 如果按钮被按下（LOW）且已经过了消抖延时
  if (btnState == LOW && (millis() - lastButtonPress) > 50) {
    Serial.println("按钮被按下！");
    counter = 0;  // 重置计数器
    Serial.println("计数器已重置为0");
    lastButtonPress = millis();
  }

  // 短暂延时，防止读取过快
  delay(1);
}