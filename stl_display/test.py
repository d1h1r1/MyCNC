# -*- coding: utf-8 -*-
"""
@Time ： 2023/12/7 9:33
@Auth ： RS迷途小书童
@File ：Projection of point cloud to 2D.py
@IDE ：PyCharm
@Purpose：点云数据投影至平面并显示
"""
import matplotlib  # 导入 matplotlib 库，主要用于绘图
import numpy as np  # 导入 numpy 库，主要用于处理数组
import open3d as o3d  # 导入 Open3D 库，用于处理点云数据
import matplotlib.pyplot as plt  # 导入 matplotlib.pyplot 库，用于创建图像和画图


def point_show(path, save_path):
    # 定义一个函数 point_show，输入参数是点云文件的路径 path 和要保存图像的路径 save_path
    matplotlib.use('tkAgg')
    # 在这里指定GUI后端，这里选择 tkAgg 作为图形用户界面后端
    pcd = o3d.io.read_point_cloud(path)
    # 使用 Open3D 读取点云数据
    print(pcd)  # 输出点云的个数
    points = np.asarray(pcd.points)
    # 将点云数据转化为 numpy 数组
    # print(points.shape)  # 输出数组的形状（行列数）
    fig = plt.figure(figsize=(16, 10))  # 创建一个新的图形窗口，设置其大小为8x4
    ax1 = fig.add_subplot(121, projection='3d')  # 在图形窗口中添加一个3D绘图区域
    ax1.scatter(points[:, 0], points[:, 1], points[:, 2], c='g', s=0.01,
                alpha=0.5)  # 在这个区域中绘制点云数据的散点图，设置颜色为绿色，点的大小为0.01，透明度为0.5
    ax2 = fig.add_subplot(122)  # 在图形窗口中添加一个2D绘图区域
    # 1行2列的图形布局，其中该子图是第2个子图
    ax2.scatter(points[:, 1], points[:, 2], c='g', s=0.01, alpha=0.5)  # 在这个区域中绘制点云数据的散点图，设置颜色为绿色，点的大小为0.01，透明度为0.5
    ax1.set_title('3D')
    ax2.set_title('2D')
    plt.show()  # 显示图形窗口中的所有内容
    plt.savefig(save_path)
    # 将图形窗口中的内容保存到指定的路径


if __name__ == "__main__":
    # 如果这个文件被直接运行而不是被导入作为模块，那么执行以下代码
    point_path = "../file/elephant.STL"
    # 定义一个变量 point_path，值为字符串 "1 - Cloud.pcd"
    out_path = r"1.png"
    # 定义一个变量 out_path，值为一个Windows文件路径
    point_show(point_path, out_path)
    # 调用 point_show 函数，输入参数是 point_path 和 out_path
