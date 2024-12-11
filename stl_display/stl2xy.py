import json

import vtk

# 读取 STL 文件
reader = vtk.vtkSTLReader()
reader.SetFileName("../file/Coin_half.stl")
# reader.SetFileName("../file/Throwing.stl")
reader.Update()

# 获取加载的 STL 数据
polydata = reader.GetOutput()

# 获取点云数据
points = polydata.GetPoints()

# 创建一个新的点列表用于存储投影后的点
projected_points = vtk.vtkPoints()
points_list = []
# 投影到 XY 平面，忽略 Z 坐标
for i in range(points.GetNumberOfPoints()):
    point = points.GetPoint(i)
    points_list.append([point[0], point[1]])
    # 保留 X 和 Y 坐标，将 Z 坐标设为 0
    projected_points.InsertNextPoint(point[0], point[1], 0)
with open("../file/point.json", "w") as f:
    f.write(str(points_list))
print(points_list)