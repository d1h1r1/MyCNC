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


def extract_plane_contours(mesh, clusters):
    """
    提取每个平面的轮廓

    参数:
    mesh (trimesh.Trimesh): 原始网格
    clusters (List[Dict]): 聚类结果

    返回:
    List[Dict]: 每个平面包含完整信息
    """

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
        print(plane_vertices)
        # print(f"    形状: {plane_vertices.shape}")
        # print(f"    示例 (前5个):")
        # for j in range(min(5, len(plane_vertices))):
        #     print(f"      {plane_vertices[j]}"

    planes = []

    for i, cluster in enumerate(clusters):
        # 提取属于该平面的面
        face_indices = cluster['faces']
        faces = mesh.faces[face_indices]
        # print("faces", len(faces))
        # 创建该平面的子网格
        plane_mesh = trimesh.Trimesh(
            vertices=mesh.vertices,
            faces=faces,
            process=False
        )

        points = plane_mesh.vertices
        # print(points)
        # print(len(points))
        # print("======================")
        # 获取轮廓（2D投影在XY平面）
        # 首先获取所有边界边
        plane_mesh = plane_mesh.process()  # 处理网格以正确计算边界

        # # 绘制二维连接线
        # plt.figure(figsize=(12, 8))
        #
        # # 绘制折线（连接所有点）
        # plt.plot(points[:, 0], points[:, 1],
        #          marker='o', linestyle='-', linewidth=2, markersize=6,
        #          color='blue', markerfacecolor='red', markeredgecolor='black')
        #
        # # 添加箭头表示方向（假设第一个点是起点）
        # for i in range(len(points) - 1):
        #     if i % 5 == 0:  # 每隔5个点添加一个箭头
        #         dx = points[i + 1, 0] - points[i, 0]
        #         dy = points[i + 1, 1] - points[i, 1]
        #         plt.arrow(points[i, 0], points[i, 1],
        #                   dx * 0.8, dy * 0.8,  # 缩短箭头长度
        #                   head_width=0.1, head_length=0.15,
        #                   fc='green', ec='green', alpha=0.5)
        #
        # # 标记起点和终点
        # plt.scatter(points[0, 0], points[0, 1], s=150, c='green', marker='s', label='Start', zorder=5)
        # plt.scatter(points[-1, 0], points[-1, 1], s=150, c='red', marker='^', label='End', zorder=5)
        #
        # # 美化图表
        # plt.xlabel('X Coordinate', fontsize=12)
        # plt.ylabel('Y Coordinate', fontsize=12)
        # plt.title('2D Trajectory Visualization (Points Connected)', fontsize=14)
        # plt.grid(True, alpha=0.3)
        # plt.legend()
        # plt.axis('equal')  # 保持纵横比一致

        # # 添加数据点标签
        # for i, (x, y, z) in enumerate(points):
        #     if i == 0 or i == len(points) - 1:  # 只标记起点和终点
        #         plt.annotate(f'P{i}', (x, y), xytext=(5, 5),
        #                      textcoords='offset points', fontsize=10)
        #
        # plt.tight_layout()
        # plt.show()
        # 获取轮廓（可能由多个封闭多边形组成）
        contours = []
        try:
            # 尝试获取2D轮廓
            if hasattr(plane_mesh, 'projected') or len(plane_mesh.vertices) > 0:
                # 方法1: 使用面片合并的方法
                section = plane_mesh.section(plane_normal=[0, 0, 1],
                                             plane_origin=[0, 0, cluster['height']])

                if section is not None:
                    # 将截面转换为2D多边形
                    contours_2d = section.to_planar()[0]
                    if contours_2d is not None and len(contours_2d.polygons_full) > 0:
                        for polygon in contours_2d.polygons_full:
                            # 转换为3D点（添加高度信息）
                            polygon_3d = np.column_stack([
                                polygon.exterior.coords.xy[0],
                                polygon.exterior.coords.xy[1],
                                np.full(len(polygon.exterior.coords.xy[0]), cluster['height'])
                            ])
                            contours.append(polygon_3d)
        except:
            pass

        # 如果无法提取轮廓，使用凸包作为替代
        if len(contours) == 0:
            try:
                # 使用凸包近似
                points_2d = plane_mesh.vertices[:, :2]
                if len(points_2d) >= 3:
                    from scipy.spatial import ConvexHull
                    hull = ConvexHull(points_2d)
                    hull_points = points_2d[hull.vertices]
                    # 闭合多边形
                    hull_points = np.vstack([hull_points, hull_points[0:1]])
                    # 转换为3D
                    hull_3d = np.column_stack([
                        hull_points[:, 0],
                        hull_points[:, 1],
                        np.full(len(hull_points), cluster['height'])
                    ])
                    contours.append(hull_3d)
            except:
                pass

        # 计算平面边界框
        plane_vertices = mesh.vertices[faces.flatten()]
        bbox = {
            'min': plane_vertices.min(axis=0),
            'max': plane_vertices.max(axis=0),
            'center': plane_vertices.mean(axis=0)
        }

        # 计算平面面积（投影到XY平面）
        area = 0
        for face in faces:
            v1, v2, v3 = mesh.vertices[face]
            # 计算三角形在XY平面的投影面积
            area += 0.5 * abs(
                v1[0] * (v2[1] - v3[1]) +
                v2[0] * (v3[1] - v1[1]) +
                v3[0] * (v1[1] - v2[1])
            )

        planes.append({
            'id': i,
            'height': cluster['height'],
            'num_faces': len(face_indices),
            'mesh': plane_mesh,
            'contours': contours,
            'bbox': bbox,
            'area': area,
            'face_indices': face_indices
        })

    return planes


