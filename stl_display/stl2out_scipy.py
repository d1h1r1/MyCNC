import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

with open("../file/point.json") as f:
    data = json.load(f)
# 假设点云是一个二维数组，每行是一个点 [x, y]
points = np.array(data)

# 计算凸包
hull = ConvexHull(points)

# 提取凸包的顶点
hull_points = points[hull.vertices]

# 绘制点云和凸包
plt.plot(points[:, 0], points[:, 1], 'o', label='Points')
plt.plot(hull_points[:, 0], hull_points[:, 1], 'r-', label='Convex Hull')
plt.fill(hull_points[:, 0], hull_points[:, 1], 'r', alpha=0.2)
plt.legend()
plt.show()

# 输出凸包顶点
print("Convex Hull vertices:", hull_points)
