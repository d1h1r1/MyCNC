import json

import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.distance import cdist

# 加载数据
with open("../../file/point.json") as f:
    data = json.load(f)

# 转换为 numpy 数组
points = np.array(data)

# 找到最近邻路径
n_points = len(points)
unvisited = list(range(n_points))
path = [unvisited.pop(0)]  # 从第一个点开始

while unvisited:
    last_point = path[-1]
    distances = cdist([points[last_point]], points[unvisited])
    nearest_idx = unvisited[np.argmin(distances)]
    path.append(nearest_idx)
    unvisited.remove(nearest_idx)

# 回到起点形成封闭路径
path.append(path[0])

# 提取路径坐标
closed_path = points[path]
x_coords, y_coords = closed_path[:, 0], closed_path[:, 1]

# 绘制图形
plt.figure(figsize=(10, 8))
plt.plot(x_coords, y_coords, '-o', markersize=5, label='Closed Contour (Nearest Neighbor)')
plt.scatter(points[:, 0], points[:, 1], color='blue', label='Points')  # 原始点
plt.title("Closed Contour Using Nearest Neighbor", fontsize=16)
plt.xlabel("X Coordinate", fontsize=14)
plt.ylabel("Y Coordinate", fontsize=14)
plt.grid(True)
plt.legend()
plt.show()
