import cv2
import numpy as np

# 假设已知红斑的实际宽度为5cm，相机焦距为800像素
KNOWN_WIDTH = 5.0  # cm
FOCAL_LENGTH = 800  # 需要相机标定获得


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


def calculate_distance(image, red_spot_contour, known_width, focal_length):
    # 获取红斑的边界矩形
    x, y, w, h = cv2.boundingRect(red_spot_contour)

    # 计算红斑在图像中的像素宽度
    pixel_width = w

    # 计算距离 (已知物体宽度 × 焦距) / 图像中的像素宽度
    distance = (known_width * focal_length) / pixel_width

    return distance


# 读取图像
image = cv2.imread('img.png')

# 检测红斑
red_spots = detect_red_spots(image)

# 在原图上绘制红斑轮廓和距离信息
for spot in red_spots:
    # 绘制轮廓
    cv2.drawContours(image, [spot], -1, (0, 255, 0), 2)

    # 计算距离
    distance = calculate_distance(image, spot, KNOWN_WIDTH, FOCAL_LENGTH)

    # 获取轮廓中心点
    M = cv2.moments(spot)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    # 显示距离
    cv2.putText(image, f"{distance:.2f}cm", (cx - 50, cy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

# 显示结果
cv2.imshow('Red Spot Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
