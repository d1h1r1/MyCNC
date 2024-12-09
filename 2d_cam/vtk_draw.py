import vtk
from svgpathtools import svg2paths


class DraggableInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, actors):
        self.actors = actors
        self.dragged_actor = None
        self.start_x = 0
        self.start_y = 0

    def OnLeftButtonDown(self):
        # 获取鼠标点击的坐标
        click_pos = render_window_interactor.GetEventPosition()
        x, y = click_pos
        print(click_pos)

        # 寻找被点击的Actor
        for actor in self.actors:
            # 计算Actor的边界框，并判断是否点击到了Actor
            bounds = actor.GetBounds()
            if bounds[0] <= x <= bounds[1] and bounds[2] <= y <= bounds[3]:
                self.dragged_actor = actor
                self.start_x = x
                self.start_y = y
                return

        # 如果没有点击到Actor，则调用父类处理
        super().OnLeftButtonDown()

    def OnMouseMove(self):
        if self.dragged_actor:
            # 获取当前鼠标位置
            current_pos = render_window_interactor.GetEventPosition()
            dx = current_pos[0] - self.start_x
            dy = current_pos[1] - self.start_y

            # 更新Actor位置
            transform = vtk.vtkTransform()
            transform.Translate(dx, dy, 0)
            self.dragged_actor.SetUserTransform(transform)

            # 更新开始位置为当前鼠标位置
            self.start_x, self.start_y = current_pos

            # 重新渲染视图
            self.GetRenderWindow().Render()

        # 调用父类处理鼠标移动事件
        super().OnMouseMove()


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

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
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

# 创建 picker 用于捕捉鼠标点击事件
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.001)  # 调整容差值为 0.001

# 设置渲染窗口交互器的 picker
interactor.SetPicker(picker)

# 添加左键按下事件的观察者
interactor.AddObserver('LeftButtonPressEvent', leftButtonPressEvent)
# 渲染窗口
render_window.Render()
render_window_interactor.Start()
