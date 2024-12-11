import json

with open("../file/point.json") as f:
    points = json.load(f)

points_list = []
points_list_child = []

for i in range(len(points)):
    point = points[i]
    if i > 0:
        if abs(points[i][0] - points[i - 1][0]) > 10 or abs(points[i][1] - points[i - 1][1]) > 10:
            points_list.append(points_list_child.copy())
            points_list_child = []
    points_list_child.append(point)

if points_list_child:
    points_list.append(points_list_child)


# print(len(points_list))
# print(points_list)
# exit()
# new_points_list = []
# x_distance = 0
# y_distance = 0
# for points in points_list:
#     start = points[0][0], points[0][1]
#     end = points[len(points)-1][0], points[len(points)-1][1]
#     points_list.remove(points)
#     for j in points_list:
#         new_start = j[0][0], j[0][1]
#         new_end = j[len(j) - 1][0], j[len(j) - 1][1]
#
#     print(start, end)
#     print("==========")

import math


# 计算两个点之间的欧几里得距离
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# 获取曲线的首尾坐标
def get_first_and_last(curve):
    return curve[0], curve[-1]


# 排序并连接曲线
def sort_and_connect_curves(curves):
    # 存储已连接的曲线
    connected_curves = []
    remaining_curves = curves.copy()  # 复制曲线列表

    # 初始选择第一条曲线
    current_curve = remaining_curves.pop(0)
    connected_curves.append(current_curve)

    # 获取当前曲线的尾坐标
    _, current_end = get_first_and_last(current_curve)

    # 循环直到所有曲线都被连接
    while remaining_curves:
        min_distance = float('inf')
        next_curve = None
        next_curve_index = -1

        # 比较当前尾坐标与所有剩余曲线的首坐标，找到最近的曲线
        for i, curve in enumerate(remaining_curves):
            first, _ = get_first_and_last(curve)
            dist = distance(current_end, first)
            if dist < min_distance:
                min_distance = dist
                next_curve = curve
                next_curve_index = i

        # 将找到的最近曲线加入连接的曲线中
        connected_curves.append(next_curve)
        # 更新当前的尾坐标
        _, current_end = get_first_and_last(next_curve)

        # 从剩余曲线中移除已连接的曲线
        remaining_curves.pop(next_curve_index)

    # 返回连接后的曲线
    return connected_curves


# 示例：3D数组中的曲线（第二层是坐标，第三层是多个曲线）
curves = [
    [[0, 0], [1, 1], [2, 2]],  # 曲线1
    [[3, 3], [4, 4], [5, 5]],  # 曲线2
    [[1, 1], [2, 1], [3, 1]],  # 曲线3
]

# 调用排序并连接曲线的函数
# print(points_list)
new_pointList = []
connected_curve = sort_and_connect_curves(points_list)
for connect in connected_curve:
    for i in connect:
        new_pointList.append(i)
print(new_pointList)
# print(connected_curve)

