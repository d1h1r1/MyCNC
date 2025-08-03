import multiprocessing
import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import traceback
scaleZ = 0.1
zoffset = 1e-10


# 插值函数：NumPy 实现
def interp_z_np(p1, p2, z):
    """使用 NumPy 向量化插值计算平面 z 上的交点 (x, y)"""
    p1 = np.asarray(p1)
    p2 = np.asarray(p2)
    dz = p2[2] - p1[2]
    if dz == 0:
        return p1[:2]  # 避免除以 0，返回投影点
    t = (z - p1[2]) / dz
    return p1[:2] + t * (p2[:2] - p1[:2])


# 裁剪三角形函数：NumPy 加速
def clip_triangle_by_z_np(tri, z):
    """将三角形按 z 平面裁剪，只保留 z >= 平面上的部分，并投影为 2D 多边形。"""
    tri = np.asarray(tri)
    z_vals = tri[:, 2]

    above_mask = z_vals >= z
    below_mask = ~above_mask

    above = tri[above_mask]
    below = tri[below_mask]

    if len(above) == 3:
        return [Polygon(tri[:, :2])]
    elif len(above) == 0:
        return []
    elif len(above) == 1:
        p_top = above[0]
        p_bot1, p_bot2 = below
        ip1 = interp_z_np(p_top, p_bot1, z)
        ip2 = interp_z_np(p_top, p_bot2, z)
        return [Polygon([p_top[:2], ip1, ip2])]
    elif len(above) == 2:
        p_top1, p_top2 = above
        p_bot = below[0]
        ip1 = interp_z_np(p_top1, p_bot, z)
        ip2 = interp_z_np(p_top2, p_bot, z)
        return [Polygon([p_top1[:2], p_top2[:2], ip2, ip1])]


# 多边形处理函数：NumPy 化
def process_polygon_np(poly, perList):
    """处理单个多边形，提取外环和内环为 NumPy 数组"""
    exterior = np.round(np.array(poly.exterior.coords), 3)
    if Polygon(exterior).area > 0.01:
        perList.append(exterior)

    for interior in poly.interiors:
        coords = np.round(np.array(interior.coords), 3)
        if Polygon(coords).area > 0.01:
            perList.append(coords)


# 主函数（供整合）
def process_slice_np(args):
    """改进后的切片处理函数"""
    import time
    i, triangles = args
    t1 = time.time()

    target_z = -scaleZ * i + zoffset
    z = target_z - zoffset
    projected_polygons = []

    for tri in triangles:
        tri = np.asarray(tri)  # tri 是 shape=(3, 3) 的三角形坐标数组
        z_vals = tri[:, 2]  # 提取第三列 z
        max_z = max(z_vals)
        min_z = min(z_vals)

        if min_z > target_z:
            xy = tri[:, :2]  # 提取前两列 (x, y)
            poly = Polygon(xy)
            if poly.area > 1e-10:
                projected_polygons.append(poly)
        elif max_z < target_z:
            continue
        else:
            try:
                clipped_polys = clip_triangle_by_z_np(tri, target_z)
                for poly in clipped_polys:
                    if poly.is_valid and poly.area > 1e-10:
                        projected_polygons.append(poly)
            except:
                traceback.print_exc()
                return z, []


    try:
        merged = unary_union(projected_polygons)
    except:
        traceback.print_exc()
        return z, []

    perList = []
    if merged.is_empty:
        return z, []

    if merged.geom_type == 'Polygon':
        process_polygon_np(merged, perList)
    elif merged.geom_type == 'MultiPolygon':
        for poly in merged.geoms:
            process_polygon_np(poly, perList)

    return z, perList


def get_scale(path, z_depth=0):
    mesh = trimesh.load(path)  # 加载模型
    triangles = mesh.triangles  # 获取三角形数据
    processes_num = 8
    # 并行处理切片
    with multiprocessing.Pool(processes=processes_num) as pool:
        results = pool.map(process_slice_np, [(i, triangles) for i in range(int(abs(z_depth * (1 / scaleZ))) + 1)])

    all_scale = {}
    for target_z, perList in results:
        all_scale[target_z] = perList
    max_points = []
    return max_points, all_scale