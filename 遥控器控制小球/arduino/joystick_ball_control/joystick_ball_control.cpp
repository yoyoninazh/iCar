const int VRX_PIN = A0; // X轴模拟输入引脚
const int VRY_PIN = A1; // Y轴模拟输入引脚
const int SW_PIN = 2;   // 按钮数字输入引脚

int xValue = 0;
int yValue = 0;
int swValue = 0;

void setup() {
  Serial.begin(9600);
  pinMode(SW_PIN, INPUT_PULLUP);
}

void loop() {
  // 读取操纵杆值
  xValue = analogRead(VRX_PIN);
  yValue = analogRead(VRY_PIN);
  swValue = digitalRead(SW_PIN);

  // 发送数据到串口
  Serial.print("X:");
  Serial.print(xValue);
  Serial.print(",Y:");
  Serial.print(yValue);
  Serial.print(",SW:");
  Serial.println(swValue);

  delay(100); // 短暂延时以防数据发送过快
}
