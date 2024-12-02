import pyvista as pv
import numpy as np

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

# 创建新的网格，仅包含符合条件的点
filtered_contours = pv.PolyData(np.array(filtered_points))
point_list = []
for i in filtered_contours.points:
    point_list.append([i[0], i[1], i[2]])
    # print(i.x, end=",")
print(point_list)
# 可视化筛选后的轮廓
p = pv.Plotter()
# p.add_mesh(mesh, color="white", opacity=0.5, label="原始网格")
p.add_mesh(filtered_contours, color="red", line_width=3, label="Z=-3 外轮廓")
p.show()
