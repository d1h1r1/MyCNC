import cv2
import numpy as np
import math


def calculate_spot_height(image, spot_contour, camera_height, horizontal_distance, focal_length_px):
    """
    计算红点离水平面的高度
    :param image: 输入图像
    :param spot_contour: 红点轮廓
    :param camera_height: 相机离地面的高度(单位:米)
    :param horizontal_distance: 红点地面投影到相机的水平距离(单位:米)
    :param focal_length_px: 相机焦距(像素)
    :return: 红点离水平面的高度(单位:米)
    """
    # 获取图像尺寸和中心点
    height, width = image.shape[:2]
    center_y = height // 2

    # 计算红点中心y坐标
    M = cv2.moments(spot_contour)
    spot_y = int(M['m01'] / M['m00'])

    # 计算垂直方向像素偏移(相对于图像中心)
    pixel_offset = center_y - spot_y  # 图像y轴向下为正，所以用中心减去红点y坐标

    # 计算垂直方向角度偏移(弧度)
    angle_offset = math.atan(pixel_offset / focal_length_px)

    # 计算红点离水平面的高度
    spot_height = camera_height - horizontal_distance * math.tan(angle_offset)

    return spot_height


def visualize_measurement(image, spot_contour, spot_height, camera_height, horizontal_distance):
    """可视化测量结果"""
    # 绘制水平参考线
    height, width = image.shape[:2]
    center_y = height // 2
    cv2.line(image, (0, center_y), (width, center_y), (0, 255, 0), 2)

    # 标记红点
    M = cv2.moments(spot_contour)
    spot_x = int(M['m10'] / M['m00'])
    spot_y = int(M['m01'] / M['m00'])
    cv2.circle(image, (spot_x, spot_y), 8, (0, 0, 255), -1)

    # 显示测量信息
    info_text = [
        f"Camera Height: {camera_height:.2f}m",
        f"Horizontal Distance: {horizontal_distance:.2f}m",
        f"Spot Height: {spot_height:.2f}m"
    ]

    for i, text in enumerate(info_text):
        cv2.putText(image, text, (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # 绘制高度指示线
    if spot_height < camera_height:
        cv2.line(image, (spot_x, spot_y), (spot_x, center_y), (255, 0, 0), 2)
        cv2.putText(image, f"{camera_height - spot_height:.2f}m",
                    (spot_x + 10, (spot_y + center_y) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    return image


# 示例使用
if __name__ == "__main__":
    # 系统参数 (需要根据实际情况设置)
    CAMERA_HEIGHT = 1.5  # 相机离地面高度(米)
    HORIZONTAL_DISTANCE = 3.0  # 红点到相机的水平距离(米)
    FOCAL_LENGTH_PX = 800  # 相机焦距(像素)

    # 读取图像
    image = cv2.imread('red_spot_image.jpg')

    # 检测红斑 (使用之前定义的detect_red_spots函数)
    red_spots = detect_red_spots(image)

    if len(red_spots) > 0:
        # 只处理最大的红斑
        largest_spot = max(red_spots, key=cv2.contourArea)

        # 计算红点高度
        spot_height = calculate_spot_height(
            image, largest_spot, CAMERA_HEIGHT, HORIZONTAL_DISTANCE, FOCAL_LENGTH_PX)

        # 可视化结果
        result_image = visualize_measurement(
            image.copy(), largest_spot, spot_height, CAMERA_HEIGHT, HORIZONTAL_DISTANCE)

        # 显示结果
        cv2.imshow('Height Measurement', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(f"红点离水平面的高度: {spot_height:.2f}米")
    else:
        print("未检测到红斑")