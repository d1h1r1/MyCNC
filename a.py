import vtk

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("MouseWheelForwardEvent", self.zoom_in)
        self.AddObserver("MouseWheelBackwardEvent", self.zoom_out)
        self.AddObserver("MouseMoveEvent", self.rotate)

    def zoom_in(self, obj, event):
        self.OnMouseWheelForward()
        self.update_camera()

    def zoom_out(self, obj, event):
        self.OnMouseWheelBackward()
        self.update_camera()

    def rotate(self, obj, event):
        self.OnMouseMove()
        self.update_camera()

    def update_camera(self):
        renderer = self.GetDefaultRenderer()
        camera = renderer.GetActiveCamera()
        (x, y) = self.GetInteractor().GetEventPosition()
        renderer.SetWorldPoint(x, y, 0, 1)
        renderer.WorldToDisplay()
        (display_x, display_y, display_z) = renderer.GetDisplayPoint()
        renderer.SetDisplayPoint(display_x, display_y, display_z)
        renderer.DisplayToWorld()
        (world_x, world_y, world_z, world_w) = renderer.GetWorldPoint()
        camera.SetFocalPoint(world_x, world_y, world_z)
        self.GetInteractor().Render()

# 创建图像数据
image_data = vtk.vtkImageData()
image_data.SetDimensions(200, 100, 1)
scalars = vtk.vtkUnsignedCharArray()
scalars.SetNumberOfTuples(100 * 200)
for i in range(100 * 200):
    scalars.SetValue(i, i % 256)
image_data.GetPointData().SetScalars(scalars)

# 设置渲染器和窗口
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# 创建图像映射和演员
image_mapper = vtk.vtkImageMapper()
image_mapper.SetInputData(image_data)
image_actor = vtk.vtkActor2D()
image_actor.SetMapper(image_mapper)

renderer.AddActor(image_actor)
renderer.ResetCamera()

arc1 = vtk.vtkArcSource()


end_point = (80.0, -15.0, 0.0)  # 假设的起点
start_point = (81.348, -15.696, 0.0)  # 终点
I = 1.375  # X 方向偏移
J = 2.945  # Y 方向偏移

center_offset = [I, J, 0]  # 圆心相对起点的偏移
center = (start_point[0] + I, start_point[1] + J, 0.0)
# 设置顺时针圆弧
arc1.SetPoint1(start_point[0], start_point[1], start_point[2])
arc1.SetPoint2(end_point[0], end_point[1], end_point[2])
arc1.SetCenter(start_point[0] + center_offset[0], start_point[1] + center_offset[1], 0)
arc1.SetResolution(100)
arc1.Update()

# 创建 Mapper 和 Actor
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(arc1.GetOutputPort())

actor2 = vtk.vtkActor()
actor2.GetProperty().SetLineWidth(5)  # 设置线宽为5
actor2.SetMapper(mapper1)
actor2.GetProperty().SetColor(0,1,0)  # 红色圆弧表示 G02

# 将 actor 添加到渲染器
# renderer.AddActor(actor1)
renderer.AddActor(actor2)

# 初始化交互器
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 设置自定义交互器样式
style = CustomInteractorStyle()
style.SetDefaultRenderer(renderer)
render_window_interactor.SetInteractorStyle(style)

# 渲染并开始交互
render_window.Render()
render_window_interactor.Start()
