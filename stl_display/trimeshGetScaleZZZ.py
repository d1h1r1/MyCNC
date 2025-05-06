import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union

# 加载模型
mesh = trimesh.load('../file/U.stl')

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

# 显示
x, y = largest.exterior.xy
print(list(largest.exterior.coords))
plt.plot(x, y, 'r-')
plt.gca().set_aspect('equal')
plt.title("俯视投影最大外轮廓")
plt.show()
