import numpy as np
import trimesh
import open3d as o3d


def keep_vertical_upward_faces(stl_path, min_z_normal=0.99):
    """
    只保留法向量垂直向上的面（z分量接近1的面）

    参数:
    stl_path (str): STL文件路径
    min_z_normal (float): 法向量z分量的最小阈值，默认0.99（接近垂直向上）

    返回:
    trimesh.Trimesh: 只包含垂直向上面的网格
    """
    # 加载网格
    mesh = trimesh.load(stl_path)

    # 计算每个面的法向量（如果还没有）
    if not hasattr(mesh, 'face_normals') or mesh.face_normals is None:
        mesh.face_normals = mesh.face_normals

    # 只保留法向量 z 分量 > 0.99 的面（接近垂直向上的面）
    # 使用更严格的阈值，确保是垂直向上的面
    # mask = mesh.face_normals[:, 2] > min_z_normal
    mask = mesh.face_normals[:, 2] == 1
    if np.sum(mask) == 0:
        print(f"警告: 没有找到法向量z分量 > {min_z_normal}的面")
        print(f"法向量z分量范围: [{mesh.face_normals[:, 2].min():.3f}, "
              f"{mesh.face_normals[:, 2].max():.3f}]")
        return None

    filtered_faces = mesh.faces[mask]

    # 创建新的网格，只包含垂直向上的面
    vertical_upward_mesh = trimesh.Trimesh(
        vertices=mesh.vertices,
        faces=filtered_faces,
        process=False
    )

    print(f"原始网格: {len(mesh.faces)} 个面")
    print(f"垂直向上面的网格: {len(filtered_faces)} 个面")
    print(f"保留比例: {len(filtered_faces) / len(mesh.faces):.2%}")

    return vertical_upward_mesh


def show_with_open3d(mesh, window_name="垂直向上的面"):
    """
    使用Open3D显示网格

    参数:
    mesh (trimesh.Trimesh): 要显示的网格
    window_name (str): 窗口名称
    """
    if mesh is None:
        print("没有网格可显示")
        return

    # 转换为Open3D网格
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)

    mesh_o3d = o3d.geometry.TriangleMesh()
    mesh_o3d.vertices = o3d.utility.Vector3dVector(vertices)
    mesh_o3d.triangles = o3d.utility.Vector3iVector(faces)

    # 计算法向量用于更好的渲染
    mesh_o3d.compute_vertex_normals()
    mesh_o3d.compute_triangle_normals()

    # 设置颜色（蓝色表示向上）
    mesh_o3d.paint_uniform_color([0.1, 0.3, 0.8])

    # 显示
    o3d.visualization.draw_geometries(
        [mesh_o3d],
        window_name=window_name,
        width=800,
        height=600
    )


def analyze_normals(stl_path):
    """
    分析网格的法向量分布

    参数:
    stl_path (str): STL文件路径
    """
    mesh = trimesh.load(stl_path)
    normals = mesh.face_normals

    print("=== 法向量分析 ===")
    print(f"总面数: {len(normals)}")
    print(f"法向量z分量统计:")
    print(f"  最小值: {normals[:, 2].min():.4f}")
    print(f"  最大值: {normals[:, 2].max():.4f}")
    print(f"  平均值: {normals[:, 2].mean():.4f}")
    print(f"  标准差: {normals[:, 2].std():.4f}")

    # 统计z分量的分布
    bins = np.linspace(-1, 1, 21)  # 分成20个区间
    hist, edges = np.histogram(normals[:, 2], bins=bins)

    print("\n法向量z分量分布:")
    for i in range(len(hist)):
        if hist[i] > 0:
            print(f"  {edges[i]:6.2f} 到 {edges[i + 1]:6.2f}: {hist[i]:4d} 个面 ({hist[i] / len(normals):6.2%})")

    # 特别关注接近1的面
    upward_threshold = 0.99
    upward_faces = np.sum(normals[:, 2] > upward_threshold)
    print(f"\n法向量z分量 > {upward_threshold}: {upward_faces} 个面 ({upward_faces / len(normals):.2%})")


if __name__ == '__main__':
    # 测试代码
    stl_path = "test.stl"

    # 首先分析法向量
    analyze_normals(stl_path)

    # 获取垂直向上的面
    mesh = keep_vertical_upward_faces(stl_path)

    if mesh is not None:
        # 显示结果
        show_with_open3d(mesh)

        # 可选：保存结果
        # output_path = "vertical_upward.stl"
        # mesh.export(output_path)
        # print(f"结果已保存到: {output_path}")