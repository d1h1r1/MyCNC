import numpy as np
import pyclipper
from matplotlib import pyplot as plt
from opencamlib import ocl
import math
import shapely.affinity as sa
import shapely.geometry as sg

"""
创建一个简单的“Zig”图案，只在一个方向上切割。
# 第一行在ymin
# 最后一行是ymax
"""


def YdirectionZigPath(xmin, xmax, ymin, ymax, z_depth, Ny, layer):
    paths = []
    dy = float(ymax - ymin) / (Ny - 1)  # y 步长
    dz = z_depth / layer
    # z = z_depth
    for i in range(1, layer + 1):
        z = 0 + i * dz
        for n in range(0, Ny):
            path = ocl.Path()
            y = ymin + n * dy  # 当前y轴
            if n == Ny - 1:
                assert (y == ymax)
            elif n == 0:
                assert (y == ymin)
            p1 = ocl.Point(xmin, y, z)  # 起始点
            p2 = ocl.Point(xmax, y, z)  # 终点
            l = ocl.Line(p1, p2)  # 直线
            path.append(l)
            paths.append(path)
    return paths


# 双向锯齿
def YdirectionAlternatingZigPath(xmin, xmax, ymin, ymax, z_depth, Ny, layer):
    paths = []
    dy = float(ymax - ymin) / (Ny - 1)  # y 步长
    dz = z_depth / layer
    for i in range(1, layer + 1):
        z = 0 + i * dz
        for n in range(0, Ny):
            path = ocl.Path()
            y = ymin + n * dy  # 当前 y 坐标
            if n == Ny - 1:
                assert (y == ymax)
            elif n == 0:
                assert (y == ymin)
            p1 = ocl.Point(xmin, y, z)  # 起始点
            p2 = ocl.Point(xmax, y, z)  # 结束点

            if n % 2 == 0:  # 偶数行从左到右
                l = ocl.Line(p1, p2)
            else:  # 奇数行从右到左
                l = ocl.Line(p2, p1)

            path.append(l)
            paths.append(path)
    return paths


"""
螺旋路径1
这种路径适用于需要处理圆形区域的情况，像是孔的加工或者从外向内的轮廓铣削。
turns: 螺旋的圈数。
segments: 每圈的分段数，总分段数为 turns * segments。
从内到外
"""


def SpiralPathOut(center_x, center_y, z_depth, max_radius, step_over, layer):
    angle_step = 2 * math.pi / 100  # 每个分段的角度增量
    paths = []  # 存储路径点
    num_turns = max_radius // step_over
    dz = z_depth / layer
    for i in range(1, layer + 1):
        z = 0 + i * dz
        for turn in range(num_turns):
            path = ocl.Path()
            for i in range(101):  # 101 点构成一圈
                angle = i * angle_step  # 当前角度
                radius = turn * step_over  # 半径逐渐增大
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                p = ocl.Point(x, y, z)
                if i > 0:  # 从第二个点开始创建线段
                    l = ocl.Line(prev_p, p)
                    path.append(l)
                prev_p = p
            paths.append(path)
    return paths


"""
螺旋路径2
center_x:螺旋路径的中心 X 坐标
center_y:螺旋路径的中心 Y 坐标。
radius:螺旋的最大半径，定义路径的覆盖范围。
z_depth:刀具的切削深度（Z 轴位置）。
num_turns:螺旋的圈数，即路径从外到内的次数。
step_over:刀具每圈之间的间隔，用于控制路径密度（通常小于刀具直径）。
从外到内
"""


def SpiralPathIn(center_x, center_y, z_depth, radius, step_over, layer):
    paths = []
    theta_step = 2 * math.pi / 100  # 控制圆滑度（100 步每圈）
    num_turns = radius // step_over
    dz = z_depth / layer
    for i in range(1, layer + 1):
        z = 0 + i * dz
        for turn in range(num_turns):
            path = ocl.Path()
            for i in range(101):  # 101 点构成一圈
                theta = i * theta_step + turn * 2 * math.pi
                r = radius - turn * step_over  # 半径逐渐减小
                if r <= 0:  # 超出半径范围
                    break
                x = center_x + r * math.cos(theta)
                y = center_y + r * math.sin(theta)
                p = ocl.Point(x, y, z)
                if i > 0:  # 从第二个点开始创建线段
                    l = ocl.Line(prev_p, p)
                    path.append(l)
                prev_p = p
            paths.append(path)
    return paths


