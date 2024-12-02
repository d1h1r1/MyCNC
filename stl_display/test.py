import vtk
from svgpathtools import svg2paths


def leftButtonPressEvent(obj, event):
    print('鼠标左键按下')

    # 获取 Picker
    # picker = obj.GetPicker()
    click_pos = interactor.GetEventPosition()
    picker.Pick(click_pos[0], click_pos[1], 0, renderer)
    # print(picker)
    # 获取点击位置的三维坐标
    pick_pos = picker.GetPickPosition()
    print('三维坐标:', pick_pos)




def svg_to_vtk(svg_file):
    # 解析SVG文件
    paths, attributes = svg2paths(svg_file)

    actors = []
    for path in paths:
        # 创建每个路径对应的PolyData
        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        point_id = 0
        for segment in path:
            start_point = segment.start
            end_point = segment.end
            points.InsertNextPoint(start_point.real, start_point.imag, 0)
            points.InsertNextPoint(end_point.real, end_point.imag, 0)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(point_id)
            lines.InsertCellPoint(point_id + 1)
            point_id += 2

        poly_data.SetPoints(points)
        poly_data.SetLines(lines)

        # 创建一个mapper来渲染路径
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # 创建一个actor来显示路径
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        actors.append(actor)

    return actors


# 创建渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 加载并渲染SVG
actors = svg_to_vtk('../file/phone.svg')  # 替换为你的SVG文件路径
for actor in actors:
    renderer.AddActor(actor)

# 创建渲染器
# renderer = vtk.vtkRenderer()
# renderer.AddActor(actor)  # 将 STL 模型添加到渚视器中
renderer.ResetCamera()  # 调整相机以适应模型

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

interactor_style = vtk.vtkInteractorStyleTrackballCamera()

# 禁用默认鼠标左键旋转
interactor_style.SetCurrentRenderer(renderer)
interactor_style.OnLeftButtonDown = lambda: None  # 取消左键事件
interactor_style.OnLeftButtonUp = lambda: None


# 将鼠标中键事件绑定为旋转
def rotate_with_middle_button():
    interactor_style.StartRotate()


def end_rotate_with_middle_button():
    interactor_style.EndRotate()


interactor_style.OnMiddleButtonDown = rotate_with_middle_button
interactor_style.OnMiddleButtonUp = end_rotate_with_middle_button

interactor.SetInteractorStyle(interactor_style)

camera = renderer.GetActiveCamera()


# 键盘事件的回调函数
def key_press_callback(obj, event):
    key = obj.GetKeySym()
    step = 10  # 平移步长
    if key == "Up":
        camera.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1] + step, camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0], camera.GetFocalPoint()[1] + step, camera.GetFocalPoint()[2])
    elif key == "Down":
        camera.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1] - step, camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0], camera.GetFocalPoint()[1] - step, camera.GetFocalPoint()[2])
    elif key == "Left":
        camera.SetPosition(camera.GetPosition()[0] - step, camera.GetPosition()[1], camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0] - step, camera.GetFocalPoint()[1], camera.GetFocalPoint()[2])
    elif key == "Right":
        camera.SetPosition(camera.GetPosition()[0] + step, camera.GetPosition()[1], camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0] + step, camera.GetFocalPoint()[1], camera.GetFocalPoint()[2])
    elif key == "r":  # 重置视图
        renderer.ResetCamera()
    renderWindow.Render()


# 绑定键盘事件
interactor.AddObserver("KeyPressEvent", key_press_callback)

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
