import vtk

# 创建一个球体源
cube = vtk.vtkCubeSource()
cube.SetXLength(4.0)  # 设置 X 轴方向的长度
cube.SetYLength(2.0)  # 设置 Y 轴方向的长度
cube.SetZLength(3.0)  # 设置 Z 轴方向的长度
# cube.Update()

# 创建映射器
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cube.GetOutputPort())

# 创建演员
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 600)

# 创建交互式渲染窗口
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 创建一个拾取器
picker = vtk.vtkCellPicker()


# 定义鼠标点击回调函数
def click_callback(obj, event):
    # 获取点击位置的屏幕坐标
    click_pos = renderWindowInteractor.GetEventPosition()

    # 使用拾取器从屏幕坐标投射到三维场景
    picker.Pick(click_pos[0], click_pos[1], 0, renderer)

    # 获取拾取到的三维坐标
    pick_position = picker.GetPickPosition()
    print(f"点击位置的三维坐标: {pick_position}")


# 绑定鼠标左键点击事件到回调函数
renderWindowInteractor.AddObserver("LeftButtonPressEvent", click_callback)

# 初始化并启动渲染
renderWindow.Render()
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()
