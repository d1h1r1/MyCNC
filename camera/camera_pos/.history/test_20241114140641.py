import cv2
import cv2.aruco as aruco
import numpy as np

# 设置摄像头
cap = cv2.VideoCapture(0)

# 设置 ArUco 字典
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 将帧转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 检测 ArUco 标记
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    
    if ids is not None and len(ids) >= 2:  # 至少需要检测到两个标记
        # 绘制检测到的标记
        print(ids)
        aruco.drawDetectedMarkers(frame, corners, ids)
        
        # 假设我们检测到的两个 ArUco 标记的 ids 分别为 0 和 1
        # 可以根据需要调整或使用实际检测到的 ID 值
        if len(ids) >= 2:
            idx_2 = np.squeeze(np.where(ids == 2))[0]
            idx_1 = np.squeeze(np.where(ids == 1))[0]
            print(idx_2, idx_1)
            # 获取两个 ArUco 标记的角点坐标
            corners_2 = corners[idx_2][0]
            corners_1 = corners[idx_1][0]
            print("--------------------")
            print(corners_2, corners_1)
            print("--------------------")
            
            
            # # 计算板子的四个角点的坐标
            # top_left = corners_2[2]  # 假设左上角标记
            # bottom_right = corners_1[3]  # 假设右下角标记

            # # 计算裁剪区域的宽高
            # x, y = int(top_left[0]), int(top_left[1])
            # w, h = int(bottom_right[0] - top_left[0]), int(bottom_right[1] - top_left[1])

            # # 裁剪图像，确保区域不超出图像边界
            # cropped = frame[y:y + h, x:x + w]
            
            # 合并两个标记的角点
            all_corners = np.concatenate((corners_1, corners_2), axis=0)

            # 计算最小和最大坐标值
            x_min, y_min = np.min(all_corners, axis=0).astype(int)
            x_max, y_max = np.max(all_corners, axis=0).astype(int)

            # 裁剪图像
            cropped_frame = frame[y_min:y_max, x_min:x_max]
            
            # 放大图像到指定尺寸，比如宽度为 500 像素，高度按比例缩放
            scale_factor = 2  # 放大倍数
            new_width = cropped_frame.shape[1] * scale_factor
            new_height = cropped_frame.shape[0] * scale_factor
            resized_frame = cv2.resize(cropped_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # 显示裁剪后的图像
            if cropped_frame.size > 0:
                cv2.imshow("Cropped Board", cropped_frame)
    
    # 显示原始图像带有标记的画面
    cv2.imshow("Aruco Detection", frame)
    
    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
