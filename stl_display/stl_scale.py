import time
import shapely.geometry as sg
import vtk


def get_scale(z_depth):
    max_area = 0
    max_area_point = []
    # 创建 STL 文件读取器
    stlReader = vtk.vtkSTLReader()
    stlReader.SetFileName("../file/Throwing.stl")  # 替换为你的 STL 文件路径
    stlReader.Update()  # 读取 STL 数据

    # 创建 PolyData 映射器
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stlReader.GetOutputPort())

    normal = [0.0, 0.0, 1.0]  # 平行于 XY 平面
    for i in range(abs(z_depth * 100)):
        pick_pos = [-1000, -1000, -0.01 * i]
        # 创建平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(pick_pos)
        plane.SetNormal(normal)

        cutter = vtk.vtkCutter()
        cutter.SetInputData(stlReader.GetOutput())
        cutter.SetCutFunction(plane)
        cutter.Update()

        # 映射交线数据
        cutter_mapper = vtk.vtkPolyDataMapper()
        cutter_mapper.SetInputConnection(cutter.GetOutputPort())

        cutter_output = cutter.GetOutput()

        # 提取连通分量
        connectivity_filter = vtk.vtkConnectivityFilter()
        connectivity_filter.SetInputData(cutter_output)
        connectivity_filter.SetExtractionModeToAllRegions()
        connectivity_filter.Update()

        # 获取连通分量的数量
        num_regions = connectivity_filter.GetNumberOfExtractedRegions()
        min_distance = float('inf')
        closest_curve = vtk.vtkPolyData()

        # 遍历每个连通分量
        for i in range(num_regions):
            connectivity_filter.InitializeSpecifiedRegionList()
            connectivity_filter.AddSpecifiedRegion(i)
            connectivity_filter.SetExtractionModeToSpecifiedRegions()
            connectivity_filter.Update()
            # 当前分量数据
            region_polydata = connectivity_filter.GetOutput()
            bounds = [0.0] * 6
            region_polydata.GetCellsBounds(bounds)
            distance = (bounds[0] - pick_pos[0]) ** 2 + (bounds[2] - pick_pos[1]) ** 2
            if distance < min_distance:
                # print(distance)
                min_distance = distance
                closest_curve = vtk.vtkPolyData()
                closest_curve.DeepCopy(region_polydata)

        # 渲染最近的封闭曲线
        if closest_curve.GetNumberOfPoints() > 0:

            num_cells = closest_curve.GetNumberOfCells()
            points_list = []
            lines = []
            points = closest_curve.GetPoints()  # 获取点集
            num_points = points.GetNumberOfPoints()
            for cell_id in range(num_cells):
                cell = closest_curve.GetCell(cell_id)
                # print(cell)
                point_ids = cell.GetPointIds()
                point1 = point_ids.GetId(0)
                point2 = point_ids.GetId(1)

                # 存储线段的两个点
                lines.append((point1, point2))

            # 构建连接顺序并忽略闭合路径
            connected_points = []
            used_lines = set()  # 用于记录已使用的线段
            used_points = set()  # 用于记录已访问的点

            # 遍历所有线段
            for start_point, end_point in lines:
                # 如果该线段已被访问或闭合，则跳过
                if (start_point, end_point) in used_lines or (end_point, start_point) in used_lines:
                    continue

                # 初始化一个新路径
                path = [start_point, end_point]
                used_lines.add((start_point, end_point))
                used_points.update(path)

                # 构建非闭合路径
                is_closed = False
                while True:
                    extended = False
                    for line in lines:
                        if line in used_lines or (line[1], line[0]) in used_lines:
                            continue

                        # 检查线段是否可以扩展路径
                        if line[0] == path[-1] and line[1] not in path:
                            path.append(line[1])
                            used_lines.add(line)
                            used_points.add(line[1])
                            extended = True
                        elif line[1] == path[-1] and line[0] not in path:
                            path.append(line[0])
                            used_lines.add(line)
                            used_points.add(line[0])
                            extended = True

                        # 如果路径首尾相连，则为闭合路径
                        if path[-1] == path[0]:
                            is_closed = True
                            break

                    if not extended or is_closed:
                        break

                # 如果不是闭合路径，记录到结果中
                if not is_closed:
                    connected_points.append(path)

            # 输出结果
            for i, path in enumerate(connected_points):
                # print(f"非闭合路径 {i + 1}: {path}")
                for point_id in path:
                    point = points.GetPoint(point_id)
                    points_list.append([point[0], point[1]])

            polygon_area = sg.Polygon(points_list).area
            if polygon_area > max_area:
                max_area = polygon_area
                max_area_point = points_list
    with open("../file/point.json", "w") as f:
        f.write(str(max_area_point))


t1 = time.time()
get_scale(10)
print(time.time() - t1)
