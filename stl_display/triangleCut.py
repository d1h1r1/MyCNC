import math
import multiprocessing
import random
import time
import traceback
from multiprocessing import Pool
from collections import OrderedDict
import pyslm
import shapely.geometry as sg
import trimesh
import concurrent.futures
from collections import defaultdict

from matplotlib import pyplot as plt
from shapely import unary_union, Polygon, LineString, polygonize, MultiLineString, GeometryCollection
from shapely.validation import explain_validity


def is_contour_inside(inner_contour, outer_contour):
    """
    判断 inner_contour 是否被 outer_contour 完全包含
    :param inner_contour: 内轮廓点列表 [(x1, y1), (x2, y2), ...]
    :param outer_contour: 外轮廓点列表 [(x1, y1), (x2, y2), ...]
    :return: True/False
    """
    outer_polygon = sg.Polygon(outer_contour)
    inner_polygon = sg.Polygon(inner_contour)

    # 判断内轮廓的所有点是否都在外轮廓内部
    return outer_polygon.contains(inner_polygon)


def find_contour_relationships(allPath, index_list):
    """
    找出同层轮廓的包含关系
    :param contours: 轮廓点云列表，每个轮廓是 [(x1, y1), (x2, y2), ...]
    :return: 关系字典 {index1: [index2, index3, ...]} 表示 index1 包含 index2, index3
    """

    relationships = {i: [] for i in index_list}
    for i in index_list:
        for j in index_list:
            if i != j and is_contour_inside(allPath[i][0][1], allPath[j][0][1]):
                relationships[j].append(i)

    return relationships


def find_outermost_contours(contours):
    """ 找到最外层且不重叠的轮廓 """
    outermost = set(contours.keys())  # 先假设所有轮廓都是最外层的

    for i, (id1, poly1) in enumerate(contours.items()):
        for j, (id2, poly2) in enumerate(contours.items()):
            if i == j:
                continue  # 跳过自己
            if poly1.contains(poly2):
                # poly1 包含 poly2，说明 poly2 不是最外层
                outermost.discard(id2)

            # elif poly1.intersects(poly2) and not poly1.touches(poly2):
            #     # poly1 和 poly2 相交（但不是单纯的接触），它们都不是最外层
            #     outermost.discard(id1)
            #     outermost.discard(id2)

    return [i for i in outermost]


def find_inter_layer_relationships(contours_by_layer):
    """
    计算不同层轮廓之间的包含关系
    :param contours_by_layer: 每层的轮廓 {z: [轮廓1, 轮廓2, ...]}
    :return: 包含关系 {(z1, index1): [(z2, index2), ...]}
    """
    relationships = {}

    layers = sorted(contours_by_layer.keys(), reverse=True)  # 按 z 轴排序
    for i in range(len(layers) - 1):

        z1, z2 = layers[i], layers[i + 1]
        contours1, contours2 = contours_by_layer[z1], contours_by_layer[z2]
        # print(z1, z2)
        for i1, contour1 in enumerate(contours1):
            # print(i1)
            for i2, contour2 in enumerate(contours2):
                if is_contour_inside(contour2, contour1):
                    relationships.setdefault((z1, i1), []).append((z2, i2))
    print(relationships)
    # return relationships


def jaccard_similarity(contour1, contour2):
    """
    计算两个轮廓的 Jaccard 相似度
    :param contour1: 轮廓 1，格式 [(x1, y1), (x2, y2), ...]
    :param contour2: 轮廓 2，格式 [(x1, y1), (x2, y2), ...]
    :return: 相似度（0~1），1 表示完全相同
    """
    poly1 = sg.Polygon(contour1)
    poly2 = sg.Polygon(contour2)
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    similar_value = intersection / union if union != 0 else 0
    return similar_value


def process_polygon(poly, perList):
    """处理单个多边形，提取外环和内环"""
    exterior = list(zip(poly.exterior.coords.xy[0], poly.exterior.coords.xy[1]))
    if sg.Polygon(exterior).area > 0.01:
        perList.append(exterior)
    for interior in poly.interiors:
        interior_coords = list(zip(interior.coords.xy[0], interior.coords.xy[1]))
        if sg.Polygon(interior_coords).area > 0.01:
            perList.append(interior_coords)


