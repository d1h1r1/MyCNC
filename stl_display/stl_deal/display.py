import trimesh

# in_stl = "../../file/MGH-18 指根下连杆 v1.0.stl"
in_stl = "output_compressed.stl"
# # 加载STL文件
# mesh = trimesh.load(in_stl)
# # # 显示模型
# # mesh.show()
#
# # 显示模型，带边线
# mesh.show(smooth=False, flags={'wireframe': True, 'cull': False})

import pyvista as pv


# 加载STL文件
mesh = pv.read(in_stl)

# 创建绘图器
plotter = pv.Plotter()

# 添加模型表面（半透明）和网格线
plotter.add_mesh(mesh, color='lightblue', opacity=0.5, show_edges=True,
                 edge_color='black', line_width=2)

# 可选：突出显示所有三角形
plotter.add_mesh(mesh.extract_all_edges(), color='red', line_width=1)

plotter.show()
