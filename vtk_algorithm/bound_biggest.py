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

# 检查是否成功提取了边界
print(f"Number of points in the boundary: {featureEdges.GetOutput().GetNumberOfPoints()}")
print(f"Number of cells (edges) in the boundary: {featureEdges.GetOutput().GetNumberOfCells()}")

# 获取提取的边界 PolyData
poly_data = featureEdges.GetOutput()

# 将所有点的 z 值设置为 0（投影到 Z=0 平面）
points = poly_data.GetPoints()
for i in range(points.GetNumberOfPoints()):
    x, y, z = points.GetPoint(i)
    points.SetPoint(i, x, y, 0)  # 修改点的 z 值为 0

# 使用 vtkFeatureEdges 过滤器处理最外围轮廓的边界
featureEdgesOnHull = vtk.vtkFeatureEdges()
featureEdgesOnHull.SetInputData(poly_data)
featureEdgesOnHull.BoundaryEdgesOn()  # 提取边界
featureEdgesOnHull.Update()

# 获取最外围轮廓的边界
hullEdges = featureEdgesOnHull.GetOutput()

# 检查最外围轮廓的边界
print(f"Number of points in the hull edges: {hullEdges.GetNumberOfPoints()}")
print(f"Number of cells (edges) in the hull edges: {hullEdges.GetNumberOfCells()}")

# 创建渲染器和渲染窗口
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 创建映射器和演员（用于显示最外围轮廓的边界）
hullEdgeMapper = vtk.vtkPolyDataMapper()
hullEdgeMapper.SetInputData(hullEdges)

hullEdgeActor = vtk.vtkActor()
hullEdgeActor.SetMapper(hullEdgeMapper)

# 将演员添加到渲染器
renderer.AddActor(hullEdgeActor)

# 设置背景色
renderer.SetBackground(0.1, 0.2, 0.4)

# 设置相机，使得我们能看到整个模型
camera = vtk.vtkCamera()
camera.SetPosition(0, 0, 10)  # 相机放远一些
camera.SetFocalPoint(0, 0, 0)  # 让相机聚焦于模型
renderer.SetActiveCamera(camera)

# 启动渲染窗口
renderWindow.Render()
renderWindowInteractor.Start()