def process_slice1(args):
    i, triangles = args
    # 设置切片层位置
    target_z = -0.1 * i
    perList = []
    projected_polygons = []
    for tri in triangles:
        if all(v[2] > target_z for v in tri):
            # 将三角形“压扁”到 Z 平面，只保留 XY
            xy = [(v[0], v[1]) for v in tri]
            poly = Polygon(xy)
            if poly.is_valid and poly.area > 0:
                projected_polygons.append(poly)

    # 合并所有压缩后的三角形为一个区域
    merged = unary_union(projected_polygons)
    if merged.geom_type == 'Polygon':
        if sg.Polygon(list(zip(*merged.exterior.xy))).area > 0.1:
            perList.append(list(zip(*merged.exterior.xy)))
        for interior in merged.interiors:
            if sg.Polygon(list(zip(*interior.xy))).area > 0.1:
                perList.append(list(zip(*interior.xy)))
    elif merged.geom_type == 'MultiPolygon':
        for poly in merged.geoms:
            if sg.Polygon(list(zip(*poly.exterior.xy))).area > 0.1:
                perList.append(list(zip(*poly.exterior.xy)))
            for interior in poly.interiors:
                if sg.Polygon(list(zip(*interior.xy))).area > 0.1:
                    perList.append(list(zip(*interior.xy)))
    for i in perList:
        print(target_z)
        x_coords, y_coords = zip(*i)
        # print(i)
        plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
        plt.show()
    return target_z, perList


def interp_z(p1, p2, z):
    """线性插值 Z 平面上的交点 (x, y)"""
    t = (z - p1[2]) / (p2[2] - p1[2])
    x = p1[0] + t * (p2[0] - p1[0])
    y = p1[1] + t * (p2[1] - p1[1])
    return (x, y)


def clip_triangle_by_z(tri, z):
    """
    将三角形按 z 平面裁剪，只保留 z >= 平面上的部分，并投影为 2D。
    返回一个或两个多边形。
    """
    above = [p for p in tri if p[2] >= z]
    below = [p for p in tri if p[2] < z]

    if len(above) == 3:
        # 全部在上方，直接投影
        return [Polygon([(p[0], p[1]) for p in tri])]
    elif len(above) == 0:
        # 全部在下方，忽略
        return []
    elif len(above) == 1:
        # 一个在上，两在下，构成一个小三角形
        p_top = above[0]
        p_bot1, p_bot2 = below
        ip1 = interp_z(p_top, p_bot1, z)
        ip2 = interp_z(p_top, p_bot2, z)
        return [Polygon([(p_top[0], p_top[1]), ip1, ip2])]
    elif len(above) == 2:
        # 两个在上，一个在下，构成一个四边形（两个三角拼起来）
        p_top1, p_top2 = above
        p_bot = below[0]
        ip1 = interp_z(p_top1, p_bot, z)
        ip2 = interp_z(p_top2, p_bot, z)
        return [Polygon([(p_top1[0], p_top1[1]), p_top2[0:2], ip2, ip1])]


def process_slice(args):
    i, triangles = args
    target_z = - 0.1 * i  # 设置切片平面位置

    projected_polygons = []

    for tri in triangles:
        z_vals = [v[2] for v in tri]
        if all(z > target_z for z in z_vals):
            # 整个三角形在平面上方，直接投影到XY平面
            xy = [(v[0], v[1]) for v in tri]
            poly = Polygon(xy)
            # print(poly)
            if poly.area > 1e-10:
                projected_polygons.append(poly)
        elif all(z < target_z for z in z_vals):
            continue  # 完全在下方，忽略
        else:
            clipped_polys = clip_triangle_by_z(tri, target_z)
            for poly in clipped_polys:
                if poly.is_valid and poly.area > 1e-10:
                    projected_polygons.append(poly)

    # 合并多边形
    try:
        merged = unary_union(projected_polygons)
    except:
        return target_z, []

    # 处理合并结果
    perList = []
    if merged.is_empty:
        return target_z, []

    if merged.geom_type == 'Polygon':
        process_polygon(merged, perList)
    elif merged.geom_type == 'MultiPolygon':
        for poly in merged.geoms:
            process_polygon(poly, perList)
    # # 绘图（可注释）
    # for i in perList:
    #     print(f"Z={target_z}")
    #     print("===============================================================")
    #     x_coords, y_coords = zip(*i)
    #     plt.plot(x_coords, y_coords, '-o', markersize=1)
    #     plt.gca().set_aspect('equal')
    #     plt.title(f"Slice at z={target_z}")
    #     plt.show()
    return target_z, perList


