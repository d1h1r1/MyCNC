import vtk


def leftButtonPressEvent(obj, event):
    print('鼠标左键按下')
    clickPos = obj.GetEventPosition()
    print('鼠标坐标:', clickPos)


# 创建 STL 文件读取器
stlReader = vtk.vtkSTLReader()
stlReader.SetFileName("elephant.stl")  # 这里是你 STL 文件的路径
stlReader.Update()  # 读取 STL 数据

# 创建 PolyData 映射器
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stlReader.GetOutputPort())

# 创建演员 (Actor) 来显示 STL 模型
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)  # 将 STL 模型添加到渲染器中
renderer.ResetCamera()  # 调整相机以适应模型

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# 添加左键按下事件的观察者
interactor.AddObserver('LeftButtonPressEvent', leftButtonPressEvent)

# 启动渲染和交互
renderWindow.Render()
interactor.Start()
