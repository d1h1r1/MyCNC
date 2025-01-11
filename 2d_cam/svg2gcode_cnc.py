import re
import time
from xml.etree import ElementTree
from svgpathtools import svg2paths
import numpy as np
import math


def svgArcToCenterParam(x1, y1, rx, ry, phi, fA, fS, x2, y2):
    # 计算弧度
    def radian(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        mod = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
        rad = math.acos(dot / mod)
        if ux * vy - uy * vx < 0.0:
            rad = -rad
        return rad

    cx, cy, startAngle, deltaAngle, endAngle = None, None, None, None, None
    PIx2 = math.pi * 2.0

    if rx < 0:
        rx = -rx
    if ry < 0:
        ry = -ry
    if rx == 0 or ry == 0:  # 无效的参数
        raise ValueError('rx 和 ry 不能为 0')

    phi = phi * math.pi / 180
    s_phi = math.sin(phi)
    c_phi = math.cos(phi)
    hd_x = (x1 - x2) / 2.0  # x 坐标差的一半
    hd_y = (y1 - y2) / 2.0  # y 坐标差的一半
    hs_x = (x1 + x2) / 2.0  # x 坐标和的一半
    hs_y = (y1 + y2) / 2.0  # y 坐标和的一半

    # 步骤 6.5.1
    x1_ = c_phi * hd_x + s_phi * hd_y
    y1_ = c_phi * hd_y - s_phi * hd_x

    # 步骤 6.6 修正超出范围的半径
    lambda_ = (x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry)
    if lambda_ > 1:
        rx = rx * math.sqrt(lambda_)
        ry = ry * math.sqrt(lambda_)

    rxry = rx * ry
    rxy1_ = rx * y1_
    ryx1_ = ry * x1_
    sum_of_sq = rxy1_ * rxy1_ + ryx1_ * ryx1_  # 求平方和
    if sum_of_sq == 0:
        raise ValueError('起点不能和终点相同')

    coe = math.sqrt(abs((rxry * rxry - sum_of_sq) / sum_of_sq))
    if fA == fS:
        coe = -coe

    # 步骤 6.5.2
    cx_ = coe * rxy1_ / ry
    cy_ = -coe * ryx1_ / rx

    # 步骤 6.5.3 计算中心点坐标
    cx = c_phi * cx_ - s_phi * cy_ + hs_x
    cy = s_phi * cx_ + c_phi * cy_ + hs_y

    xcr1 = (x1_ - cx_) / rx
    xcr2 = (x1_ + cx_) / rx
    ycr1 = (y1_ - cy_) / ry
    ycr2 = (y1_ + cy_) / ry

    # 步骤 6.5.5 计算起始角度
    startAngle = radian(1.0, 0.0, xcr1, ycr1)

    # 步骤 6.5.6 计算角度差
    deltaAngle = radian(xcr1, ycr1, -xcr2, -ycr2)
    while deltaAngle > PIx2:
        deltaAngle -= PIx2
    while deltaAngle < 0.0:
        deltaAngle += PIx2
    if fS == 0 or fS is False:
        deltaAngle -= PIx2
    endAngle = startAngle + deltaAngle
    while endAngle > PIx2:
        endAngle -= PIx2
    while endAngle < 0.0:
        endAngle += PIx2

    outputObj = {
        'cx': cx,
        'cy': cy,
        'startAngle': startAngle,
        'deltaAngle': deltaAngle,
        'endAngle': endAngle,
        'clockwise': (fS == 1 or fS is True)
    }

    return outputObj


def parse_transform(matrix, translate):
    """
    解析 SVG 中的 transform 属性（matrix 和 translate）。
    例如: 'matrix(1, 0, 0, 1, 10, 20)' 或 'translate(10, 20)'。
    """
    transform_matrix = np.identity(3)  # 初始化为单位矩阵

    # 处理 matrix 和 translate
    matrix_match = re.match(r'matrix\(([^)]+)\)', matrix.strip())
    if matrix_match:
        # 解析 matrix
        matrix_values = list(map(float, matrix_match.group(1).split()))
        # matrix = np.array(matrix_values).reshape((2, 3))  # 转换为 2x3 矩阵
        transform_matrix = np.array([
            [matrix_values[0], matrix_values[2], matrix_values[4]],
            [matrix_values[1], matrix_values[3], matrix_values[5]],
            [0, 0, 1],
        ])
    translate_match = re.match(r'translate\(([^)]+)\)', str(translate).strip())
    if translate_match:
        # 解析 translate
        tx, ty = map(float, translate_match.group(1).split(","))
        translation_matrix = np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ])
        transform_matrix @= translation_matrix
    return transform_matrix


