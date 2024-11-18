# coding=utf-8
import sys
import cv2
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from main_ui import Ui_MainWindow
from custom_roi_label import ROILabel

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 创建UI实例并设置UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 使用自定义的ROILabel替换self.ui.label
        self.ui.label = ROILabel(self)
        self.ui.label.setGeometry(50, 50, 640, 480)
        self.ui.label.roi_selected.connect(self.on_roi_selected)  # 连接ROI选择信号
        
        # Get ArUco marker dict that can be detected.
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        # Get ArUco marker params.
        self.aruco_params = cv2.aruco.DetectorParameters_create()

        self.cap = cv2.VideoCapture(1)
        # 设置计时器来读取视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 刷新率，大约每秒显示 33 帧

        self.ui.pushButton.clicked.connect(self.take_photo)
        
    def get_calculate_params(self, img):
        # Convert the image to a gray image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # self ArUco marker.
        corners, ids, rejectImaPoint = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )
        """
        Two Arucos must be present in the picture and in the same order.
        There are two Arucos in the Corners, and each aruco contains the pixels of its four corners.
        Determine the center of the aruco by the four corners of the aruco.
        """
        if len(corners) > 0:
            if ids is not None:
                if len(corners) <= 1 or ids[0] == 1:
                    return None
                x1 = x2 = y1 = y2 = 0
                point_11, point_21, point_31, point_41 = corners[0][0]
                x1, y1 = int((point_11[0] + point_21[0] + point_31[0] + point_41[0]) / 4.0), int(
                    (point_11[1] + point_21[1] + point_31[1] + point_41[1]) / 4.0)
                point_1, point_2, point_3, point_4 = corners[1][0]
                x2, y2 = int((point_1[0] + point_2[0] + point_3[0] + point_4[0]) / 4.0), int(
                    (point_1[1] + point_2[1] + point_3[1] + point_4[1]) / 4.0)

                return x1, x2, y1, y2
        return None

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()  # 保存最后一帧
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            print("qt_img: ", qt_img)
            # print(self.get_calculate_params(frame))
            x1, x2, y1, y2 = self.get_calculate_params(frame)
            self.draw_marker(frame, x1, y1)
            self.draw_marker(frame, x2, y2)
            self.ui.label.setPixmap(QPixmap.fromImage(qt_img))
            
    # draw aruco
    def draw_marker(self, img, x, y):
        # draw rectangle on img
        cv2.rectangle(
            img,
            (x - 20, y - 20),
            (x + 20, y + 20),
            (0, 255, 0),
            thickness=2,
            lineType=cv2.FONT_HERSHEY_COMPLEX,
        )

    def take_photo(self):
        self.timer.stop()  # 停止视频显示
        # 将最后一帧图像固定在label中
        rgb_frame = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.ui.label.setPixmap(QPixmap.fromImage(qt_img))
        print("Timer stopped. You can now select ROI in the label.")

    def on_roi_selected(self, roi_rect):
        # 处理选定的ROI区域
        print("Selected ROI:", roi_rect)
        x, y, w, h = roi_rect.x(), roi_rect.y(), roi_rect.width(), roi_rect.height()
        print(f"ROI位置和大小：X={x}, Y={y}, Width={w}, Height={h}")
        
        # 从self.last_frame裁剪选择的区域
        selected_region = self.last_frame[y:y+h, x:x+w]
        # 可以在这里进一步处理选定的区域，例如显示在另一个标签中或保存

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
