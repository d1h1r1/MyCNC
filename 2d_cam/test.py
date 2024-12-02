from svgpathtools import svg2paths, Arc, Line

# 1. 解析 SVG 文件
svg_file = '../file/phone.svg'
paths, attributes = svg2paths(svg_file)

# 2. 将 SVG 路径转换为 pythreejs 路径
threejs_paths = []

for path in paths:
    for segment in path:
        print(segment)

        # if isinstance(segment, Arc):
        #     print("arc", segment)
        #     start_x, start_y = segment.start.real, segment.start.imag
        #     end_x, end_y = segment.end.real, segment.end.imag
        #
        #     # 计算圆心
        #     # 需要根据弧的几何特性计算圆心，这里提供一个简单的方法
        #     # 假设圆心在 x, y 平面
        #     center_x = (start_x + end_x) / 2
        #     center_y = (start_y + end_y) / 2
        #     if segment.sweep:
        #         pass
        # elif isinstance(segment, Line):
        #     print("line", segment)
        # else:
        #     continue
        # print(i.start)
        # start_points = np.array([[segment.start.real, segment.start.imag] for segment in path])
        # print(start_points)
        # end_points = np.array([[segment.end.real, segment.end.imag] for segment in path])
        # print(end_points)
        print("=================================================")
#     # 将每个 SVG 路径转换为 three.js 路径
#     points = np.array([[segment.start.real, segment.start.imag] for segment in path])
#     path_geometry = p3.Geometry(vertices=[p3.Vector3(*point) for point in points])
#     threejs_paths.append(path_geometry)
#
# # 3. 创建 three.js 场景
# scene = p3.Scene(children=[
#     p3.AmbientLight(intensity=0.5),
#     p3.DirectionalLight(position=[3, 5, 1], intensity=0.7),
# ])
#
# # 4. 将路径添加到场景中
# path_meshes = []
#
# for geometry in threejs_paths:
#     material = p3.LineBasicMaterial(color='red')
#     mesh = p3.Line(geometry=geometry, material=material)
#     path_meshes.append(mesh)
#
# scene.add(*path_meshes)
#
# # 5. 设置相机
# camera = p3.PerspectiveCamera(position=[0, 0, 5], lookAt=[0, 0, 0])
#
# # 6. 创建渲染器
# renderer = p3.WebGLRenderer(camera=camera, scene=scene, width=800, height=600)
#
# # 7. 渲染
# renderer
