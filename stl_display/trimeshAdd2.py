import trimesh
import numpy as np
from shapely.ops import cascaded_union, polygonize
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt

# 读取 STL 模型
mesh = trimesh.load("../file\吸泵外壳.stl")  # 加载模型

# 每毫米切一层
min_z = mesh.bounds[0][2]
max_z = mesh.bounds[1][2]
z_levels = np.arange(min_z, max_z + 1, 1.0)

for z in z_levels:
    # 选出所有 Z 方向低于当前层的三角形
    faces = mesh.faces
    vertices = mesh.vertices

    mask = np.any(vertices[faces][:, :, 2] <= z, axis=1)
    sliced_faces = faces[mask]

    if len(sliced_faces) == 0:
        continue

    submesh = mesh.submesh([mask], append=True)

    # 投影到 XY 平面（去掉 Z 坐标）
    projected = submesh.copy()
    projected.vertices[:, 2] = 0.0  # 压平

    # 转为2D多边形组合（Shapely）
    paths = projected.edges_unique
    segments = projected.vertices[paths]

    # 用 Shapely polygonize
    from shapely.geometry import LineString

    lines = [LineString(s[:, :2]) for s in segments]
    polygons = list(polygonize(lines))
    unioned = cascaded_union(polygons)

    # 显示（可选）
    if isinstance(unioned, Polygon):
        unioned = [unioned]
    elif isinstance(unioned, MultiPolygon):
        unioned = list(unioned.geoms)
    else:
        unioned = []

    print(f"Z = {z:.2f}, 闭合区域数量: {len(unioned)}")

    # 绘图
    for poly in unioned:
        x, y = poly.exterior.xy
        plt.plot(x, y)
    plt.title(f"Z = {z:.2f}")
    plt.axis('equal')
    plt.show()
