import open3d as o3d
import numpy as np
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.gp import gp_Pnt
from geomdl import BSpline
from geomdl.visualization import VisMPL


# 1️⃣ 读取 STL
mesh = o3d.io.read_triangle_mesh("../file/配合25凸.stl")
mesh.compute_vertex_normals()
points = np.asarray(mesh.vertices)

# 2️⃣ 采样点（降采样）
pcd = mesh.sample_points_poisson_disk(number_of_points=400)
pts = np.asarray(pcd.points)

# 3️⃣ 简化：假设表面近似为一个网格结构（参数化 u,v）
# 这里我们做一个简单的 reshape，假设可以投影到规则网格
n = int(np.sqrt(len(pts)))
pts = pts[:n * n].reshape((n, n, 3))

# 4️⃣ 转换为 OpenCascade 的点阵结构
occ_points = TColgp_Array2OfPnt(1, n, 1, n)
for i in range(n):
    for j in range(n):
        x, y, z = pts[i, j]
        occ_points.SetValue(i + 1, j + 1, gp_Pnt(x, y, z))

# 5️⃣ 拟合 NURBS 曲面
surf_builder = GeomAPI_PointsToBSplineSurface(occ_points)
nurbs_surface = surf_builder.Surface()

# 6️⃣ 提取控制点和可视化（用 geomdl）
num_u, num_v = 10, 10
eval_pts = []
for i in range(num_u):
    for j in range(num_v):
        u = i / (num_u - 1)
        v = j / (num_v - 1)
        p = nurbs_surface.Value(u, v)
        eval_pts.append([p.X(), p.Y(), p.Z()])

eval_pts = np.array(eval_pts).reshape((num_u, num_v, 3))

# 7️⃣ 用 geomdl 绘制曲面
surf = BSpline.Surface()
surf.degree_u = 3
surf.degree_v = 3
surf.set_ctrlpts(eval_pts.reshape(-1, 3).tolist(), num_u, num_v)
surf.knotvector_u = [0, 0, 0, 0, 1, 1, 1, 1]
surf.knotvector_v = [0, 0, 0, 0, 1, 1, 1, 1]

vis_config = VisMPL.VisConfig(ctrlpts=False, legend=False)
surf.vis = VisMPL.VisSurface(vis_config)
surf.render()
