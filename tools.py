import cv2
import matplotlib.pyplot as plt
import numpy as np

class ImageDisplayer:
    def __init__(self):
        pass

    def display_cv2_image(self, cv2_image):
        """
        Display a cv2 image using matplotlib without blocking the main thread.
        
        Parameters:
        cv2_image (numpy.ndarray): The cv2 image to display.
        """
        # 开启matplotlib的交互模式
        plt.ion()
        # 创建一个新的figure和axis
        self.fig, self.ax = plt.subplots()
        # 初始化图像的显示
        self.image_plot = self.ax.imshow(np.zeros((10, 10, 3)), cmap='gray')
        # 隐藏坐标轴
        self.ax.axis('off')
        # 显示窗口，但不阻塞
        plt.show(block=False)
        # 确保图像为RGB格式，因为cv2使用BGR
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        # 更新图像数据
        self.image_plot.set_data(rgb_image)
        # 强制重绘
        self.fig.canvas.draw()
        # 暂停一小段时间，让matplotlib有时间处理事件
        plt.pause(0.001)

    def cv2_display(self, cv2_image, window_name="CV2 Image"):
        """
        Display a cv2 image in a non-blocking way using cv2.
        
        Parameters:
        cv2_image (numpy.ndarray): The cv2 image to display.
        window_name (str): The name of the window where the image will be displayed.
        """
        # 创建一个窗口
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # 设置窗口的宽度和高度
        scale_percent = 200  # 百分比
        width = int(cv2_image.shape[1] * scale_percent / 100)
        height = int(cv2_image.shape[0] * scale_percent / 100)
        cv2.resizeWindow(window_name, width, height)
        # 显示图像
        cv2.imshow(window_name, cv2_image)
        # 使用非阻塞等待，这里1毫秒足够短，可以保证非阻塞
        key = cv2.waitKey(1)
        # 如果用户按下了'q'键，则退出
        if key == ord('q'):
            cv2.destroyAllWindows()

