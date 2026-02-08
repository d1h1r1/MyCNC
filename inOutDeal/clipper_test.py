import time

import pyclipper
import pyclipr as pr
import matplotlib.pyplot as plt
import shapely
from clipper import clipper2_func

poly1 = [(0, 0), (10, 0), (10, 10), (0, 10)]
poly2 = [(5, 5), (15, 5), (15, 15), (5, 15)]

t1 = time.time()
for i in range(10000):
    # a = pyclipper.Area(poly1)
    clipper2_func.offset_polygon([poly1], 1)
t2 = time.time()


for i in range(10000):
    # b = shapely.Polygon(poly1).area
    shapely.Polygon(poly1).buffer(1, join_style=2, cap_style=2)
t3 = time.time()
print(t2 - t1)
print(t3 - t2)

# x_coords, y_coords = zip(*poly1)
# plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
#
#
# x_coords, y_coords = zip(*poly2)
# plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
# plt.show()
#
# plt.show()


# pc = pr.Clipper()
# pc.scaleFactor = 1000
#
# pc.addPath(poly1, pr.Subject)
# pc.addPath(poly2, pr.Subject)
#
# merged = pc.execute(pr.Union, pr.FillRule.EvenOdd)
# print(merged)

# plt.figure()
# plt.axis('equal')
#
# # 绘制原始多边形
#
# # 绘制开放路径的交集
# plt.plot(merged[0][:, 0], merged[0][:, 1], color='#222', linewidth=1.0, linestyle='dashed', marker='.', markersize=20.0)
#
# plt.show()
