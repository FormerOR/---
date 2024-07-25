import cv2
import numpy as np
import serial
import time

class ThermalImageProcessor:
    def __init__(self, port="COM8", baud_rate=115200, rect_size=20):
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection
        
        self.target_width = 640
        self.target_height = 480
        self.scale_factor = 2.0
        self.rect_size = rect_size
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)
        self.max_temp = 0.0
        self.temp_with_rect = None

    def multi_stage_upscale(self, image):
        current_width, current_height = image.shape[1], image.shape[0]
        while current_width < self.target_width or current_height < self.target_height:
            next_width = min(int(current_width * self.scale_factor), self.target_width)
            next_height = min(int(current_height * self.scale_factor), self.target_height)
            image = cv2.resize(image, (next_width, next_height), interpolation=cv2.INTER_CUBIC)
            current_width, current_height = next_width, next_height
        return image
    
    def get_rect_coords(self):
        return self.rect_start, self.rect_end
    
    def get_max_temp(self):
        return self.max_temp

    def process_and_display(self):
        try:
            while True:
                line = self.ser.readline()
                if line:
                    decoded_line = line.decode('utf-8', errors='ignore').rstrip()
                    try:
                        temp_values = [float(val) for val in decoded_line.split(',') if val.strip()]
                    except ValueError:
                        continue
                    
                    if len(temp_values) == 768:
                        temp_array = np.array(temp_values).reshape(24, 32)
                        temp_normalized = cv2.normalize(temp_array, None, 0, 255, cv2.NORM_MINMAX)
                        temp_uint8 = temp_normalized.astype('uint8')
                        temp_resized = self.multi_stage_upscale(temp_uint8)
                        temp_colormap = cv2.applyColorMap(temp_resized, cv2.COLORMAP_JET)
                        
                        temp_smoothed = cv2.GaussianBlur(temp_colormap, (91, 91), 0)
                        temp_smoothed = cv2.GaussianBlur(temp_smoothed, (91, 91), 0)
                        temp_smoothed = cv2.GaussianBlur(temp_smoothed, (91, 91), 0)
                        
                        self.max_temp = np.amax(temp_array)
                        max_index = np.unravel_index(np.argmax(temp_array, axis=None), temp_array.shape)
                        max_row, max_col = max_index
                        
                        start_row = max(0, max_row - self.rect_size // 2)
                        end_row = min(24, max_row + self.rect_size // 2)
                        start_col = max(0, max_col - self.rect_size // 2)
                        end_col = min(32, max_col + self.rect_size // 2)
                        
                        temp_with_rect = temp_smoothed.copy()
                        cv2.rectangle(temp_with_rect, (start_col*20, start_row*20), (end_col*20, end_row*20), (255, 255, 255), 2)
                        self.rect_start = (start_col*20, start_row*20)
                        self.rect_end = (end_col*20, end_row*20)
                        self.temp_with_rect = temp_with_rect
                        
                        # Uncomment the following lines to display the image
                        # cv2.imshow('Thermal Image with Rectangle', temp_with_rect)
                        # if cv2.waitKey(1) & 0xFF == ord('q'):
                        #     break
        except KeyboardInterrupt:
            print("Program interrupted by user")
        finally:
            self.close_resources()

    def close_resources(self):
        if self.ser.is_open:  # Only close if the port is open
            try:
                self.ser.close()
                print("Serial port COM8 closed")
            except serial.SerialException as e:
                print(f"Failed to close serial port: {e}")
        
        # cv2.destroyAllWindows()
        print("OpenCV windows closed")

# Usage example
if __name__ == "__main__":
    processor = ThermalImageProcessor()
    processor.process_and_display()