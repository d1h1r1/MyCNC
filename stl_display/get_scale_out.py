import vtk

# 创建 STL 文件读取器
cube = vtk.vtkSTLReader()
cube.SetFileName("elephant.stl")  # 替换为你的 STL 文件路径
cube.Update()  # 读取 STL 数据


# 定义一个平面
pick_pos = [50.61344749553384, 68.86563948557948, 17.0]  # 平面原点
normal = [0, 0, 1]    # 平面法向量

plane = vtk.vtkPlane()
plane.SetOrigin(pick_pos)
plane.SetNormal(normal)

# 使用 vtkCutter 计算平面与模型的交线
cutter = vtk.vtkCutter()
cutter.SetInputData(cube.GetOutput())
cutter.SetCutFunction(plane)
cutter.Update()

# 映射交线数据
cutter_mapper = vtk.vtkPolyDataMapper()
cutter_mapper.SetInputConnection(cutter.GetOutputPort())

cutter_actor = vtk.vtkActor()
cutter_actor.SetMapper(cutter_mapper)
cutter_actor.GetProperty().SetColor(1, 0, 0)  # 红色表示平面的外轮廓线
cutter_actor.GetProperty().SetLineWidth(2)

# 显示原始立方体
cube_mapper = vtk.vtkPolyDataMapper()
cube_mapper.SetInputConnection(cube.GetOutputPort())

cube_actor = vtk.vtkActor()
cube_actor.SetMapper(cube_mapper)
cube_actor.GetProperty().SetOpacity(0.5)  # 半透明

# 设置渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
renderer.AddActor(cutter_actor)
renderer.AddActor(cube_actor)
renderer.SetBackground(0.1, 0.2, 0.4)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# 开始渲染
render_window.Render()
interactor.Start()
