import multiprocessing
import trimesh
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
import traceback
from itertools import repeat

# 常量设置
SCALE_Z = 0.1
Z_OFFSET = 1e-10
MIN_AREA = 1e-10  # 多边形最小面积阈值
MIN_AREA_LARGE = 0.01  # 外环/内环最小面积阈值
ROUND_DECIMALS = 3  # 坐标舍入小数位


def interp_z_np(p1, p2, z):
    """向量化Z轴插值计算"""
    dz = p2[2] - p1[2]
    t = np.where(dz != 0, (z - p1[2]) / dz, 0)
    return p1[:2] + t * (p2[:2] - p1[:2])


def clip_triangle_batch(triangles, z):
    """批量处理三角形切片"""
    results = []
    z_vals = triangles[:, :, 2]

    # 计算每个三角形的最小/最大Z值
    min_z = np.min(z_vals, axis=1)
    max_z = np.max(z_vals, axis=1)

    # 提前过滤完全在平面上方或下方的三角形
    mask_above = min_z > z
    mask_below = max_z < z
    mask_clip = ~(mask_above | mask_below)

    # 处理完全在平面上方的三角形
    for tri in triangles[mask_above]:
        poly = Polygon(tri[:, :2])
        if poly.area > MIN_AREA:
            results.append(poly)

    # 处理需要裁剪的三角形
    for tri in triangles[mask_clip]:
        z_tri = tri[:, 2]
        above = z_tri >= z
        below = ~above

        if np.sum(above) == 1:
            p_top = tri[above][0]
            p_bots = tri[below]
            ip1 = interp_z_np(p_top, p_bots[0], z)
            ip2 = interp_z_np(p_top, p_bots[1], z)
            poly = Polygon([p_top[:2], ip1, ip2])
        elif np.sum(above) == 2:
            p_tops = tri[above]
            p_bot = tri[below][0]
            ip1 = interp_z_np(p_tops[0], p_bot, z)
            ip2 = interp_z_np(p_tops[1], p_bot, z)
            poly = Polygon([p_tops[0][:2], p_tops[1][:2], ip2, ip1])

        if poly.is_valid and poly.area > MIN_AREA:
            results.append(poly)

    return results


def process_slice(args):
    """优化后的切片处理函数"""
    i, all_triangles = args
    target_z = -SCALE_Z * i + Z_OFFSET
    z = target_z - Z_OFFSET

    try:
        # 批量处理三角形
        polygons = clip_triangle_batch(all_triangles, target_z)

        if not polygons:
            return z, []

        # 合并多边形
        merged = unary_union(polygons)
        if merged.is_empty:
            return z, []

        # 处理结果多边形
        per_list = []
        if merged.geom_type == 'Polygon':
            process_polygon(merged, per_list)
        elif merged.geom_type == 'MultiPolygon':
            for poly in merged.geoms:
                process_polygon(poly, per_list)

        return z, per_list

    except Exception:
        traceback.print_exc()
        return z, []


def process_polygon(poly, per_list):
    """处理单个多边形"""
    exterior = np.round(np.array(poly.exterior.coords), ROUND_DECIMALS)
    if Polygon(exterior).area > MIN_AREA_LARGE:
        per_list.append(exterior)

    for interior in poly.interiors:
        coords = np.round(np.array(interior.coords), ROUND_DECIMALS)
        if Polygon(coords).area > MIN_AREA_LARGE:
            per_list.append(coords)


def get_scale(path, z_depth=0):
    """优化后的主函数"""
    # 加载模型并预处理
    mesh = trimesh.load(path)
    all_triangles = np.asarray(mesh.triangles)  # 一次性转换所有三角形

    # 计算切片数量
    slice_count = int(abs(z_depth * (1 / SCALE_Z))) + 1
    processes_num = 8
    # 使用多进程处理
    with multiprocessing.Pool(processes=processes_num) as pool:
        results = pool.map(process_slice, zip(range(slice_count), repeat(all_triangles)))

    # 整理结果
    all_scale = {z: per_list for z, per_list in results}

    return [], all_scale
