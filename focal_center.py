import vtk

# 创建渲染器、渲染窗口和交互器
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# 创建一些示例对象（例如，立方体和球体）
cube = vtk.vtkCubeSource()
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
ren.AddActor(cubeActor)

sphere = vtk.vtkSphereSource()
sphere.SetCenter(5, 5, 5)
sphereMapper = vtk.vtkPolyDataMapper()
sphereMapper.SetInputConnection(sphere.GetOutputPort())
sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)
ren.AddActor(sphereActor)

# 计算场景中所有对象的综合边界框
ren.ResetCamera()
bounds = ren.ComputeVisiblePropBounds()

# 创建相机并设置自适应参数
camera = vtk.vtkCamera()
camera.SetClippingRange(0.1, 1000)

# 计算中心点
centerX = (bounds[0] + bounds[1]) / 2
centerY = (bounds[2] + bounds[3]) / 2
centerZ = (bounds[4] + bounds[5]) / 2
camera.SetFocalPoint(centerX, centerY, centerZ)

# 计算适当的相机位置
distance = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
camera.SetPosition(centerX, centerY - distance * 1.5, centerZ + distance / 2)

# 设置视角和上方向
camera.SetViewAngle(30)
camera.SetViewUp(0, 0, 1)

# 将相机设置为活动相机
ren.SetActiveCamera(camera)

# 初始化并开始渲染
iren.Initialize()
renWin.Render()
iren.Start()
