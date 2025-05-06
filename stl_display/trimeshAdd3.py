import random

import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt

# 加载 STL 模型
# mesh = trimesh.load("../file\吸泵外壳.stl")  # 加载模型
# mesh = trimesh.load("../file\MGH-20 关节R安装件 v1.0.stl")  # 加载模型
# mesh = trimesh.load("../file\MGH-19 指根上连杆 v1.0.stl")  # 加载模型
mesh = trimesh.load("../file\MGH-18 指根下连杆 v1.0.stl")  # 加载模型

for i in range(0, 10):
    target_z = -i - 0.01
    projected_polygons = []

    for tri in mesh.triangles:
        if all(v[2] > target_z for v in tri):
            # 将三角形“压扁”到 Z=10 平面，只保留 XY
            xy = [(v[0], v[1]) for v in tri]
            poly = Polygon(xy)
            if poly.is_valid and poly.area > 0:
                projected_polygons.append(poly)

    # 合并所有压缩后的三角形为一个区域
    merged = unary_union(projected_polygons)
    color_list = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta', 'indigo',
                  'yellow']
    a = 0
    # 可视化结果
    fig, ax = plt.subplots()
    if merged.geom_type == 'Polygon':
        a += 1
        if a > len(color_list) -1:
            a = 0
        color = color_list[a]
        ax.plot(*merged.exterior.xy, color=color)
        for interior in merged.interiors:
            a += 1
            if a > len(color_list) - 1:
                a = 0
            color = color_list[a]
            ax.plot(*interior.xy,  color=color)

    elif merged.geom_type == 'MultiPolygon':
        for poly in merged.geoms:
            a += 1
            if a > len(color_list) - 1:
                a = 0
            color = color_list[a]
            ax.plot(*poly.exterior.xy, color=color)
            for interior in poly.interiors:
                a += 1
                if a > len(color_list) - 1:
                    a = 0
                color = color_list[a]
                ax.plot(*interior.xy, color=color)

    ax.set_aspect('equal')
    plt.title(f"Z {target_z}")
    plt.show()