def visualize_planes_3d(planes):
    """
    3D可视化所有平面及其轮廓

    参数:
    planes (List[Dict]): 平面信息列表
    """
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 创建颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, len(planes)))

    for i, plane in enumerate(planes):
        color = colors[i]

        # 绘制平面网格（半透明）
        if hasattr(plane['mesh'], 'vertices') and len(plane['mesh'].vertices) > 0:
            ax.plot_trisurf(
                plane['mesh'].vertices[:, 0],
                plane['mesh'].vertices[:, 1],
                plane['mesh'].vertices[:, 2],
                triangles=plane['mesh'].faces,
                alpha=0.3,
                color=color,
                edgecolor='none'
            )

        # 绘制轮廓
        for contour in plane['contours']:
            if len(contour) > 0:
                # 绘制闭合轮廓线
                ax.plot(contour[:, 0], contour[:, 1], contour[:, 2],
                        color=color, linewidth=2, label=f'Plane {i + 1}: h={plane["height"]:.3f}')

        # 标记平面高度
        ax.text(plane['bbox']['center'][0],
                plane['bbox']['center'][1],
                plane['height'],
                f'Z={plane["height"]:.3f}',
                fontsize=8, color=color)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Detected Planes (Total: {len(planes)})')

    # 添加图例
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.15, 1))

    # 设置视角
    ax.view_init(elev=30, azim=45)

    plt.tight_layout()
    plt.show()


