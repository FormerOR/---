import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置主窗口标题
        self.setWindowTitle("Real-time Plot with PyQtGraph")
        
        # 创建一个中心小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建一个垂直布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 初始化数据
        self.x = []  # 时间轴
        self.y1 = []  # 数据序列1
        self.y2 = []  # 数据序列2
        self.y3 = []  # 数据序列3
        
        # 创建一个PlotWidget并添加到布局中
        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)
        
        # 设置一些图形属性
        self.graphWidget.setBackground('w')  # 白色背景
        self.graphWidget.setTitle("Real-Time Data Plotting")  # 图表标题
        self.graphWidget.setLabel('left', 'Values', color='black', size=30)  # y轴标签
        self.graphWidget.setLabel('bottom', 'Time', color='black', size=30)  # x轴标签
        self.graphWidget.showGrid(x=True, y=True)  # 显示网格
        
        # 绘制初始数据
        self.data_line1 = self.graphWidget.plot(self.x, self.y1, pen='r', name='Data 1')  # 红色线条
        self.data_line2 = self.graphWidget.plot(self.x, self.y2, pen='g', name='Data 2')  # 绿色线条
        self.data_line3 = self.graphWidget.plot(self.x, self.y3, pen='b', name='Data 3')  # 蓝色线条
        
        # 定时器，每秒更新数据
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start(1000)  # 每隔1000毫秒更新一次
        
    def update_plot_data(self):
        # 生成新数据点
        new_x = len(self.x)
        new_y1 = random.randint(0, 100)
        new_y2 = random.randint(0, 100)
        new_y3 = random.randint(0, 100)
        
        # 更新数据
        self.x.append(new_x)
        self.y1.append(new_y1)
        self.y2.append(new_y2)
        self.y3.append(new_y3)
        
        # 更新图形
        self.data_line1.setData(self.x, self.y1)
        self.data_line2.setData(self.x, self.y2)
        self.data_line3.setData(self.x, self.y3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())