import vtk

# 读取 STL 文件
reader = vtk.vtkSTLReader()
reader.SetFileName("../file/coin_half.stl")  # 替换为你的 STL 文件路径
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

# 获取 PolyData 对象
poly_data = featureEdges.GetOutput()

# 将所有点的 z 值设置为 0（投影到 Z=0 平面）
points = poly_data.GetPoints()
for i in range(points.GetNumberOfPoints()):
    x, y, z = points.GetPoint(i)
    points.SetPoint(i, x, y, 0)  # 修改点的 z 值为 0

# 创建渲染器和渲染窗口
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 创建映射器和演员（用于显示提取的边缘）
edgeMapper = vtk.vtkPolyDataMapper()
edgeMapper.SetInputData(poly_data)  # 使用修改后的 PolyData

edgeActor = vtk.vtkActor()
edgeActor.SetMapper(edgeMapper)

# 将演员添加到渲染器
renderer.AddActor(edgeActor)

# 设置背景色
renderer.SetBackground(0.1, 0.2, 0.4)

# 启动渲染窗口
renderWindow.Render()
renderWindowInteractor.Start()