def visualize_planes_2d(planes):
    """
    2D投影可视化所有平面轮廓

    参数:
    planes (List[Dict]): 平面信息列表
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 创建颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, len(planes)))

    # 子图1: XY平面投影
    ax1 = axes[0]
    for i, plane in enumerate(planes):
        color = colors[i]
        for contour in plane['contours']:
            if len(contour) > 0:
                # 只取XY坐标
                ax1.plot(contour[:, 0], contour[:, 1],
                         color=color, linewidth=1.5,
                         label=f'Plane {i + 1}: h={plane["height"]:.3f}')

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Plane Contours (XY Projection)')
    ax1.axis('equal')
    ax1.grid(True, alpha=0.3)

    # 子图2: 高度分布
    ax2 = axes[1]
    heights = [plane['height'] for plane in planes]
    areas = [plane['area'] for plane in planes]

    # 使用散点图显示高度和面积
    scatter = ax2.scatter(range(len(planes)), heights, s=np.array(areas) * 100,
                          c=colors, alpha=0.6)

    ax2.set_xlabel('Plane Index')
    ax2.set_ylabel('Height (Z)')
    ax2.set_title('Plane Height Distribution (Bubble size = Area)')
    ax2.grid(True, alpha=0.3)

    # 添加高度标签
    for i, (h, a) in enumerate(zip(heights, areas)):
        ax2.text(i, h, f'{h:.3f}\n({a:.1f})',
                 fontsize=8, ha='center', va='bottom')

    # 添加图例
    handles = [plt.Line2D([0], [0], color=color, lw=2) for color in colors]
    labels = [f'Plane {i + 1}' for i in range(len(planes))]
    ax1.legend(handles, labels, loc='upper right', fontsize=8)

    plt.tight_layout()
    plt.show()


def export_plane_info(planes, output_file="planes_info.txt"):
    """
    导出平面信息到文本文件

    参数:
    planes (List[Dict]): 平面信息列表
    output_file (str): 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("PLANE DETECTION REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total Planes Detected: {len(planes)}\n")
        f.write("-" * 40 + "\n\n")

        for i, plane in enumerate(planes):
            f.write(f"PLANE {i + 1}:\n")
            f.write(f"  Height: {plane['height']:.6f}\n")
            f.write(f"  Number of Faces: {plane['num_faces']}\n")
            f.write(f"  Area: {plane['area']:.6f}\n")
            f.write(f"  Bounding Box:\n")
            f.write(
                f"    Min: ({plane['bbox']['min'][0]:.3f}, {plane['bbox']['min'][1]:.3f}, {plane['bbox']['min'][2]:.3f})\n")
            f.write(
                f"    Max: ({plane['bbox']['max'][0]:.3f}, {plane['bbox']['max'][1]:.3f}, {plane['bbox']['max'][2]:.3f})\n")
            f.write(
                f"    Center: ({plane['bbox']['center'][0]:.3f}, {plane['bbox']['center'][1]:.3f}, {plane['bbox']['center'][2]:.3f})\n")

            if plane['contours']:
                f.write(f"  Number of Contours: {len(plane['contours'])}\n")
                for j, contour in enumerate(plane['contours']):
                    f.write(f"  Contour {j + 1}: {len(contour)} points\n")
            else:
                f.write(f"  Contours: Not available\n")

            f.write("\n")

        # 统计信息
        f.write("=" * 60 + "\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("=" * 60 + "\n")

        heights = [plane['height'] for plane in planes]
        areas = [plane['area'] for plane in planes]

        f.write(f"\nHeight Statistics:\n")
        f.write(f"  Min Height: {min(heights):.6f}\n")
        f.write(f"  Max Height: {max(heights):.6f}\n")
        f.write(f"  Height Range: {max(heights) - min(heights):.6f}\n")
        f.write(f"  Mean Height: {np.mean(heights):.6f}\n")
        f.write(f"  Std Height: {np.std(heights):.6f}\n")

        f.write(f"\nArea Statistics:\n")
        f.write(f"  Total Area: {sum(areas):.6f}\n")
        f.write(f"  Min Area: {min(areas):.6f}\n")
        f.write(f"  Max Area: {max(areas):.6f}\n")
        f.write(f"  Mean Area: {np.mean(areas):.6f}\n")

    print(f"平面信息已导出到: {output_file}")


def show_with_open3d(mesh, planes=None):
    """
    使用Open3D显示网格和平面

    参数:
    mesh: 原始网格或平面网格
    planes: 平面信息列表（可选）
    """
    geometries = []

    # 如果有平面信息，显示平面
    if planes:
        for i, plane in enumerate(planes):
            # 创建平面网格
            plane_mesh_o3d = o3d.geometry.TriangleMesh()
            plane_mesh_o3d.vertices = o3d.utility.Vector3dVector(plane['mesh'].vertices)
            plane_mesh_o3d.triangles = o3d.utility.Vector3iVector(plane['mesh'].faces)
            plane_mesh_o3d.compute_vertex_normals()

            # 为每个平面设置不同颜色
            color = plt.cm.tab20(i / max(1, len(planes) - 1))[:3]  # 取RGB
            plane_mesh_o3d.paint_uniform_color(color)

            geometries.append(plane_mesh_o3d)

            # 添加轮廓线（如果有）
            for contour in plane['contours']:
                if len(contour) > 1:
                    # 创建线集
                    lines = []
                    for j in range(len(contour) - 1):
                        lines.append([j, j + 1])
                    if np.allclose(contour[0], contour[-1]):  # 闭合轮廓
                        lines.append([len(contour) - 1, 0])

                    line_set = o3d.geometry.LineSet()
                    line_set.points = o3d.utility.Vector3dVector(contour)
                    line_set.lines = o3d.utility.Vector2iVector(lines)
                    line_set.paint_uniform_color(color)
                    geometries.append(line_set)
    else:
        # 显示单个网格
        mesh_o3d = o3d.geometry.TriangleMesh()
        mesh_o3d.vertices = o3d.utility.Vector3dVector(mesh.vertices)
        mesh_o3d.triangles = o3d.utility.Vector3iVector(mesh.faces)
        mesh_o3d.compute_vertex_normals()
        mesh_o3d.paint_uniform_color([0.1, 0.3, 0.8])
        geometries.append(mesh_o3d)

    # 显示所有几何体
    o3d.visualization.draw_geometries(
        geometries,
        window_name=f"Detected Planes: {len(planes) if planes else 1}",
        width=1024,
        height=768
    )


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
    planes = extract_plane_contours(mesh, clusters)

    # # 4. 显示和分析结果
    # print("\n4. 可视化结果...")
    # print(planes)
    # 4.1 3D可视化
    visualize_planes_3d(planes)

    # 4.2 2D可视化
    # visualize_planes_2d(planes)

    # 4.3 Open3D可视化
    # show_with_open3d(mesh, planes)

    # # 5. 导出结果
    # print("\n5. 导出结果...")
    # export_plane_info(planes)
    #
    # # 6. 打印摘要
    # print("\n" + "=" * 60)
    # print("DETECTION COMPLETE")
    # print("=" * 60)
    # print(f"Total planes detected: {len(planes)}")
    # for i, plane in enumerate(planes):
    #     print(f"  Plane {i + 1}: Height={plane['height']:.6f}, "
    #           f"Area={plane['area']:.2f}, "
    #           f"Faces={plane['num_faces']}")
    # print("=" * 60)


if __name__ == '__main__':
    # 指定你的STL文件路径
    stl_file = "in.stl"  # 修改为你的文件路径
    main(stl_file)
