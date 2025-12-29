import numpy as np
from meshlib import mrmeshnumpy as mn
from meshlib import mrmeshpy as mm

def polygon_to_closed_extruded_mesh(polygon2d: np.ndarray, z_min: float, z_max: float):
    """
    polygon2d: (N,2) numpy 数组，多边形顶点 (顺序很重要，应构成一个简单闭合多边形)
    z_min, z_max: 底面和顶面的高度
    返回：一个封闭 (watertight) MeshLib Mesh
    """
    # 顶点构造
    n = polygon2d.shape[0]
    bottom = np.hstack([polygon2d, np.full((n, 1), z_min, dtype=np.float32)])
    top    = np.hstack([polygon2d, np.full((n, 1), z_max, dtype=np.float32)])
    verts = np.vstack([bottom, top])  # 顶点顺序：底面 + 顶面

    # 三角面 (faces)：底面、顶面 + 侧面
    faces = []

    # 底面，fan 三角化 (假设 polygon2d 是简单多边形)
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])

    # 顶面 (注意顶面法线方向，为了封闭，要反转扇出方向)
    offset = n
    for i in range(1, n - 1):
        faces.append([offset + 0, offset + i + 1, offset + i])

    # 侧面 (extrude)
    for i in range(n):
        j = (i + 1) % n
        # 底 i -> 底 j -> 顶 j
        faces.append([i, j, offset + j])
        # 底 i -> 顶 j -> 顶 i
        faces.append([i, offset + j, offset + i])

    faces = np.array(faces, dtype=np.int32)

    # 构造 MeshLib mesh
    mesh = mn.meshFromFacesVerts(faces, verts.astype(np.float32))

    # 刷新缓存 (非常重要)
    mesh.invalidateCaches()

    return mesh

# --- 使用示例 ---

if __name__ == "__main__":
    # 定义一个简单多边形 (例如五边形)
    polygon = np.array([
        [0.0, 0.0],
        [2.0, 0.0],
        [3.0, 1.0],
        [1.5, 2.0],
        [0.0, 1.5]
    ], dtype=np.float32)

    zmin, zmax = 0.0, -20
    mesh = polygon_to_closed_extruded_mesh(polygon, zmin, zmax)

    # 保存为 STL
    mm.saveMesh(mesh, "closed_extruded_mesh.stl")

    # 打印信息
    verts_np = mn.getNumpyVerts(mesh)
    faces_np = mn.getNumpyFaces(mesh.topology)
    print("顶点数量:", verts_np.shape[0])
    print("三角形面数量:", faces_np.shape[0])
