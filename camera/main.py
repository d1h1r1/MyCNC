# 轮廓提取、属性、近似轮廓、边界矩形和外接圆
import cv2
import cv2 as cv
import numpy as np
import cv2.aruco as aruco
import json
import time
import serial
import threading

ser = serial.Serial(port="COM23", baudrate=115200)
unlock_command = "$X\n"
home_command = "$H\n"
set_zero = "S0\n"
help_command = "$$\n"
state_command = "?\n"

drawing = False  # 标记是否在绘制
ix, iy = -1, -1  # 起始点坐标
x, y = 0, 0
axis = [0, 0, 0, 0]

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
aruco_params = cv2.aruco.DetectorParameters_create()
on_aruco = [-291.938, -9.666]
under_aruco = [-6.166, -133.086]
points_list = []
z_probe_command = [0, "G91G38.2Z-50F200\n", "G0Z2\n", "G38.2Z-3F30\n", "G90G01Z-3F1000\n"]
lx_probe_command = [0, 1, "G91G38.2X50F200\n", "G0X-2\n", "G38.2X3F30\n", "G0X-2F1000\n", "G90G01Z-3F1000\n"]
rx_probe_command = [0, 1, "G91G38.2X-50F200\n", "G0X2\n", "G38.2X-3F30\n", "G0X2F1000\n", "G90G01Z-3F1000\n"]
ony_probe_command = [0, 1, "G91G38.2Y-50F200\n", "G0Y2\n", "G38.2Y-3F30\n", "G0Y2F1000\n", "G90G01Z-3F1000\n"]
undery_probe_command = [0, 1, "G91G38.2Y50F200\n", "G0Y-2\n", "G38.2Y3F30\n", "G0Y-2F1000\n", "G90G01Z-3F1000\n"]


# time.sleep(3)
#
# data = ser.read_all()
# print(data.decode(), "==========")
#
# ser.write(home_command.encode())
# time.sleep(0.05)
# data = ser.read_all()
# print(data.decode(), "==========")
# s = input()
#
# ser.write(state_command.encode())
# time.sleep(0.05)
# data = ser.read_all()
# print(data.decode(), "==========")
# s = input()


def find_contour(img):
    # 转二进制
    imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # 阈值 二进制图像
    ret, binary = cv.threshold(imgray, 127, 255, 0)
    # 根据二值图找到轮廓
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    # 轮廓      层级                               轮廓检索模式(推荐此)  轮廓逼近方法
    # print(contours)
    filtered_contours = []
    areas = []
    approx_list = []
    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)  # 设置精度
        # 角数
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # 面积
        area = cv2.contourArea(contour)
        print(area)
        if 1000 < area < 50000:
            # if len(approx) == 4:
            approx_list.append(approx)
            areas.append(area)
            filtered_contours.append(contour)
    # min_index = areas.index(min(areas))
    # for point in approx_list[min_index]:
    #     cv2.circle(img, (point[0][0], point[0][1]), 1, (0, 255, 0), -1)  # 在角点位置绘制小圆圈
    #     cv2.putText(img, str(point[0][0]) + "," + str(point[0][1]), point[0], cv2.FONT_HERSHEY_SIMPLEX,
    #                 0.5, (255, 0, 0), 1)

    # image = cv.drawContours(img, filtered_contours[min_index], -1, (0, 0, 255), 1)
    #                           轮廓     第几个(默认-1：所有)   颜色       线条厚度
    return filtered_contours, areas, approx_list


def draw_rectangle(event, x, y, flags, param):
    global drawing
    if event == cv2.EVENT_LBUTTONDOWN:  # 按下鼠标左键时记录起始点
        drawing = True
        axis[0], axis[1] = x, y
        axis[2], axis[3] = x, y
    elif event == cv2.EVENT_MOUSEMOVE:  # 鼠标移动时更新框
        if drawing:
            axis[2], axis[3] = x, y
    elif event == cv2.EVENT_LBUTTONUP:  # 松开鼠标时绘制矩形框
        drawing = False
        axis[2], axis[3] = x, y


