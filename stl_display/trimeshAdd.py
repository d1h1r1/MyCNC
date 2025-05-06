import trimesh
import numpy as np


def slice_and_compress_z(mesh, z_level):
    """
    对 mesh 进行 Z 切片，将 Z > z_level 的所有点压缩到 z_level 平面。

    Parameters:
    - mesh: trimesh.Trimesh
    - z_level: float

    Returns:
    - new_mesh: trimesh.Trimesh
    """
    vertices = mesh.vertices.copy()
    # 压缩 z > z_level 的顶点
    vertices[:, 2] = np.minimum(vertices[:, 2], z_level)

    # 创建新 mesh
    new_mesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=False)
    return new_mesh


# 示例：加载并压缩
mesh = trimesh.load("../file\吸泵外壳.stl")  # 加载模型
z_target = -7.5  # 切片高度
compressed_mesh = slice_and_compress_z(mesh, z_target)

# 显示或保存结果
compressed_mesh.show()
# compressed_mesh.export("compressed.stl")
