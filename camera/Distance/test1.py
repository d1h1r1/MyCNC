import cv2
import numpy as np
import math


# 相机参数 (需要根据实际相机进行标定)
FOCAL_LENGTH_PX = 800  # 焦距(像素)
SENSOR_WIDTH_MM = 6.17  # 传感器宽度(mm) 例如iPhone的1/2.55英寸传感器

def measure_position_offset(image, red_spot_contour, focal_length_px, sensor_width_mm):
    """
    计算红点相对于图像中心的位置偏移
    :param image: 输入图像
    :param red_spot_contour: 红点轮廓
    :param focal_length_px: 焦距(像素)
    :param sensor_width_mm: 传感器宽度(mm)
    :return: (水平偏移角度, 垂直偏移角度, 水平偏移距离, 垂直偏移距离)
    """
    # 获取图像中心坐标
    height, width = image.shape[:2]
    center_x, center_y = width // 2, height // 2

    # 计算红点中心坐标
    M = cv2.moments(red_spot_contour)
    spot_x = int(M['m10'] / M['m00'])
    spot_y = int(M['m01'] / M['m00'])

    # 计算像素偏移量
    pixel_offset_x = spot_x - center_x
    pixel_offset_y = center_y - spot_y  # 图像y轴向下为正，这里取反

    # 计算角度偏移(弧度)
    angle_offset_x = math.atan(pixel_offset_x / focal_length_px)
    angle_offset_y = math.atan(pixel_offset_y / focal_length_px)

    # 计算每像素对应的物理尺寸(mm/pixel)
    mm_per_pixel = sensor_width_mm / width

    # 计算实际偏移距离(mm)
    distance_offset_x = pixel_offset_x * mm_per_pixel
    distance_offset_y = pixel_offset_y * mm_per_pixel

    return angle_offset_x, angle_offset_y, distance_offset_x, distance_offset_y


def visualize_offsets(image, spot_contour, angle_x, angle_y, distance_x, distance_y):
    """可视化偏移量"""
    # 绘制图像中心十字线
    height, width = image.shape[:2]
    center_x, center_y = width // 2, height // 2
    cv2.line(image, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 2)
    cv2.line(image, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 2)

    # 绘制红点中心
    M = cv2.moments(spot_contour)
    spot_x = int(M['m10'] / M['m00'])
    spot_y = int(M['m01'] / M['m00'])
    cv2.circle(image, (spot_x, spot_y), 5, (0, 0, 255), -1)

    # 绘制中心到红点的连线
    cv2.line(image, (center_x, center_y), (spot_x, spot_y), (255, 0, 0), 2)

    # 显示偏移信息
    text1 = f"X Angle: {math.degrees(angle_x):.2f} deg, Y Angle: {math.degrees(angle_y):.2f} deg"
    text2 = f"X Offset: {distance_x:.2f} mm, Y Offset: {distance_y:.2f} mm"

    cv2.putText(image, text1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(image, text2, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    return image


def preprocess_image(image):
    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红斑的HSV范围（根据实际情况调整）
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # 创建红色区域的掩膜
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 形态学操作去除噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def detect_red_spots(image):
    mask = preprocess_image(image)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选较大的轮廓（根据实际情况调整面积阈值）
    min_area = 100
    red_spots = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            red_spots.append(cnt)

    return red_spots


def track_red_spot(video_source=0):
    # 初始化相机
    cap = cv2.VideoCapture(video_source)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 检测红斑
        red_spots = detect_red_spots(frame)

        if len(red_spots) > 0:
            largest_spot = max(red_spots, key=cv2.contourArea)

            # 计算偏移量
            angle_x, angle_y, dist_x, dist_y = measure_position_offset(
                frame, largest_spot, FOCAL_LENGTH_PX, SENSOR_WIDTH_MM)

            # 可视化
            frame = visualize_offsets(
                frame, largest_spot, angle_x, angle_y, dist_x, dist_y)

            # 可以在这里添加控制逻辑，比如控制云台对准红点
            # control_gimbal(angle_x, angle_y)

        cv2.imshow('Red Spot Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# 示例使用
if __name__ == "__main__":
    track_red_spot(1)

    #
    # # 读取图像
    # image = cv2.imread('img.png')
    #
    # # 检测红斑 (使用之前定义的detect_red_spots函数)
    # red_spots = detect_red_spots(image)
    #
    # if len(red_spots) > 0:
    #     # 只处理最大的红斑
    #     largest_spot = max(red_spots, key=cv2.contourArea)
    #
    #     # 计算偏移量
    #     angle_x, angle_y, dist_x, dist_y = measure_position_offset(
    #         image, largest_spot, FOCAL_LENGTH_PX, SENSOR_WIDTH_MM)
    #
    #     # 可视化结果
    #     result_image = visualize_offsets(
    #         image.copy(), largest_spot, angle_x, angle_y, dist_x, dist_y)
    #
    #     # 显示结果
    #     cv2.imshow('Position Offset Measurement', result_image)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    # else:
    #     print("未检测到红斑")

