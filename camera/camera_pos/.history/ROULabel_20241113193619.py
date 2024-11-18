from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen

class ROILabel(QLabel):
    roi_selected = pyqtSignal(QRect)  # 定义信号，用于传递选定的ROI区域

    def __init__(self, parent=None):
        super(ROILabel, self).__init__(parent)
        self.start_point = None  # 矩形的起点
        self.end_point = None    # 矩形的终点
        self.is_drawing = False  # 是否正在绘制

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.is_drawing = True
            self.update()  # 触发重绘

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()  # 触发重绘

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.is_drawing = False
            self.update()  # 触发重绘
            # 发出信号，传递选择的ROI区域
            roi_rect = QRect(self.start_point, self.end_point).normalized()
            self.roi_selected.emit(roi_rect)  # 传递选定的ROI区域

    def paintEvent(self, event):
        super(ROILabel, self).paintEvent(event)
        if self.start_point and self.end_point:
            # 在 QLabel 上绘制矩形
            painter = QPainter(self)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
