import json

import vtk
import numpy as np

with open("../file/point.json") as f:
    data = json.load(f)

# x_coords, y_coords = zip(*data)

# 假设点云是一个二维数组，每行是一个点 [x, y]
points = np.array(data)

# 创建 VTK 点集合
vtk_points = vtk.vtkPoints()
for point in points:
    vtk_points.InsertNextPoint(point[0], point[1], 0)  # 假设 z=0

# 创建 PolyData 对象
polydata = vtk.vtkPolyData()
polydata.SetPoints(vtk_points)

# 使用 vtkConvexHull2D 计算凸包
convex_hull = vtk.vtkConvexHull2D()
convex_hull.SetInputData(polydata)
convex_hull.Update()

# 获取凸包的点
hull_points = convex_hull.GetOutput().GetPoints()

# 输出凸包的点
hull_points_array = []
points_list = []
for i in range(hull_points.GetNumberOfPoints()):
    # print(hull_points.GetPoint(i))
    hull_points_array.append(hull_points.GetPoint(i))
    points_list.append([hull_points.GetPoint(i)[0], hull_points.GetPoint(i)[1]])

print(points_list)
# print("Convex Hull vertices:", np.array(hull_points_array))
