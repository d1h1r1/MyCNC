import time

from meshlib import mrmeshpy as mm
import trimesh

s1 = time.time()
path1 = "../../file/开瓶器-LOGO.stl"
path2 = "../../file/30.stl"
path = "../../file/一键智铣/复杂/Halloween_Fidget_Web_-_Large_22_Layers.stl"
path3 = "closed_extruded_mesh.stl"
# 加载 / 创建两个 mesh
meshA = mm.loadMesh(path)  # 或者用 mm.make... 创建
meshB = mm.loadMesh(path3)
# 或者变换第二个 mesh（做偏移 /旋转等）
# meshB.transform(mm.AffineXf3f.translation(mm.Vector3f(0.1, 0.1, 0.1)))

# 检查三角形碰撞对
# coll_pairs = mm.findCollidingTriangles(meshA, meshB)
# for pair in coll_pairs:
#     print("A 面:", pair.aFace, "B 面:", pair.bFace)

# # 获取 bitset（哪几个面有碰撞）
# bitsetA, bitsetB = mm.findCollidingTriangleBitsets(meshA, meshB)
# print("MeshA 碰撞三角面数量:", bitsetA.count())
# print("MeshB 碰撞三角面数量:", bitsetB.count())

# 快速布尔碰撞检查
is_colliding = not mm.findCollidingTriangles(meshA, meshB, firstIntersectionOnly=True).empty()
print("是否有碰撞:", is_colliding)
s2 = time.time()

print(s2 - s1)