def generate_arc_gcode(x1, y1, x2, y2, cx, cy, startAngle, endAngle, clockwise, feedrate=1000):
    # 如果是顺时针，使用 G2，否则使用 G3
    gcode_command = "G2" if clockwise else "G3"

    # 计算终止点角度，防止超出圆弧的范围
    # endAngle = startAngle + deltaAngle
    while endAngle > math.pi * 2:
        endAngle -= math.pi * 2
    while endAngle < 0:
        endAngle += math.pi * 2

    # G-code 中通常使用 X, Y 来指定圆弧的终点，I, J 来指定圆心的偏移量
    # I, J 是相对于起始点 (x1, y1) 的圆心偏移
    I = cx - x1
    J = cy - y1

    # 输出 G-code
    gcode = f"G0 X{x1:.3f} Y{y1:.3f} F{feedrate}"  # 先移动到起始点
    gcode += f"\n{gcode_command} X{x2:.3f} Y{y2:.3f} I{I:.3f} J{J:.3f} F{feedrate}"

    return gcode


# 贝塞尔曲线插值
def interpolate_bezier(p0, p1, p2, p3, num_points=10):
    points = []
    for t in np.linspace(0, 1, num_points):
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        points.append((x, y))
    return points


# 主函数：将 SVG 转换为 G-code
def svg_to_gcode(svg_file, z_per, z_depth, feed_height=20, feed_rate=1000, num_points=10):
    paths, attributes = svg2paths(svg_file)
    root = ElementTree.parse(svg_file).getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    matrix_list = []

    for path in root.findall(".//svg:g", namespace):
        matrix = path.attrib.get('transform')
        matrix_list.append(matrix)
    with open("svg_cnc.nc", 'w') as gcode_file:
        # 写入 G-code 文件的头部
        gcode_file.write("G21\nG0 G17 G49 G80 G90\n")
        gcode_file.write(f"F{feed_rate}\n")
        # 遍历路径并转换为 G-code
        layer = math.ceil(abs(z_depth / z_per))
        for i in range(1, layer + 1):
            z = 0 - z_per * i
            num = 0
            for path in paths:
                end_point = (0, 0)
                try:
                    matrix = matrix_list[num]
                    translate = attributes[num]['transform']
                    transform_matrix = parse_transform(matrix, translate)
                except:
                    transform_matrix = np.identity(3)
                num += 1
                for segment in path:
                    if segment.__class__.__name__ == 'Line':

                        start = np.array([[segment.start.real], [segment.start.imag], [1]])
                        new_start = np.dot(transform_matrix, start)[0][0], np.dot(transform_matrix, start)[1][0]
                        end = np.array([[segment.end.real], [segment.end.imag], [1]])
                        new_end = np.dot(transform_matrix, end)[0][0], np.dot(transform_matrix, end)[1][0]
                        if end_point != new_start:
                            gcode_file.write(f"G0 Z{feed_height} F{feed_rate}\n")
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                            gcode_file.write(f"G0 Z{z} F{feed_rate}\n")
                            gcode_file.write(f"G1 X{new_end[0]:.3f} Y{-new_end[1]:.3f}\n")
                            # flag = False
                        else:
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                            gcode_file.write(f"G1 X{new_end[0]:.3f} Y{-new_end[1]:.3f}\n")
                        end_point = (new_end[0], new_end[1])

                    elif segment.__class__.__name__ == 'CubicBezier':
                        start = np.array([[segment.start.real], [segment.start.imag], [1]])
                        new_start = np.dot(transform_matrix, start)[0][0], np.dot(transform_matrix, start)[1][0]
                        end = np.array([[segment.end.real], [segment.end.imag], [1]])
                        new_end = np.dot(transform_matrix, end)[0][0], np.dot(transform_matrix, end)[1][0]
                        control1 = np.array([[segment.control1.real], [segment.control1.imag], [1]])
                        new_control1 = np.dot(transform_matrix, control1)[0][0], np.dot(transform_matrix, control1)[1][
                            0]
                        control2 = np.array([[segment.control2.real], [segment.control2.imag], [1]])
                        new_control2 = np.dot(transform_matrix, control2)[0][0], np.dot(transform_matrix, control2)[1][
                            0]

                        # 对于三次贝塞尔曲线，使用插值法转换为直线段
                        if end_point != new_start:
                            gcode_file.write(f"G0 Z{feed_height} F{feed_rate}\n")
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                            gcode_file.write(f"G0 Z{z} F{feed_rate}\n")
                            # flag = False
                        else:
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                        points = interpolate_bezier(
                            (new_start[0], -new_start[1]),
                            (new_control1[0], -new_control1[1]),
                            (new_control2[0], -new_control2[1]),
                            (new_end[0], -new_end[1]),
                            num_points
                        )
                        for i in range(1, len(points)):
                            gcode_file.write(f"G1 X{points[i][0]:.3f} Y{points[i][1]:.3f}\n")
                        end_point = (new_end[0], new_end[1])

                    elif segment.__class__.__name__ == 'QuadraticBezier':
                        start = np.array([[segment.start.real], [segment.start.imag], [1]])
                        new_start = np.dot(transform_matrix, start)[0][0], np.dot(transform_matrix, start)[1][0]
                        end = np.array([[segment.end.real], [segment.end.imag], [1]])
                        new_end = np.dot(transform_matrix, end)[0][0], np.dot(transform_matrix, end)[1][0]
                        control = np.array([[segment.control.real], [segment.control.imag], [1]])
                        new_control = np.dot(transform_matrix, control)[0][0], np.dot(transform_matrix, control)[1][0]
                        if end_point != new_start:
                            gcode_file.write(f"G0 Z{feed_height} F{feed_rate}\n")
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                            gcode_file.write(f"G0 Z{z} F{feed_rate}\n")
                            # flag = False
                        else:
                            gcode_file.write(f"G0 X{new_start[0]:.3f} Y{-new_start[1]:.3f}\n")
                        # 对于二次贝塞尔曲线，使用插值法转换为直线段
                        points = interpolate_bezier(
                            (new_start[0], -new_start[1]),
                            (new_control[0], -new_control[1]),
                            (new_end[0], -new_end[1]),
                            num_points
                        )
                        for i in range(1, len(points)):
                            gcode_file.write(f"G1 X{points[i][0]:.3f} Y{points[i][1]:.3f}\n")
                        end_point = (new_end[0], new_end[1])

                    elif segment.__class__.__name__ == 'Arc':
                        start = np.array([[segment.start.real], [segment.start.imag], [1]])
                        new_start = np.dot(transform_matrix, start)[0][0], np.dot(transform_matrix, start)[1][0]
                        end = np.array([[segment.end.real], [segment.end.imag], [1]])
                        new_end = np.dot(transform_matrix, end)[0][0], np.dot(transform_matrix, end)[1][0]
                        # 对于圆弧路径，转换为 G2/G3 命令
                        start = (new_start[0], -new_start[1])
                        end = (new_end[0], -new_end[1])
                        rx = -segment.radius.real
                        ry = -segment.radius.imag
                        x_rotation = segment.rotation
                        large_arc_flag = not segment.large_arc
                        sweep_flag = segment.sweep
                        a = svgArcToCenterParam(start[0], start[1], rx, ry, x_rotation, large_arc_flag, sweep_flag,
                                                end[0],
                                                end[1])

                        x1, y1 = start  # 起始点
                        x2, y2 = end
                        cx, cy = a['cx'], a['cy']  # 圆心
                        startAngle = a['startAngle']  # 起始角度
                        endAngle = a['endAngle']  # 角度差
                        clockwise = a['clockwise']  # 顺时针
                        # 如果是顺时针，使用 G2，否则使用 G3
                        gcode_command = "G2" if clockwise else "G3"

                        # 计算终止点角度，防止超出圆弧的范围
                        # endAngle = startAngle + deltaAngle
                        while endAngle > math.pi * 2:
                            endAngle -= math.pi * 2
                        while endAngle < 0:
                            endAngle += math.pi * 2

                        # G-code 中通常使用 X, Y 来指定圆弧的终点，I, J 来指定圆心的偏移量
                        # I, J 是相对于起始点 (x1, y1) 的圆心偏移
                        I = cx - x1
                        J = cy - y1

                        # 输出 G-code
                        if end_point != new_start:
                            gcode_file.write(f"G0 Z{feed_height} F{feed_rate}\n")
                            gcode_file.write(f"G0 X{x1:.3f} Y{y1:.3f} F{feed_rate}\n")  # 先移动到起始点
                            gcode_file.write(f"G0 Z{z} F{feed_rate}\n")
                            # flag = False
                        else:
                            gcode_file.write(f"G0 X{x1:.3f} Y{y1:.3f} F{feed_rate}\n")  # 先移动到起始点
                        gcode_file.write(f"{gcode_command} X{x2:.3f} Y{y2:.3f} I{I:.3f} J{J:.3f} F{feed_rate}")
                        end_point = (new_end[0], new_end[1])

        # 结束 G-code
        gcode_file.write("M30\n")


# 使用示例
# svg_to_gcode('../file/logo.svg', 'output.nc')
# svg_to_gcode('../file/phone.svg', 'output.nc')
svg_file = 'image.svg'
z_per = 1
z_depth = -10
feed_height = 20
feed_rate = 1000
num_points = 10
svg_to_gcode(svg_file, z_per, z_depth, feed_height, feed_rate, num_points)
