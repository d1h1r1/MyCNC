import vtk

# 创建一个 vtkAppendPolyData 对象
append_filter = vtk.vtkAppendPolyData()

# 假设你有多个点对
points = [((0, 0, 0), (1, 1, 1)), ((1, 1, 1), (2, 2, 2)), ((2, 2, 2), (3, 3, 3))]

for p1, p2 in points:
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(p1)
    line_source.SetPoint2(p2)
    line_source.Update()

    append_filter.AddInputData(line_source.GetOutput())

# 更新 append_filter
append_filter.Update()

# 创建 mapper 和 actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(append_filter.GetOutput())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1, 0, 0)  # 设置颜色为红色

# 创建渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 添加 actor 到渲染器
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)  # 设置背景颜色

# 开始渲染
render_window.Render()
render_window_interactor.Start()
