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
        
    def set_cut_params(self, x1, y1, x2, y2):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        
    def transform_frame(self, frame):
        """
        Calibrate the camera according to the calibration parameters.
        Enlarge the video pixel by 2.2 times, which means enlarge the video size by 2.2 times.
        If two ARuco values have been calculated, clip the video.
        :param frame:
        :return: Judging whether it is recognized normally
        """
        try:
            # enlarge the image by 1.5 times
            fx = 2.2  # 1.5 -> origin param
            fy = 2.2  # 1.5
            frame = cv2.resize(frame, (0, 0), fx=fx, fy=fy,
                               interpolation=cv2.INTER_CUBIC)
            if self.x1 != self.x2:
                frame = frame[245:765, 510:1025]
                # 只保留白色板子区域，裁剪参数，frame[x1:x2,y1:y2]，其中x1和x2是裁剪画面上下范围区域，y1和y2是裁剪画面左右范围区域，x1越大，越往下裁剪，x2越大,越往下裁剪，y1 y2越大，越往右裁剪，反之往左裁剪
                # frame = frame[245:760, 498:1020]
                # the cutting ratio here is adjusted according to the actual situation
                # frame = frame[int(self.y2 * 0.8):int(self.y1 * 1.08),  # 0.78 1.1
                #         int(self.x1 * 0.89):int(self.x2 * 1.06)]  # 0.84 1.08
            return frame
        except Exception as e:
            self.loger.error('Interception failed' + str(e))
            pass

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
                x1, x2, y1, y2 = self.get_calculate_params(frame)
                self.draw_marker(frame, x1, y1)
                self.draw_marker(frame, x2, y2)
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
