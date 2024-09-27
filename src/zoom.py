import vtk


class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.AddObserver("MouseWheelForwardEvent", self.OnMouseWheelForward)
        self.AddObserver("MouseWheelBackwardEvent", self.OnMouseWheelBackward)
        self.zoom_factor = 1.0

    def OnMouseWheelForward(self, obj, event):
        self.zoom_factor *= 1.1  # 每次滚动放大10%
        print(f"当前缩放比例: {self.zoom_factor:.2f}x")
        # self.OnMouseWheelForwardEvent()
        return

    def OnMouseWheelBackward(self, obj, event):
        self.zoom_factor /= 1.1  # 每次滚动缩小10%
        print(f"当前缩放比例: {self.zoom_factor:.2f}x")
        # self.OnMouseWheelBackwardEvent()
        return


# 创建一个渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 创建一个立方体源
cubeSource = vtk.vtkCubeSource()

# 创建一个映射器和一个actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cubeSource.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 将actor添加到渲染器
renderer.AddActor(actor)

# 设置背景颜色
renderer.SetBackground(0.1, 0.2, 0.4)

# 设置自定义的交互样式
style = MouseInteractorStyle()
renderWindowInteractor.SetInteractorStyle(style)

# 开始渲染
renderWindow.Render()
renderWindowInteractor.Start()
