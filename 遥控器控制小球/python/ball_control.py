import pygame
import serial
import sys
import serial.tools.list_ports
import random
import math

# 初始化Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("摇杆控制小球")

# 小球参数
BALL_RADIUS = 20
ball_x = WINDOW_WIDTH // 2
ball_y = WINDOW_HEIGHT // 2
BALL_SPEED = 5  # 基础速度
MAX_SPEED = 10  # 最大速度
ACCELERATION = 0.2  # 加速度
current_speed_x = 0
current_speed_y = 0

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 扩展颜色定义
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
COLORS = [BLUE, GREEN, YELLOW, PURPLE, ORANGE]

class Ball:
    def __init__(self, x, y, radius, color, speed=3):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.direction = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        
        # 碰到边界时反弹
        if self.x <= self.radius or self.x >= WINDOW_WIDTH - self.radius:
            self.direction = math.pi - self.direction
        if self.y <= self.radius or self.y >= WINDOW_HEIGHT - self.radius:
            self.direction = -self.direction
            
        # 确保位置在边界内
        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# 创建随机位置的小球
def create_random_balls(num_balls, player_pos):
    balls = []
    for i in range(num_balls):
        while True:
            x = random.randint(BALL_RADIUS, WINDOW_WIDTH - BALL_RADIUS)
            y = random.randint(BALL_RADIUS, WINDOW_HEIGHT - BALL_RADIUS)
            # 确保新球与玩家球的距离足够远
            if math.sqrt((x - player_pos[0])**2 + (y - player_pos[1])**2) > 100:
                balls.append(Ball(x, y, BALL_RADIUS, COLORS[i]))
                break
    return balls

# 碰撞检测
def check_collision(player_x, player_y, balls):
    for ball in balls:
        distance = math.sqrt((player_x - ball.x)**2 + (player_y - ball.y)**2)
        if distance < BALL_RADIUS * 2:
            return True
    return False

# 注释掉原有的串口检测代码
# ports = list(serial.tools.list_ports.comports())
# if not ports:
#     print("未找到任何可用的串口设备")
#     print("请确保Arduino已正确连接到电脑")
#     sys.exit()

# print("可用的串口设备：")
# for i, port in enumerate(ports):
#     print(f"{i}: {port.device} - {port.description}")

# 使用固定的串口地址
try:
    ser = serial.Serial('/dev/cu.usbmodem11301', 9600, timeout=1)
    print(f"成功连接到设备: /dev/cu.usbmodem11301")
except serial.SerialException as e:
    print(f"串口连接错误: {e}")
    print("请检查：")
    print("1. Arduino是否已正确连接到电脑")
    print("2. 是否有其他程序正在使用该串口")
    print("3. 是否有权限访问该串口（Linux/Mac可能需要sudo权限）")
    sys.exit()

def apply_deadzone(value, threshold=50):  # 降低死区阈值
    if abs(value - 512) < threshold:
        return 512
    return value

def smooth_movement(current, target, smooth_factor=0.1):
    return current + (target - current) * smooth_factor

def clean_data(data_str):
    """Parse data string in format 'X:value,Y:value,SW:value'"""
    try:
        parts = data_str.strip().split(',')
        if len(parts) != 3:  # 严格检查数据格式
            return None
            
        x_str = parts[0].split(':')[1] if ':' in parts[0] else ''
        y_str = parts[1].split(':')[1] if ':' in parts[1] else ''
        
        if x_str.isdigit() and y_str.isdigit():
            x_val = int(x_str)
            y_val = int(y_str)
            # 确保数值在有效范围内
            if 0 <= x_val <= 1023 and 0 <= y_val <= 1023:
                return x_val, y_val
    except Exception as e:
        print(f"数据解析错误: {e}")
    return None

# Replace print messages before main loop
print("Game initialized, waiting for serial data...")
print("Press Ctrl+C to exit")

# 初始化其他小球
other_balls = create_random_balls(5, (ball_x, ball_y))
game_over = False

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 添加重新开始游戏的功能
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                # 重置游戏
                ball_x = WINDOW_WIDTH // 2
                ball_y = WINDOW_HEIGHT // 2
                current_speed_x = 0
                current_speed_y = 0
                other_balls = create_random_balls(5, (ball_x, ball_y))
                game_over = False

    if not game_over:
        try:
            # 读取串口数据
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # 使用新的数据清理函数
                parsed_data = clean_data(line)
                if parsed_data:
                    x_raw, y_raw = parsed_data
                    
                    x_raw = apply_deadzone(x_raw)
                    y_raw = apply_deadzone(y_raw)
                    
                    # 调整映射逻辑
                    target_speed_x = (x_raw - 512) / 512.0 * MAX_SPEED
                    target_speed_y = (y_raw - 512) / 512.0 * MAX_SPEED
                    
                    # 增加速度系数
                    current_speed_x = smooth_movement(current_speed_x, target_speed_x, 0.4)
                    current_speed_y = smooth_movement(current_speed_y, target_speed_y, 0.4)
                    
                    # 更新位置
                    ball_x += current_speed_x
                    ball_y += current_speed_y
                    
                    # 边界检查
                    ball_x = max(BALL_RADIUS, min(WINDOW_WIDTH - BALL_RADIUS, ball_x))
                    ball_y = max(BALL_RADIUS, min(WINDOW_HEIGHT - BALL_RADIUS, ball_y))
                    
            # 更新其他小球位置
            for ball in other_balls:
                ball.move()

            # 检测碰撞
            if check_collision(ball_x, ball_y, other_balls):
                game_over = True
                print("游戏结束！按空格键重新开始")

        except serial.SerialException as e:
            print(f"串口通信错误: {e}")
            break  # 串口错误时退出程序
        except Exception as e:
            print(f"未知错误: {e}")
            continue

    # 绘制
    screen.fill(WHITE)
    
    # 绘制其他小球
    for ball in other_balls:
        ball.draw(screen)
    
    # 绘制玩家控制的红球
    pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)
    
    # 如果游戏结束，显示提示文字
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over - Space to Restart', True, (0, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.time.delay(16)  # 约60FPS

# 清理
ser.close()
pygame.quit()