"""
平行偏移路径
polygon:描述初始区域的多边形顶点，表示要加工的封闭区域。
step_over:每次偏移的距离（通常小于刀具直径），控制路径的密集程度
"""


def OffsetPath(polygon, diameter, z_depth, layer, step_over):
    cap_style = 2  # 1 (round), 2 (flat), 3 (square)
    join_style = 2  # 1 (round), 2 (mitre), and 3 (bevel)
    mitre_limit = 5  # 默认是 5

    original_polygon = sg.Polygon(polygon)  # 输入多边形
    cut_polygon = original_polygon.buffer(-diameter * 0.5 - 0.001, resolution=16, cap_style=cap_style, join_style=join_style, mitre_limit=mitre_limit)

    dz = z_depth / layer
    paths = []
    for j in range(1, layer + 1):
        current_polygon = cut_polygon
        z = 0 + j * dz  # 当前z轴
        try:
            while not current_polygon.is_empty and current_polygon.area > 0:
                # 如果是 MultiPolygon，遍历每个 Polygon
                if isinstance(current_polygon, sg.MultiPolygon):
                    polygons = list(current_polygon.geoms)
                else:
                    polygons = [current_polygon]

                for poly in polygons:
                    if poly.is_empty or poly.area <= 0:
                        continue

                    path = ocl.Path()
                    coords = list(poly.exterior.coords)  # 提取外边界点
                    for i in range(len(coords) - 1):  # 创建线段
                        p1 = ocl.Point(coords[i][0], coords[i][1], z)
                        p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1], z)
                        l = ocl.Line(p1, p2)
                        path.append(l)
                    p1 = ocl.Point(coords[0][0], coords[0][1], z)
                    p2 = ocl.Point(coords[1][0], coords[1][1], z)
                    l = ocl.Line(p1, p2)
                    path.append(l)
                    paths.append(path)

                # 偏移当前多边形
                current_polygon = current_polygon.buffer(-step_over, resolution=16)
        except Exception as e:
            print(f"Error: {e}")

    return paths


"""
曲线跟随
curve_points: 曲线点列表（例如从矢量文件中读取）。
diameter: 刀具直径
z_depth: 切削深度
layer： 切削层数
"""


def ContourPath(polygon, diameter, z_depth, layer):
    cap_style = 2  # 1 (round), 2 (flat), 3 (square)
    join_style = 2  # 1 (round), 2 (mitre), and 3 (bevel)
    mitre_limit = 5  # 默认是 5

    original_polygon = sg.Polygon(polygon)  # 输入多边形
    cut_polygon = original_polygon.buffer(-diameter * 0.5 - 0.001, resolution=64, cap_style=cap_style,
                                          join_style=join_style, mitre_limit=mitre_limit)

    dz = z_depth / layer
    paths = []
    for j in range(1, layer + 1):
        current_polygon = cut_polygon
        z = 0 + j * dz  # 当前z轴
        if isinstance(current_polygon, sg.MultiPolygon):
            polygons = list(current_polygon.geoms)
        else:
            polygons = [current_polygon]

        for poly in polygons:
            if poly.is_empty or poly.area <= 0:
                continue
            path = ocl.Path()
            coords = list(poly.exterior.coords)  # 提取外边界点
            for i in range(len(coords) - 1):  # 创建线段
                p1 = ocl.Point(coords[i][0], coords[i][1], z)
                p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1], z)
                l = ocl.Line(p1, p2)
                path.append(l)
            p1 = ocl.Point(coords[0][0], coords[0][1], z)
            p2 = ocl.Point(coords[1][0], coords[1][1], z)
            l = ocl.Line(p1, p2)
            path.append(l)
            paths.append(path)
    return paths
