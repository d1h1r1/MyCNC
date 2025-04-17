from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt

# 外轮廓（矩形）
outer = Polygon([
    (0, 0),
    (10, 0),
    (10, 10),
    (0, 10)
])

# 创建两个内轮廓（需要减去的区域）
hole1 = Polygon([
    (2, 2),
    (4, 2),
    (4, 4),
    (2, 4)
])

hole2 = Polygon([
    (6, 6),
    (8, 6),
    (8, 8),
    (6, 8)
])

# 将所有内轮廓合并成一个 geometry（组合）
holes_union = unary_union([hole1, hole2])

# 求差集：外轮廓 - 所有内轮廓
pocket = outer.difference(holes_union)

# 储存所有缩小的路径
paths = []

# 初始区域
current = pocket
step = 0.05  # 每次缩小的距离

while not current.is_empty and current.area > 0.1:
    paths.append(current)
    current = current.buffer(-step)

# === 可视化 ===
fig, ax = plt.subplots(figsize=(6, 6))
colors = plt.cm.viridis_r  # colormap

for i, path in enumerate(paths):
    color = colors(i / len(paths))
    if path.geom_type == 'Polygon':
        xs, ys = path.exterior.xy
        ax.fill(xs, ys, color=color, alpha=0.6, edgecolor='black')
    elif path.geom_type == 'MultiPolygon':
        for geom in path.geoms:
            xs, ys = geom.exterior.xy
            ax.fill(xs, ys, color=color, alpha=0.6, edgecolor='black')

ax.set_title("逐步缩小的区域（pocketing）")
ax.axis('equal')
plt.show()
