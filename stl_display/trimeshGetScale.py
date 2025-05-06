import trimesh
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LinearRing


def extract_outer_contour(path2D):
    """从 path2D 中提取闭合轮廓，并返回最大面积的 Polygon"""
    polygons = []

    for entity in path2D.entities:
        indices = entity.points
        points = path2D.vertices[indices]

        if len(points) < 3:
            continue

        # 判断是否闭合
        if np.allclose(points[0], points[-1]):
            ring = LinearRing(points)
            if ring.is_valid:
                poly = Polygon(ring)
                # x_coords, y_coords = zip(*list(poly.exterior.coords))
                # plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
                polygons.append(poly)

    if polygons:
        return max(polygons, key=lambda p: p.area)
    else:
        return None


# 加载 STL 模型
mesh = trimesh.load("../file/U.stl")

z_min = mesh.bounds[0][2]
z_max = mesh.bounds[1][2]
step = 0.1

z_levels = np.arange(z_min + step, z_max, step)

max_contour = None
max_area = -1
best_z = None

for z in z_levels:
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if section is None:
        continue

    try:
        path2D, _ = section.to_2D()
    except Exception as e:
        print(f"⚠️ to_2D error at z={z}: {e}")
        continue

    contour = extract_outer_contour(path2D)
    if contour and contour.area > max_area:
        max_area = contour.area
        max_contour = contour
        best_z = z

# 显示最大轮廓
if max_contour:
    print(f"✅ 最大外轮廓在 z={best_z:.2f}，面积={max_area:.2f}")
    x, y = max_contour.exterior.xy
    plt.plot(x, y, 'r-')
    plt.gca().set_aspect('equal')
    plt.title(f"最大外轮廓 (Z={best_z:.2f})")
    plt.show()
else:
    print("❌ 没有找到外轮廓")
