# coding=utf-8
import sys


from PyQt5.QtWidgets import QMainWindow, QApplication
from main_ui import Ui_Form

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
class Main:
    def __init__(self):
        self.main_window = MainWindow()
        self.main_ui = Ui_Form()
        self.main_ui.setupUi(self.main_window)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())