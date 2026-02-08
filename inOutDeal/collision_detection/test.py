import time

import trimesh
import numpy as np

path = "../../file/一键智铣/复杂/Halloween_Fidget_Web_-_Large_22_Layers.stl"

mesh = trimesh.load(path, force='mesh')


def fast_collision(contour, zmin, zmax, mesh):
    origins = np.array([[x, y, zmin - 1] for x, y in contour])
    dirs = np.array([[0, 0, 1]] * len(contour))

    # 批量加速
    hits = mesh.ray.intersects_any(origins, dirs)
    return np.any(hits)


polygon = [
    [0.0, 0.0],
    [2.0, 0.0],
    [3.0, 1.0],
    [1.5, 2.0],
    [0.0, 1.5]
]


s = time.time()
a = fast_collision(polygon, 20, 100, mesh)
s2 = time.time()
print(s2-s)
