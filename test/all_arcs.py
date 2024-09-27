import vtk
import math


def calculate_angle(center, point):
    return math.atan2(point[1] - center[1], point[0] - center[0])


def create_arc(center, radius, start_angle, end_angle, clockwise=True):
    points = vtk.vtkPoints()
    num_points = 100  # 圆弧上的点数
    angle_step = (end_angle - start_angle) / (num_points - 1)
    if clockwise:
        angle_step = -angle_step

    for i in range(num_points):
        angle = start_angle + i * angle_step
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.InsertNextPoint(x, y, center[2])

    return points


# 创建一个 vtkAppendPolyData 对象
append_filter = vtk.vtkAppendPolyData()

# 假设你有多个圆弧的参数
arcs = [
    ((0, 0, 0), (1, 1, 0), (2, 0, 0)),
    ((2, 0, 0), (3, -1, 0), (4, 0, 0))
]

for start_point, end_point, center_offset in arcs:
    radius = math.sqrt(center_offset[0] ** 2 + center_offset[1] ** 2)
    center = (
        start_point[0] + center_offset[0], start_point[1] + center_offset[1], start_point[2] + center_offset[2]
    )

    start_angle = calculate_angle(center, start_point)
    end_angle = calculate_angle(center, end_point)

    points = create_arc(center, radius, start_angle, end_angle, clockwise=True)

    # 创建圆弧polyline
    polyline = vtk.vtkPolyLine()
    polyline.GetPointIds().SetNumberOfIds(points.GetNumberOfPoints())
    for i in range(points.GetNumberOfPoints()):
        polyline.GetPointIds().SetId(i, i)

    # 创建一个 vtkPolyData 对象
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.SetLines(vtk.vtkCellArray())
    poly_data.GetLines().InsertNextCell(polyline)

    append_filter.AddInputData(poly_data)

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
