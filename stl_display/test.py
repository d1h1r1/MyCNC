import time
from multiprocessing import freeze_support

import triangleCut


def test():
    import matplotlib.pyplot as plt
    from shapely.geometry import MultiLineString
    from shapely.ops import polygonize
    import numpy as np

    def intersect_triangle_with_plane(tri, z):
        points = []
        for i in range(3):
            p1, p2 = tri[i], tri[(i + 1) % 3]
            z1, z2 = p1[2], p2[2]
            if (z1 - z) * (z2 - z) < 0:
                t = (z - z1) / (z2 - z1)
                x = p1[0] + t * (p2[0] - p1[0])
                y = p1[1] + t * (p2[1] - p1[1])
                points.append((x, y))
            elif z1 == z and z2 != z:
                points.append((p1[0], p1[1]))
        return points if len(points) == 2 else None

    def process_slice(i, triangles, layer_height=0.25):
        target_z = layer_height * i
        lines = []
        for tri in triangles:
            segment = intersect_triangle_with_plane(tri, target_z)
            if segment:
                lines.append(segment)

        print(f"Z={target_z}, {len(lines)} line segments")
        for line in lines:
            print("  ", line)

        polygons = list(polygonize(MultiLineString(lines)))
        perList = []
        for poly in polygons:
            if poly.area > 0.0001:
                perList.append(list(poly.exterior.coords))

        for i in perList:
            x, y = zip(*i)
            plt.plot(x, y, '-o', markersize=2)
        if perList:
            plt.title(f"Slice at Z={target_z}")
            plt.gca().set_aspect('equal')
            plt.show()

        return target_z, perList

    # 定义一个 1x1x1 的立方体，8个顶点，12个三角面
    cube = [
        # bottom
        [(0, 0, 0), (1, 0, 0), (1, 1, 0)],
        [(0, 0, 0), (1, 1, 0), (0, 1, 0)],
        # top
        [(0, 0, 1), (1, 1, 1), (1, 0, 1)],
        [(0, 0, 1), (0, 1, 1), (1, 1, 1)],
        # sides
        [(0, 0, 0), (0, 0, 1), (1, 0, 1)],
        [(0, 0, 0), (1, 0, 1), (1, 0, 0)],

        [(1, 0, 0), (1, 0, 1), (1, 1, 1)],
        [(1, 0, 0), (1, 1, 1), (1, 1, 0)],

        [(1, 1, 0), (1, 1, 1), (0, 1, 1)],
        [(1, 1, 0), (0, 1, 1), (0, 1, 0)],

        [(0, 1, 0), (0, 1, 1), (0, 0, 1)],
        [(0, 1, 0), (0, 0, 1), (0, 0, 0)],
    ]

    # 多层切片
    for i in range(5):  # z = 0, 0.25, 0.5, 0.75, 1.0
        process_slice(i, cube, layer_height=0.25)


if __name__ == '__main__':
    freeze_support()
    # test()
    save_path = "82.stl"
    t1 = time.time()
    max_area_point, all_scale, detailFlag = triangleCut.get_scale(save_path)
    t2 = time.time()
    print(t2 - t1)
    allPath, inOutPath = triangleCut.scalePocket(all_scale, max_area_point, save_path)
