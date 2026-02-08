import json

import numpy as np
import open3d as o3d
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import shapely.geometry as sg

# === 1. 读取 JSON 点云数据 ===
with open("points24.json") as f:
    data = json.load(f)

points = np.array([[p['x'], p['y'], p['z']] for p in data])

# =========================
# 2. 点云去噪
# =========================
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

pcd_clean, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
points_clean = np.asarray(pcd_clean.points)
print(f"去噪后点数: {len(points_clean)}")

# =========================
# 3. 按 z 分层 + xy DBSCAN 聚类
# =========================
z_threshold = 5  # 每层 z 高度误差
eps_xy = 40  # xy 聚类距离阈值
min_samples = 20  # 平面上最少点数

planes = []
plane_labels = np.full(points_clean.shape[0], -1)  # 初始化为噪声
label_counter = 0

# 分层
unique_z_layers = np.unique(np.round(points_clean[:, 2] / z_threshold) * z_threshold)
for z_val in unique_z_layers:
    layer_idx = np.where(np.abs(points_clean[:, 2] - z_val) < z_threshold)[0]
    layer_points = points_clean[layer_idx][:, :2]  # 只用 xy 做聚类
    if len(layer_points) == 0:
        continue
    db = DBSCAN(eps=eps_xy, min_samples=min_samples).fit(layer_points)
    labels_layer = db.labels_
    for i, lbl in enumerate(labels_layer):
        if lbl != -1:
            plane_labels[layer_idx[i]] = label_counter + lbl
    label_counter += max(labels_layer) + 1 if max(labels_layer) != -1 else 0

num_planes = len(set(plane_labels)) - (1 if -1 in plane_labels else 0)
print(f"检测到 {num_planes} 个平面")

# =========================
# 4. 可视化不同平面
# =========================
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'cyan', 'magenta']
all_place = []
for i, lbl in enumerate(set(plane_labels)):
    if lbl == -1: continue  # 过滤掉噪点
    cluster_points = points_clean[plane_labels == lbl]
    if len(cluster_points) < 10: continue  # 过滤掉少点
    polyArea = sg.Polygon(cluster_points).area  # 输入多边形
    if polyArea < 10: continue # 过滤掉面积太小的区域
    all_place.append(cluster_points)
    color = 'black' if lbl == -1 else colors[i % len(colors)]
    ax.scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2],
               color=color, s=20, label=f"Plane {lbl}" if lbl != -1 else "Noise")

print(len(all_place))

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.title("按 z 分层 + xy DBSCAN 平面聚类")
plt.show()
