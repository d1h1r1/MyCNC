import numpy as np
import re
from scipy.optimize import leastsq
from skimage.measure import CircleModel, ransac

# 解析 G-code，提取 X 和 Y 坐标
gcode = """
; Postprocessed by [ArcWelder](https://github.com/FormerLurker/ArcWelderLib)
; Copyright(C) 2021 - Brad Hochgesang
; Version: 1.2.0, Branch: HEAD, BuildDate: 2021-11-21T20:25:43Z
; resolution=0.05mm
; path_tolerance=5.0%
; max_radius=9999.00mm
; g90_influences_extruder=True
; default_xyz_precision=3
; default_e_precision=5
; extrusion_rate_variance_percent=5.0%

G1 X-10.996 Y4.718 Z-2.496 F1000
G1 X-10.703 Y5.409 Z-2.496 F1000
G1 X-9.887 Y6.787 Z-2.500 F1000
G1 X-8.894 Y8.044 Z-2.500 F1000
G1 X-7.743 Y9.158 Z-2.500 F1000
G1 X-6.453 Y10.108 Z-2.500 F1000
G1 X-5.048 Y10.878 Z-2.500 F1000
G1 X-3.553 Y11.454 Z-2.500 F1000
G1 X-1.995 Y11.825 Z-2.500 F1000
G1 X-0.401 Y11.986 Z-2.500 F1000
G1 X1.200 Y11.932 Z-2.500 F1000
G1 X2.780 Y11.666 Z-2.500 F1000
G1 X4.310 Y11.191 Z-2.500 F1000
G1 X5.763 Y10.517 Z-2.500 F1000
G1 X7.114 Y9.655 Z-2.500 F1000
G1 X8.337 Y8.620 Z-2.500 F1000
G1 X9.412 Y7.432 Z-2.500 F1000
G1 X10.318 Y6.111 Z-2.500 F1000
G1 X11.041 Y4.682 Z-2.500 F1000
G1 X11.566 Y3.168 Z-2.500 F1000
G1 X11.885 Y1.598 Z-2.500 F1000
G1 X11.992 Y-0.000 Z-2.500 F1000
G1 X11.885 Y-1.598 Z-2.500 F1000
G1 X11.566 Y-3.168 Z-2.500 F1000
G1 X11.041 Y-4.682 Z-2.500 F1000
G1 X10.318 Y-6.111 Z-2.500 F1000
G1 X9.412 Y-7.432 Z-2.500 F1000
G1 X8.337 Y-8.620 Z-2.500 F1000
G1 X7.114 Y-9.655 Z-2.500 F1000
G1 X5.763 Y-10.517 Z-2.500 F1000
G1 X4.310 Y-11.191 Z-2.500 F1000
G1 X2.780 Y-11.666 Z-2.500 F1000
G1 X1.200 Y-11.932 Z-2.500 F1000
G1 X-0.401 Y-11.986 Z-2.500 F1000
G1 X-1.995 Y-11.825 Z-2.500 F1000
G1 X-3.553 Y-11.454 Z-2.500 F1000
G1 X-5.048 Y-10.878 Z-2.500 F1000
G1 X-6.453 Y-10.108 Z-2.500 F1000
G1 X-7.743 Y-9.158 Z-2.500 F1000
G1 X-8.894 Y-8.044 Z-2.500 F1000
G1 X-9.887 Y-6.787 Z-2.500 F1000
G1 X-10.703 Y-5.409 Z-2.500 F1000
G1 X-11.329 Y-3.934 Z-2.500 F1000
G1 X-11.752 Y-2.389 Z-2.500 F1000
G1 X-11.966 Y-0.801 Z-2.500 F1000
G1 X-11.966 Y0.799 Z-2.500 F1000
G1 X-11.752 Y2.385 Z-2.500 F1000
G2 X-11.330 Y3.929 I432.155 J-117.285
G1 X-10.996 Y4.718 Z-2.500 F1000

"""

# 正则表达式提取 X, Y 坐标
pattern = r"X([-+]?\d*\.\d+) Y([-+]?\d*\.\d+)"
matches = re.findall(pattern, gcode)
x = np.array([float(m[0]) for m in matches])
y = np.array([float(m[1]) for m in matches])


# 计算点到圆的距离
def calc_R(x, y, xc, yc):
    xc = 0
    yc = 0
    return np.sqrt((x - xc) ** 2 + (y - yc) ** 2)


# 误差函数
def f_2(c, x, y):
    Ri = calc_R(x, y, *c)
    return Ri - Ri.mean()


# 拟合圆
def fit_circle(x, y):
    x_m, y_m = np.mean(x), np.mean(y)  # 估计圆心
    center_estimate = x_m, y_m
    center, _ = leastsq(f_2, center_estimate, args=(x, y))
    Ri = calc_R(x, y, *center)
    print(Ri)
    R = Ri.mean()
    return center[0], center[1], R, Ri.std()  # 返回圆心、半径、标准差


# 执行拟合
xc, yc, R, std_dev = fit_circle(x, y)

# RANSAC 进一步优化（适合有离群点的情况）
points = np.column_stack((x, y))
ransac_model, inliers = ransac(points, CircleModel, min_samples=3, residual_threshold=0.5, max_trials=1000)
xc_ransac, yc_ransac, R_ransac = ransac_model.params

# 判断是否是圆
threshold_std = 0.8  # 设定标准差阈值
threshold_inlier = 0.9  # 设定 RANSAC 内点比例阈值

is_circle_std = std_dev < threshold_std
is_circle_ransac = np.sum(inliers) / len(points) > threshold_inlier
#
print(f"最小二乘法拟合圆心: ({xc:.2f}, {yc:.2f})")
print(f"最小二乘法拟合半径: {R:.2f}")
print(f"标准差: {std_dev:.2f}")
print(f"是否是圆（最小二乘法）: {'是' if is_circle_std else '否'}")

print(f"\nRANSAC 拟合圆心: ({xc_ransac:.2f}, {yc_ransac:.2f})")
print(f"RANSAC 拟合半径: {R_ransac:.2f}")
print(f"内点比例: {np.sum(inliers) / len(points):.2f}")
print(f"是否是圆（RANSAC）: {'是' if is_circle_ransac else '否'}")

print(np.sqrt((-11.966) ** 2 + (0) ** 2))