#include <Arduino.h>

const int VRx_PIN = A0;
const int VRy_PIN = A1;
const int SW_PIN = 2;

// 数据平滑处理
const int SAMPLES = 5;  // 采样次数
int xSamples[SAMPLES];
int ySamples[SAMPLES];
int sampleIndex = 0;

// 计算平均值
int getAverage(int arr[], int size) {
  long sum = 0;
  for(int i = 0; i < size; i++) {
    sum += arr[i];
  }
  return sum / size;
}

void setup() {
  Serial.begin(9600);  // 改回9600波特率
  pinMode(SW_PIN, INPUT_PULLUP);
  
  // 初始化采样数组
  for(int i = 0; i < SAMPLES; i++) {
    xSamples[i] = 512;
    ySamples[i] = 512;
  }
}

void loop() {
  // 采样
  xSamples[sampleIndex] = analogRead(VRx_PIN);
  ySamples[sampleIndex] = analogRead(VRy_PIN);
  sampleIndex = (sampleIndex + 1) % SAMPLES;

  // 计算平均值
  int xValue = getAverage(xSamples, SAMPLES);
  int yValue = getAverage(ySamples, SAMPLES);
  int swState = digitalRead(SW_PIN);

  // 发送数据
  Serial.print("X:");
  Serial.print(xValue);
  Serial.print(",Y:");
  Serial.print(yValue);
  Serial.print(",SW:");
  Serial.println(swState);

  delay(20);  // 降低延时到20ms，提高响应速度
}