import numpy as np
from stl import mesh
import matplotlib.pyplot as plt


def generate_toolpath(stl_file, slice_height=1.0):
    # 读取 STL 文件
    model = mesh.Mesh.from_file(stl_file)
    # print(model)
    # 提取模型的所有三角形顶点
    vertices = model.vectors.reshape(-1, 3)
    # print(vertices)
    # 获取模型的 Z 高度范围
    z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()

    # 生成切片高度
    slices = np.arange(z_min, z_max, slice_height)
    # print(slices)
    # 存储每个切片的刀路
    toolpaths = []

    for z in slices:
        # 提取当前切片的轮廓
        slice_edges = []
        # print(model.vectors)
        for triangle in model.vectors:
            # print(triangle)
            # print("====================================================")
            # 检查三角形与切片平面是否相交
            edges = []
            for i in range(3):
                p1 = triangle[i]
                p2 = triangle[(i + 1) % 3]
                if (p1[2] <= z <= p2[2]) or (p2[2] <= z <= p1[2]):
                    # 计算交点
                    t = (z - p1[2]) / (p2[2] - p1[2])
                    intersection = p1 + t * (p2 - p1)
                    edges.append(intersection[:2])  # 仅保留 X 和 Y

            if len(edges) == 2:  # 如果切平面穿过三角形的两条边
                slice_edges.append(edges)

        # 提取刀路点
        slice_points = [point for edge in slice_edges for point in edge]
        toolpaths.append(slice_points)
        # contours = connect_points_to_contours(slice_edges)
        # toolpaths.append(contours)

    return toolpaths


def plot_toolpath(toolpaths):
    plt.figure(figsize=(10, 8))
    for layer, points in enumerate(toolpaths):
        if len(points) > 0:
            points = np.array(points)
            plt.scatter(points[:, 0], points[:, 1], label=f"Layer {layer}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Toolpath")
    plt.legend()
    plt.show()

    # for i in toolpaths:
    #     for contour in i:
    #         contour = np.array(contour)
    #         plt.plot(contour[:, 0], contour[:, 1])
    # plt.show()


def connect_points_to_contours(edges):
    """
    根据边的点集连接成轮廓。
    :param edges: 所有切片生成的边 [(P1, P2), (P3, P4), ...]
    :return: 一组轮廓路径 [[P1, P2, P3, P1], [P4, P5, ...], ...]
    """
    from collections import defaultdict

    # 构建点的邻接表
    connections = defaultdict(list)
    for edge in edges:
        P1, P2 = tuple(edge[0]), tuple(edge[1])
        connections[P1].append(P2)
        connections[P2].append(P1)

    # 构建轮廓路径
    contours = []
    visited = set()  # 记录已经访问过的点

    for start_point in connections:
        if start_point in visited:
            continue

        # 构建单个轮廓
        contour = []
        current = start_point
        prev = None

        while current not in visited:
            contour.append(current)
            visited.add(current)

            # 找下一个点
            neighbors = connections[current]
            next_point = None
            for neighbor in neighbors:
                if neighbor != prev:  # 避免回到上一个点
                    next_point = neighbor
                    break

            prev = current
            current = next_point

            if next_point is None:  # 无法继续，轮廓结束
                break

        if len(contour) > 1:  # 确保有效轮廓
            contours.append(contour)

    return contours


# 使用示例
stl_file = "../file/elephant.stl"  # 替换为你的 STL 文件路径
toolpaths = generate_toolpath(stl_file, slice_height=1)
print(toolpaths)
plot_toolpath(toolpaths)
