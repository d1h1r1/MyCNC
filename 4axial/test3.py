import time
import numpy as np
import trimesh
from scipy.spatial import Delaunay
from shapely import Polygon, Point
import alphashape


def precise_unwrap(model_path, output_path=None, rotation_axis='y', debug=False):
    """
    改进的模型展开函数（优化了三角网格重建时的异常点处理）

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
        # 计算极坐标参数
        theta = np.arctan2(vertices[:, 2], vertices[:, 0])
        radius = np.sqrt(vertices[:, 0] ** 2 + vertices[:, 2] ** 2)

        # 排序处理
        sorted_idx = np.argsort(theta)
        sorted_theta = theta[sorted_idx]
        sorted_radius = radius[sorted_idx]

        # 增量展开长度计算（处理角度跳变）
        delta_theta = np.diff(sorted_theta, prepend=sorted_theta[0] - 2 * np.pi)
        delta_theta = (delta_theta + np.pi) % (2 * np.pi) - np.pi
        unwrap_len = np.cumsum(delta_theta * sorted_radius)

        # 构建展开坐标
        unwrapped = np.column_stack([
            unwrap_len,
            sorted_radius,
            vertices[sorted_idx, 1]  # 保持原始高度
        ])

        # 恢复原始顺序
        unwrapped = unwrapped[np.argsort(sorted_idx)]

    else:  # rotation_axis == 'x'
        # 类似处理x轴旋转情况
        theta = np.arctan2(vertices[:, 2], vertices[:, 1])
        radius = np.sqrt(vertices[:, 1] ** 2 + vertices[:, 2] ** 2)

        sorted_idx = np.argsort(theta)
        sorted_theta = theta[sorted_idx]
        sorted_radius = radius[sorted_idx]

        delta_theta = np.diff(sorted_theta, prepend=sorted_theta[0] - 2 * np.pi)
        delta_theta = (delta_theta + np.pi) % (2 * np.pi) - np.pi
        unwrap_len = np.cumsum(delta_theta * sorted_radius)

        unwrapped = np.column_stack([
            vertices[sorted_idx, 0],  # 保持原始高度
            unwrap_len,
            sorted_radius
        ])

        unwrapped = unwrapped[np.argsort(sorted_idx)]

    # 改进的三角网格重建
    points_2d = unwrapped[:, :2]
    tri = Delaunay(points_2d)

    try:
        # 使用alpha shape算法计算边界
        alpha_shape = alphashape.alphashape(points_2d, alpha=0.1)  # 更宽松的alpha值

        if isinstance(alpha_shape, Polygon):
            # 创建有效区域多边形
            poly = alpha_shape
            # 计算每个三角形的质心并筛选
            filtered_simplices = []
            for simplex in tri.simplices:
                triangle_pts = points_2d[simplex]
                centroid = np.mean(triangle_pts, axis=0)
                if poly.contains(Point(centroid)):
                    # 额外检查三角形边长是否过大
                    edge_lengths = np.linalg.norm(triangle_pts[[1, 2, 0]] - triangle_pts, axis=1)
                    if np.all(edge_lengths < np.percentile(edge_lengths, 90)):  # 过滤过长边
                        filtered_simplices.append(simplex)
            simplices = np.array(filtered_simplices)
        else:
            simplices = tri.simplices
    except Exception as e:
        if debug:
            print(f"Alpha shape计算失败，使用原始三角剖分: {str(e)}")
        simplices = tri.simplices

    # 创建最终网格
    new_mesh = trimesh.Trimesh(
        vertices=unwrapped,
        faces=simplices,
        process=False
    )

    if output_path:
        new_mesh.export(output_path)

    if debug:
        print(f"处理完成，耗时: {time.time() - t1:.2f}秒")
        print(f"原始顶点数: {len(vertices)}，展开后顶点数: {len(unwrapped)}")
        print(f"生成三角形数量: {len(simplices)}")

    return unwrapped


# 使用示例
if __name__ == "__main__":
    result = precise_unwrap(
        "xq2.stl",
        "1.stl",
        rotation_axis='x',
        debug=True
    )