import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QLabel, QTextEdit, QGridLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from pyqtgraph import PlotWidget, mkPen
from MainFlow import MainFlow  # 假设你的MainFlow类在一个单独的文件中
import numpy as np
import cv2

class FireRiskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fire Risk Monitoring')
        self.setGeometry(100, 100, 1600, 800)
        self.main_flow = None
        self.main_flow_thread = None
        self.event = threading.Event()

        # 创建一个中心小部件
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 创建一个水平的分割器
        splitter = QSplitter(Qt.Horizontal)
        # 创建一个frame用于显示图像
        self.image_frame = QLabel(self)
        self.frameLayout = QVBoxLayout()
        

        # 右侧的图像标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        # 第二个图像标签
        self.image_label2 = QLabel(self)
        self.image_label2.setAlignment(Qt.AlignCenter)
        # 第三个图像标签
        self.image_label3 = QLabel(self)
        self.image_label3.setAlignment(Qt.AlignCenter)
        # 将图像标签添加到frame中
        self.frameLayout.addWidget(self.image_label3)
        self.frameLayout.addWidget(self.image_label2)
        self.frameLayout.addWidget(self.image_label)
        self.image_frame.setLayout(self.frameLayout)
        splitter.addWidget(self.image_frame)

        # 左侧的布局
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 初始化数据
        self.x = []  # 时间轴
        self.y1 = []  # 数据序列1
        self.y2 = []  # 数据序列2
        self.y3 = []  # 数据序列3

        # 创建一个PlotWidget用于绘制折线图
        self.graphWidget = PlotWidget()
        left_layout.addWidget(self.graphWidget)
        # 设置一些图形属性
        self.graphWidget.setBackground('w')  # 白色背景
        self.graphWidget.setTitle("不同类型火灾风险度检测")  # 图表标题
        self.graphWidget.setLabel('left', '风险值', color='red', size=30)  # y轴标签
        self.graphWidget.setLabel('bottom', '时间', color='blue', size=30)  # x轴标签
        self.graphWidget.showGrid(x=True, y=True)  # 显示网格
        # 设置图例
        self.graphWidget.addLegend()

        # 绘制初始数据
        self.data_line1 = self.graphWidget.plot(self.x, self.y1, pen={'color': 'r', 'width': 5}, name='A')  # 红色线条
        self.data_line2 = self.graphWidget.plot(self.x, self.y2, pen={'color': 'g', 'width': 5}, name='B')  # 绿色线条
        self.data_line3 = self.graphWidget.plot(self.x, self.y3, pen={'color': 'b', 'width': 5}, name='CE')  # 蓝色线条

        # 日志文本框
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        left_layout.addWidget(self.log_text)
        # 设置字体
        self.font = QFont("MicrosoftYaHei", 24)  # 字体名称和字号
        self.log_text.setFont(self.font)

        # 添加重启按钮
        restart_button = QPushButton('重启 MainFlow', self)
        restart_button.clicked.connect(self.restart_main_flow)
        left_layout.addWidget(restart_button)

        # 将左侧布局添加到分割器
        splitter.addWidget(left_widget)

        # 将分割器添加到主布局
        layout.addWidget(splitter)

        # 创建一个定时器，用于更新UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

        # 初始化 MainFlow 实例
        self.init_main_flow()

    def init_main_flow(self):
        self.main_flow = MainFlow()
        self.main_flow_thread = threading.Thread(target=self.main_flow.run, args=(self.event,))
        self.main_flow_thread.start()
        print("MainFlow started.")

    def update_ui(self):
        # 更新图像
        if self.main_flow.cropped_img is not None:
            qimage = self.pil_to_qimage(self.main_flow.cropped_img)
            pixmap = QPixmap.fromImage(qimage)
            width = qimage.width()
            height = qimage.height()
            scale_rate = 2
            # 放大图像
            scaled_pixmap = pixmap.scaled(width*scale_rate, height*scale_rate, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

        # 更新第二个图像
        if self.main_flow.temp_with_rect is not None:
            qimage2 = self.cv_to_qimage(self.main_flow.temp_with_rect)
            pixmap2 = QPixmap.fromImage(qimage2)
            width2 = qimage2.width()
            height2 = qimage2.height()
            scale_rate2 = 1
            # 放大图像
            scaled_pixmap2 = pixmap2.scaled(width2*scale_rate2, height2*scale_rate2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label2.setPixmap(scaled_pixmap2)
        
        # 更新第三个图像
        if self.main_flow.rec_img is not None:
            qimage3 = self.pil_to_qimage(self.main_flow.rec_img)
            pixmap3 = QPixmap.fromImage(qimage3)
            width3 = qimage3.width()
            height3 = qimage3.height()
            scale_rate3 = 1
            # 放大图像
            scaled_pixmap3 = pixmap3.scaled(width3*scale_rate3, height3*scale_rate3, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label3.setPixmap(scaled_pixmap3)

        # 更新日志和图表前先检查数据是否可用
        if self.main_flow.detected_objects is not None and self.main_flow.risks is not None:
            self.log_text.clear()

            # 直接从数组中获取所有物体的名称
            object_names = ', '.join(self.main_flow.detected_objects)
            self.log_text.append(f"检测到物体：{object_names}, 最高温度：{self.main_flow.max_temp}")

            # 输出风险信息
            self.log_text.append(f"A类(普通固体材料)风险度：{self.main_flow.risks['A']}")
            self.log_text.append(f"B类(易燃液体)风险度：{self.main_flow.risks['B']}")
            self.log_text.append(f"C、E类(电气设备)风险度：{self.main_flow.risks['CE']}")

            # 更新数据
            new_x = len(self.x)
            self.x.append(new_x)
            x_part = self.x
            self.y1.append(self.main_flow.risks['A'])
            self.y2.append(self.main_flow.risks['B'])
            self.y3.append(self.main_flow.risks['CE'])

            # # 保持列表中元素的数量不超过20个
            threshold1 = 200
            threshold2 = 100
            if len(self.x) > threshold1:
                x_part = x_part[-threshold2:]  
                self.y1 = self.y1[-threshold2:]
                self.y2 = self.y2[-threshold2:]
                self.y3 = self.y3[-threshold2:]

            # 更新图形
            self.data_line1.setData(x_part, self.y1)
            self.data_line2.setData(x_part, self.y2)
            self.data_line3.setData(x_part, self.y3)

    def restart_main_flow(self):
        # 终止旧的线程
        if self.main_flow_thread is not None and self.main_flow_thread.is_alive():
            # self.main_flow.__del__()
            self.event.set()
            self.main_flow_thread.join()
            self.event.clear()

        # 创建新的 MainFlow 实例
        self.init_main_flow()

    @staticmethod
    def pil_to_qimage(pil_image):
        """Converts a PIL image to a QImage."""
        # 确保PIL图像的模式为RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # 将PIL图像转换为NumPy数组
        img_array = np.array(pil_image)
        
        # 确定颜色空间和QImage格式
        if img_array.shape[2] == 3:  # 检查图像是否有三个通道
            # 如果原始图像是RGB模式，则不需要转换
            qimage_format = QImage.Format_RGB888
        else:
            raise ValueError("Unsupported number of channels.")

        # 创建QImage
        qimage = QImage(img_array.data, img_array.shape[1], img_array.shape[0], img_array.strides[0], qimage_format)
        return qimage
    
    @staticmethod
    def cv_to_qimage(cv_image):
        """Converts an OpenCV image (numpy array) to a QImage."""
        # 确保图像的通道顺序是BGR
        if cv_image.shape[2] == 3:  # 检查图像是否有三个通道
            # 如果原始图像是BGR模式，将其转换为RGB
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        elif cv_image.shape[2] == 4:  # 检查图像是否有四个通道
            # 如果原始图像是BGRA模式，将其转换为RGBA
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
        else:
            raise ValueError("Unsupported number of channels.")
        
        # 创建QImage
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        return qimage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FireRiskApp()
    ex.show()
    sys.exit(app.exec_())