import xml.etree.ElementTree as ET
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


def generate_arc_gcode(x1, y1, x2, y2 ,cx, cy, startAngle, endAngle, clockwise, feedrate=1000):
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


# 计算圆弧的G2/G3命令
def arc_to_gcode(start, end, rx, ry, x_rotation, large_arc_flag, sweep_flag, num_points=10):
    # 将角度转换为弧度
    sweep_flag = 1 if sweep_flag else 0
    large_arc_flag = 1 if large_arc_flag else 0

    # 计算圆心坐标（此方法有些复杂，需要根据起点、终点、旋转和标志计算圆心）
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)

    # 使用适当的公式将 arc 参数转换为 G2/G3
    points = []
    for t in np.linspace(0, 1, num_points):
        x = start[0] + t * (end[0] - start[0])
        y = start[1] + t * (end[1] - start[1])
        points.append((x, y))

    return points


# 主函数：将 SVG 转换为 G-code
def svg_to_gcode(svg_file, output_file, feed_rate=1000, num_points=10):
    num = 0
    tree = ET.parse('image.svg')
    root = tree.getroot()
    print(f"Root tag: {root.tag}")
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for path in root.findall(".//svg:g", namespace):
        d = path.attrib.get('transform')
        print(f"Path Data (d): {d}")

    for path in root.findall(".//svg:path", namespace):
        # 获取路径数据
        d = path.attrib.get('d')
        # 获取变换矩阵
        transform = path.attrib.get('transform')

        print(f"Path Data (d): {d}")
        print(f"Transform: {transform}")
    exit()
    # print(attributes)
    with open(output_file, 'w') as gcode_file:
        # 写入 G-code 文件的头部
        gcode_file.write("G21\nG0 G17 G49 G80 G90\n")
        gcode_file.write(f"F{feed_rate} ; Set feed rate\n")

        # 遍历路径并转换为 G-code
        for path in paths:
            # a = attribute_dictionary_list[num]
            # print(a)
            num += 1
            for segment in path:
                # print(segment)
                if segment.__class__.__name__ == 'Line':
                    # 对于直线段，直接输出 G1 命令
                    start = segment.start
                    end = segment.end
                    gcode_file.write(f"G0 X{start.real:.3f} Y{-start.imag:.3f}\n")
                    gcode_file.write(f"G1 X{end.real:.3f} Y{-end.imag:.3f}\n")

                elif segment.__class__.__name__ == 'CubicBezier':
                    # 对于三次贝塞尔曲线，使用插值法转换为直线段
                    gcode_file.write(f"G0 X{segment.start.real:.3f} Y{-segment.start.imag:.3f}\n")
                    points = interpolate_bezier(
                        (segment.start.real, -segment.start.imag),
                        (segment.control1.real, -segment.control1.imag),
                        (segment.control2.real, -segment.control2.imag),
                        (segment.end.real, -segment.end.imag),
                        num_points
                    )
                    for i in range(1, len(points)):
                        gcode_file.write(f"G1 X{points[i][0]:.3f} Y{points[i][1]:.3f}\n")

                elif segment.__class__.__name__ == 'QuadraticBezier':
                    gcode_file.write(f"G0 X{segment.start.real:.3f} Y{-segment.start.imag:.3f}\n")
                    # 对于二次贝塞尔曲线，使用插值法转换为直线段
                    points = interpolate_bezier(
                        (segment.start.real, -segment.start.imag),
                        (segment.control.real, -segment.control.imag),
                        (segment.end.real, -segment.end.imag),
                        num_points
                    )
                    for i in range(1, len(points)):
                        gcode_file.write(f"G1 X{points[i][0]:.3f} Y{points[i][1]:.3f}\n")

                elif segment.__class__.__name__ == 'Arc':
                    gcode_file.write(f"G0 X{segment.start.real:.3f} Y{-segment.start.imag:.3f}\n")
                    # 对于圆弧路径，转换为 G2/G3 命令
                    start = (segment.start.real, -segment.start.imag)
                    # gcode_file.write(f"G0 X{segment.start.real:.3f} Y{segment.start.imag:.3f}\n")
                    end = (segment.end.real, -segment.end.imag)
                    rx = -segment.radius.real
                    ry = -segment.radius.imag
                    x_rotation = segment.rotation
                    large_arc_flag = not segment.large_arc
                    sweep_flag = segment.sweep
                    a = svgArcToCenterParam(start[0], start[1], rx, ry, x_rotation, large_arc_flag, sweep_flag, end[0], end[1])

                    # 示例调用
                    x1, y1 = start  # 起始点
                    x2, y2 = end
                    cx, cy = a['cx'], a['cy']  # 圆心
                    startAngle = a['startAngle']  # 起始角度
                    endAngle = a['endAngle']  # 角度差
                    clockwise = a['clockwise']  # 顺时针

                    gcode = generate_arc_gcode(x1, y1, x2, y2, cx, cy, startAngle, endAngle, clockwise)
                    # print(gcode)
                    gcode_file.write(gcode + "\n")
                    # points = arc_to_gcode(start, end, rx, ry, x_rotation, large_arc_flag, sweep_flag, num_points)
                    # # 输出圆弧的 G2/G3 命令
                    # for point in points:
                    #     gcode_file.write(f"G1 X{point[0]:.3f} Y{point[1]:.3f}\n")

        # 结束 G-code
        gcode_file.write("M30 ; End of program\n")


# 使用示例
# svg_to_gcode('../file/logo.svg', 'output.nc')
# svg_to_gcode('../file/phone.svg', 'output.nc')
svg_to_gcode('image.svg', 'output.nc')