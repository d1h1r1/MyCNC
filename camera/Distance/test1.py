import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# 训练数据 (x, y, 距离cm)
data = [
    (317, 233, 0),
    (300, 234, 10),
    (280, 234, 20),
    (260, 234, 30),
    (240, 234, 40),
]

# 多项式回归模型
X = np.array([[x, y] for x, y, _ in data])
y = np.array([d for _, _, d in data])
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
model = LinearRegression()
model.fit(X_poly, y)


def predict_distance(x, y):
    """预测坐标对应的距离"""
    input_poly = poly.transform([[x, y]])
    return model.predict(input_poly)[0]


# 初始化摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 转换为HSV颜色空间（检测红色）
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义红色范围（0°-10° 和 160°-180°）
    lower_red1 = np.array([0, 50, 50])  # 低饱和度+高亮度，避免暗红色干扰
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # 提取红色区域
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # 提取高亮区域（亮度 > 220）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask_bright = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # 红色 + 高亮 = 激光点
    mask_laser = cv2.bitwise_and(mask_red, mask_bright)

    # 形态学处理（去除小噪点）
    kernel = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask_laser, cv2.MORPH_OPEN, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 找到面积最大的轮廓（激光点）
        largest_cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_cnt)

        # 忽略太小的噪点（面积 < 10 像素）
        if area > 10:
            # 计算质心
            M = cv2.moments(largest_cnt)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # 绘制激光点中心
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)  # 绿色中心点
            cv2.putText(frame, f"({cx}, {cy})", (cx + 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # 计算并显示预测距离
            distance = predict_distance(cx, cy)
            cv2.putText(frame, f"Dist: {distance:.1f}cm", (cx + 10, cy + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 显示检测结果
    cv2.imshow("Red Laser Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()