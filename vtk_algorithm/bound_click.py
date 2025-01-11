import vtk

reader = vtk.vtkSTLReader()
reader.SetFileName("../file/Batarang_Hush.stl")  # 替换为你的 STL 文件路径
reader.Update()  # 读取 STL 数据

# 将 vtkUnstructuredGrid 转换为 vtkPolyData
geometryFilter = vtk.vtkGeometryFilter()
geometryFilter.SetInputConnection(reader.GetOutputPort())
geometryFilter.Update()

# 创建 vtkFeatureEdges 对象
featureEdges = vtk.vtkFeatureEdges()
featureEdges.SetInputConnection(geometryFilter.GetOutputPort())  # 使用 PolyData 作为输入
featureEdges.BoundaryEdgesOn()  # 提取边界边缘
featureEdges.Update()

# 创建映射器和演员
edgeMapper = vtk.vtkPolyDataMapper()
edgeMapper.SetInputConnection(featureEdges.GetOutputPort())

edgeActor = vtk.vtkActor()
edgeActor.SetMapper(edgeMapper)

# 设置默认颜色
edgeActor.GetProperty().SetColor(1, 1, 1)  # 白色边缘

# 创建渲染器和渲染窗口
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 添加演员到渲染器
renderer.AddActor(edgeActor)
renderer.SetBackground(0.1, 0.2, 0.4)

# 创建 CellPicker
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.01)  # 设置拾取容差


def on_left_button_press(obj, event):
    click_pos = renderWindowInteractor.GetEventPosition()
    picker.Pick(click_pos[0], click_pos[1], 0, renderer)  # 进行拾取操作
    picked_id = picker.GetCellId()  # 获取被拾取单元 ID
    if picked_id >= 0:  # 如果拾取到单元
        # 获取 PolyData 和颜色数据
        poly_data = featureEdges.GetOutput()
        colors = poly_data.GetCellData().GetScalars()

        # 如果没有颜色数据，则初始化为 vtkUnsignedCharArray
        if not colors or not isinstance(colors, vtk.vtkUnsignedCharArray):
            colors = vtk.vtkUnsignedCharArray()
            colors.SetName("Colors")
            colors.SetNumberOfComponents(3)  # 设置 RGB 分量
            colors.SetNumberOfTuples(poly_data.GetNumberOfCells())  # 初始化为单元数量
            for i in range(poly_data.GetNumberOfCells()):
                colors.SetTuple3(i, 255, 255, 255)  # 默认设置为白色
            poly_data.GetCellData().SetScalars(colors)  # 绑定颜色数据

        # 修改选中单元的颜色
        colors.SetTuple3(picked_id, 255, 0, 0)  # 设置为红色
        poly_data.Modified()  # 标记数据更新
        renderWindow.Render()  # 刷新渲染


# 为交互器添加事件监听
renderWindowInteractor.AddObserver("LeftButtonPressEvent", on_left_button_press)

# 启动渲染和交互
renderWindow.Render()
renderWindowInteractor.Start()
