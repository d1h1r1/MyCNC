# coding=utf-8
import sys
import cv2

from PyQt5.QtWidgets import QMainWindow, QApplication
from main_ui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 创建UI实例并设置UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.cap = cv2.VideoCapture(0)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())