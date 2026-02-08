import json
import numpy as np
import open3d as o3d
import alphashape
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from sklearn.cluster import DBSCAN

# ==========================
# 1. 读取点云
# ==========================
with open("boundPoints.json", "r") as f:
    data = json.load(f)

points = np.array([[p['x'], p['y'], p['z']] for p in data])

# ==========================
# 2. 点云去噪
# ==========================
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# 半径滤波
pcd, ind = pcd.remove_radius_outlier(nb_points=5, radius=20)
# 统计滤波
pcd, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

points_clean = np.asarray(pcd.points)

# ==========================
# 3. 筛选高度凸起点
# ==========================
z_thresh = 67
points_high = points_clean[points_clean[:, 2] > z_thresh]

print(f"原始点数: {len(points)}, 去噪后: {len(points_clean)}, 高于阈值点数: {len(points_high)}")

# ==========================
# 4. 聚类划分障碍物
# ==========================
# 只用平面坐标 (x, y)
X = points_high[:, :2]

db = DBSCAN(eps=40, min_samples=5).fit(X)  # eps 半径可调
labels = db.labels_

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f"检测到 {n_clusters} 个障碍物区域")

# ==========================
# 5. 每个障碍物生成 alpha-shape 轮廓
# ==========================
plt.figure()
for cluster_id in set(labels):
    if cluster_id == -1:
        continue  # -1 表示噪声点

    cluster_points = X[labels == cluster_id]
    plt.scatter(cluster_points[:, 0], cluster_points[:, 1], s=5, label=f'障碍物 {cluster_id}')

    if len(cluster_points) > 3:  # 至少能生成轮廓
        hull_shape = alphashape.alphashape(cluster_points, alpha=0.5)
        if isinstance(hull_shape, Polygon):
            hx, hy = hull_shape.exterior.xy
            plt.plot(hx, hy, 'r-')
        else:  # MultiPolygon
            for poly in hull_shape.geoms:
                hx, hy = poly.exterior.xy
                plt.plot(hx, hy, 'r-')

plt.axis('equal')
plt.legend()
plt.title("按区域划分的障碍物")
plt.show()
