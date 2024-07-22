import serial
import base64
from datetime import datetime
from PIL import Image
import io

# 设置串口参数
ser = serial.Serial('COM6', 115200)  # 请替�?'COMX'为实际的串口�?


def save_image(base64_string):
    # 解码Base64字符串为字节�?
    image_bytes = base64.b64decode(base64_string)

    # 创建图像对象
    image = Image.open(io.BytesIO(image_bytes))

    # 获取当前时间作为时间�?
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # 保存图像，命名为时间�?
    image.save(f"{timestamp}.jpg")
    print(f"Saved image {timestamp}.jpg")


def process_received_data(data):
    if data.startswith(b"--start--") and data.endswith(b"--end--"):
        # 从数据中提取Base64编码的图像部�?
        base64_string = data[len(b"--start--"): -len(b"--end--")].strip()
        # 保存图像
        save_image(base64_string)
    else:
        print("Invalid data format:", data)


while True:
    # print("Waiting for data...")
    if ser.in_waiting > 0:
        # 从串口接收数�?
        received_data = ser.readline().strip()
        print("Received:", received_data)  # 打印接收到的数据
        # 处理接收到的数据
        process_received_data(received_data)