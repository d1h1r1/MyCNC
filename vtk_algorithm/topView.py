import numpy as np
import matplotlib.pyplot as plt
import pyslm
# from pyslm import Slice
from shapely.geometry import MultiPolygon, Polygon
from scipy.spatial import ConvexHull


def get_top_view_contour(stl_file, layer_height=0.1):
    # 读取 STL 并切片
    # slices = Slice.load_stl(stl_file, layer_height)
    solidPart = pyslm.Part('stl')
    solidPart.setGeometry(stl_file)
    slices = solidPart.getVectorSlice(layer_height)
    # 存储所有轮廓点（投影到XY平面）
    all_contours = []

    for layer in slices:
        for contour in layer:
            xy_contour = [(x, y) for x, y, _ in contour]  # 只取 XY 坐标
            all_contours.extend(xy_contour)

    # 转换为 NumPy 数组
    all_contours = np.array(all_contours)

    # 计算外轮廓（凸包）
    hull = ConvexHull(all_contours)
    top_contour = all_contours[hull.vertices]

    return top_contour


# 运行代码
stl_file = "../file/elephant.stl"  # 你的 STL 文件
top_contour = get_top_view_contour(stl_file)

# 绘制外轮廓
plt.figure(figsize=(6, 6))
plt.plot(top_contour[:, 0], top_contour[:, 1], 'r-', label="Top View Contour")
plt.scatter(top_contour[:, 0], top_contour[:, 1], c='b', s=10)
plt.axis("equal")
plt.legend()
plt.title("俯视图外轮廓")
plt.show()
