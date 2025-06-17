import random
import time

import numpy as np
import shapely.geometry as sg
import trimesh
import vtk
import pyslm.visualise
from matplotlib import pyplot as plt
from collections import defaultdict
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union


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
            if i != j and is_contour_inside(allPath[i][0], allPath[j][0]):
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


def get_per_scale():
    path = "D:\gitlab\cnc_server\src\../file\select_current_stl_file.stl"
    z_depth = -15
    mesh = trimesh.load(path)         # 加载模型

    # 2. 获取中间高度
    z_center = (mesh.bounds[0][2] + mesh.bounds[1][2]) / 2

    # 3. 截取上半部分
    upper = mesh.slice_plane(plane_origin=[0, 0, z_center], plane_normal=[0, 0, 1])

    if upper is None:
        raise ValueError("未能截取上半部分，可能是模型问题或截面无效")

    # 4. 计算需要移动的距离（将其最低点平移到 z_center）
    upper_min_z = upper.bounds[0][2]
    offset = z_center - upper_min_z
    # 构造平移矩阵
    transform = np.eye(4)
    transform[2, 3] = offset  # z 轴平移
    # 应用平移
    upper.apply_transform(transform)
    # 5. 合并原始模型和上半部分
    combined = trimesh.util.concatenate([mesh, upper])

    # 显示结果
    combined.show()


def get_scale(path, z_depth):
    solidPart = pyslm.Part('stl')
    solidPart.setGeometry(path)
    print(path)
    all_scale = {}
    max_num = 0
    for i in range(int(abs(z_depth * 10)) + 1):
        # 设置切片层位置
        z = -0.1 * i
        try:
            geomSlice = solidPart.getVectorSlice(z)
        except:
            continue
        if len(geomSlice) > max_num:
            max_num = len(geomSlice)
        all_scale[z] = geomSlice

    if max_num >= 50:
        detailFlag = False
    else:
        detailFlag = True

    # 加载模型
    mesh = trimesh.load(path)
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
    return max_points, all_scale, detailFlag


def test_all_scale(all_scale):
    allPath = []
    max_list = [0, 0]
    scaleKey = all_scale.keys()
    for z in scaleKey:
        # 获取每层的点云
        per_layer = all_scale[z]
        layer_list = []
        # 将array数组转成列表方便查看
        for j in per_layer:
            points_list = []
            for point in j:
                points_list.append(list(point))
            layer_list.append(points_list)
        # 遍历该模型全部外轮廓，并比较，若相似则修改相似轮廓的深度，不相似添加新的轮廓
        for pointsPath in layer_list:
            flag = True
            for path in allPath:
                # 判断两个轮廓之间的相似度
                if jaccard_similarity(path[0], pointsPath) >= 0.95:
                    path[1][1] = z
                    flag = False
            if flag:
                allPath.append([pointsPath, [z, 0], 0])  # [[点云]， [起始高度，结束高度]，切割类型]
    height_list = []
    # 遍历所有轮廓，将轮廓的高度存储起来，后续
    for path in allPath:
        # x_coords, y_coords = zip(*path[0])
        # plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
        height_list.append(path[1])

    # 获取所有唯一的层高（所有起始和终止点）
    all_heights = sorted(set(h for c in height_list for h in c), reverse=True)
    # 生成每层的轮廓
    layer_map = defaultdict(list)
    for height in all_heights:
        for i in range(len(height_list)):
            contour = height_list[i]
            start, end = contour
            if end <= height <= start:  # 判断该轮廓是否在这个高度层
                layer_map[height].append(i)
    # 遍历每层高度内的全部轮廓，判断他们的包含关系，来判断切割类型是内切(奇数)还是外切(偶数)
    for height in sorted(layer_map.keys(), reverse=True):
        index_list = layer_map[height]

        pointNum = {}
        layer_dist = find_contour_relationships(allPath, index_list)
        for key in layer_dist:
            for i in layer_dist[key]:
                # print(key, i)
                if i in pointNum:
                    pointNum[i] += 1
                else:
                    pointNum[i] = 1
        # 设置切割类型是内切(奇数)还是外切(偶数)
        for layer in pointNum.keys():
            num = pointNum[layer]
            allPath[layer][2] = num % 2
    # 遍历全部轮廓，去除最大外轮廓(防止将支撑切除)
    for k in range(len(allPath)):
        pathArea = sg.Polygon(allPath[k][0]).area
        if pathArea > max_list[1]:
            max_list[1] = pathArea
            max_list[0] = k
    if len(allPath) != 0:
        allPath.pop(max_list[0])
    # plt.show()
    return allPath, max_list[0]


