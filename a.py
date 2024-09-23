import vtk
import math


def calculate_angle(center, point):
    """
    计算给定点相对于圆心的角度
    """
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return math.atan2(dy, dx)


def create_arc(center, radius, start_angle, end_angle, num_points=100):
    """
    创建圆弧
    """
    points = vtk.vtkPoints()
    for i in range(num_points + 1):
        angle = start_angle + (end_angle - start_angle) * (i / num_points)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.InsertNextPoint(x, y, center[2])  # z = center[2]保持不变
    return points


class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, renderer, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.renderer = renderer
        self.camera = renderer.GetActiveCamera()
        self.mouse_position = (0, 0)

    def left_button_press_event(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition()
        self.mouse_position = click_pos
        print(f"Mouse click position: {click_pos}")

        # 将屏幕坐标转化为世界坐标
        self.convert_screen_to_world(click_pos)

        # 继续事件循环
        self.OnLeftButtonDown()

    def convert_screen_to_world(self, screen_pos):
        """
        将鼠标的屏幕坐标转化为三维世界坐标
        """
        x, y = screen_pos

        # 获取深度值
        z = self.renderer.GetZ(x, y)

        # 将屏幕坐标（x, y, z）转换为世界坐标
        self.renderer.SetDisplayPoint(x, y, z)
        self.renderer.DisplayToWorld()
        world_point = self.renderer.GetWorldPoint()
        print(f"World coordinates: {world_point}")

        # 移动摄像机，使旋转中心变成鼠标位置
        self.camera.SetFocalPoint(world_point[:3])
        print(f"Camera focal point moved to: {self.camera.GetFocalPoint()}")


# 设置圆的参数
center = (0, 0, 0)  # 圆心坐标
radius = 5  # 半径
start_point = (5, 0, 0)  # 起始点
end_point = (0, 5, 0)  # 终止点

# 计算起始点和终止点相对于圆心的角度
start_angle = calculate_angle(center, start_point)  # 起始角度
end_angle = calculate_angle(center, end_point)  # 终止角度

# 确保顺时针和逆时针角度范围正确
if end_angle < start_angle:
    cw_arc_start = start_angle
    cw_arc_end = end_angle + 2 * vtk.vtkMath.Pi()  # 顺时针角度范围
else:
    cw_arc_start = start_angle
    cw_arc_end = end_angle

# 创建顺时针圆弧
cw_arc_points = create_arc(center, radius, cw_arc_start, cw_arc_end)

# 创建逆时针圆弧
ccw_arc_points = create_arc(center, radius, cw_arc_end, cw_arc_start + 2 * vtk.vtkMath.Pi())

# 创建顺时针圆弧polyline
cw_arc_polyline = vtk.vtkCellArray()
cw_arc_polyline.InsertNextCell(cw_arc_points.GetNumberOfPoints())
for i in range(cw_arc_points.GetNumberOfPoints()):
    cw_arc_polyline.InsertCellPoint(i)

# 创建逆时针圆弧polyline
ccw_arc_polyline = vtk.vtkCellArray()
ccw_arc_polyline.InsertNextCell(ccw_arc_points.GetNumberOfPoints())
for i in range(ccw_arc_points.GetNumberOfPoints()):
    ccw_arc_polyline.InsertCellPoint(i)

# 创建顺时针圆弧的polydata
cw_arc_data = vtk.vtkPolyData()
cw_arc_data.SetPoints(cw_arc_points)
cw_arc_data.SetLines(cw_arc_polyline)

# 创建逆时针圆弧的polydata
ccw_arc_data = vtk.vtkPolyData()
ccw_arc_data.SetPoints(ccw_arc_points)
ccw_arc_data.SetLines(ccw_arc_polyline)

# 可视化顺时针圆弧
cw_arc_mapper = vtk.vtkPolyDataMapper()
cw_arc_mapper.SetInputData(cw_arc_data)
cw_arc_actor = vtk.vtkActor()
cw_arc_actor.SetMapper(cw_arc_mapper)
cw_arc_actor.GetProperty().SetColor(1, 0, 0)  # 顺时针圆弧为红色

# 可视化逆时针圆弧
ccw_arc_mapper = vtk.vtkPolyDataMapper()
ccw_arc_mapper.SetInputData(ccw_arc_data)
ccw_arc_actor = vtk.vtkActor()
ccw_arc_actor.SetMapper(ccw_arc_mapper)
ccw_arc_actor.GetProperty().SetColor(0, 0, 1)  # 逆时针圆弧为蓝色

# 创建渲染器、窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 添加actor到渲染器
renderer.AddActor(cw_arc_actor)
renderer.AddActor(ccw_arc_actor)
renderer.SetBackground(1, 1, 1)  # 设置背景为白色

# 设置自定义鼠标交互样式
style = CustomInteractorStyle(renderer)
render_window_interactor.SetInteractorStyle(style)

# 开始渲染
render_window.Render()
render_window_interactor.Start()
