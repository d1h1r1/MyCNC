import vtk
from matplotlib import pyplot as plt

reader = vtk.vtkSTLReader()
reader.SetFileName("../file/Elephant.stl")  # 替换为你的 STL 文件路径
# reader.SetFileName("../file/灵巧手末端.stl")  # 替换为你的 STL 文件路径
reader.Update()  # 读取 STL 数据
# 将 vtkUnstructuredGrid 转换为 vtkPolyData
geometryFilter = vtk.vtkGeometryFilter()
geometryFilter.SetInputConnection(reader.GetOutputPort())
geometryFilter.Update()

# 创建 vtkFeatureEdges 对象
featureEdges = vtk.vtkFeatureEdges()
featureEdges.SetInputConnection(geometryFilter.GetOutputPort())  # 使用 PolyData 作为输入
featureEdges.BoundaryEdgesOn()  # 提取边界边缘
# featureEdges.FeatureEdgesOff()  # 不提取特征边缘
# featureEdges.ManifoldEdgesOff()  # 不提取流形边缘
# featureEdges.NonManifoldEdgesOff()  # 不提取非流形边缘
featureEdges.Update()

# 创建渲染器和渲染窗口
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# 创建映射器和演员（用于显示提取的边缘）
edgeMapper = vtk.vtkPolyDataMapper()
edgeMapper.SetInputConnection(featureEdges.GetOutputPort())

# 当前分量数据
region_polydata = featureEdges.GetOutput()
bounds = [0.0] * 6
region_polydata.GetCellsBounds(bounds)
num_cells = region_polydata.GetNumberOfCells()
points_list = []
lines = []

points = region_polydata.GetPoints()  # 获取点集
num_points = points.GetNumberOfPoints()
pointStartEnd = []
for cell_id in range(num_cells):
    cell = region_polydata.GetCell(cell_id)

    point_ids = cell.GetPointIds()
    point1ID = point_ids.GetId(0)
    point2ID = point_ids.GetId(1)
    point1 = points.GetPoint(point1ID)
    point2 = points.GetPoint(point2ID)
    print(point1, point2)
    # x_coords, y_coords = point1[0], point1[1]
    # plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
    # x_coords, y_coords = point2[0], point2[1]
    # plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
    # print(points.GetPoint(point1), points.GetPoint(point2))
    # print(point1, point2)

# plt.show()
edgeActor = vtk.vtkActor()
edgeActor.SetMapper(edgeMapper)

# 将演员添加到渲染器
renderer.AddActor(edgeActor)

# 设置背景色
renderer.SetBackground(0.1, 0.2, 0.4)

# 启动渲染窗口
renderWindow.Render()
renderWindowInteractor.Start()
