import vtk


def leftButtonPressEvent(obj, event):
    print('鼠标左键按下')

    # 获取 Picker
    # picker = obj.GetPicker()
    click_pos = interactor.GetEventPosition()
    picker.Pick(click_pos[0], click_pos[1], 0, renderer)
    # print(picker)
    # 获取点击位置的三维坐标
    pick_pos = picker.GetPickPosition()
    print('三维坐标:', pick_pos)

    # 获取点击的面（cell）
    cell_id = picker.GetCellId()
    if cell_id != -1:
        print(f"点击的是面 {cell_id}")
        # picked_actor = picker.GetActor()
        # bounds = picked_actor.GetBounds()  # 获取边界框
        # print(f"Picked object's bounds: {bounds}")
        normal = [0.0, 0.0, 1.0]  # 平行于 XY 平面

        # 创建平面
        plane = vtk.vtkPlane()
        plane.SetOrigin(pick_pos)
        plane.SetNormal(normal)

        cutter = vtk.vtkCutter()
        cutter.SetInputData(stlReader.GetOutput())
        cutter.SetCutFunction(plane)
        cutter.Update()

        # # 映射交线数据
        # cutter_mapper = vtk.vtkPolyDataMapper()
        # cutter_mapper.SetInputConnection(cutter.GetOutputPort())
        #
        # cutter_actor = vtk.vtkActor()
        # cutter_actor.SetMapper(cutter_mapper)
        # cutter_actor.GetProperty().SetColor(1, 0, 0)  # 红色表示平面的外轮廓线
        # cutter_actor.GetProperty().SetLineWidth(2)
        #
        # # # 设置渲染器、渲染窗口和交互器
        # renderer.AddActor(cutter_actor)
        # # 开始渲染
        # renderWindow.Render()

        cutter_output = cutter.GetOutput()

        # 提取连通分量
        connectivity_filter = vtk.vtkConnectivityFilter()
        connectivity_filter.SetInputData(cutter_output)
        connectivity_filter.SetExtractionModeToAllRegions()
        connectivity_filter.Update()

        # 获取连通分量的数量
        num_regions = connectivity_filter.GetNumberOfExtractedRegions()
        # print(num_regions)
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
            # print(f"Xmin, Xmax: ({bounds[0]}, {bounds[1]})")
            # print(f"Ymin, Ymax: ({bounds[2]}, {bounds[3]})")
            # print(f"Zmin, Zmax: ({bounds[4]}, {bounds[5]})")
            distance = (bounds[0] - pick_pos[0]) ** 2 + (bounds[2] - pick_pos[1]) ** 2
            if distance < min_distance:
                print(distance)
                min_distance = distance
                closest_curve = vtk.vtkPolyData()
                closest_curve.DeepCopy(region_polydata)

        # 渲染最近的封闭曲线
        if closest_curve.GetNumberOfPoints() > 0:
            # print(closest_curve)
            closest_mapper = vtk.vtkPolyDataMapper()
            closest_mapper.SetInputData(closest_curve)

            closest_actor = vtk.vtkActor()
            closest_actor.SetMapper(closest_mapper)
            closest_actor.GetProperty().SetColor(0, 1, 0)  # 绿色表示最近的曲线
            closest_actor.GetProperty().SetLineWidth(3)
            # print(closest_mapper)
            renderer.AddActor(closest_actor)
            renderWindow.Render()

            # 要通过 bounds 获取曲线的轨迹，bounds 本身是不够的，因为它只提供曲线的轴对齐包围盒的范围，而没有包含曲线的具体点数据或几何细节。

            # 1.通过 bounds 辅助获取曲线内的点：
            # 如果 bounds 提供了曲线的边界范围，但你只能从中提取点数据，可以结合过滤器筛选出在 bounds 范围内的点。
            num_cells = closest_curve.GetNumberOfCells()
            filtered_points = []
            points = closest_curve.GetPoints()  # 获取点集
            num_points = points.GetNumberOfPoints()
            for cell_id in range(num_cells):
                bounds = [0.0] * 6  # 用于存储当前单元的边界
                closest_curve.GetCellBounds(cell_id, bounds)

                for i in range(num_points):
                    point = points.GetPoint(i)  # 获取点坐标
                    x, y, z = point
                    if bounds[0] <= x <= bounds[1] and bounds[2] <= y <= bounds[3] and bounds[4] <= z <= bounds[5]:
                        filtered_points.append((point[0], point[1]))
            print(filtered_points)

            # print(points)
        else:
            print("未找到封闭曲线")

    else:
        print("没有点击到有效的面")


# 创建 STL 文件读取器
stlReader = vtk.vtkSTLReader()
stlReader.SetFileName("../file/left_elephant2.stl")  # 替换为你的 STL 文件路径
stlReader.Update()  # 读取 STL 数据

# 获取模型的 PolyData
stlPolyData = stlReader.GetOutput()
# print(stlPolyData)
# 创建 PolyData 映射器
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stlReader.GetOutputPort())

# 创建演员 (Actor) 来显示 STL 模型
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)  # 将 STL 模型添加到渚视器中
renderer.ResetCamera()  # 调整相机以适应模型

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# 创建渲染窗口交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

interactor_style = vtk.vtkInteractorStyleTrackballCamera()

# 禁用默认鼠标左键旋转
interactor_style.SetCurrentRenderer(renderer)
interactor_style.OnLeftButtonDown = lambda: None  # 取消左键事件
interactor_style.OnLeftButtonUp = lambda: None


# 将鼠标中键事件绑定为旋转
def rotate_with_middle_button():
    interactor_style.StartRotate()


def end_rotate_with_middle_button():
    interactor_style.EndRotate()


interactor_style.OnMiddleButtonDown = rotate_with_middle_button
interactor_style.OnMiddleButtonUp = end_rotate_with_middle_button

interactor.SetInteractorStyle(interactor_style)

camera = renderer.GetActiveCamera()


# 键盘事件的回调函数
def key_press_callback(obj, event):
    key = obj.GetKeySym()
    step = 10  # 平移步长
    if key == "Up":
        camera.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1] + step, camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0], camera.GetFocalPoint()[1] + step, camera.GetFocalPoint()[2])
    elif key == "Down":
        camera.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1] - step, camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0], camera.GetFocalPoint()[1] - step, camera.GetFocalPoint()[2])
    elif key == "Left":
        camera.SetPosition(camera.GetPosition()[0] - step, camera.GetPosition()[1], camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0] - step, camera.GetFocalPoint()[1], camera.GetFocalPoint()[2])
    elif key == "Right":
        camera.SetPosition(camera.GetPosition()[0] + step, camera.GetPosition()[1], camera.GetPosition()[2])
        camera.SetFocalPoint(camera.GetFocalPoint()[0] + step, camera.GetFocalPoint()[1], camera.GetFocalPoint()[2])
    elif key == "r":  # 重置视图
        renderer.ResetCamera()
    renderWindow.Render()


# 绑定键盘事件
interactor.AddObserver("KeyPressEvent", key_press_callback)

# 创建 picker 用于捕捉鼠标点击事件
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.001)  # 调整容差值为 0.001

# 设置渲染窗口交互器的 picker
interactor.SetPicker(picker)

# 添加左键按下事件的观察者
interactor.AddObserver('LeftButtonPressEvent', leftButtonPressEvent)

# 启动渲染和交互
renderWindow.Render()
interactor.Start()
