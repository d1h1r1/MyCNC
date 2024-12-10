import json
import math
import time

import matplotlib.pyplot as plt

# 提取点的坐标

with open("../file/point.json") as f:
    data = json.load(f)

start = time.time()
for i in data:
    # print(i)
    pass
end = time.time()

print(end-start)


def SpiralPathPart(center_x, center_y, z_depth, min_radius, max_radius, step_over, layer):
    angle_step = 2 * math.pi / 100  # 每个分段的角度增量
    paths = []  # 存储路径点
    num_turns = int((max_radius - min_radius) // step_over)
    # print(num_turns)
    dz = z_depth / layer
    for i in range(1, layer + 1):
        z = 0 + i * dz
        for turn in range(1, num_turns + 1):
            path = ocl.Path()
            for i in range(101):  # 101 点构成一圈
                angle = i * angle_step  # 当前角度
                radius = turn * step_over + min_radius  # 半径逐渐增大
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                p = ocl.Point(x, y, z)
                if i > 0:  # 从第二个点开始创建线段
                    l = ocl.Line(prev_p, p)
                    path.append(l)
                prev_p = p
            paths.append(path)
    return paths
