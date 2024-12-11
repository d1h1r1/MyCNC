import trimesh

# 读取 STL 文件
mesh = trimesh.load_mesh('../../file/elephant.stl')

# 投影到 XY 平面 (获取顶点的投影)
projection_2d = mesh.project_to_planes(plane_normal=[0, 0, 1])  # XY 平面

# 获取投影后的轮廓
contours = projection_2d.convex_hull

# 打印或绘制轮廓
print("投影轮廓顶点：", contours.vertices)
