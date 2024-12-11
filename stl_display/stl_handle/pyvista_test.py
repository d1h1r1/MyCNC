import pyvista as pv

# 读取 STL 文件
mesh = pv.read('../../file/elephant.stl')

# 投影到 XY 平面
projected_mesh = mesh.project_points(plane_normal=[0, 0, 1])

# 获取投影后的轮廓
contours = projected_mesh.contour()

# 绘制投影轮廓
contours.plot()
