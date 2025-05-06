import trimesh
import numpy as np
import matplotlib.pyplot as plt

# 载入STL模型
mesh = trimesh.load("../file\吸泵外壳.stl")  # 加载模型

# 获取模型Z轴范围
min_z = mesh.bounds[0][2]
max_z = mesh.bounds[1][2]

# 每隔1mm进行切片
slice_thickness = 1.0
z_levels = np.arange(min_z, max_z + slice_thickness, slice_thickness)

# 遍历每个高度进行切片
for z in z_levels:
    # 使用一个平面进行切割
    slice = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])

    if slice is None:
        continue  # 没有交叉时跳过

    # 转换为2D路径（投影轮廓）
    slice_2D, _ = slice.to_planar()

    # 显示切片（可选）
    slice_2D.show()

    # 或导出为路径数据（例如 laser path、gcode）
    for entity in slice_2D.entities:
        print(f"Z = {z:.2f}mm: path = {entity}")
