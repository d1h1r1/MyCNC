import json
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np

# 加载数据
with open("../../file/point.json") as f:
    data = json.load(f)

# 转换为 numpy 数组
points = np.array(data)

# 构建 Delaunay 三角剖分
tri = Delaunay(points)

# 提取边界：从三角剖分中找出外边缘
edges = set()
for simplex in tri.simplices:
    for i in range(3):
        edge = tuple(sorted([simplex[i], simplex[(i + 1) % 3]]))
        if edge in edges:
            edges.remove(edge)
        else:
            edges.add(edge)

# 将边界重新连接成封闭路径
boundary_points = list(edges)
boundary_points = sorted(boundary_points, key=lambda edge: edge[0])  # 简单排序
path = [boundary_points[0][0]]
while len(path) < len(boundary_points):
    for edge in boundary_points:
        if edge[0] == path[-1]:
            path.append(edge[1])
            break
        elif edge[1] == path[-1]:
            path.append(edge[0])
            break

# 提取路径坐标
closed_path = points[path]
x_coords, y_coords = closed_path[:, 0], closed_path[:, 1]

# 绘制图形
plt.figure(figsize=(10, 8))
plt.plot(x_coords, y_coords, '-o', markersize=5, label='Closed Contour')
plt.scatter(points[:, 0], points[:, 1], color='blue', label='Points')  # 原始点
plt.title("Closed Contour Using Delaunay Triangulation", fontsize=16)
plt.xlabel("X Coordinate", fontsize=14)
plt.ylabel("Y Coordinate", fontsize=14)
plt.grid(True)
plt.legend()
plt.show()
