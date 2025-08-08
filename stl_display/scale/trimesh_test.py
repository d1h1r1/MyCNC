import time
import trimesh
import numpy as np
from matplotlib import pyplot as plt


def fast_stl_slicing(stl_path, layer_height):
    # Load the mesh
    mesh = trimesh.load(stl_path)

    # Get mesh bounds to determine slicing range
    z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2]

    # Generate slicing planes
    z_levels = np.arange(z_min, z_max, layer_height)
    plane_origins = np.column_stack([np.zeros(len(z_levels)),
                                     np.zeros(len(z_levels)),
                                     z_levels])
    # Slice at each plane
    sections = []
    for origin in plane_origins:
        section = trimesh.intersections.mesh_plane(
            mesh=mesh,
            plane_normal=[0, 0, 1],  # Z-axis normal
            plane_origin=origin,  # Single origin point
            # engine='auto'
        )
        if len(section) > 0:
            sections.append(section)
    return sections


# 使用示例
if __name__ == "__main__":
    # contours = fast_stl_slicing("../../file/配合25凸.stl", 0.2)
    # t1 = time.time()
    # contours = fast_stl_slicing("../../file/2.方形凹_简单.stl", 0.1)
    # t2 = time.time()
    # print(t2 - t1)
    # print(f"共获取 {len(contours)} 层轮廓")


    # all_list = []
    # all_dict = {}
    # # print(contours)
    # for i in contours:
    #     z = 0
    #     # print(i)
    #     # print("-----------------")
    #     # print(j)
    #     paths = []
    #     for j in i:
    #         path = []
    #         # print(j)
    #         # print("------------")
    #         for k in j:
    #             plt.plot(k[0], k[1], '-o', markersize=1)
    #             # print("111", len(k))
    #             # print(k)
    #             path.append([k[0], k[1], k[2]])
    #             z = k[2]
    #         # print(path)
    #         # print("-----------------")
    #         paths.append(path)
    #     print(z, paths)
    #     plt.show()

        # all_dict[z] = paths

    # print(all_dict.keys())


    # contours = fast_stl_slicing("../../file/配合25凸.stl", 0.1)
    contours = fast_stl_slicing("../../file/MGH-18 指根下连杆 v1.0.stl", 0.1)
    print(f"共获取 {len(contours)} 层轮廓")
    # print(contours)
    for contour in contours:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        print(contour)
        print("=================")
        for segment in contour:
            # Extract x, y, z coordinates
            x = segment[:, 0]
            y = segment[:, 1]
            z = segment[:, 2]

            # Plot the line
            ax.plot(x, y, z, '-o', markersize=2, linewidth=1)
            # print(segment)
            # print("================")
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        ax.set_title('3D Contour Visualization')

        # Improve the viewing angle
        ax.view_init(elev=20, azim=45)
        plt.show()
