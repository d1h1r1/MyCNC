import json

import numpy as np
import matplotlib.pyplot as plt
import alphashape

with open("../file/point.json") as f:
    data = json.load(f)
# 假设点云是一个二维数组，每行是一个点 [x, y]
points = np.array(data)

# 使用 Alpha Shape 计算外轮廓
alpha = 1.5  # 调整 alpha 参数以控制外轮廓的精度
alpha_shape = alphashape.alphashape(points, alpha)

# 检查 alpha_shape 是否是 MultiPolygon 类型
if alpha_shape.geom_type == 'MultiPolygon':
    # 如果是 MultiPolygon，使用 geoms 获取多个 Polygon 对象
    for polygon in alpha_shape.geoms:
        boundary_points = np.array(list(polygon.exterior.coords))
        plt.plot(boundary_points[:, 0], boundary_points[:, 1], 'r-', label='Alpha Shape Boundary')
        plt.fill(boundary_points[:, 0], boundary_points[:, 1], 'r', alpha=0.2)
else:
    # 如果是单个 Polygon，直接提取外轮廓
    boundary_points = np.array(list(alpha_shape.exterior.coords))
    plt.plot(boundary_points[:, 0], boundary_points[:, 1], 'r-', label='Alpha Shape Boundary')
    plt.fill(boundary_points[:, 0], boundary_points[:, 1], 'r', alpha=0.2)

# 绘制点云
plt.plot(points[:, 0], points[:, 1], 'o', label='Points')
plt.legend()
plt.show()

# 输出 Alpha Shape 外轮廓的点
print("Alpha Shape boundary points:", boundary_points)
