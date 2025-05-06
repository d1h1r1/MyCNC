# import pyclipper
# from matplotlib import pyplot as plt
#
outer_points = [[39.673, 21.591], [38.913, 21.58], [38.066, 21.548], [37.145, 21.497], [36.167, 21.428],
                [35.146, 21.343], [34.097, 21.243], [33.035, 21.131], [31.975, 21.008], [30.931, 20.875],
                [30.931, 20.875], [30.931, 38.689], [30.931, 38.689], [30.896, 39.059], [30.797, 39.408],
                [30.639, 39.729], [30.429, 40.017], [30.173, 40.266], [29.876, 40.469], [29.546, 40.622],
                [29.188, 40.718], [28.808, 40.751], [28.808, 40.751], [15.918, 40.751], [15.918, 40.751],
                [15.532, 40.718], [15.162, 40.622], [14.817, 40.469], [14.503, 40.266], [14.23, 40.017],
                [14.003, 39.729], [13.832, 39.408], [13.724, 39.059], [13.686, 38.689], [13.686, 38.689],
                [13.686, -33.492], [13.686, -33.492], [13.704, -34.009], [13.771, -34.464], [13.902, -34.863],
                [14.115, -35.213], [14.426, -35.522], [14.852, -35.797], [15.409, -36.043], [16.115, -36.268],
                [16.985, -36.48], [16.985, -36.48], [19.093, -36.951], [21.353, -37.399], [23.746, -37.814],
                [26.248, -38.188], [28.84, -38.513], [31.501, -38.78], [34.209, -38.981], [36.944, -39.108],
                [39.684, -39.153], [39.684, -39.153], [45.149, -38.798], [50.023, -37.748], [54.293, -36.025],
                [57.945, -33.652], [60.963, -30.65], [63.336, -27.041], [65.047, -22.847], [66.085, -18.091],
                [66.433, -12.795], [66.433, -12.795], [66.433, -4.767], [66.433, -4.767], [66.102, 0.394],
                [65.121, 5.078], [63.485, 9.25], [61.19, 12.876], [58.231, 15.92], [54.605, 18.349], [50.306, 20.127],
                [45.33, 21.219], [39.673, 21.591]]
inner_points = [[49.156, -12.806], [49.08, -15.166], [48.831, -17.354], [48.379, -19.34], [47.692, -21.098],
                [46.741, -22.599], [45.495, -23.815], [43.921, -24.718], [41.991, -25.28], [39.673, -25.474],
                [39.673, -25.474], [38.514, -25.463], [37.385, -25.432], [36.294, -25.383], [35.247, -25.319],
                [34.252, -25.242], [33.316, -25.154], [32.446, -25.059], [31.648, -24.958], [30.931, -24.853],
                [30.931, -24.853], [30.931, 7.27], [30.931, 7.27], [31.82, 7.368], [32.771, 7.459], [33.766, 7.54],
                [34.787, 7.611], [35.817, 7.671], [36.838, 7.72], [37.833, 7.756], [38.784, 7.778], [39.673, 7.786],
                [39.673, 7.786], [41.991, 7.592], [43.921, 7.031], [45.495, 6.131], [46.741, 4.92], [47.692, 3.428],
                [48.379, 1.683], [48.831, -0.285], [49.08, -2.448], [49.156, -4.777], [49.156, -4.777],
                [49.156, -12.806]]
#

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union

def generate_pocket_paths(outer, inner, step=0.2, num_samples=100):
    """
    生成环状区域逐步偏移的刀路点云
    :param outer: shapely Polygon，外边界
    :param inner: shapely Polygon，内边界
    :param step: 每次偏移的步长
    :param num_samples: 每层采样点数
    :return: 所有偏移层的点云列表
    """
    offset_layers = []  # 存储每一层的点云

    # 计算偏移过程
    current_boundary = outer
    while True:
        # 计算新的偏移区域
        new_boundary = current_boundary.buffer(-step)

        # 如果偏移后和内边界相交，则停止外轮廓偏移
        if new_boundary.intersects(inner) or new_boundary.distance(inner) < step:
            break

        # 采样点云
        points = []
        coords_list = list(new_boundary.exterior.coords)
        sample_indices = np.linspace(0, len(coords_list) - 1, num_samples, dtype=int)
        for i in sample_indices:
            points.append(coords_list[i])
        offset_layers.append(np.array(points))

        # 更新当前边界
        current_boundary = new_boundary

    # 内轮廓开始向内偏移
    current_boundary = inner
    while True:
        # 计算新的偏移区域（正向 buffer）
        new_boundary = current_boundary.buffer(step)

        # 如果偏移后变得过大（无效），停止
        if not new_boundary.is_valid:
            break

        # 采样点云
        points = []
        coords_list = list(new_boundary.exterior.coords)
        sample_indices = np.linspace(0, len(coords_list) - 1, num_samples, dtype=int)
        for i in sample_indices:
            points.append(coords_list[i])
        offset_layers.append(np.array(points))

        # 更新当前边界
        current_boundary = new_boundary

    return offset_layers  # 返回所有层的点云


# 创建不规则环形区域
outer_boundary = Polygon(outer_points)
inner_boundary = Polygon(inner_points)

# 生成刀路
offset_distance = 2  # 每次偏移的步进
num_samples = 200  # 采样点数
pocket_paths = generate_pocket_paths(outer_boundary, inner_boundary, offset_distance, num_samples)

# 绘制结果
fig, ax = plt.subplots()
ax.plot(*outer_boundary.exterior.xy, 'b-', label="原外边界")
ax.plot(*inner_boundary.exterior.xy, 'r-', label="原内边界")

# 画出每一层偏移路径
for i, points in enumerate(pocket_paths):
    ax.scatter(points[:, 0], points[:, 1], s=5, label=f"偏移层 {i+1}")

ax.set_aspect('equal')
ax.legend()
plt.show()
