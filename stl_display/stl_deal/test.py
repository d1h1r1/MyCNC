import time

import trimesh
import numpy as np


def compress_stl_top_view(input_stl, output_stl, grid_step=0.5):
    mesh = trimesh.load_mesh(input_stl, force='mesh')
    direction = np.array([[0, 0, -1]])

    min_bound = mesh.bounds[0]
    max_bound = mesh.bounds[1]

    xs = np.arange(min_bound[0], max_bound[0], grid_step)
    ys = np.arange(min_bound[1], max_bound[1], grid_step)
    # print(min_bound)
    # print(max_bound)
    # print(xs)
    # print(ys)
    verts = mesh.vertices.copy()

    for x in xs:
        for y in ys:
            ray_origin = np.array([[x, y, max_bound[2] + 1]])
            locations, index_ray, index_tri = mesh.ray.intersects_location(
                ray_origins=ray_origin, ray_directions=direction
            )
            if len(locations) > 0:
                # 获取俯视最高点的 Z
                # top_z = np.max(locations[:, 2])
                top_z = np.min(locations[:, 2])
                # 找到所有被击中的三角形
                hit_faces = np.unique(index_tri)
                for f in hit_faces:
                    for vid in mesh.faces[f]:
                        if verts[vid, 2] <= top_z+1:
                            verts[vid, 2] = -10

    new_mesh = trimesh.Trimesh(vertices=verts, faces=mesh.faces)
    new_mesh.export(output_stl)
    print(f"压缩完成，已保存到 {output_stl}")


if __name__ == "__main__":
    t1 = time.time()
    # in_stl = "../../file/MGH-19 指根上连杆 v1.0.stl"
    in_stl = "../../file/MGH-18 指根下连杆 v1.0.stl"
    # in_stl = "../../file/MGH-20 关节R安装件 v1.0.stl"
    compress_stl_top_view(in_stl, "output_compressed.stl", grid_step=0.5)
    t2 = time.time()
    print(t2 - t1)
