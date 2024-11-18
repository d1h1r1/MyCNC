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
        
        self._init_ = 20
        self.init_num = 0
        self.nparams = 0
        self.num = 0
        self.real_sx = self.real_sy = 0

        self.cap = cv2.VideoCapture(1)
        # 设置计时器来读取视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 刷新率，大约每秒显示 33 帧

        self.ui.pushButton.clicked.connect(self.take_photo)
        
    def set_cut_params(self, x1, y1, x2, y2):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        
    def transform_frame(self, frame):
        """Judging whether it is recognized normally"""
        try:
            # enlarge the image by 1.5 times
            fx = 1.5
            fy = 1.5
            frame = cv2.resize(frame, (0, 0), fx=fx, fy=fy,
                               interpolation=cv2.INTER_CUBIC)
            if self.x1 != self.x2:
                # the cutting ratio here is adjusted according to the actual situation
                frame = frame[int(self.y2 * 0.78):int(self.y1 * 1.1),
                        int(self.x1 * 0.84):int(self.x2 * 1.08)]
            return frame
        except Exception as e:
            # self.loger.error('Interception failed' + str(e))
            pass
        
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
        try:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame.copy()  # 保存最后一帧
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                print("qt_img: ", qt_img)
                # print(self.get_calculate_params(frame))
                if self._init_ > 0:
                    self._init_ -= 1
                    if self.camera_status:
                        # The video color is converted back to RGB, so that it is the realistic color
                        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Convert the read video data into QImage format
                        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                                    QtGui.QImage.Format_RGB888)
                        # Display the QImage in the Label that displays the video
                        self.show_camera_lab.setPixmap(QtGui.QPixmap.fromImage(showImage))
                        return

                # calculate the parameters of camera clipping
                QApplication.processEvents()
                if self.init_num < 20:
                    if self.get_calculate_params(frame) is None:
                        if self.camera_status:
                            show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                                        QtGui.QImage.Format_RGB888)
                            self.show_camera_lab.setPixmap(
                                QtGui.QPixmap.fromImage(showImage))
                        return
                    else:
                        x1, x2, y1, y2 = self.get_calculate_params(frame)
                        self.draw_marker(frame, x1, y1)
                        self.draw_marker(frame, x2, y2)
                        self.sum_x1 += x1
                        self.sum_x2 += x2
                        self.sum_y1 += y1
                        self.sum_y2 += y2
                        self.init_num += 1
                        return
                elif self.init_num == 20:
                    self.set_cut_params(
                        (self.sum_x1) / 20.0,
                        (self.sum_y1) / 20.0,
                        (self.sum_x2) / 20.0,
                        (self.sum_y2) / 20.0,
                    )
                    self.sum_x1 = self.sum_x2 = self.sum_y1 = self.sum_y2 = 0
                    self.init_num += 1
                    return

                # # calculate params of the coords between cube and mycobot
                QApplication.processEvents()
                if self.nparams < 10:
                    if self.get_calculate_params(frame) is None:
                        if self.camera_status:
                            show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                                        QtGui.QImage.Format_RGB888)
                            self.show_camera_lab.setPixmap(
                                QtGui.QPixmap.fromImage(showImage))
                        continue
                    else:
                        x1, x2, y1, y2 = self.get_calculate_params(frame)
                        self.draw_marker(frame, x1, y1)
                        self.draw_marker(frame, x2, y2)
                        self.sum_x1 += x1
                        self.sum_x2 += x2
                        self.sum_y1 += y1
                        self.sum_y2 += y2
                        self.nparams += 1
                        continue
                elif self.nparams == 10:
                    self.nparams += 1
                    # calculate and set params of calculating real coord between cube and mycobot
                    self.set_params(
                        (self.sum_x1 + self.sum_x2) / 20.0,
                        (self.sum_y1 + self.sum_y2) / 20.0,
                        abs(self.sum_x1 - self.sum_x2) / 10.0 +
                        abs(self.sum_y1 - self.sum_y2) / 10.0
                    )
                    self.loger.info("Color recognition ok")
                    continue
                self.ui.label.setPixmap(QPixmap.fromImage(qt_img))
        except:
            pass
            
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