def get_aruco(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 检测 ArUco 标记
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    if ids is not None and len(ids) >= 2:  # 至少需要检测到两个标记
        # 绘制检测到的标记
        aruco.drawDetectedMarkers(img, corners, ids)
        # 假设我们检测到的两个 ArUco 标记的 ids 分别为 0 和 1
        # 可以根据需要调整或使用实际检测到的 ID 值
        if len(ids) >= 2:
            idx_2 = np.squeeze(np.where(ids == 2))[0]
            idx_1 = np.squeeze(np.where(ids == 1))[0]
            # 获取两个 ArUco 标记的角点坐标
            corners_2 = corners[idx_2][0]
            corners_1 = corners[idx_1][0]
            # 合并两个标记的角点
            all_corners = np.concatenate((corners_1, corners_2), axis=0)

            # 计算最小和最大坐标值
            x_min, y_min = np.min(all_corners, axis=0).astype(int)
            x_max, y_max = np.max(all_corners, axis=0).astype(int)
            # print(x_min, y_min, x_max, y_max)
            # 裁剪图像
            cropped_frame = img[y_min:y_max, x_min:x_max]
            scale = abs(under_aruco[0] - on_aruco[0]) / abs(x_max - x_min)
        else:
            return 0, 0
    else:
        return 0, 0
    return scale, cropped_frame


def grbl_control():
    for i in z_probe_command:
        if i == 0:
            z_probe_move = f"G90G01X{center_xy_real[0]}Y{center_xy_real[1]}F1000\n"
            ser.write(z_probe_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        else:
            ser.write(i.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
    s = input()
    data = ser.read_all()
    print("z_probe: ", data.decode(), "==========")
    all_str = data.decode()
    start_index = all_str.rfind("PRB") + 4
    end_index = all_str.rfind("]") - 2
    txt = "[" + all_str[start_index: end_index] + "]"
    z_coord = json.loads(txt)[2]
    print(z_coord)

    for i in lx_probe_command:
        if i == 0:
            l_probe_move = f"G90G01X{l_run_real[0]}Y{l_run_real[1]}F1000\n"
            ser.write(l_probe_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        elif i == 1:
            z_move = f"G90G01Z{z_coord - 1}F1000\n"
            ser.write(z_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        else:
            ser.write(i.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
    s = input()
    data = ser.read_all()
    print("l_probe: ", data.decode(), "==========")
    all_str = data.decode()
    start_index = all_str.rfind("PRB") + 4
    end_index = all_str.rfind("]") - 2
    txt = "[" + all_str[start_index: end_index] + "]"
    lx_coord = json.loads(txt)[0]
    print(lx_coord)

    for i in rx_probe_command:
        if i == 0:
            r_probe_move = f"G90G01X{r_run_real[0]}Y{r_run_real[1]}F1000\n"
            ser.write(r_probe_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        elif i == 1:
            z_move = f"G90G01Z{z_coord - 1}F1000\n"
            ser.write(z_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        else:
            ser.write(i.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
    s = input()
    data = ser.read_all()
    print("r_probe: ", data.decode(), "==========")
    all_str = data.decode()
    start_index = all_str.rfind("PRB") + 4
    end_index = all_str.rfind("]") - 2
    txt = "[" + all_str[start_index: end_index] + "]"
    rx_coord = json.loads(txt)[0]
    print(rx_coord)

    for i in ony_probe_command:
        if i == 0:
            on_probe_move = f"G90G01X{on_run_real[0]}Y{on_run_real[1]}F1000\n"
            ser.write(on_probe_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        elif i == 1:
            z_move = f"G90G01Z{z_coord - 1}F1000\n"
            ser.write(z_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        else:
            ser.write(i.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
    s = input()
    data = ser.read_all()
    print("on_probe: ", data.decode(), "==========")
    all_str = data.decode()
    start_index = all_str.rfind("PRB") + 4
    end_index = all_str.rfind("]") - 2
    txt = "[" + all_str[start_index: end_index] + "]"
    ony_coord = json.loads(txt)[1]
    print(ony_coord)

    for i in undery_probe_command:
        if i == 0:
            under_probe_move = f"G90G01X{under_run_real[0]}Y{under_run_real[1]}F1000\n"
            ser.write(under_probe_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        elif i == 1:
            z_move = f"G90G01Z{z_coord - 1}F1000\n"
            ser.write(z_move.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")
        else:
            ser.write(i.encode())
            time.sleep(0.05)
            data = ser.read_all()
            print(data.decode(), "==========")

    s = input()
    data = ser.read_all()
    print("under_probe: ", data.decode(), "==========")
    all_str = data.decode()
    start_index = all_str.rfind("PRB") + 4
    end_index = all_str.rfind("]") - 2
    txt = "[" + all_str[start_index: end_index] + "]"
    undery_coord = json.loads(txt)[1]
    print(undery_coord)

    center_coord = [(lx_coord + rx_coord) * 0.5, (ony_coord + undery_coord) * 0.5, z_coord]
    print(center_coord)

    s = input()
    xycenter_move = f"G90G01X{center_coord[0]}Y{center_coord[1]}F1000\n"
    ser.write(xycenter_move.encode())
    time.sleep(0.05)
    data = ser.read_all()
    print(data.decode(), "==========")

    s = input()
    zcenter_move = f"G90G01Z{center_coord[2]}F200\n"
    ser.write(zcenter_move.encode())
    time.sleep(0.05)
    data = ser.read_all()
    print(data.decode(), "==========")


if __name__ == '__main__':
    # s = input("""1：识别全部轮廓
    # 2: 框选轮廓：""")
    s = "1"
    drawing = False
    finish = False
    cap = cv2.VideoCapture(1)
    cv2.namedWindow("Camera")
    cv2.setMouseCallback("Camera", draw_rectangle)

    while True:
        ret, img = cap.read()
        scale, img = get_aruco(img)
        # print(scale)
        if scale == 0:
            continue
        cv2.rectangle(img, (axis[0], axis[1]), (axis[2], axis[3]), (0, 255, 0), 1)  #
        if s == "1":
            filtered_contours, areas, approx_list = find_contour(img)
            cv.drawContours(img, filtered_contours, -1, (0, 0, 255), 1)
            for approx in approx_list:
                for point in approx:
                    cv2.circle(img, (point[0][0], point[0][1]), 1, (0, 255, 0), -1)  # 在角点位置绘制小圆圈
                    cv2.putText(img, str(point[0][0]) + "," + str(point[0][1]), point[0], cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 0, 0), 1)
        cv2.imshow("Camera", img)
        key = cv2.waitKey(1) & 0xFF
        # if s == "2":
        if key == ord('y'):
            copy_img = img[axis[1]: axis[3], axis[0]: axis[2]]
            filtered_contours, areas, approx_list = find_contour(copy_img)
            # 计算最小和最大坐标值
            min_index = areas.index(min(areas))
            for point in approx_list[min_index]:
                cv2.circle(img, (point[0][0] + axis[0], point[0][1] + axis[1]), 1, (0, 255, 0), -1)  # 在角点位置绘制小圆圈
                cv2.putText(img, str(point[0][0] + axis[0]) + "," + str(point[0][1] + axis[1]),
                            (point[0][0] + axis[0], point[0][1] + axis[1]), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 0, 0), 1)
                points_list.append([point[0][0] + axis[0], point[0][1] + axis[1]])
            # print(points_list)
            if points_list[0][0] < points_list[3][0]:
                l_x = points_list[0][0]
            else:
                l_x = points_list[3][0]
            if points_list[1][0] > points_list[2][0]:
                r_x = points_list[1][0]
            else:
                r_x = points_list[2][0]
            if points_list[0][1] < points_list[1][1]:
                on_y = points_list[0][1]
            else:
                on_y = points_list[1][1]
            if points_list[2][1] > points_list[3][1]:
                under_y = points_list[2][1]
            else:
                under_y = points_list[3][1]
            center_xy = ((r_x + l_x) * 0.5, (under_y + on_y) * 0.5)
            cv2.circle(img, (int(center_xy[0]), int(center_xy[1])), 2, (0, 0, 255), -1)  # 在角点位置绘制小圆圈
            cv2.putText(img, str(center_xy[0]) + "," + str(center_xy[1]),
                        (int(center_xy[0]), int(center_xy[1])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            offset = 10
            l_run = (l_x - offset, center_xy[1])
            r_run = (r_x + offset, center_xy[1])
            on_run = (center_xy[0], on_y - offset)
            under_run = (center_xy[0], under_y + offset)

            cv2.circle(img, (int(l_run[0]), int(l_run[1])), 2, (0, 0, 255), -1)  # 在角点位置绘制小圆圈
            cv2.putText(img, str(l_run[0]) + "," + str(l_run[1]),
                        (int(l_run[0]), int(l_run[1])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

            cv2.circle(img, (int(r_run[0]), int(r_run[1])), 2, (0, 0, 255), -1)  # 在角点位置绘制小圆圈
            cv2.putText(img, str(r_run[0]) + "," + str(r_run[1]),
                        (int(r_run[0]), int(r_run[1])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

            cv2.circle(img, (int(on_run[0]), int(on_run[1])), 2, (0, 0, 255), -1)  # 在角点位置绘制小圆圈
            cv2.putText(img, str(on_run[0]) + "," + str(on_run[1]),
                        (int(on_run[0]), int(on_run[1])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

            cv2.circle(img, (int(under_run[0]), int(under_run[1])), 2, (0, 0, 255), -1)  # 在角点位置绘制小圆圈
            cv2.putText(img, str(under_run[0]) + "," + str(under_run[1]),
                        (int(under_run[0]), int(under_run[1])), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

            cv2.imshow("Camera", img)

            l_run_real = (
                round((l_x - offset) * scale + on_aruco[0], 3), round(on_aruco[1] - (center_xy[1]) * scale, 3))
            r_run_real = (
                round((r_x + offset) * scale + on_aruco[0], 3), round(on_aruco[1] - (center_xy[1]) * scale, 3))
            on_run_real = (
                round((center_xy[0]) * scale + on_aruco[0], 3), round(on_aruco[1] - (on_y - offset) * scale, 3))
            under_run_real = (
                round((center_xy[0]) * scale + on_aruco[0], 3), round(on_aruco[1] - (under_y + offset) * scale, 3))
            center_xy_real = (
                round(center_xy[0] * scale + on_aruco[0], 3), round(on_aruco[1] - (center_xy[1]) * scale, 3))
            print(center_xy_real)
            print(l_run_real, r_run_real, on_run_real, under_run_real)
            threading.Thread(target=grbl_control).start()
            cv2.waitKey(0)