def get_scale(path, z_depth=0):
    mesh = trimesh.load(path)  # 加载模型
    triangles = mesh.triangles  # 获取三角形数据
    z_depth = -math.ceil(mesh.extents[2])
    # processes_num = 50
    # # 创建待处理任务
    # tasks = [(i, triangles) for i in range(int(abs(z_depth * 10)) + 1)]
    #
    # # 使用 ThreadPoolExecutor 替代 multiprocessing.Pool
    # with concurrent.futures.ThreadPoolExecutor(max_workers=processes_num) as executor:
    #     results = list(executor.map(process_slice, tasks))
    #

    processes_num = 1
    # 并行处理切片
    with multiprocessing.Pool(processes=processes_num) as pool:
        results = pool.map(process_slice, [(i, triangles) for i in range(int(abs(z_depth * 10)) + 1)])

    all_scale = {}
    for target_z, perList in results:
        all_scale[target_z] = perList

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
    detailFlag = True
    return max_points, all_scale, detailFlag


def get_max_scale(path):
    mesh = trimesh.load(path)  # 加载模型
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
    detailFlag = True
    return max_points


def scalePocket(all_scale, max_area_point, save_path):
    # 读取 STL 模型
    mesh = trimesh.load_mesh(save_path)
    allPath = []
    scaleKey = all_scale.keys()
    # start = time.time()
    num = 0
    for z in scaleKey:
        # 获取每层的点云
        per_layer = all_scale[z]
        # 将array数组转成列表方便查看
        layer_list = per_layer
        # layer_list = [j.tolist() for j in per_layer]
        # print(z, len(layer_list), len(allPath))
        # 遍历该模型全部外轮廓，并比较，若相似则修改相似轮廓的深度，不相似添加新的轮廓
        for pointsPath in layer_list:
            # t1 = time.time()
            # 是否添加轮廓
            flag = True
            for path in allPath:
                num += 1
                # 判断两个轮廓之间的相似度
                if jaccard_similarity(path[0][1], pointsPath) >= 0.95:
                    pathArea1 = sg.Polygon(pointsPath).area
                    # 判断轮廓是否与最大外轮廓相似
                    if jaccard_similarity(max_area_point, pointsPath) >= 0.95:
                        path[0][1] = max_area_point
                    else:
                        if pathArea1 > path[4]:
                            path[0][1] = pointsPath
                            path[4] = pathArea1
                        else:
                            if sg.Polygon(path[0][0]).area > pathArea1:
                                path[0][0] = pointsPath
                    flag = False
                    # 更新深度
                    path[1][1] = z

            if flag:
                # 计算轮廓面积
                pathArea2 = sg.Polygon(pointsPath).area
                allPath.append(
                    [[pointsPath, pointsPath], [z, 0], 0, [], pathArea2])  # [[最小点云, 最大点云]， [起始高度，结束高度]，切割类型, [内外轮廓情况]]
    # 判断是否有多个相同最大轮廓
    maxList = []
    startDepth = -999
    endDepth = 0
    for i in range(len(allPath)):
        if allPath[i][0][1] == max_area_point:
            maxList.append(allPath[i])
            maxPath = allPath[i].copy()
            # 获取相同轮廓z轴范围
            if allPath[i][1][0] > startDepth:
                startDepth = allPath[i][1][0]
            if allPath[i][1][1] < endDepth:
                endDepth = allPath[i][1][1]
    # 删除全部相同轮廓
    for i in maxList:
        allPath.remove(i)
    if maxList:
        maxPath[1][0] = startDepth
        maxPath[1][1] = endDepth
        # 添加一个最大轮廓
        allPath.append(maxPath)

    # 判断是否有异常轮廓(只有开始没有结束)
    newPath = []
    for i in allPath:
        if i[1][1] != 0:
            newPath.append(i)
    allPath = newPath

    # 遍历全部轮廓，获取内外切情况
    a = 0
    for i in allPath:
        a += 1
        path = i[0][1]
        pathZ = i[1][0]
        pointsPathPlus = sg.Polygon(path).buffer(0.5).exterior.coords
        for j in pointsPathPlus:
            is_inside = mesh.contains([[j[0], j[1], pathZ]])
            if is_inside[0]:
                i[2] = 1
                break
            else:
                i[2] = 0
    height_list = []
    # 遍历所有轮廓，将轮廓的高度存储起来，后续
    for path in allPath:
        height_list.append(path[1])
    # 获取所有唯一的层高（所有起始和终止点）
    all_heights = sorted(set(h for c in height_list for h in c), reverse=True)
    # 生成每层的轮廓
    layer_map = defaultdict(list)
    for height in all_heights:
        layer_map[height] = [[], []]
        for i in range(len(height_list)):
            contour = height_list[i]
            start, end = contour
            if end <= height <= start:  # 判断该轮廓是否在这个高度层
                try:
                    if all_heights[all_heights.index(height) + 1] <= end:
                        layer_map[height][0] = [height, end]
                        # print(3, end, contour)
                    else:
                        if all_heights[all_heights.index(height) + 1].is_integer():
                            # print(1, all_heights[all_heights.index(height) + 1], contour)
                            layer_map[height][0] = [height, all_heights[all_heights.index(height) + 1] + 0.1]
                        else:
                            # print(2, all_heights[all_heights.index(height) + 1], contour)
                            layer_map[height][0] = [height, all_heights[all_heights.index(height) + 1] + 0.1]
                    layer_map[height][1].append(i)
                except:
                    pass
    allList = []
    # 遍历每层高度内的全部轮廓，判断他们的包含关系
    for height in sorted(layer_map.keys(), reverse=True):
        index_list = layer_map[height][1]
        height_list = layer_map[height][0]
        if index_list == [] and height_list == []:
            continue
        layer_dist = find_contour_relationships(allPath, index_list)
        if [height_list, layer_dist] not in allList:
            allList.append([height_list, layer_dist])

        pointNum = {}
        inOut = {}
        # 判断轮廓内外切情况，获取轮廓内外轮廓
        for key in layer_dist:
            for i in layer_dist[key]:
                if inOut.get(i):
                    inOut[i][0].append(key)
                else:
                    inOut[i] = [[key], []]
                if inOut.get(key):
                    inOut[key][1].append(i)
                else:
                    inOut[key] = [[], [i]]
                if i in pointNum:
                    pointNum[i] += 1
                else:
                    pointNum[i] = 1
        # 设置切割类型是内切(奇数)还是外切(偶数)
        for layer in pointNum.keys():
            num = pointNum[layer]
            # print(layer, num)
            if num % 2 == 1:
                pass
            allPath[layer][2] = num % 2

    # 获取每个索引的所有高度范围
    index_ranges = defaultdict(list)
    for key in layer_map:
        height_range, indices = layer_map[key]
        if height_range and indices:
            start, end = height_range
            for index in indices:
                index_ranges[index].append((start, end))

    # 合并范围（允许接近的范围合并，设置一个很小的阈值）
    def merge_ranges(ranges, threshold=0.2):  # 如果两个范围的间隙 <= threshold，就合并
        if not ranges:
            return []
        ranges = sorted(ranges)
        merged = [list(ranges[0])]
        for current_start, current_end in ranges[1:]:
            last_start, last_end = merged[-1]
            if current_start <= last_end + threshold:  # 允许接近的范围合并
                new_start = min(last_start, current_start)
                new_end = max(last_end, current_end)
                merged[-1] = [new_start, new_end]
            else:
                merged.append([current_start, current_end])
        return merged

    # 合并每个索引的范围
    for index in index_ranges:
        index_ranges[index] = merge_ranges(index_ranges[index])

    # 计算每个索引的最低点和最高点
    index_min_max = {}
    for index in index_ranges:
        all_heights = []
        for start, end in index_ranges[index]:
            all_heights.extend([start, end])
        min_height = min(all_heights)  # 最低点
        max_height = max(all_heights)  # 最高点
        index_min_max[index] = (min_height, max_height)

    # 输出结果
    for index in sorted(index_min_max.keys()):
        min_h, max_h = index_min_max[index]
        allPath[index][1] = [max_h, min_h]
        # print(f"索引 {index}: 最低点 = {min_h}, 最高点 = {max_h}")

    # print("===========================================")
    # print(allPath)
    # color_list = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta', 'indigo',
    #               'yellow']
    # for i in range(len(allPath)):
    #     try:
    #         x_coords, y_coords = zip(*allPath[i][0][1])
    #         color = random.choices(color_list)[0]
    #         plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path', color=color)
    #         # 添加文字标签
    #         plt.text(x_coords[0], y_coords[0], i, fontsize=20, color=color, ha='right')
    #     except:
    #         x_coords, y_coords, z = zip(*allPath[i][0][1])
    #         color = random.choices(color_list)[0]
    #         plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path', color=color)
    #         # 添加文字标签
    #         plt.text(x_coords[0], y_coords[0], i, fontsize=20, color=color, ha='right')
    #     print(i, allPath[i][1], allPath[i][2])
    #     print("=====================================")
    # plt.show()
    # print(allPath)
    return allPath, allList
