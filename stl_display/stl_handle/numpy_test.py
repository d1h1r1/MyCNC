import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import alphashape

# 读取 STL 文件
your_mesh = mesh.Mesh.from_file('../../file/elephant.stl')

# 提取三角形顶点
vertices = your_mesh.vectors.reshape(-1, 3)

# 投影到 XY 平面（忽略 Z 坐标）
projected_points = vertices[:, :2]  # 只取 X 和 Y 坐标

# 计算凸包
hull = ConvexHull(projected_points)

# 计算凹包
concave_hull = alphashape.alphashape(projected_points, alpha=0.5)

# 绘制结果
plt.figure(figsize=(8, 8))

# 绘制凸包
plt.plot(projected_points[hull.vertices, 0], projected_points[hull.vertices, 1], 'r-', lw=2, label="Convex Hull")

# 绘制凹包
if concave_hull is not None:
    x, y = concave_hull.exterior.coords.xy
    plt.fill(x, y, alpha=0.3, color='blue', label="Concave Hull")

# 绘制所有点
plt.plot(projected_points[:, 0], projected_points[:, 1], 'b.', markersize=2)

# 设置标签和标题
plt.title('2D Projection with Convex and Concave Hulls')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.axis('equal')
plt.show()
