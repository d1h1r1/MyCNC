import json
import numpy as np
import open3d as o3d
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import shapely.geometry as sg

# =========================
# 1. 读取 JSON 点云数据
# =========================
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
# 3. Z 方向 DBSCAN 聚类（自动分层）
# =========================
z_eps = 1  # Z 方向聚类阈值
min_samples_z = 20
z_vals = points_clean[:, 2].reshape(-1, 1)

db_z = DBSCAN(eps=z_eps, min_samples=min_samples_z).fit(z_vals)
z_labels = db_z.labels_

# =========================
# 4. XY DBSCAN 聚类（每层内）
# =========================
eps_xy = 40
min_samples_xy = 20
plane_labels = np.full(points_clean.shape[0], -1)
label_counter = 0

for z_lbl in set(z_labels):
    if z_lbl == -1:
        continue  # 忽略 Z 噪声点
    idx_layer = np.where(z_labels == z_lbl)[0]
    layer_points_xy = points_clean[idx_layer][:, :2]

    if len(layer_points_xy) == 0:
        continue

    db_xy = DBSCAN(eps=eps_xy, min_samples=min_samples_xy).fit(layer_points_xy)
    labels_xy = db_xy.labels_

    for i, lbl in enumerate(labels_xy):
        if lbl != -1:
            plane_labels[idx_layer[i]] = label_counter + lbl
    label_counter += max(labels_xy) + 1 if max(labels_xy) != -1 else 0

num_planes = len(set(plane_labels)) - (1 if -1 in plane_labels else 0)
print(f"检测到 {num_planes} 个平面")

# =========================
# 5. 可视化不同平面
# =========================
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'cyan', 'magenta']
all_planes = []

for i, lbl in enumerate(set(plane_labels)):
    if lbl == -1:
        continue  # 过滤噪声点
    cluster_points = points_clean[plane_labels == lbl]
    if len(cluster_points) < 10:
        continue  # 过滤小点簇

    polyArea = sg.Polygon(cluster_points[:, :2]).area  # XY 投影面积
    if polyArea < 10:
        continue  # 过滤面积太小
    z_max = np.max(cluster_points[:, 2])
    print(z_max)
    all_planes.append(cluster_points)
    color = colors[i % len(colors)]
    ax.scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2],
               color=color, s=20, label=f"Plane {lbl}")

print(f"有效平面数量: {len(all_planes)}")

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.title("Z DBSCAN + XY DBSCAN 平面聚类")
plt.show()
