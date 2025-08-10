import time
import trimesh
import numpy as np


def compress_stl_top_view_by_verts(input_stl, output_stl):
    mesh = trimesh.load_mesh(input_stl, force='mesh')
    direction = np.array([[0, 0, -1]])

    verts = mesh.vertices.copy()
    # 取出所有顶点的 XY 坐标，去重
    xy_points = np.unique(verts[:, :2], axis=0)

    for xy in xy_points:
        ray_origin = np.array([[xy[0], xy[1], mesh.bounds[1][2] + 1]])
        locations, index_ray, index_tri = mesh.ray.intersects_location(
            ray_origins=ray_origin, ray_directions=direction
        )
        if len(locations) > 0:
            top_z = np.max(locations[:, 2])
            hit_faces = np.unique(index_tri)
            for f in hit_faces:
                for vid in mesh.faces[f]:
                    if verts[vid, 2] < top_z:
                        verts[vid, 2] = -10

    new_mesh = trimesh.Trimesh(vertices=verts, faces=mesh.faces)
    new_mesh.export(output_stl)
    print(f"压缩完成，已保存到 {output_stl}")


if __name__ == "__main__":
    t1 = time.time()
    # in_stl = "../../file/MGH-19 指根上连杆 v1.0.stl"
    in_stl = "../../file/MGH-18 指根下连杆 v1.0.stl"
    compress_stl_top_view_by_verts(in_stl, "output_compressed_by_verts.stl")
    t2 = time.time()
    print(f"用顶点XY坐标生成射线耗时: {t2 - t1:.2f} 秒")
