import trimesh
from shapely import Polygon, unary_union

mesh = trimesh.load("6.stl")  # 加载模型
# 获取模型的边界框（AABB）
bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]
print(bounds)
min_x, min_y = bounds[0][0], bounds[0][1]  # XY最小值
max_x, max_y = bounds[1][0], bounds[1][1]  # XY最大值
print([[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]])
print(min_x, min_y, max_x, max_y)
exit()
# 投影：将三角面投影到 XY 平面
# 每个投影面是一个 2D 三角形（忽略 Z）
projected = mesh.copy()
projected.vertices[:, 2] = 0  # 把所有 Z 坐标设为 0

# 创建 2D 投影后的轮廓（封闭多边形）
polygons = []

for face in projected.faces:
    tri_pts = projected.vertices[face]
    poly = Polygon(tri_pts)
    if poly.is_valid and not poly.is_empty:
        polygons.append(poly)

# 合并所有三角形为一个大轮廓（可能带洞）
merged = unary_union(polygons)

# 如果合并结果是 MultiPolygon，只取最大外轮廓
if merged.geom_type == 'MultiPolygon':
    largest = max(merged.geoms, key=lambda p: p.area)
else:
    largest = merged

max_points = list(largest.exterior.coords)
print(max_points)
