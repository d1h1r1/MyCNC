from stl import mesh

your_mesh = mesh.Mesh.from_file('../file/Throwing.stl')

# print('法线', your_mesh.normals)
# print('面', your_mesh.points)
for i in your_mesh.points:
    print(i)
# print('v0表示三角面第一个点', your_mesh.v0)
# print('v0表示三角面第二个点', your_mesh.v1)
# print('v0表示三角面第三个点', your_mesh.v2)
# print('x表示所有点的x坐标', your_mesh.x)
# print('x表示所有点的y坐标', your_mesh.y)
# print('x表示所有点的z坐标', your_mesh.z)
