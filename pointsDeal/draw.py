import open3d as o3d
import numpy as np
import json
import matplotlib.pyplot as plt

# === 1. 读取点云数据 ===
with open("11.json") as f:
    data = json.load(f)
points = np.array([[p['x'], p['y'], p['z']] for p in data])

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

pcd_denoised, ind = pcd.remove_radius_outlier(nb_points=1, radius=10)
points = np.asarray(pcd_denoised.points)

# # === 2. 半径去噪 ===
# pcd_denoised, ind = pcd.remove_radius_outlier(nb_points=3, radius=20)
# points = np.asarray(pcd_denoised.points)

# === 3. 假设点是按扫描顺序存的（重要！）
xs, ys, zs = points[:,0], points[:,1], points[:,2]

# 3D 可视化
ax2 = plt.axes(projection="3d")
ax2.scatter(xs, ys, zs, s=1, c="gray")
ax2.scatter(xs, ys, zs, c='r', marker='^', s=50)
ax2.set_title("3D 点云中的凸起")

plt.show()
