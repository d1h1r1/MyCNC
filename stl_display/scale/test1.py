import numpy as np
import pyclipper
import trimesh
import multiprocessing

# 参数设置
scaleZ = 0.1        # 切层厚度
zoffset = 1e-10     # 避免浮点精度误差
clipper_scale = 1e6 # pyclipper 要求整数坐标

# 线性插值计算 z 平面上的交点
def interp_z_np(p1, p2, z):
    t = (z - p1[2]) / (p2[2] - p1[2])
    x = p1[0] + t * (p2[0] - p1[0])
    y = p1[1] + t * (p2[1] - p1[1])
    return [x, y]

# 裁剪单个三角面片与 z 平面交线，返回线段 (最多一条)
def clip_triangle_by_z_np(tri, z):
    below = tri[:, 2] < z
    above = tri[:, 2] > z
    on = tri[:, 2] == z

    if np.all(below) or np.all(above):
        return []

    points = []
    for i in range(3):
        p1, p2 = tri[i], tri[(i + 1) % 3]
        if (p1[2] - z) * (p2[2] - z) < 0:
            points.append(interp_z_np(p1, p2, z))
        elif p1[2] == z:
            points.append(p1[:2].tolist())
        elif p2[2] == z:
            points.append(p2[:2].tolist())

    if len(points) < 2:
        return []
    return [points]


# 确保路径闭合（首尾点一致）
def close_path(path, tol=1e-6):
    if len(path) < 3:
        return None
    if np.linalg.norm(np.array(path[0]) - np.array(path[-1])) > tol:
        path.append(path[0])
    return path


# 使用 pyclipper 合并轮廓
def union_paths_pyclipper(paths, scale=clipper_scale):
    pc = pyclipper.Pyclipper()
    valid_paths = []
    for p in paths:
        p = close_path(p.copy())
        if p and len(p) >= 3:
            p_scaled = [(int(x * scale), int(y * scale)) for x, y in p]
            valid_paths.append(p_scaled)
    if not valid_paths:
        return []
    pc.AddPaths(valid_paths, pyclipper.PT_SUBJECT, True)
    solution = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
    return [[(x / scale, y / scale) for x, y in path] for path in solution]


# 单层处理函数（用于多进程）
def process_slice(args):
    z, triangles = args
    segments = []
    for tri in triangles:
        segs = clip_triangle_by_z_np(tri, z)
        segments.extend(segs)
    contours = union_paths_pyclipper(segments)
    return z, contours


# 主函数：输入 STL 路径，输出每层等高线轮廓
def get_scale(path, z_depth=1.0):
    mesh = trimesh.load(path)
    triangles = mesh.triangles
    num_processes = 8
    z_values = [i * scaleZ for i in range(int(z_depth / scaleZ) + 1)]
    args = [(z, triangles) for z in z_values]

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(process_slice, args)

    # 排序 & 输出
    contours_by_layer = {z: contour for z, contour in results}
    return contours_by_layer

