import serial
import time
from PIL import Image
import io
import base64
from datetime import datetime
import os

# 串行端口配置
port = 'COM6'  # 或者是 '/dev/ttyUSB0'
baudrate = 115200

# 打开端口
ser = serial.Serial(port, baudrate)

# 定义开始和结束标记
START_MARKER = b"--start--"
END_MARKER = b"--end--"

# 缓冲区用于存储接收到的数据
buffer = bytearray()

# 获取时间戳，新建文件夹用于存储图像，命名为imgs+格式月日时分秒格式
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
dir_name = f"imgs_{timestamp}"
# 创建文件夹
os.mkdir(f"imgs_{timestamp}")


def save_image(base64_string):
    # print("Decoded Data Preview:")
    # print(base64_string[:10])

    # 创建图像对象
    image = Image.open(io.BytesIO(base64_string))

    # 获取当前时间作为时间戳
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # 保存图像，命名为时间戳
    # image.save(f"{timestamp}.jpg")
    image.save(f"{dir_name}/{timestamp}.jpg")
    print(f"Saved image {timestamp}.jpg")

while True:
    data = ser.read(ser.in_waiting)  # 读取所有可用数据
    buffer.extend(data)  # 添加新数据到缓冲区
    
    start_index = buffer.find(START_MARKER)
    end_index = buffer.find(END_MARKER)
    
    while start_index != -1 and end_index != -1 and end_index > start_index:
        # 找到了一个完整数据包
        base64_data = buffer[start_index+len(START_MARKER):end_index]

        print("Received Data Preview:")
        print(base64_data[:10])
        
        # 清除已处理的数据
        del buffer[:end_index + len(END_MARKER)]
        
        # 处理数据包
        save_image(base64_data)
        
        # 查找下一个数据包的位置
        start_index = buffer.find(START_MARKER)
        end_index = buffer.find(END_MARKER)
    
    # 如果没有找到结束标记，则跳过开始标记
    if start_index != -1 and end_index == -1:
        del buffer[:start_index]
    
    time.sleep(0.01)  # 避免CPU占用过高