from stl import mesh
import numpy as np
import matplotlib.pyplot as plt

# 读取 STL 文件
your_mesh = mesh.Mesh.from_file('../../file/elephant.stl')

# 提取三角形顶点
vertices = your_mesh.vectors.reshape(-1, 3)

# 投影到 XY 平面 (忽略 Z 坐标)
projected_points = vertices[:, :2]  # 只取 X 和 Y 坐标

# 获取包络轮廓（凸包）
from scipy.spatial import ConvexHull
hull = ConvexHull(projected_points)

# 绘制包络轮廓
plt.plot(projected_points[hull.vertices, 0], projected_points[hull.vertices, 1], 'r-', lw=2)
plt.plot(projected_points[:, 0], projected_points[:, 1], 'b.', markersize=2)
plt.show()
