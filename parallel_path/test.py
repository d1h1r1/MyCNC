import json

import shapely.geometry as sg
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

# 输入原始多边形
with open("../file/point.json") as f:
    polygon_coords = json.load(f)
# polygon_coords = [(0, 0), (5, 0), (5, 5), (0, 5)]  # 示例坐标
original_polygon = sg.Polygon(polygon_coords)

# 设置平行切割线的间隔
cut_interval = 1  # 每个切割线之间的间隔
y_min, y_max = original_polygon.bounds[1], original_polygon.bounds[3]  # 获取多边形的y轴边界
# 生成平行切割线
cut_lines = []
y_position = y_min + cut_interval
while y_position < y_max:
    # 创建一条与x轴平行的线
    cut_line = sg.LineString([(original_polygon.bounds[0], y_position), 
                              (original_polygon.bounds[2], y_position)])
    cut_lines.append(cut_line)
    y_position += cut_interval

# 绘制原始多边形
fig, ax = plt.subplots()
x, y = original_polygon.exterior.xy
# ax.fill(x, y, alpha=0.5, fc='blue', label="Original Polygon")

# 遍历每条切割线并与多边形做交集
for cut_line in cut_lines:
    intersection = original_polygon.intersection(cut_line)
    # 绘制每条切割后的多边形
    # bounds = intersection.bounds
    # print(bounds)
    # print("start", (bounds[0], bounds[1]))
    # print("end", (bounds[2], bounds[3]))
    if isinstance(intersection, sg.LineString):
        # print(intersection.xy)
        # print("x1", intersection.xy[0][0])
        # print("x2", intersection.xy[0][1])
        # print("y1", intersection.xy[1][0])
        # print("y2", intersection.xy[1][1])
        print("point", (intersection.xy[0][0], intersection.xy[1][0]), (intersection.xy[0][1], intersection.xy[1][1]))
        pass
        # print(intersection.bounds)
    elif isinstance(intersection, sg.MultiLineString):
        for line in intersection.geoms:
            print("point", (line.xy[0][0], line.xy[1][0]),
                  (line.xy[0][1], line.xy[1][1]))
            # print(line)
        # print("============================================")
        pass
    #     x, y = intersection.exterior.xy
    # ax.fill(x, y, alpha=0.3, fc='red')

# 显示图形
plt.legend()
plt.show()
