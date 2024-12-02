from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QVBoxLayout, \
    QPushButton, QWidget, QSlider
import sys
import math
from svgpathtools import svg2paths


class DragableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.is_dragging = False  # 标记是否正在拖动
        self.last_pos = QPointF()  # 上次鼠标位置

    def wheelEvent(self, event):
        """重写滚轮事件，缩放视图"""
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9  # 根据滚轮的方向确定缩放因子
        self.scale(factor, factor)  # 调整视图缩放因子

    def mousePressEvent(self, event):
        """鼠标按下时开始拖动"""
        if event.button() == Qt.LeftButton:  # 按下左键
            self.is_dragging = True
            self.last_pos = event.pos()  # 记录当前鼠标位置
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动时拖动视图"""
        if self.is_dragging:
            delta = event.pos() - self.last_pos  # 计算鼠标移动的距离
            self.translate(delta.x(), delta.y())  # 移动视图
            self.last_pos = event.pos()  # 更新当前鼠标位置
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放时停止拖动"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()


class SvgEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置界面
        self.setWindowTitle("SVG Editor")
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene()
        self.view = DragableGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.scale(25, 25)  # 初始放大倍数
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)

        self.load_button = QPushButton("Load SVG")
        self.load_button.clicked.connect(self.load_svg)
        self.layout.addWidget(self.load_button)

        # 线条宽度调整滑块
        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setRange(0, 10)
        self.line_width_slider.setValue(3)  # 初始线条宽度
        self.line_width_slider.valueChanged.connect(self.update_line_width)
        self.layout.addWidget(self.line_width_slider)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.svg_item = None
        self.svg_paths = None
        self.line_width = 0

    def wheelEvent(self, event):
        """处理鼠标滚轮事件进行缩放"""
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9  # 放大或缩小因子
        self.view.scale(factor, factor)  # 调整视图缩放因子

    def load_svg(self):
        # 打开文件对话框选择SVG文件
        file_path = "../file/phone.svg"
        if file_path:
            self.svg_paths, _ = svg2paths(file_path)
            self.render_svg()

    def render_svg(self):
        """渲染SVG文件内容"""
        self.scene.clear()
        if self.svg_paths:
            for path in self.svg_paths:
                painter_path = QPainterPath()
                for segment in path:
                    if segment.__class__.__name__ == 'Line':
                        painter_path.moveTo(segment.start.real, segment.start.imag)
                        painter_path.lineTo(segment.end.real, segment.end.imag)
                    elif segment.__class__.__name__ == 'CubicBezier':
                        painter_path.moveTo(segment.start.real, segment.start.imag)
                        painter_path.cubicTo(segment.control1.real, segment.control1.imag,
                                             segment.control2.real, segment.control2.imag,
                                             segment.end.real, segment.end.imag)
                    elif segment.__class__.__name__ == 'QuadraticBezier':
                        painter_path.moveTo(segment.start.real, segment.start.imag)
                        painter_path.quadTo(segment.control.real, segment.control.imag,
                                            segment.end.real, segment.end.imag)
                    elif segment.__class__.__name__ == 'Arc':
                        painter_path.moveTo(segment.start.real, segment.start.imag)
                        painter_path.lineTo(segment.end.real, segment.end.imag)

                # 设置线条宽度
                pen = QPen(Qt.black)
                pen.setWidth(self.line_width)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)

                # 渲染路径到场景
                item = self.scene.addPath(painter_path, pen)
                item.setFlag(item.ItemIsMovable)
                item.setFlag(item.ItemIsSelectable)

    def update_line_width(self):
        """更新线条宽度"""
        self.line_width = self.line_width_slider.value()
        self.render_svg()  # 更新渲染


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SvgEditor()
    editor.show()
    sys.exit(app.exec_())
