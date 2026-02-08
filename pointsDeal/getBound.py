from shapely.geometry import LineString, Polygon
import json
import numpy as np
import open3d as o3d
import alphashape
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from sklearn.cluster import DBSCAN
import shapely as sg


def intersects_any(line, polygons):
    """检测射线是否与任何障碍物相交"""
    for poly in polygons:
        if line.intersects(poly):
            return True
    return False


def find_clear_line(cx, cy, polygons, direction="x", step=10, max_shift=2000):
    """
    从中心点出发，沿指定方向寻找一条不与障碍物相交的线
    direction: "x" -> 水平线, "y" -> 垂直线
    """
    if direction == "x":
        # 初始射线 (水平线)
        line = LineString([(cx - max_shift, cy), (cx + max_shift, cy)])
        if not intersects_any(line, polygons):
            return line

        # 向上 / 向下 平移
        for shift in range(step, max_shift, step):
            line_up = LineString([(cx - max_shift, cy + shift), (cx + max_shift, cy + shift)])
            line_down = LineString([(cx - max_shift, cy - shift), (cx + max_shift, cy - shift)])
            if not intersects_any(line_up, polygons):
                return line_up
            if not intersects_any(line_down, polygons):
                return line_down

    elif direction == "y":
        # 初始射线 (垂直线)
        line = LineString([(cx, cy - max_shift), (cx, cy + max_shift)])
        if not intersects_any(line, polygons):
            return line

        # 向左 / 向右 平移
        for shift in range(step, max_shift, step):
            line_left = LineString([(cx - shift, cy - max_shift), (cx - shift, cy + max_shift)])
            line_right = LineString([(cx + shift, cy - max_shift), (cx + shift, cy + max_shift)])
            if not intersects_any(line_left, polygons):
                return line_left
            if not intersects_any(line_right, polygons):
                return line_right

    return None  # 没找到


# ==========================
# 1. 读取点云
# ==========================
with open("11.json", "r") as f:
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
print(points_clean)
print("=======================")
z_thresh = 19.2
points_high = points_clean[
    (points_clean[:, 2] > z_thresh + 10) & (points_clean[:, 2] < z_thresh + 100)
]
print(points_high)

print(f"原始点数: {len(points)}, 去噪后: {len(points_clean)}, 高于阈值点数: {len(points_high)}")

# ==========================
# 4. 聚类划分障碍物
# ==========================
# 只用平面坐标 (x, y)
X = points_high[:, :2]

db = DBSCAN(eps=40, min_samples=5).fit(X)  # eps 半径可调
labels = db.labels_

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
# print(f"检测到 {n_clusters} 个障碍物区域")

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

# ==================
# 集成到你的障碍物结果里
# ==================
# 统一收集所有障碍物 polygon
all_polygons = []
for cluster_id in set(labels):
    if cluster_id == -1:
        continue
    cluster_points = X[labels == cluster_id]
    if len(cluster_points) > 3:
        # print(cluster_points)
        # hull_shape = alphashape.alphashape(cluster_points, alpha=0.5)
        # print(hull_shape)
        hull_shape = sg.Polygon(cluster_points)

        if isinstance(hull_shape, Polygon):
            all_polygons.append(hull_shape)
        else:  # MultiPolygon
            all_polygons.extend(list(hull_shape.geoms))

# 长方体中心点 (假设已知)
cx, cy =  -121.85, -95.3415

line_x = find_clear_line(cx, cy, all_polygons, direction="x", step=20, max_shift=200)
line_y = find_clear_line(cx, cy, all_polygons, direction="y", step=20, max_shift=200)

# print(line_x, line_y)
# ==================
# 绘图
# ==================
plt.figure()
for poly in all_polygons:
    hx, hy = poly.exterior.xy
    plt.plot(hx, hy, "r-")

if line_x:
    lx, ly = line_x.xy
    plt.plot(lx, ly, "b--", label="X方向通道")
if line_y:
    lx, ly = line_y.xy
    plt.plot(lx, ly, "g--", label="Y方向通道")

plt.scatter([cx], [cy], c="black", marker="x", s=100, label="中心点")
plt.legend()
plt.axis("equal")
plt.title("从中心出发寻找平行X/Y轴的通道")
plt.show()
