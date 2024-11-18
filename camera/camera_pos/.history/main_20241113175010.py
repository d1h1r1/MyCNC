# coding=utf-8
import sys
import cv2

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from main_ui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 创建UI实例并设置UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.cap = cv2.VideoCapture(0)
        # 设置计时器来读取视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 刷新率，大约每秒显示 33 帧

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 将 BGR 格式转换为 RGB 格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 将 numpy 数组转换为 QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 设置 QLabel 显示视频帧
            self.label.setPixmap(QPixmap.fromImage(qt_img))

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())