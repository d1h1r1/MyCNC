import vtk


def leftButtonPressEvent(obj, event):
    print('鼠标左键按下')

    # 获取 Picker
    picker = obj.GetPicker()

    # 获取点击位置的三维坐标
    pick_pos = picker.GetPickPosition()
    print('三维坐标:', pick_pos)

    # 获取点击的面（cell）
    cell_id = picker.GetCellId()
    if cell_id != -1:
        print(f"点击的是面 {cell_id}")
    else:
        print("没有点击到有效的面")


# 创建 STL 文件读取器
stlReader = vtk.vtkSTLReader()
stlReader.SetFileName("elephant.stl")  # 替换为你的 STL 文件路径
stlReader.Update()  # 读取 STL 数据

# 获取模型的 PolyData
stlPolyData = stlReader.GetOutput()
print(stlPolyData)
# 创建 PolyData 映射器
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stlReader.GetOutputPort())

# 创建演员 (Actor) 来显示 STL 模型
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)  # 将 STL 模型添加到渚视器中
renderer.ResetCamera()  # 调整相机以适应模型

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# 创建 picker 用于捕捉鼠标点击事件
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.001)  # 调整容差值为 0.001

# 设置渲染窗口交互器的 picker
interactor.SetPicker(picker)

# 添加左键按下事件的观察者
interactor.AddObserver('LeftButtonPressEvent', leftButtonPressEvent)

# 启动渲染和交互
renderWindow.Render()
interactor.Start()
