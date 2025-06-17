import cv2
import imutils
import numpy as np
from imutils import contours
from skimage import measure
import numpy as np
import cv2
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# x,y,distance
data = [
    (322, 237, 0),
    (312, 240, 10),
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


# 打开摄像头
cap = cv2.VideoCapture(0)  # 如果有多个摄像头设备，可以尝试 cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    # cv2.imshow('blurred', blurred)
    # cv2.waitKey(0)
    thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)[1]
    # cv2.imshow('thresh', thresh)
    # cv2.waitKey(0)
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)
    labels = measure.label(thresh, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    for label in np.unique(labels):
        if label == 0:
            continue
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        if numPixels > 100:
            mask = cv2.add(mask, labelMask)
    # cv2.imshow('mask', mask)
    # cv2.waitKey(0)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 40, 40])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # _, mask_bright = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    # 限制亮度区间（去掉泛白区域，只保留激光点）
    # mask_bright = cv2.inRange(gray, 150, 255)  # 调整 220 这个阈值

    mask_combined = cv2.bitwise_and(mask_red, mask.copy())
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    try:
        cnts = contours.sort_contours(cnts)[0]
    except:
        continue
    max_brightness = -1
    brightest_point = None
    best_contour = None
    for (i, c) in enumerate(cnts):
        area = cv2.contourArea(c)
        if 50 < area < 50000:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                (x, y, w, h) = cv2.boundingRect(c)
                aspect_ratio = w / h
                if not 0.8 <= aspect_ratio <= 1.2:
                    continue  # 不是接近正方形
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                brightness = gray[cy, cx]
                # 更新最亮点
                # 计算中心区域平均亮度（例如半径为5的圆区域）
                radius_check = 10
                mask_circle = np.zeros_like(gray, dtype=np.uint8)
                cv2.circle(mask_circle, (cx, cy), radius_check, 255, -1)
                mean_val = cv2.mean(gray, mask=mask_circle)[0]

                # 更新最亮点（用平均亮度）
                if mean_val > max_brightness:
                    max_brightness = mean_val
                    brightest_point = (cx, cy)
                    best_contour = c  # 保存该轮廓

                # cv2.circle(frame, (int(cX), int(cY)), int(radius),
                #            (0, 0, 255), 3)
                # cv2.putText(frame, "{}".format(i + 1), (x, y - 2),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    # 只绘制最亮红点
    if brightest_point:
        cx, cy = brightest_point
        cv2.circle(frame, (cx, cy), 6, (255, 0, 0), -1)
        cv2.putText(frame, f"({cx}, {cy}) L:{max_brightness}", (cx + 10, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        print(f"最亮红点位置: ({cx}, {cy})，亮度: {max_brightness}")
        # 测试
        print(f"距离: {round(predict_distance(cx, cy),3)}")
        cv2.putText(frame, f"({round(predict_distance(cx, cy),2)}", (cx + 10, cy - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        # 用矩形框出轮廓
        x, y, w, h = cv2.boundingRect(best_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 蓝色框
    # 显示画面
    cv2.imshow("Laser Distance Estimation", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
