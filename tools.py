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
        # ����matplotlib�Ľ���ģʽ
        plt.ion()
        # ����һ���µ�figure��axis
        self.fig, self.ax = plt.subplots()
        # ��ʼ��ͼ�����ʾ
        self.image_plot = self.ax.imshow(np.zeros((10, 10, 3)), cmap='gray')
        # ����������
        self.ax.axis('off')
        # ��ʾ���ڣ���������
        plt.show(block=False)
        # ȷ��ͼ��ΪRGB��ʽ����Ϊcv2ʹ��BGR
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        # ����ͼ������
        self.image_plot.set_data(rgb_image)
        # ǿ���ػ�
        self.fig.canvas.draw()
        # ��ͣһС��ʱ�䣬��matplotlib��ʱ�䴦���¼�
        plt.pause(0.001)

    def cv2_display(self, cv2_image, window_name="CV2 Image"):
        """
        Display a cv2 image in a non-blocking way using cv2.
        
        Parameters:
        cv2_image (numpy.ndarray): The cv2 image to display.
        window_name (str): The name of the window where the image will be displayed.
        """
        # ����һ������
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # ���ô��ڵĿ�Ⱥ͸߶�
        scale_percent = 200  # �ٷֱ�
        width = int(cv2_image.shape[1] * scale_percent / 100)
        height = int(cv2_image.shape[0] * scale_percent / 100)
        cv2.resizeWindow(window_name, width, height)
        # ��ʾͼ��
        cv2.imshow(window_name, cv2_image)
        # ʹ�÷������ȴ�������1�����㹻�̣����Ա�֤������
        key = cv2.waitKey(1)
        # ����û�������'q'�������˳�
        if key == ord('q'):
            cv2.destroyAllWindows()

