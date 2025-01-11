import vtk
from PIL import Image, ImageDraw
import numpy as np
import cv2
from scipy.ndimage import binary_erosion

# 读取 STL 文件
reader = vtk.vtkSTLReader()
reader.SetFileName("../file/coin_half.stl")  # 替换为你的 STL 文件路径
reader.Update()

# 将 vtkUnstructuredGrid 转换为 vtkPolyData
geometryFilter = vtk.vtkGeometryFilter()
geometryFilter.SetInputConnection(reader.GetOutputPort())
geometryFilter.Update()

# 获取三角形面片的顶点数据
poly_data = geometryFilter.GetOutput()
cells = poly_data.GetPolys()

# 设置图像的尺寸
image_width, image_height = 800, 800
image = Image.new('1', (image_width, image_height), 0)  # 创建一个二进制图像，背景为黑色
draw = ImageDraw.Draw(image)

# 遍历三角形面片
cell_id = 0
num_cells = cells.GetNumberOfCells()

while cell_id < num_cells:
    # 获取当前单元（三角形）
    points = cells.GetCell(cell_id).GetPoints()
    if points.GetNumberOfPoints() == 3:
        # 获取三角形的三个顶点 (忽略 z 坐标，直接投影到 2D)
        p1 = points.GetPoint(0)
        p2 = points.GetPoint(1)
        p3 = points.GetPoint(2)

        # 进行坐标变换，将 3D 坐标投影到 2D
        x1, y1 = int(p1[0] * 100 + image_width / 2), int(p1[1] * 100 + image_height / 2)
        x2, y2 = int(p2[0] * 100 + image_width / 2), int(p2[1] * 100 + image_height / 2)
        x3, y3 = int(p3[0] * 100 + image_width / 2), int(p3[1] * 100 + image_height / 2)

        # 使用 PIL 绘制三角形
        draw.polygon([x1, y1, x2, y2, x3, y3], outline=1, fill=1)

    cell_id += 1

# 将 PIL 图像转换为 NumPy 数组
binary_image = np.array(image)

# 使用 OpenCV 进行二进制侵蚀操作
kernel = np.ones((5, 5), np.uint8)
eroded_image = cv2.erode(binary_image.astype(np.uint8), kernel, iterations=1)

# 获取轮廓（减法）
contour_image = binary_image.astype(np.uint8) - eroded_image

# 显示原始二进制图像和轮廓
cv2.imshow('Binary Image', binary_image.astype(np.uint8) * 255)
cv2.imshow('Eroded Image', eroded_image * 255)
cv2.imshow('Contours', contour_image * 255)
cv2.waitKey(0)
cv2.destroyAllWindows()
