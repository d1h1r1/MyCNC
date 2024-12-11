import vtk
from vtkmodules.util import colors
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

# 创建 STL 文件读取器
stlReader = vtk.vtkSTLReader()
# stlReader.SetFileName("../file/elephant.stl")  # 替换为你的 STL 文件路径
# stlReader.SetFileName("../file/Coin_half.stl")  # 替换为你的 STL 文件路径
# stlReader.SetFileName("../file/myhand.stl")  # 替换为你的 STL 文件路径
stlReader.SetFileName("../file/Throwing.stl")  # 替换为你的 STL 文件路径
stlReader.Update()  # 读取 STL 数据

# 获取模型的 PolyData
stlPolyData = stlReader.GetOutput()
# print(stlPolyData)
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

normal = [0.0, 0.0, 1.0]  # 平行于 XY 平面
pick_pos = [-1000, 0, -3.2]
# 创建平面
plane = vtk.vtkPlane()
plane.SetOrigin(pick_pos)
plane.SetNormal(normal)

cutter = vtk.vtkCutter()
cutter.SetInputData(stlReader.GetOutput())
cutter.SetCutFunction(plane)
cutter.Update()

# 获取 cutter 的输出（假设已经执行了切割操作）
output = cutter.GetOutput()

# 获取交线的点和线（cells）
points = output.GetPoints()
# lines = output.GetCells()

# 获取点云的数量
num_points = points.GetNumberOfPoints()
# num_lines = lines.GetNumberOfCells()

# 用于存储最外轮廓的点
outer_points = set()

# # 遍历所有的线段（每条线段包含多个点）
# for i in range(num_lines):
#     # 每条线段的点索引
#     line = lines.GetCell(i)
#     num_line_points = line.GetNumberOfPoints()
#
#     # 将线段的所有点加入到外轮廓点集
#     for j in range(num_line_points):
#         point_id = line.GetPointId(j)
#         outer_points.add(point_id)

# 获取外轮廓点坐标
outer_points_coords = []
for point_id in outer_points:
    point = points.GetPoint(point_id)
    outer_points_coords.append(point)

# 打印外轮廓点坐标
for i, point in enumerate(outer_points_coords):
    print(f"Point {i}: {point}")

# 如果需要将这些外轮廓点保存为 vtkPolyData
outer_polydata = vtk.vtkPolyData()
outer_points_vtk = vtk.vtkPoints()

# 添加外轮廓点
for point in outer_points_coords:
    outer_points_vtk.InsertNextPoint(point)

outer_polydata.SetPoints(outer_points_vtk)

# 如果需要将外轮廓点保存为 PLY 或其他格式，可以继续使用写入器
writer = vtk.vtkPLYWriter()
writer.SetFileName("outer_contour_points.ply")
writer.SetInputData(outer_polydata)
writer.Write()
