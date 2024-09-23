import vtk
import math


def calculate_angle(center, point):
    """
    计算给定点相对于圆心的角度
    """
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return math.atan2(dy, dx)


def create_arc(center, radius, start_angle, end_angle, num_points=100, clockwise=True):
    """
    创建圆弧，顺时针或逆时针
    """
    points = vtk.vtkPoints()
    if not clockwise:
        if end_angle < start_angle:
            end_angle += 2 * vtk.vtkMath.Pi()
    else:
        if start_angle < end_angle:
            start_angle += 2 * vtk.vtkMath.Pi()

    for i in range(num_points + 1):
        angle = start_angle + (end_angle - start_angle) * (i / num_points)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.InsertNextPoint(x, y, center[2])  # z = center[2]保持不变
    return points


start_point = (80.0, -15.0, 0.0)  # 假设的起点
end_point = (81.348, -15.696, 0.0)  # 终点
I = 1.375  # X 方向偏移
J = 2.945  # Y 方向偏移
radius = math.sqrt(I ** 2 + J ** 2)

center_offset = [I, J, 0]  # 圆心相对起点的偏移
center = (start_point[0] + I, start_point[1] + J, 0.0)

# 计算起始点和终止点相对于圆心的角度
start_angle = calculate_angle(center, start_point)  # 起始角度
end_angle = calculate_angle(center, end_point)  # 终止角度

ccw_arc_points = create_arc(center, radius, end_angle, start_angle, clockwise=True)


# 创建逆时针圆弧polyline
ccw_arc_polyline = vtk.vtkCellArray()
ccw_arc_polyline.InsertNextCell(ccw_arc_points.GetNumberOfPoints())
for i in range(ccw_arc_points.GetNumberOfPoints()):
    ccw_arc_polyline.InsertCellPoint(i)

# 创建逆时针圆弧的polydata
ccw_arc_data = vtk.vtkPolyData()
ccw_arc_data.SetPoints(ccw_arc_points)
ccw_arc_data.SetLines(ccw_arc_polyline)
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
renderer.AddActor(ccw_arc_actor)
renderer.SetBackground(1, 1, 1)  # 设置背景为白色

# 开始渲染
render_window.Render()
render_window_interactor.Start()
