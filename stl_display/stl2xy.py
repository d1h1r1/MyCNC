import json

import vtk

# 读取 STL 文件
reader = vtk.vtkSTLReader()
# reader.SetFileName("../file/Coin_half.stl")
reader.SetFileName("../file/Throwing.stl")
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
exit()
# 创建一个新的 PolyData 来存储投影后的点
projected_polydata = vtk.vtkPolyData()
projected_polydata.SetPoints(projected_points)

# 显示投影后的点
point_mapper = vtk.vtkPolyDataMapper()
point_mapper.SetInputData(projected_polydata)

point_actor = vtk.vtkActor()
point_actor.SetMapper(point_mapper)
point_actor.GetProperty().SetColor(1, 0, 0)  # 红色表示平面的外轮廓线
point_actor.GetProperty().SetLineWidth(2)
# 创建渲染器
renderer = vtk.vtkRenderer()

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 将点添加到渲染器中
renderer.AddActor(point_actor)

# 设置渲染参数
renderer.SetBackground(0, 0, 1)  # 白色背景

# 开始渲染
renderWindow.Render()
renderWindowInteractor.Start()
