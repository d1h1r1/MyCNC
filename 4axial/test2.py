import time

import alphashape
import numpy as np
import trimesh
from scipy.spatial import Delaunay
from shapely import Polygon, Point


def precise_unwrap(model_path, output_path=None, rotation_axis='y', debug=False):
    """
    改进的模型展开函数（使用增量方式计算展开长度）

    参数:
        model_path: 输入模型路径
        output_path: 输出路径(可选)
        rotation_axis: 旋转轴('x'或'y')
        debug: 是否显示调试信息
    """
    # 加载并预处理模型
    mesh = trimesh.load(model_path)
    vertices = mesh.vertices.copy()

    t1 = time.time()

    if rotation_axis == 'y':
        # 计算每个点的极坐标参数
        theta = np.arctan2(vertices[:, 2], vertices[:, 0])
        radius = np.sqrt(vertices[:, 0] ** 2 + vertices[:, 2] ** 2)

        # 对点进行排序（按角度）
        sorted_indices = np.argsort(theta)
        sorted_theta = theta[sorted_indices]
        sorted_radius = radius[sorted_indices]

        # 计算增量展开长度
        delta_theta = np.diff(sorted_theta, prepend=sorted_theta[0] - 2 * np.pi)
        # 处理角度跳变（2π -> 0）
        delta_theta = (delta_theta + np.pi) % (2 * np.pi) - np.pi
        unwrap_length = np.cumsum(delta_theta * sorted_radius)

        # 构建展开后的坐标
        unwrapped = np.column_stack([
            unwrap_length,
            sorted_radius,
            vertices[sorted_indices, 1]  # 原始高度
        ])

        # 恢复原始顺序
        unsort_indices = np.argsort(sorted_indices)
        unwrapped = unwrapped[unsort_indices]

    else:  # rotation_axis == 'x'
        # 计算每个点的极坐标参数
        theta = np.arctan2(vertices[:, 2], vertices[:, 1])
        radius = np.sqrt(vertices[:, 1] ** 2 + vertices[:, 2] ** 2)

        # 对点进行排序（按角度）
        sorted_indices = np.argsort(theta)
        sorted_theta = theta[sorted_indices]
        sorted_radius = radius[sorted_indices]

        # 计算增量展开长度
        delta_theta = np.diff(sorted_theta, prepend=sorted_theta[0] - 2 * np.pi)
        # 处理角度跳变（2π -> 0）
        delta_theta = (delta_theta + np.pi) % (2 * np.pi) - np.pi
        unwrap_length = np.cumsum(delta_theta * sorted_radius)

        # 构建展开后的坐标
        unwrapped = np.column_stack([
            vertices[sorted_indices, 0],  # 原始高度
            unwrap_length,
            sorted_radius
        ])

        # 恢复原始顺序
        unsort_indices = np.argsort(sorted_indices)
        unwrapped = unwrapped[unsort_indices]

    # 使用Delaunay三角剖分重建表面
    tri = Delaunay(unwrapped[:, :2])

    try:
        # raise ValueError
        # 你的展开点
        points_2d = unwrapped[:, :2]
        alpha_shape = alphashape.alphashape(points_2d, alpha=0.5)  # 调整alpha参数

        max_points = list(alpha_shape.exterior.coords)
        boundary_2d = max_points
        print(boundary_2d)
        poly = Polygon(boundary_2d)
        # 重建表面网格
        filtered_simplices = []
        for simplex in tri.simplices:
            triangle_pts = points_2d[simplex]
            centroid = np.mean(triangle_pts, axis=0)
            if poly.contains(Point(centroid)):
                filtered_simplices.append(simplex)
        filtered_simplices = np.array(filtered_simplices)
    except:
        filtered_simplices = tri.simplices

    new_mesh = trimesh.Trimesh(
        vertices=unwrapped,
        faces=filtered_simplices,
        process=False
    )

    if output_path:
        new_mesh.export(output_path)

    return unwrapped


# 使用示例
if __name__ == "__main__":
    # 尝试两种旋转轴查看效果
    result = precise_unwrap(
        "xq2.stl",
        f"6.stl",
        rotation_axis='x',
        debug=True
    )