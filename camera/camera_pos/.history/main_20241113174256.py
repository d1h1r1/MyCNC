# coding=utf-8
import sys


from PyQt5.QtWidgets import QMainWindow, QApplication
from main_ui import Ui_Form

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
class Main:
    def __init__(self):
        self.main_window = None
        self.main_ui = None
        
    def _init_main_window(self):
        self.main_window = MainWindow()
        self.main_ui = Ui_Form()
        self.main_ui.setupUi(self.main_window)
        
    
        
    def run(self):
        app = QApplication(sys.argv)
        self._init_main_window()
        self.main_window.show()
        sys.exit(app.exec_())
        
if __name__ == '__main__':
    