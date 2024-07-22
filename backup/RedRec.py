import cv2
import numpy as np
import serial
import time

# 串口和波特率
arduino_port = "COM8"  # 请根据实际情况更改COM端口
baud = 115200  # 设置与Arduino代码中相同的波特率

# 创建串行对象
ser = serial.Serial(arduino_port, baud, timeout=1)

# 等待串口连接
time.sleep(2)

def multi_stage_upscale(image, target_width, target_height):
    """
    逐步放大图像到指定的目标分辨率，使用双三次插值以减少块效应。
    
    参数:
    image: 输入的图像，是一个numpy数组。
    target_width: 目标宽度。
    target_height: 目标高度。
    
    返回:
    upscaled_image: 放大后的图像。
    """
    # 当前宽度和高度
    current_width, current_height = image.shape[1], image.shape[0]
    
    # 放大比例，开始时设为2，可以根据需要调整
    scale_factor = 2.0
    
    while current_width < target_width or current_height < target_height:
        # 计算下一步的宽度和高度
        next_width = min(int(current_width * scale_factor), target_width)
        next_height = min(int(current_height * scale_factor), target_height)
        
        # 使用双三次插值放大图像
        image = cv2.resize(image, (next_width, next_height), interpolation=cv2.INTER_CUBIC)
        
        # 更新当前宽度和高度
        current_width, current_height = next_width, next_height
    
    return image

try:
    while True:
        # 读取一行数据
        line = ser.readline()
        
        # 检查是否读取到数据
        if line:
            decoded_line = line.decode('utf-8', errors='ignore').rstrip()
            # 将字符串数据转换成浮点数列表
            try:
                temp_values = [float(val) for val in decoded_line.split(',') if val.strip()]
            except ValueError:
                continue  # 如果转换失败，跳过当前循环

            if len(temp_values) == 768:  # 确保接收到完整的768个温度值
                # 将温度数据重塑成24x32的数组
                temp_array = np.array(temp_values).reshape(24, 32)
                
                # 标准化温度数据到0-255
                temp_normalized = cv2.normalize(temp_array, None, 0, 255, cv2.NORM_MINMAX)
                
                # 转换为8位无符号整型
                temp_uint8 = temp_normalized.astype('uint8')
                
                # 放大图像
                # temp_resized = cv2.resize(temp_uint8, (640, 480), interpolation=cv2.INTER_LANCZOS4)
                temp_resized = multi_stage_upscale(temp_uint8, 640, 480)

                # 应用伪彩色映射以提高可视化效果
                temp_colormap = cv2.applyColorMap(temp_resized, cv2.COLORMAP_JET)
                
                # 高斯滤波平滑处理
                temp_smoothed = cv2.GaussianBlur(temp_colormap, (91, 91), 0)
                # 二次平滑处理
                temp_smoothed = cv2.GaussianBlur(temp_smoothed, (91, 91), 0)
                # 三次平滑处理
                temp_smoothed = cv2.GaussianBlur(temp_smoothed, (91, 91), 0)
                
                # 找出最高温度点的坐标和绘制矩形框
                max_temp = np.amax(temp_array)
                max_index = np.unravel_index(np.argmax(temp_array, axis=None), temp_array.shape)
                max_row, max_col = max_index
                
                # 以最高温度点为中心，定义矩形框的大小
                rect_size = 12
                start_row = max(0, max_row - rect_size // 2)
                end_row = min(24, max_row + rect_size // 2)
                start_col = max(0, max_col - rect_size // 2)
                end_col = min(32, max_col + rect_size // 2)
                
                # 在原图像上绘制矩形框
                temp_with_rect = temp_smoothed.copy()
                cv2.rectangle(temp_with_rect, (start_col*20, start_row*20), (end_col*20, end_row*20), (255, 255, 255), 2)
                # 输出矩形框的四个顶点坐标
                print("Top-Left: ({}, {})".format(start_col, start_row))
                print("Bottom-Right: ({}, {})".format(end_col, end_row))

                
                # 显示带矩形框的热成像图
                cv2.imshow('Thermal Image with Rectangle', temp_with_rect)
                
                # 按'q'��出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
except KeyboardInterrupt:
    print("程序被用户中断")
finally:
    # 关闭串口连接
    ser.close()
    cv2.destroyAllWindows()