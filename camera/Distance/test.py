import cv2
import numpy as np

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# x,y,distance
data = [
    (317, 233, 0),
    (300, 234, 10),
    (280, 234, 20),
    (260, 234, 30),
    (240, 234, 40),
]
X = np.array([[x, y] for x, y, _ in data])
y = np.array([d for _, _, d in data])

# 多项式拟合（2次）
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)


# 预测一个新点的距离
def predict_distance(x, y):
    input_poly = poly.transform([[x, y]])
    return model.predict(input_poly)[0]


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 60, 60])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 60, 60])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # _, mask_bright = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    # 限制亮度区间（去掉泛白区域，只保留激光点）
    mask_bright = cv2.inRange(gray, 200, 255)  # 调整 220 这个阈值

    mask_combined = cv2.bitwise_and(mask_red, mask_bright)

    # 找红点和最亮
    contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 找红点
    # contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_brightness = -1
    brightest_point = None
    best_contour = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 100 < area:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                brightness = gray[cy, cx]
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = w / h
                if not 0.8 <= aspect_ratio <= 1.2:
                    continue  # 不是接近正方形

                # 更新最亮点
                if brightness > max_brightness:
                    max_brightness = brightness
                    brightest_point = (cx, cy)
                    best_contour = cnt  # 保存该轮廓
    # 只绘制最亮红点
    if brightest_point:
        cx, cy = brightest_point
        cv2.circle(frame, (cx, cy), 6, (255, 0, 0), -1)
        cv2.putText(frame, f"({cx}, {cy}) L:{max_brightness}", (cx + 10, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        print(f"最亮红点位置: ({cx}, {cy})，亮度: {max_brightness}")
        # 测试
        print(f"预测 ({cx}, {cy}) 的距离: {predict_distance(cx, cy):.2f} cm")
        cv2.putText(frame, f"({predict_distance(cx, cy)}", (cx + 10, cy - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        # 用矩形框出轮廓
        x, y, w, h = cv2.boundingRect(best_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 蓝色框

    cv2.imshow("Red Bright Spot Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
