import random

import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import shapely.geometry as sg

# 加载 STL 模型
# mesh = trimesh.load("../file\吸泵外壳.stl")  # 加载模型
mesh = trimesh.load("../file\MGH-20 关节R安装件 v1.0.stl")  # 加载模型
# mesh = trimesh.load("../file\MGH-19 指根上连杆 v1.0.stl")  # 加载模型
# mesh = trimesh.load("../file\MGH-18 指根下连杆 v1.0.stl")  # 加载模型
all_scale = {}

for i in range(0, 15):
    perList = []
    target_z = -i - 0.01
    projected_polygons = []

    for tri in mesh.triangles:
        if all(v[2] > target_z for v in tri):
            # 将三角形“压扁”到 Z 平面，只保留 XY
            xy = [(v[0], v[1]) for v in tri]
            poly = Polygon(xy)
            if poly.is_valid and poly.area > 0:
                projected_polygons.append(poly)

    # 合并所有压缩后的三角形为一个区域
    merged = unary_union(projected_polygons)
    if merged.geom_type == 'Polygon':
        if sg.Polygon(list(zip(*merged.exterior.xy))).area > 1:
            perList.append(list(zip(*merged.exterior.xy)))
        for interior in merged.interiors:
            if sg.Polygon(list(zip(*interior.xy))).area > 1:
                perList.append(list(zip(*interior.xy)))
    elif merged.geom_type == 'MultiPolygon':
        for poly in merged.geoms:
            if sg.Polygon(list(zip(*poly.exterior.xy))).area > 1:
                perList.append(list(zip(*poly.exterior.xy)))
            for interior in poly.interiors:
                if sg.Polygon(list(zip(*interior.xy))).area > 1:
                    perList.append(list(zip(*interior.xy)))
    all_scale[target_z] = perList

print(all_scale)
