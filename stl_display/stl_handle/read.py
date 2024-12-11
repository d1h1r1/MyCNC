import numpy as np
from stl import mesh
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 加载 STL 文件
# your_mesh = mesh.Mesh.from_file('../../file/Throwing.stl')
# your_mesh = mesh.Mesh.from_file('../../file/Coin_half.STL')
your_mesh = mesh.Mesh.from_file('../../file/elephant.STL')
# 获取所有顶点
vertices = your_mesh.vectors.reshape(-1, 3)
point_list = []
for i in vertices:
    # print(i)
    point_list.append([i[0], i[1]])
    print(f"G01 X{i[0]} Y{i[1]} Z0 F1000")
# print(point_list)
with open("../../file/point.json", "w") as f:
    f.write(str(point_list))
