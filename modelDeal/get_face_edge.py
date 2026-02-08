import numpy as np
import trimesh
import matplotlib.pyplot as plt
import warnings
from collections import defaultdict

from shapely import Polygon

warnings.filterwarnings('ignore')


def filter_occluded_upward_faces(full_mesh: trimesh.Trimesh,
                                 upward_mesh: trimesh.Trimesh,
                                 eps=1e-4):
    """
    过滤掉在 +Z 方向上被其他三角面遮挡的向上三角面

    Args:
        full_mesh: 原始完整 STL mesh（用于遮挡检测）
        upward_mesh: 已筛选出的向上三角面 mesh
        eps: 射线起点偏移，避免自相交

    Returns:
        trimesh.Trimesh: 过滤后的向上三角面 mesh
    """

    # 加速结构
    intersector = trimesh.ray.ray_triangle.RayMeshIntersector(full_mesh)

    centers = upward_mesh.triangles_center
    normals = upward_mesh.face_normals

    keep_faces = []

    for i, (center, normal) in enumerate(zip(centers, normals)):
        # 只处理真正向上的面
        if normal[2] <= 0:
            continue

        # 射线起点（略微抬高）
        origin = center + normal * eps
        direction = np.array([0.0, 0.0, 1.0])

        # 发射射线
        locations, index_ray, index_tri = intersector.intersects_location(
            np.array([origin]),
            np.array([[0.0, 0.0, 1.0]]),
            multiple_hits=False
        )

        # 如果在上方击中其他三角面，则认为被遮挡
        if len(locations) == 0:
            keep_faces.append(i)

    # print(f"遮挡过滤：{len(keep_faces)} / {len(upward_mesh.faces)} 个面被保留")
    if len(keep_faces) == 0:
        return None
    return trimesh.Trimesh(
        vertices=upward_mesh.vertices,
        faces=upward_mesh.faces[keep_faces],
        process=False
    )


def keep_vertical_upward_faces(stl_path):
    """
    只保留法向量垂直向上的面
    """
    mesh = trimesh.load(stl_path)

    if not hasattr(mesh, 'face_normals') or mesh.face_normals is None:
        mesh.face_normals = mesh.face_normals

    mask = mesh.face_normals[:, 2] == 1

    if np.sum(mask) == 0:
        print(f"警告: 没有找到法向量z分量垂直向上的面")
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

    # 按高度排序（从高到低）
    clusters.sort(key=lambda x: x['height'], reverse=True)

    # print(f"找到 {len(clusters)} 个不同高度的平面:")
    # for i, cluster in enumerate(clusters):
    #     print(f"  平面 {i + 1}: 高度 = {cluster['height']:.6f}, 包含 {len(cluster['faces'])} 个面")

    return clusters


def extract_boundary_edges(mesh, face_indices):
    faces = mesh.faces[face_indices]

    # 所有三角形边
    edges = np.vstack([
        faces[:, [0, 1]],
        faces[:, [1, 2]],
        faces[:, [2, 0]],
    ])

    # 无向边（排序）
    edges = np.sort(edges, axis=1)

    # 统计出现次数
    edges_unique, counts = np.unique(edges, axis=0, return_counts=True)

    # 只出现一次的边 = 边界边
    boundary_edges = edges_unique[counts == 1]
    return boundary_edges


def boundary_edges_to_loops(boundary_edges):
    adj = defaultdict(list)
    for a, b in boundary_edges:
        adj[a].append(b)
        adj[b].append(a)

    loops = []
    visited = set()

    for start in adj:
        if start in visited:
            continue

        loop = [start]
        visited.add(start)
        curr = start

        while True:
            next_nodes = [n for n in adj[curr] if n not in visited]
            if not next_nodes:
                break
            nxt = next_nodes[0]
            loop.append(nxt)
            visited.add(nxt)
            curr = nxt
        loop.append(start)
        loops.append(loop)

    return loops


