import pyvista as pv
import numpy as np
from scipy.spatial import distance

# 读取 STL 文件
mesh = pv.read("../file/elephant.stl")

# 提取外轮廓 (使用 `extract_feature_edges`)
contours = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, non_manifold_edges=False)

# 设置 Z 坐标阈值，保留 Z 接近 -3 的线条
z_threshold = -3
tolerance = 0.1  # 设置一个容差值，根据需要调整

# 筛选出 z 接近 -3 的点
filtered_points = []
for point in contours.points:
    if np.abs(point[2] - z_threshold) < tolerance:  # 判断 z 值是否接近 -3
        filtered_points.append(point)

filtered_points = np.array(filtered_points)

# 计算所有点对之间的距离
dist_matrix = distance.cdist(filtered_points, filtered_points)

# 设置一个距离阈值，表示相邻点属于同一个轮廓
distance_threshold = 0.2  # 这个值可以根据具体情况调整

# 初始化轮廓分组
visited = np.zeros(len(filtered_points), dtype=bool)
contour_groups = []

# 遍历每个点，找到属于同一轮廓的点
for i, point in enumerate(filtered_points):
    if not visited[i]:
        # 新轮廓的起始点
        group = [i]
        visited[i] = True

        # 使用距离阈值进行连接
        to_visit = [i]
        while to_visit:
            current_point = to_visit.pop()
            # 找到所有与当前点距离小于阈值的点
            neighbors = np.where(dist_matrix[current_point] < distance_threshold)[0]
            for neighbor in neighbors:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    group.append(neighbor)
                    to_visit.append(neighbor)

        # 将这组点加入到轮廓组中
        contour_groups.append(filtered_points[group])

# 可视化所有闭合轮廓
p = pv.Plotter()

# 原始网格
p.add_mesh(mesh, color="white", opacity=0.5, label="原始网格")

# 绘制每个闭合轮廓
for idx, group in enumerate(contour_groups):
    contour_mesh = pv.PolyData(group)
    p.add_mesh(contour_mesh, color=np.random.rand(3, ), line_width=3, label=f"闭合轮廓 {idx + 1}")

p.show()
