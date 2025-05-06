import trimesh

# 读取 STL 模型
mesh = trimesh.load_mesh("../file/elephant.stl")

# 你要判断的点坐标（例如：x=1, y=2, z=3）
point = [0, 0, -5.0]

# 判断点是否在模型内
is_inside = mesh.contains([point])

# 输出结果
if is_inside[0]:
    print(f"点 {point} 在模型内部")
else:
    print(f"点 {point} 不在模型内部")
