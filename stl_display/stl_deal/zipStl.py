import time

import meshlib.mrmeshpy as mr
import numpy as np
# file_path = "../../file/coin.stl"
file_path = "../../file/灵巧手末端.stl"
# file_path = "../../file/T.stl"

t1 = time.time()
mesh = mr.loadMesh(file_path)
sclse = 0.1

# decimate it with max possible deviation 0.5:
settings = mr.DecimateSettings()
settings.maxError = sclse
result = mr.decimateMesh(mesh, settings)
# print(result.facesDeleted)
# # 708298
# print(result.vertsDeleted)
# # 354149

# save low-resolution mesh:
mr.saveMesh(mesh, "simplified-busto.stl")
t2 = time.time()

print("1", t2 - t1)

import trimesh
import open3d as o3d

# 1. 读取 STL 模型
mesh = trimesh.load(file_path)

# 2. 转换成 open3d 格式
o3d_mesh = o3d.geometry.TriangleMesh(
    o3d.utility.Vector3dVector(mesh.vertices),
    o3d.utility.Vector3iVector(mesh.faces)
)

# 3. 网格简化（例如保留原来 30% 的面）
target_reduction = sclse  # 70% 面会被移除
simplified_mesh = o3d_mesh.simplify_quadric_decimation(
    int(len(mesh.faces) * (1 - target_reduction))
)

# 4. 转回 trimesh 并保存
simplified_trimesh = trimesh.Trimesh(
    vertices=np.asarray(simplified_mesh.vertices),
    faces=np.asarray(simplified_mesh.triangles)
)

simplified_trimesh.export("model_simplified.stl")
t3 = time.time()


print("2", t3 - t2)
