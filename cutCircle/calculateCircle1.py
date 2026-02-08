import math
import re


def parse_gcode(gcode):
    """
    解析 G-code，提取包含圆弧命令的行。

    :param gcode: G-code 字符串
    :return: 提取出的包含圆弧命令的列表
    """
    # 使用正则表达式查找 G2 或 G3 指令并提取相关数据（坐标和半径）
    pattern = re.compile(r"X([\d\.-]+)\s*Y([\d\.-]+)\s*R([\d\.-]+)")
    matches = re.findall(pattern, gcode)
    print(matches)
    # 返回所有圆弧指令
    return [(float(match[0]), float(match[1]), float(match[2])) for match in matches]


def calculate_arc_radius_error(x0, y0, r, x1, y1):
    """
    计算当前位置到目标位置的距离，并验证是否能形成有效的圆弧。

    :param x0: 当前坐标 x
    :param y0: 当前坐标 y
    :param r: 圆弧的半径
    :param x1: 目标坐标 x
    :param y1: 目标坐标 y
    :return: 返回是否成功，若失败则返回错误信息
    """

    # 计算当前位置到目标位置的距离 d
    x = x1 - x0
    y = y1 - y0
    distance = math.sqrt(x ** 2 + y ** 2)

    # 计算 h_x2_div_d
    h_x2_div_d = 4.0 * r * r - x ** 2 - y ** 2

    # 如果 h_x2_div_d 小于 0，表示不能形成有效圆弧
    if h_x2_div_d < 0:
        return False, f"错误: 圆弧半径无法满足条件，h_x2_div_d = {h_x2_div_d}. 当前位置到目标点的距离 ({distance}) 大于给定半径 ({r})。"

    return True, f"成功: 圆弧可以形成，h_x2_div_d = {h_x2_div_d}. 当前位置到目标点的距离 ({distance}) 小于给定半径 ({r})。"


def validate_gcode(gcode):
    """
    验证 G-code 中的圆弧指令是否有效。

    :param gcode: G-code 字符串
    :return: 返回每个圆弧指令的验证结果
    """
    # 解析 G-code
    arcs = parse_gcode(gcode)

    # 初始位置，假设从 (0, 0) 开始
    current_x, current_y = 0.0, 0.0

    results = []

    # 遍历每个圆弧指令，验证是否有效
    for x1, y1, r in arcs:
        success, message = calculate_arc_radius_error(current_x, current_y, r, x1, y1)
        results.append(f"{11}: {message}")

        # 更新当前位置为目标位置
        current_x, current_y = x1, y1

    return results


# 测试 G-code 数据
gcode = """
N14 G54
N16 G17 G0 G90 X33.564 Y-2.483 S9800 M3
N20 Z5.5
N22 G94 G3 X33.564 Y-2.483 Z4.908 I-1.063 J2.482 F1000.
N24 X33.564 Y-2.483 Z4.315 I-1.063 J2.482
N26 X33.564 Y-2.483 Z3.723 I-1.063 J2.482
N28 X33.564 Y-2.483 Z3.13 I-1.063 J2.482
N30 X33.564 Y-2.483 Z2.538 I-1.063 J2.482
N32 X33.564 Y-2.483 Z1.945 I-1.063 J2.482
N34 X33.564 Y-2.483 Z1.353 I-1.063 J2.482
N36 X33.564 Y-2.483 Z0.761 I-1.063 J2.482
N38 X33.564 Y-2.483 Z0.168 I-1.063 J2.482
N40 X33.564 Y-2.483 Z-0.424 I-1.063 J2.482
N42 X33.564 Y-2.483 Z-1.017 I-1.063 J2.482
N44 X33.564 Y-2.483 Z-1.609 I-1.063 J2.482
N46 X33.564 Y-2.483 Z-2.201 I-1.063 J2.482
N48 X33.564 Y-2.483 Z-2.794 I-1.063 J2.482
N50 X29.801 Y-0.001 Z-3.2 R-2.7
N52 X32.667 Y2.731 R-2.718
N54 X30.634 Y-2.193 R2.827
N56 X30.875 Y2.426 R-2.902
N58 X34.249 Y-2.538 R-3.002
N60 X29.755 Y1.492 R-3.1
N62 X34.059 Y-2.878 R3.184
N64 X29.747 Y1.844 R-3.291
N66 X34.19 Y-3.03 R3.381
N68 X29.648 Y2.05 R-3.488
N70 X34.494 Y-3.086 R3.586
N72 X29.559 Y2.275 R-3.693
N74 X34.959 Y-3.002 R3.795
N76 X29.348 Y2.347 R-3.903
N78 X35.247 Y-3.035 R4.008
N80 X29.277 Y2.607 R-4.118
N82 X35.528 Y-3.067 R4.226
N84 X29.222 Y2.882 R-4.337
N86 X35.806 Y-3.102 R4.449
N88 X29.182 Y3.171 R4.561
N90 X35.919 Y-3.311 R-4.675
"""

# 验证 G-code
results = validate_gcode(gcode)

# 打印验证结果
for result in results:
    print(result)
