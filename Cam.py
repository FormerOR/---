import serial
import time
from PIL import Image
import io
import base64
from datetime import datetime
import os
import matplotlib.pyplot as plt
import cv2
import numpy as np

class SerialImageReceiver:
    def __init__(self, port='COM6', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate)
        self.START_MARKER = b"--start--"
        self.END_MARKER = b"--end--"
        self.buffer = bytearray()
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.dir_name = f"imgs/imgs_{self.timestamp}"
        self.img = None
        os.makedirs(self.dir_name, exist_ok=True)

    def receive_image(self):
        while True:
            data = self.ser.read(self.ser.in_waiting)
            self.buffer.extend(data)
            
            start_index = self.buffer.find(self.START_MARKER)
            end_index = self.buffer.find(self.END_MARKER)
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                base64_data = self.buffer[start_index+len(self.START_MARKER):end_index]
                # image_data = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(base64_data))
                del self.buffer[:end_index + len(self.END_MARKER)]
                self.img = image
                return image
            
            if start_index != -1 and end_index == -1:
                del self.buffer[:start_index]
            
            time.sleep(0.005)

    def save_image(self, img):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = os.path.join(self.dir_name, f"{timestamp}.jpg")
        img.save(image_path)
        # print(f"Saved image {timestamp}.jpg")

    # def show_image(self,img):
    #     """
    #     Display the given PIL Image instance using matplotlib.
        
    #     Parameters:
    #     img (PIL.Image.Image): The image to be displayed.
    #     """
    #     # Convert the image to RGB format if it's not already (useful for grayscale images)
    #     img_rgb = img.convert('RGB')
        
    #     # Show the image using matplotlib
    #     plt.imshow(img_rgb)
    #     plt.axis('off')  # Hide axes for cleaner display
    #     plt.show()

    # def pil_to_cv2_and_show(self,pil_image):
    #     """
    #     Converts a PIL Image to an OpenCV compatible format and displays it.
        
    #     Parameters:
    #     pil_image (PIL.Image.Image): The PIL image object to convert and display.
    #     """
    #     # Convert PIL image to NumPy array
    #     cv2_image = np.array(pil_image)
        
    #     # Check if the image is color (has three channels) and convert to BGR
    #     if cv2_image.shape[2] == 3:  # Check if the image has three channels
    #         cv2_image = cv2_image[:, :, ::-1].copy()  # Convert RGB to BGR
        
    #     # Display the image using OpenCV
    #     cv2.imshow('PIL Image converted to OpenCV', cv2_image)

    #     # Wait for a key press and exit on 'q'
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         cv2.destroyAllWindows()
        

    def get_image(self):
        return self.img

    def close(self):
        self.ser.close()


if __name__ == "__main__":
    receiver = SerialImageReceiver()
    try:
        while True:
            image = receiver.receive_image()
            if image is not None:
                receiver.save_image(image)
                # receiver.show_image(image)
                # receiver.pil_to_cv2_and_show(image)
    except KeyboardInterrupt:
        pass
    finally:
        receiver.close()