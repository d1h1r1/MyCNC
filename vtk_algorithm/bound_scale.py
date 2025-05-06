import vtk

# 读取 STL 文件
reader = vtk.vtkSTLReader()
reader.SetFileName("../file/Elephant.stl")  # 替换为你的 STL 文件路径
reader.Update()

# 使用 vtkGeometryFilter 将 UnstructuredGrid 转换为 PolyData
geometryFilter = vtk.vtkGeometryFilter()
geometryFilter.SetInputConnection(reader.GetOutputPort())
geometryFilter.Update()

# 提取边界轮廓
featureEdges = vtk.vtkFeatureEdges()
featureEdges.SetInputConnection(geometryFilter.GetOutputPort())
featureEdges.BoundaryEdgesOn()  # 只提取边界边
featureEdges.Update()

# 获取 PolyData 结果
polyData = featureEdges.GetOutput()
points = polyData.GetPoints()  # 获取点数据
lines = polyData.GetLines()    # 获取线数据

# 存储每条轮廓线的点云
contours = []

# 遍历所有线段
idList = vtk.vtkIdList()
for i in range(lines.GetNumberOfCells()):
    lines.GetCell(i, idList)  # 获取当前线段的点 ID
    contour = []
    for j in range(idList.GetNumberOfIds()):
        pointId = idList.GetId(j)  # 获取点的 ID
        x, y, z = points.GetPoint(pointId)  # 获取点坐标
        contour.append((x, y, z))
    contours.append(contour)

# 打印所有轮廓点云
for i, contour in enumerate(contours):
    print(f"轮廓 {i + 1}: {len(contour)} 个点")
    for point in contour:
        print(point)