def extract_ordered_contours(mesh, cluster):
    boundary_edges = extract_boundary_edges(mesh, cluster['faces'])
    loops = boundary_edges_to_loops(boundary_edges)
    contours = []
    for loop in loops:
        pts = mesh.vertices[loop]
        contours.append(pts)

    return contours


def visualize_contours_2d(contours):
    plt.figure(figsize=(8, 8))

    for i, contour in enumerate(contours):
        plt.plot(
            contour[:, 0],
            contour[:, 1],
            '-o',
            linewidth=2,
            markersize=3,
            label=f'Contour {i}'
        )

        # 起点
        plt.scatter(contour[0, 0], contour[0, 1], c='green', s=80)
        # 终点（闭合验证）
        plt.scatter(contour[-1, 0], contour[-1, 1], c='red', s=80)

    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.title('Ordered Plane Contours')
    plt.show()


def get_points(mesh, clusters):
    face_edge_dist = defaultdict(dict)
    for i, cluster in enumerate(clusters):
        height = cluster['height']
        contours = extract_ordered_contours(mesh, cluster)
        face_edge_dist[height]['contours'] = contours
        # visualize_contours_2d(contours)
    return face_edge_dist


def is_contour_inside(inner_contour, outer_contour):
    """
    判断 inner_contour 是否被 outer_contour 完全包含

    Args:
        inner_contour: 内轮廓点列表
        outer_contour: 外轮廓点列表
    return:
        True/False
    """
    outer_polygon = Polygon(outer_contour)
    inner_polygon = Polygon(inner_contour)

    # 判断内轮廓的所有点是否都在外轮廓内部
    return outer_polygon.contains(inner_polygon)


def find_contour_relationships(all_path):
    """
    找出同层轮廓的包含关系

     Args:
        all_path: 轮廓点云列表，每个轮廓是 [(x1, y1), (x2, y2), ...]
        index_list: 单一层的包含关系
    return:
        dir: 关系字典 {index1: [index2, index3, ...]} 表示 index1 包含 index2, index3
    """

    relationships = {i: [] for i in range(len(all_path))}
    for i in range(len(all_path)):
        for j in range(len(all_path)):
            if i != j and is_contour_inside(all_path[i], all_path[j]):
                relationships[j].append(i)

    return relationships


def contours_in_out(relation_dist):
    point_num = {}
    in_out_list = [1 for i in range(len(relation_dist))]
    # 判断轮廓内外切情况，获取轮廓内外轮廓
    for key in relation_dist:
        for i in relation_dist[key]:
            if i in point_num:
                point_num[i] += 1
            else:
                point_num[i] = 0
    # 设置切割类型是内切(奇数)还是外切(偶数)
    for layer in point_num.keys():
        num = point_num[layer]
        if num % 2 == 1:
            pass
        in_out_list[layer] = num % 2
    return in_out_list


def get_edge_relation(face_dist):
    for i in face_dist.keys():
        points_list = face_dist[i]['contours']
        print("height", i)
        relation_dist = find_contour_relationships(points_list)
        in_out_list = contours_in_out(relation_dist)
        face_dist[i]["relation"] = relation_dist
        face_dist[i]["in_out"] = in_out_list
        return face_dist


def main(stl_path):
    """
    主函数：处理STL文件，提取平面轮廓和高度
    """
    full_mesh = trimesh.load(stl_path)

    mesh = keep_vertical_upward_faces(stl_path)

    # 过滤垂直向上，但是被遮挡的面
    mesh = filter_occluded_upward_faces(
        full_mesh=full_mesh,
        upward_mesh=mesh
    )

    if mesh is None:
        print("错误: 没有找到垂直向上的面！")
        return

    clusters = cluster_faces_by_height(mesh, height_tolerance=0.01)
    if not clusters:
        print("错误: 没有找到任何平面！")
        return

    face_edge_dist = get_points(mesh, clusters)
    face_dist = get_edge_relation(face_edge_dist)
    print(face_dist)
    # print(face_edge_dist)


if __name__ == '__main__':
    # 指定你的STL文件路径
    stl_file = "test.stl"  # 修改为你的文件路径
    main(stl_file)