def scalePocket(all_scale, max_area_point, save_path):
    # 读取 STL 模型
    mesh = trimesh.load_mesh(save_path)
    allPath = []
    max_list = [0, 0]
    scaleKey = all_scale.keys()
    num = 0
    for z in scaleKey:
        # 获取每层的点云
        per_layer = all_scale[z]
        # 将array数组转成列表方便查看
        layer_list = [j.tolist() for j in per_layer]
        # print(z, len(layer_list), len(allPath))
        # 遍历该模型全部外轮廓，并比较，若相似则修改相似轮廓的深度，不相似添加新的轮廓
        for pointsPath in layer_list:
            # t1 = time.time()
            # 是否添加轮廓
            flag = True
            for path in allPath:
                num += 1
                # 判断两个轮廓之间的相似度,拟合成大的
                if jaccard_similarity(path[0], pointsPath) >= 0.95:
                    pathArea1 = sg.Polygon(path[0]).area
                    pathArea2 = path[4]
                    # 判断轮廓是否与最大外轮廓相似
                    if jaccard_similarity(max_area_point, pointsPath) >= 0.95:
                        path[0] = max_area_point
                    else:
                        if pathArea1 > pathArea2 and path[0] != max_area_point:
                            path[0] = pointsPath
                    flag = False
                    # 更新深度
                    path[1][1] = z

            if flag:
                # 计算轮廓面积
                pathArea2 = sg.Polygon(pointsPath).area
                allPath.append([pointsPath, [z, 0], 0, [], pathArea2])  # [[点云]， [起始高度，结束高度]，切割类型, [内外轮廓情况]]

    # 将模型底部的轮廓清除
    # for i in range(len(allPath) - 1, -1, -1):
    #     path = allPath[i][0]
    #     pathZ = allPath[i][1][0]
    #     try:
    #         pointsPathPlus = sg.Polygon(path).buffer(-0.01).exterior.coords
    #     except:
    #         print("双轮廓")
    #         continue
    #     for j in pointsPathPlus:
    #         # 判断点上面1mm处
    #         is_inside = mesh.contains([[j[0], j[1], pathZ + 0.5]])
    #         if is_inside[0]:
    #             break
    #     if is_inside[0]:
    #         if path == max_area_point:
    #             for k in range(len(path) - 1, -1, -1):
    #                 is_inside = mesh.contains([[path[k][0], path[k][1], pathZ + 0.5]])
    #                 if is_inside[0]:
    #                     del path[k]
    #             continue
    #         # print(path)
    #         # print("===============================")
    #         del allPath[i]

    # 判断是否有多个相同最大轮廓
    maxList = []
    startDepth = -999
    endDepth = 0
    for i in range(len(allPath)):
        if allPath[i][0] == max_area_point:
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
    for k in range(len(allPath)):
        pathArea = sg.Polygon(allPath[k][0]).area
        if pathArea > max_list[1]:
            max_list[1] = pathArea
            max_list[0] = k
    for i in allPath:
        path = i[0]
        pathZ = i[1][0]
        pointsPathPlus = sg.Polygon(path).buffer(0.01).exterior.coords
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
            layer_map[height][0] = contour
            start, end = contour
            if end <= height <= start:  # 判断该轮廓是否在这个高度层
                if allPath[i][2] == 0:
                    layer_map[height][1].append(i)
    allCutOut = []
    # 遍历每层高度内的全部轮廓，判断他们的包含关系
    for height in sorted(layer_map.keys(), reverse=True):
        index_list = layer_map[height][1]
        heightDepth = layer_map[height][0]
        layer_dist = find_contour_relationships(allPath, index_list)
        print(height, layer_dist)
        allScale = list(layer_dist.keys())
        # 判断轮廓内外切情况，获取轮廓内外轮廓
        for key in layer_dist:
            for i in layer_dist[key]:
                if i in allScale:
                    allScale.remove(i)
        allCutOut.append([heightDepth, allScale])
        # print(allScale)
    # print(allCutOut)

    color_list = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta', 'indigo',
                  'yellow']
    for i in range(len(allPath)):
        try:
            x_coords, y_coords = zip(*allPath[i][0])
            color = random.choices(color_list)[0]
            plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path', color=color)
        except:
            x_coords, y_coords, z = zip(*allPath[i][0])
            color = random.choices(color_list)[0]
            plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path', color=color)
        # 添加文字标签
        plt.text(x_coords[0], y_coords[0], i, fontsize=20, color=color, ha='right')
        # print(i, allPath[i])
        # print("=====================================")
    # plt.show()
    # print(allPath)
    return allPath, max_area_point, allCutOut
    # return allPath, max_list[0]
