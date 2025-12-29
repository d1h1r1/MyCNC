import numpy as np
import trimesh


def is_likely_relief(mesh: trimesh.Trimesh, max_thickness_ratio=0.1, normal_consistency_threshold=0.8):
    # 检测是否封闭
    if not mesh.is_watertight:
        # 如果不是封闭体，可能是浮雕或开放结构
        non_watertight_flag = True
    else:
        non_watertight_flag = False

    # 法线方向一致性：统计每个三角形法线与某主方向（例如 mesh.mean_normal）之间的夹角
    normals = mesh.face_normals
    mean_norm = normals.mean(axis=0)
    # 归一化
    mean_norm = mean_norm / (np.linalg.norm(mean_norm) + 1e-8)
    cosines = normals.dot(mean_norm)
    # 看有多少面的法线 / 主方向接近
    aligned_ratio = np.sum(cosines > 0.9) / len(cosines)

    # 厚度测算：对每个顶点或每个面中心，沿法线方向射线交点，测厚度
    # 这里用一个近似：对每个顶点，做双向 ray 查询到网格交点距离
    thicknesses = []
    for v, n in zip(mesh.vertices, mesh.vertex_normals):
        # 两方向 ray
        dists = mesh.ray.intersects_location([v], [n])[1]  # 正方向
        dists2 = mesh.ray.intersects_location([v], [-n])[1]  # 反方向
        # 简化处理：取最近交点距离作为半厚度
        # （注意要排除自身交点等噪声）
        if len(dists) > 0 and len(dists2) > 0:
            thicknesses.append(min(dists[0], dists2[0]))
    if len(thicknesses) == 0:
        avg_thick = 0
    else:
        avg_thick = np.mean(thicknesses)
        max_thick = np.max(thicknesses)

    # 如果厚度很小（相对于模型最大边长） + 法线一致性高 + 非 watertight，则可能为浮雕
    bounding_size = mesh.bounding_box.extents.max()
    thickness_ratio = max_thick / bounding_size if bounding_size > 0 else 0

    # 判断规则
    if (non_watertight_flag or aligned_ratio > normal_consistency_threshold) and thickness_ratio < max_thickness_ratio:
        return True
    else:
        return False


mesh = trimesh.load_mesh("../file/T.stl")
print(is_likely_relief(mesh))
