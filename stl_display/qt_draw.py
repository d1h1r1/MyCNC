import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QVBoxLayout, \
    QPushButton, QWidget, QSlider
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QColor
from svgpathtools import svg2paths


def calculate_center(x1, y1, x2, y2, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag):
    # 1. 计算弧线的中点
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx ** 2 + dy ** 2)

    # 2. 检查弧的有效性，确保 rx 和 ry 足够大来生成弧
    if dist > 2 * rx or dist > 2 * ry:
        raise ValueError("Arc cannot fit within the given radii.")

    # 3. 根据大弧标志和扫过标志计算参数
    angle = math.atan2(dy, dx)
    if sweep_flag == 0:
        angle += math.pi  # 逆时针
    if large_arc_flag == 1:
        angle += math.pi  # 大弧时的额外调整

    # 4. 基于这些参数计算圆心位置（简化版本）
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # 返回圆心坐标
    return (cx, cy)


class DragableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.is_dragging = False  # 标记是否正在拖动
        self.last_pos = QPointF()  # 上次鼠标位置

    def wheelEvent(self, event):
        """重写滚轮事件，缩放视图"""
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9
        self.scale(factor, factor)  # 调整视图缩放因子

    def mousePressEvent(self, event):
        """鼠标按下时开始拖动"""

        if event.button() == Qt.LeftButton:  # 按下左键
            print(1)
            self.is_dragging = True
            self.last_pos = event.pos()  # 记录当前鼠标位置
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动时拖动视图"""
        if self.is_dragging:
            delta = event.pos() - self.last_pos  # 计算鼠标移动的距离
            print(delta)
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
        self.view = QGraphicsView(self.scene)
        # self.view = DragableGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.scale(25, 25)  # 将视图放大10倍
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)

        # 加载按钮
        self.load_button = QPushButton("Load SVG")
        self.load_button.clicked.connect(self.load_svg)
        self.layout.addWidget(self.load_button)

        # 放大和缩小按钮
        # self.zoom_in_button = QPushButton("Zoom In")
        # self.zoom_in_button.clicked.connect(self.zoom_in)
        # self.layout.addWidget(self.zoom_in_button)
        #
        # self.zoom_out_button = QPushButton("Zoom Out")
        # self.zoom_out_button.clicked.connect(self.zoom_out)
        # self.layout.addWidget(self.zoom_out_button)

        # # 线条宽度调整滑块
        # self.line_width_slider = QSlider(Qt.Horizontal)
        # self.line_width_slider.setRange(0, 10)  # 设置线条宽度范围
        # self.line_width_slider.setValue(3)  # 初始线条宽度
        # self.line_width_slider.valueChanged.connect(self.update_line_width)
        # self.layout.addWidget(self.line_width_slider)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.svg_item = None
        self.svg_paths = None
        self.line_width = 0  # 默认线条宽度

    def wheelEvent(self, event):
        """处理鼠标滚轮事件进行缩放"""
        angle = event.angleDelta().y()  # 获取滚轮的旋转量
        factor = 1.1 if angle > 0 else 0.9  # 滚动向上时放大，向下时缩小
        self.view.scale(factor, factor)  # 调整视图缩放因子

    def load_svg(self):
        # 打开文件对话框选择SVG文件
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg)")
        file_path = "../file/phone.svg"
        if file_path:
            self.svg_paths, _ = svg2paths(file_path)
            self.render_svg()

    def render_svg(self):
        # 清空场景
        self.scene.clear()
        if self.svg_paths:
            for path in self.svg_paths:
                painter_path = QPainterPath()
                # 遍历路径段
                for segment in path:
                    # print(segment)
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
                        # x1, y1 = segment.start.real, segment.start.imag,  # 起点坐标
                        # x2, y2 = segment.end.real, segment.end.imag  # 终点坐标
                        # rx, ry = math.sqrt((x1 - x2)**2 + (y1 - y2)**2), math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                        # # rx, ry = segment.radius.real, segment.radius.imag  # 半径
                        # x_axis_rotation = segment.rotation  # 旋转角度
                        # large_arc_flag = segment.large_arc  # 小弧
                        # sweep_flag = segment.sweep  # 顺时针
                        #
                        # # 计算圆心
                        # cx, cy = calculate_center(x1, y1, x2, y2, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag)
                        # print(cx, cy)
                        # rect = QRectF(cx - rx, cy - ry, 2 * rx, 2 * ry)
                        #
                        # # 使用 arcTo 绘制弧线
                        # painter_path.arcTo(rect, 1 * 16, -2 * 16)

                        # painter = QPainter(self)
                        # painter.setRenderHint(QPainter.Antialiasing)
                        # # painter_path.moveTo(segment.start.real, segment.start.imag)
                        # #
                        # dx = segment.end.real - segment.start.real
                        # dy = segment.end.imag - segment.start.imag
                        # # 计算弧线中点
                        # xm = (segment.start.real + segment.end.real) / 2
                        # ym = (segment.start.imag + segment.end.imag) / 2
                        # # 计算椭圆的中心
                        # # 我们知道弧线上的两个点距离椭圆中心的距离为半径
                        # # 使用已知的 x 和 y 半径进行几何推算
                        # cx = xm + (segment.radius.real * dy / math.sqrt(dx ** 2 + dy ** 2))
                        # cy = ym - (segment.radius.imag * dx / math.sqrt(dx ** 2 + dy ** 2))
                        # # center = QPoint(cx, cy)
                        # # 圆的半径
                        # radius = segment.radius.real
                        # # 第一个点
                        # # point1 = QPoint(250, 200)  # 圆上的点
                        # # # 第二个点
                        # # point2 = QPoint(200, 100)  # 圆上的另一个点
                        #
                        # # 计算角度
                        # angle1 = math.degrees(math.atan2(segment.start.imag - cy, segment.start.real - cx))
                        # angle2 = math.degrees(math.atan2(segment.end.imag - cy, segment.end.real - cx))
                        #
                        # # 弧的起始角度和结束角度
                        # start_angle = angle1 * 16  # QPainter的角度单位是1/16度
                        # span_angle = (angle2 - angle1) * 16
                        # painter.setPen(QColor(0, 0, 0))  # 黑色笔刷
                        # rect = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
                        # painter.drawArc(rect, int(start_angle), int(span_angle))
                        # # # 计算起始角度和结束角度
                        # # start_angle = math.degrees(math.atan2(segment.start.imag - cy, segment.start.real - cx))
                        # # end_angle = math.degrees(math.atan2(segment.end.imag - cy, segment.end.real - cx))
                        # # # 创建QPainterPath对象
                        # # # 定义矩形：以椭圆的中心点为(cx, cy)，宽度为x半径，长度为y半径
                        # # rect = QRectF(cx - segment.radius.real, cy, 2 * segment.radius.real, 2 * segment.radius.imag)
                        # # # 绘制弧线
                        # painter_path.arcTo(rect, start_angle, end_angle - start_angle)

                        pass

                # 设置线条宽度
                pen = QPen(Qt.black)  # 黑色线条
                pen.setWidth(self.line_width)  # 设置线条宽度
                pen.setCapStyle(Qt.RoundCap)  # 设置线条端点样式
                pen.setJoinStyle(Qt.RoundJoin)  # 设置线条连接样式

                # 使用 QGraphicsPathItem 渲染 QPainterPath
                item = self.scene.addPath(painter_path, pen)
                item.setFlag(item.ItemIsMovable)  # 可以拖动路径
                item.setFlag(item.ItemIsSelectable)  # 可以选择路径

    # def zoom_in(self):
    #     """放大页面"""
    #     self.view.scale(1.2, 1.2)  # 将视图放大1.2倍
    #
    # def zoom_out(self):
    #     """缩小页面"""
    #     self.view.scale(0.8, 0.8)  # 将视图缩小0.8倍

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
