import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QVBoxLayout, \
    QPushButton, QWidget, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from svgpathtools import svg2paths


class SvgEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置界面
        self.setWindowTitle("SVG Editor")
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.scale(25, 25)  # 将视图放大10倍
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)

        # 加载按钮
        self.load_button = QPushButton("Load SVG")
        self.load_button.clicked.connect(self.load_svg)
        self.layout.addWidget(self.load_button)

        # 放大和缩小按钮
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.layout.addWidget(self.zoom_out_button)

        # 线条宽度调整滑块
        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setRange(0, 10)  # 设置线条宽度范围
        self.line_width_slider.setValue(3)  # 初始线条宽度
        self.line_width_slider.valueChanged.connect(self.update_line_width)
        self.layout.addWidget(self.line_width_slider)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.svg_item = None
        self.svg_paths = None
        self.line_width = 0  # 默认线条宽度

    def load_svg(self):
        # 打开文件对话框选择SVG文件
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg)")

        if file_path:
            self.svg_paths, _ = svg2paths(file_path)
            self.render_svg()

    def render_svg(self):
        # 清空场景
        self.scene.clear()
        flag = False
        if self.svg_paths:
            for path in self.svg_paths:
                painter_path = QPainterPath()

                # 遍历路径段
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
                        print(segment)
                        painter_path.moveTo(segment.start.real, segment.start.imag)
                        painter_path.arcTo(segment.start.real, segment.start.imag,
                                           abs(segment.end.real - segment.start.real), abs(segment.end.imag - segment.start.imag),
                                           segment.rotation, 180
                                           )

                # 设置线条宽度
                pen = QPen(Qt.black)  # 黑色线条
                pen.setWidth(self.line_width)  # 设置线条宽度
                pen.setCapStyle(Qt.RoundCap)  # 设置线条端点样式
                pen.setJoinStyle(Qt.RoundJoin)  # 设置线条连接样式

                # 使用 QGraphicsPathItem 渲染 QPainterPath
                item = self.scene.addPath(painter_path, pen)
                item.setFlag(item.ItemIsMovable)  # 可以拖动路径
                item.setFlag(item.ItemIsSelectable)  # 可以选择路径

    def zoom_in(self):
        """放大页面"""
        self.view.scale(1.2, 1.2)  # 将视图放大1.2倍

    def zoom_out(self):
        """缩小页面"""
        self.view.scale(0.8, 0.8)  # 将视图缩小0.8倍

    def update_line_width(self):
        """更新线条宽度"""
        self.line_width = self.line_width_slider.value()
        self.render_svg()  # 更新渲染

    def change_line_width(self, width):
        """动态调整线条宽度"""
        self.line_width = width
        self.render_svg()  # 更新渲染


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SvgEditor()
    editor.show()
    sys.exit(app.exec_())
