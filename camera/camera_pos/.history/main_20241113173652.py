# coding=utf-8

from PyQt5.QtWidgets import QMainWindow
from main_ui import Ui_Form

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        # 创建UI实例并设置UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)