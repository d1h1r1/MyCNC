import vtk


class Lines:
    """ lines """

    def __init__(self, points, color=(0, 255, 255)):
        """ line """
        self.append_filter = vtk.vtkAppendPolyData()
        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        self.colors.SetName("Colors")
        self.line_sources = []

        for i, (p1, p2) in enumerate(points):
            line_source = vtk.vtkLineSource()
            line_source.SetPoint1(p1)
            line_source.SetPoint2(p2)
            line_source.Update()
            self.line_sources.append(line_source)

            # 为每个点设置颜色
            # color = colors[i]
            num_points = line_source.GetOutput().GetNumberOfPoints()
            for _ in range(num_points):
                self.colors.InsertNextTuple(color)

            self.append_filter.AddInputData(line_source.GetOutput())

        self.append_filter.Update()

        # 将颜色数组添加到合并后的数据中
        output = self.append_filter.GetOutput()
        output.GetPointData().SetScalars(self.colors)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(output)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

    def add_to_renderer(self, renderer):
        renderer.AddActor(self.actor)

    def update_line_color(self, index, new_color):
        """ 更新指定线段的颜色 """
        if index < 0 or index >= len(self.line_sources):
            print("索引超出范围")
            return

        line_source = self.line_sources[index]
        num_points = line_source.GetOutput().GetNumberOfPoints()

        # 更新颜色数组
        start_idx = sum(self.line_sources[i].GetOutput().GetNumberOfPoints() for i in range(index))
        for i in range(num_points):
            self.colors.SetTuple(start_idx + i, new_color)

        self.colors.Modified()
        self.append_filter.Update()


# 示例使用
points = [((0, 0, 0), (1, 1, 1)), ((1, 1, 1), (2, 2, 2)), ((2, 2, 2), (3, 3, 3))]
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # 红色、绿色、蓝色

lines = Lines(points)

# 创建渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 添加线段到渲染器
lines.add_to_renderer(renderer)

renderer.SetBackground(0.1, 0.2, 0.4)  # 设置背景颜色

# 开始渲染
render_window.Render()

# 修改第二段线段的颜色为黄色
# lines.update_line_color(1, (255, 255, 0))

# 重新渲染
# render_window.Render()
render_window_interactor.Start()
