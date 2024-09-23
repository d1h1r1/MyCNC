import math

import vtk

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
interactorStyle.Rotate = lambda: None  # 禁用旋转功能
renderWindowInteractor.SetInteractorStyle(interactorStyle)

lines = vtk.vtkCellArray()

end_point = (80.0, -15.0, 0.0)  # 假设的起点
start_point = (81.348, -15.696, 0.0)  # 终点
I = 1.375  # X 方向偏移
J = 2.945  # Y 方向偏移
id = 0
radius = math.sqrt(I ** 2 + J ** 2)

center_offset = [I, J, 0]  # 圆心相对起点的偏移
center = (start_point[0] + I, start_point[1] + J, 0.0)

resolution = 50
points = vtk.vtkPoints()
for n in range(0, resolution):
    line = vtk.vtkLine()
    angle1 = (float(n) / (float(resolution))) * 2 * math.pi
    angle2 = (float(n + 1) / (float(resolution))) * 2 * math.pi
    p1 = (center[0] + radius * math.cos(angle1), center[1] + radius * math.sin(angle1), center[2])
    p2 = (center[0] + radius * math.cos(angle2), center[1] + radius * math.sin(angle2), center[2])
    points.InsertNextPoint(p1)
    points.InsertNextPoint(p2)
    line.GetPointIds().SetId(0, id)
    id = id + 1
    line.GetPointIds().SetId(1, id)
    id = id + 1
    lines.InsertNextCell(line)

pdata = vtk.vtkPolyData()
pdata.SetPoints(points)
pdata.SetLines(lines)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(pdata)
actor1 = vtk.vtkActor()
actor1.GetProperty().SetLineWidth(5)  # 设置线宽为5
actor1.SetMapper(mapper)
actor1.GetProperty().SetColor(1, 0, 0)  # 红色圆弧表示 G02

arc1 = vtk.vtkArcSource()

# 设置顺时针圆弧
arc1.SetPoint1(start_point[0], start_point[1], start_point[2])
arc1.SetPoint2(end_point[0], end_point[1], end_point[2])
arc1.SetCenter(start_point[0] + center_offset[0], start_point[1] + center_offset[1], 0)
arc1.SetResolution(100)
arc1.Update()

# 创建 Mapper 和 Actor
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(arc1.GetOutputPort())
actor2 = vtk.vtkActor()
actor2.GetProperty().SetLineWidth(5)  # 设置线宽为5
actor2.SetMapper(mapper1)
actor2.GetProperty().SetColor(0,1,0)  # 红色圆弧表示 G02

# 将 actor 添加到渲染器
# renderer.AddActor(actor1)
renderer.AddActor(actor2)

renderer.SetBackground(0.1, 0.2, 0.4)  # 设置背景颜色

# 渲染并开始交互
renderWindow.Render()
renderWindowInteractor.Start()
# SetMapper(mapper)
# SetColor(color)
