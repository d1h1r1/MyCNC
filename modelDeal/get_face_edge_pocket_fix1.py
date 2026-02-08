import numpy as np
import trimesh
import open3d as o3d
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import warnings

warnings.filterwarnings('ignore')


def keep_vertical_upward_faces(stl_path, min_z_normal=0.99):
    """
    只保留法向量垂直向上的面（z分量接近1的面）
    """
    mesh = trimesh.load(stl_path)

    if not hasattr(mesh, 'face_normals') or mesh.face_normals is None:
        mesh.face_normals = mesh.face_normals

    mask = mesh.face_normals[:, 2] == 1

    if np.sum(mask) == 0:
        print(f"警告: 没有找到法向量z分量 > {min_z_normal}的面")
        return None

    filtered_faces = mesh.faces[mask]

    vertical_upward_mesh = trimesh.Trimesh(
        vertices=mesh.vertices,
        faces=filtered_faces,
        process=False
    )

    return vertical_upward_mesh


def cluster_faces_by_height(mesh, height_tolerance=0.01):
    """
    根据高度将面聚类成不同的平面

    参数:
    mesh (trimesh.Trimesh): 只有垂直向上的面的网格
    height_tolerance (float): 高度容差，在容差范围内的面视为同一平面

    返回:
    List[Dict]: 每个平面包含以下信息:
        - 'faces': 面的索引
        - 'height': 平面的高度（平均z坐标）
        - 'centers': 面中心的z坐标数组
    """
    # 计算每个面的中心点
    centers = mesh.triangles_center

    # 获取每个面中心的z坐标
    z_coords = centers[:, 2]

    # 对z坐标进行排序
    sorted_indices = np.argsort(z_coords)
    sorted_z = z_coords[sorted_indices]

    # 使用DBSCAN或简单聚类根据高度分组
    clusters = []
    current_cluster = [sorted_indices[0]]
    current_height = sorted_z[0]

    for i in range(1, len(sorted_z)):
        if abs(sorted_z[i] - current_height) < height_tolerance:
            current_cluster.append(sorted_indices[i])
        else:
            # 保存当前聚类
            cluster_z_values = z_coords[current_cluster]
            clusters.append({
                'faces': np.array(current_cluster),
                'height': np.mean(cluster_z_values),
                'centers': cluster_z_values
            })
            # 开始新的聚类
            current_cluster = [sorted_indices[i]]
            current_height = sorted_z[i]

    # 添加最后一个聚类
    if current_cluster:
        cluster_z_values = z_coords[current_cluster]
        clusters.append({
            'faces': np.array(current_cluster),
            'height': np.mean(cluster_z_values),
            'centers': cluster_z_values
        })

    # 按高度排序（从低到高）
    clusters.sort(key=lambda x: x['height'])

    print(f"找到 {len(clusters)} 个不同高度的平面:")
    for i, cluster in enumerate(clusters):
        print(f"  平面 {i + 1}: 高度 = {cluster['height']:.6f}, 包含 {len(cluster['faces'])} 个面")

    return clusters

def get_points(mesh, clusters):
    for i, cluster in enumerate(clusters):
        # 提取属于该平面的面
        face_indices = cluster['faces']
        faces = mesh.faces[face_indices]

        print(f"平面 {i + 1}: 包含 {len(faces)} 个面")

        # 方法1：提取这个平面实际使用的顶点
        # 获取这些面涉及的所有顶点索引
        used_vertex_indices = np.unique(faces.flatten())
        print(f"  使用的顶点索引: {len(used_vertex_indices)} 个")

        # 获取这些顶点的坐标
        plane_vertices = mesh.vertices[used_vertex_indices]
        print(f"  实际顶点坐标:")
        # print(plane_vertices)
        # print(f"    形状: {plane_vertices.shape}")
        # print(f"    示例 (前5个):")
        # for j in range(min(5, len(plane_vertices))):
        #     print(f"      {plane_vertices[j]}"
        #
        points = plane_vertices
        # 绘制二维连接线
        plt.figure(figsize=(12, 8))

        # 绘制折线（连接所有点）
        plt.plot(points[:, 0], points[:, 1],
                 marker='o', linestyle='-', linewidth=2, markersize=6,
                 color='blue', markerfacecolor='red', markeredgecolor='black')

        # 添加箭头表示方向（假设第一个点是起点）
        for i in range(len(points) - 1):
            if i % 5 == 0:  # 每隔5个点添加一个箭头
                dx = points[i + 1, 0] - points[i, 0]
                dy = points[i + 1, 1] - points[i, 1]
                plt.arrow(points[i, 0], points[i, 1],
                          dx * 0.8, dy * 0.8,  # 缩短箭头长度
                          head_width=0.1, head_length=0.15,
                          fc='green', ec='green', alpha=0.5)

        # 标记起点和终点
        plt.scatter(points[0, 0], points[0, 1], s=150, c='green', marker='s', label='Start', zorder=5)
        plt.scatter(points[-1, 0], points[-1, 1], s=150, c='red', marker='^', label='End', zorder=5)

        # 美化图表
        plt.xlabel('X Coordinate', fontsize=12)
        plt.ylabel('Y Coordinate', fontsize=12)
        plt.title('2D Trajectory Visualization (Points Connected)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.axis('equal')  # 保持纵横比一致

        # 添加数据点标签
        for i, (x, y, z) in enumerate(points):
            if i == 0 or i == len(points) - 1:  # 只标记起点和终点
                plt.annotate(f'P{i}', (x, y), xytext=(5, 5),
                             textcoords='offset points', fontsize=10)

        plt.tight_layout()
        plt.show()


def main(stl_path="test1.stl"):
    """
    主函数：处理STL文件，提取平面轮廓和高度
    """
    # print("=" * 60)
    # print("PLANE DETECTION FROM STL FILE")
    # print("=" * 60)

    # 1. 提取垂直向上的面
    # print("\n1. 提取垂直向上的面...")
    mesh = keep_vertical_upward_faces(stl_path)

    if mesh is None:
        print("错误: 没有找到垂直向上的面！")
        return

    # print(f"  找到 {len(mesh.faces)} 个垂直向上的面")

    # 2. 按高度聚类面
    # print("\n2. 按高度聚类面...")
    clusters = cluster_faces_by_height(mesh, height_tolerance=0.01)
    if not clusters:
        print("错误: 没有找到任何平面！")
        return

    # 3. 提取每个平面的轮廓
    # print("\n3. 提取平面轮廓...")
    # planes = extract_plane_contours(mesh, clusters)

    get_points(mesh, clusters)

    # # 4. 显示和分析结果
    # print("\n4. 可视化结果...")
    # print(planes)
    # 4.1 3D可视化
    # visualize_planes_3d(planes)


if __name__ == '__main__':
    # 指定你的STL文件路径
    stl_file = "test.stl"  # 修改为你的文件路径
    main(stl_file)
