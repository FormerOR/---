import threading
import Cam  
import Thermal  
import time
import numpy as np
import cv2
from tools import ImageDisplayer
import os
from datetime import datetime
import YOLOv8Detector
import FireRiskEstimator


class MainFlow:
    def __init__(self):
        self.CamReceiver = Cam.SerialImageReceiver(port='COM6', baudrate=115200)
        self.red_processor = Thermal.ThermalImageProcessor(port="COM8", baud_rate=115200, rect_size=20)
        self.displayer = ImageDisplayer()
        self.stop_event = threading.Event()
        self.img = None
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)
        self.cropped_img = None
        self.detector = YOLOv8Detector.YOLOv8Detector()
        self.fire_risk_estimator = FireRiskEstimator.FireRiskEstimator()
        self.max_temp = 0
        self.detect_objects = None
        self.risks = None

    def receive_and_save_images(self):
        try:
            while not self.stop_event.is_set():
                while True:
                    image = self.CamReceiver.receive_image()
                    if image is not None:
                        self.img = image
                        # self.CamReceiver.save_image(image)
                        print("...Cam img got√...")
                        # self.CamReceiver.pil_to_cv2_and_show(image)
        except Exception as e:
            print(f"Error in receive_and_save_images: {e}")
        finally:
            self.CamReceiver.close()

    def process_and_display(self):
        try:
            while not self.stop_event.is_set():
                self.red_processor.process_and_display()
        except Exception as e:
            print(f"Error in process_and_display: {e}")
    
    def crop_image(self, image, start, end):
        # 以矩形区域裁剪图像
        # start和end是矩形区域的左上角和右下角坐标
        self.cropped_img = image.crop((start[0], start[1], end[0], end[1]))
        return self.cropped_img
    
    def pil_to_cv2(self, pil_image):
        # Convert PIL image to NumPy array
        cv2_image = np.array(pil_image)
        
        # Convert RGB color space to BGR (OpenCV standard)
        if cv2_image.shape[2] == 3:  # Check if the image has three channels
            cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)
        
        return cv2_image
    
    def run(self):
        # 创建并启动线程
        thread_receive = threading.Thread(target=self.receive_and_save_images)
        thread_process = threading.Thread(target=self.process_and_display)
        thread_receive.start()
        thread_process.start()

        # 等待用户中断
        try:
            while True:
                self.rect_start, self.rect_end = self.red_processor.get_rect_coords()
                if self.img is not None:
                    self.crop_image(self.img, self.rect_start, self.rect_end)
                    cv2_img = self.pil_to_cv2(self.cropped_img)
                    self.displayer.cv2_display(cv2_img)
                    # 保存裁剪后的图像到cropped_imgs文件夹
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    cropped_img_path = os.path.join("cropped_imgs", f"{timestamp}.jpg")
                    cv2.imwrite(cropped_img_path, cv2_img)
                    # 使用YOLOv8检测物体
                    self.detected_objects = self.detector.predict_opencv_image(cv2_img)
                    self.max_temp = self.red_processor.get_max_temp()
                    # 估计火灾风险
                    dict = self.fire_risk_estimator.make_dict(self.detected_objects,self.max_temp)
                    self.risks = self.fire_risk_estimator.estimate_risks(dict, self.max_temp)
                    # print(self.risks)
                time.sleep(0.5)  # 防止主线程退出
        except KeyboardInterrupt:
            # 设置停止事件以通知线程退出
            self.stop_event.set()
            # 等待线程结束
            thread_receive.join()
            thread_process.join()
            print("Threads stopped.")

if __name__ == "__main__":
    main_flow = MainFlow()
    main_flow.run()