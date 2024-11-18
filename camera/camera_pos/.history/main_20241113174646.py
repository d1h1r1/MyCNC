# coding=utf-8
import sys


from PyQt5.QtWidgets import QMainWindow, QApplication
from main_ui import Ui_Form

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 创建UI实例并设置UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())