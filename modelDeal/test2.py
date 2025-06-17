import open3d as o3d


def poisson_reconstruction(input_file, output_file, depth=8):
    """
    使用泊松重建提高模型分辨率

    参数:
        input_file: 输入STL文件路径
        output_file: 输出STL文件路径
        depth: 泊松重建的深度(8-10通常足够)
    """
    # 加载STL文件
    mesh = o3d.io.read_triangle_mesh(input_file)

    # 计算顶点法线
    mesh.compute_vertex_normals()

    # 执行泊松重建
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        o3d.geometry.PointCloud(mesh.vertices),
        depth=depth
    )[0]

    # 保存结果
    o3d.io.write_triangle_mesh(output_file, poisson_mesh)
    print(f"泊松重建完成，保存到 {output_file}")


# 使用示例
poisson_reconstruction('../file/配合件凸面.stl', 'output_poisson.stl', depth=9)
