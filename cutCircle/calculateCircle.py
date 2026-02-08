import math


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


# 测试数据
x0, y0 = 33.564, -2.483  # 当前坐标
r = -2.7  # 圆弧半径
x1, y1 = 29.801, -0.001  # 目标坐标

# 运行测试
success, message = calculate_arc_radius_error(x0, y0, r, x1, y1)
print(message)

# N52 X32.667 Y2.731 R-2.718
# N54 X30.634 Y-2.193 R2.827
# N56 X30.875 Y2.426 R-2.902
# N58 X34.249 Y-2.538 R-3.002
# N60 X29.755 Y1.492 R-3.1
# N62 X34.059 Y-2.878 R3.184
# N64 X29.747 Y1.844 R-3.291
# N66 X34.19 Y-3.03 R3.381
# N68 X29.648 Y2.05 R-3.488
# N70 X34.494 Y-3.086 R3.586
# N72 X29.559 Y2.275 R-3.693
# N74 X34.959 Y-3.002 R3.795
# N76 X29.348 Y2.347 R-3.903
# N78 X35.247 Y-3.035 R4.008
# N80 X29.277 Y2.607 R-4.118

# N84 X29.222, 2.882 R-4.337
# N86 X35.806, -3.102 R4.449
# N88 X29.182, 3.171 R4.561
# N90 X35.919, -3.311 R-4.675