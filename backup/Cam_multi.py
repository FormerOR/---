import serial
import time
from PIL import Image
import io
import base64
from datetime import datetime
import os
import threading

class SerialImageReceiver:
    def __init__(self, port='COM6', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate)
        self.START_MARKER = b"--start--"
        self.END_MARKER = b"--end--"
        self.buffer = bytearray()
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.dir_name = f"imgs_{self.timestamp}"
        os.makedirs(self.dir_name, exist_ok=True)
        self.received_image_event = threading.Event()
        self.image = None
        self.sleep_time = 0.01
        self.last_save_time = 0

    def _receive_image_thread(self):
        while not self.received_image_event.is_set():
            data = self.ser.read(self.ser.in_waiting)
            self.buffer.extend(data)
            
            start_index = self.buffer.find(self.START_MARKER)
            end_index = self.buffer.find(self.END_MARKER)
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                base64_data = self.buffer[start_index+len(self.START_MARKER):end_index]
                # image_data = base64.b64decode(base64_data)
                self.image = Image.open(io.BytesIO(base64_data))
                del self.buffer[:end_index + len(self.END_MARKER)]
                self.received_image_event.set()
            
            if start_index != -1 and end_index == -1:
                del self.buffer[:start_index]
            
            time.sleep(self.sleep_time)

    def receive_image(self):
        if not self.received_image_event.is_set():
            self.received_image_event.clear()
            self.receive_thread = threading.Thread(target=self._receive_image_thread)
            self.receive_thread.start()
            self.receive_thread.join()  # 等待线程完成
        return self.image

    def save_image(self, img):
        current_time = time.time()
        if current_time - self.last_save_time >= 1.0:
            self.last_save_time = current_time
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_path = os.path.join(self.dir_name, f"{timestamp}.jpg")
            img.save(image_path)
            print(f"Saved image {timestamp}.jpg")

    def close(self):
        self.ser.close()
        self.received_image_event.set()


if __name__ == "__main__":
    receiver = SerialImageReceiver()
    try:
        while True:
            image = receiver.receive_image()
            if image is not None:
                receiver.save_image(image)
    except KeyboardInterrupt:
        pass
    finally:
        receiver.close()