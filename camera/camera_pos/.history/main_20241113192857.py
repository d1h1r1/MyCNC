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
        # self.showFullScreen()
        self.cap = cv2.VideoCapture(1)
        # 设置计时器来读取视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 刷新率，大约每秒显示 33 帧
        
        self.ui.pushButton.clicked.connect(self.take_photo)

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
            self.ui.label.setPixmap(QPixmap.fromImage(qt_img))
            self.current_frame = frame  # 保存当前帧供后续使用 = frame  # 保存当前帧供后续使用
        return frame
            
    def take_photo(self):
        self.timer.stop()
        if hasattr(self, 'current_frame'):
            # 使用当前帧捕获并显示 ROI 选择窗口
            roi = cv2.selectROI("Select ROI", self.current_frame, showCrosshair=False, fromCenter=False)
            if roi:
                # 提取 ROI
                x, y, w, h = roi
                roi_img = self.current_frame[y:y+h, x:x+w]
                
                # 将 ROI 显示在 QLabel 上
                roi_rgb = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)
                roi_qimage = QImage(roi_rgb.data, roi_rgb.shape[1], roi_rgb.shape[0], roi_rgb.shape[1] * 3, QImage.Format_RGB888)
                self.ui.label.setPixmap(QPixmap.fromImage(roi_qimage))
                cv2.destroyAllWindows()
        

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())