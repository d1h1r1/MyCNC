import trimesh
import numpy as np


def get_top_z(mesh, grid_step=0.5):
    direction = np.array([[0, 0, -1]])
    min_bound = mesh.bounds[0]
    max_bound = mesh.bounds[1]

    xs = np.arange(min_bound[0], max_bound[0], grid_step)
    ys = np.arange(min_bound[1], max_bound[1], grid_step)

    max_z = -np.inf
    for x in xs:
        for y in ys:
            ray_origin = np.array([[x, y, max_bound[2] + 1]])
            locations, _, _ = mesh.ray.intersects_location(
                ray_origins=ray_origin, ray_directions=direction
            )
            if len(locations) > 0:
                local_max_z = np.max(locations[:, 2])
                if local_max_z > max_z:
                    max_z = local_max_z
    return max_z


def compress_stl_by_clipping(input_stl, output_stl, grid_step=0.5):
    mesh = trimesh.load_mesh(input_stl, force='mesh')
    top_z = get_top_z(mesh, grid_step)
    print(f"模型顶层最大Z: {top_z}")

    # 定义裁剪平面，法线向上，位于顶层最大Z
    plane_origin = np.array([0, 0, top_z])
    plane_normal = np.array([0, 0, 1])

    # 裁剪模型，切除低于平面的部分
    clipped = mesh.slice_plane(plane_origin=plane_origin, plane_normal=plane_normal)

    clipped.export(output_stl)
    print(f"裁剪完成，已保存到 {output_stl}")


if __name__ == "__main__":
    in_stl = "../../file/MGH-19 指根上连杆 v1.0.stl"
    compress_stl_by_clipping(in_stl, "output_compressed_by_clip.stl", grid_step=0.5)
