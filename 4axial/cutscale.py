import pyslm
from matplotlib import pyplot as plt

solidPart = pyslm.Part('stl')
solidPart.setGeometry("82.stl")
all_scale = {}
max_num = 0
z_depth = 60
for i in range(int(abs(z_depth)) + 1):
    # 设置切片层位置
    z = -i*0.1
    geomSlice = solidPart.getVectorSlice(z)
    print(geomSlice)
    print(z)
    if not geomSlice:
        continue
    for j in geomSlice:
        x_coords, y_coords = zip(*j)
        plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
        plt.show()
