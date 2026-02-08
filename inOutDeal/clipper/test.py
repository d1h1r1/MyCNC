import trimesh
import numpy as np
from matplotlib import pyplot as plt

# path = "../../file/方孔.stl"
path = "../../file/开瓶器-LOGO.stl"
mesh = trimesh.load_mesh(path)


def segment_intersects_mesh(mesh, p0, p1):
    direction = p1 - p0
    length = np.linalg.norm(direction)
    direction = direction / length

    # Embree 做光线检测（超级快）
    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=[p0],
        ray_directions=[direction]
    )

    if len(locations) == 0:
        return False

    dist = np.linalg.norm(locations[0] - p0)

    return dist <= length + 1e-9


def contour_intersect(mesh, pts):
    for i in range(len(pts) - 1):
        p0 = pts[i]
        p1 = pts[i + 1]
        if segment_intersects_mesh(mesh, p0, p1):
            return True
    return False


point = [[2.711, 18.122, -0.1],
         [3.07, 18.251, -0.1],
         [3.611, 18.572, -0.1],
         [3.901, 18.83, -0.1],
         [4.257, 19.3, -0.1],
         [4.402, 19.566, -0.1],
         [4.543, 19.955, -0.1],
         [4.597, 20.183, -0.1],
         [4.644, 20.6, -0.1],
         [4.632, 20.907, -0.1],
         [4.519, 21.487, -0.1],
         [4.375, 21.843, -0.1],
         [4.033, 22.371, -0.1],
         [3.766, 22.648, -0.1],
         [3.251, 23.009, -0.1],
         [2.903, 23.165, -0.1],
         [2.292, 23.309, -0.1],
         [1.909, 23.324, -0.1],
         [1.322, 23.235, -0.1],
         [1.024, 23.14, -0.1],
         [0.65, 22.953, -0.1],
         [0.461, 22.83, -0.1],
         [0.141, 22.566, -0.1],
         [-0.065, 22.335, -0.1],
         [-0.385, 21.84, -0.1],
         [-0.527, 21.486, -0.1],
         [-0.648, 20.869, -0.1],
         [-0.648, 20.482, -0.1],
         [-0.527, 19.864, -0.1],
         [-0.385, 19.51, -0.1],
         [-0.043, 18.981, -0.1],
         [0.225, 18.702, -0.1],
         [0.741, 18.34, -0.1],
         [1.089, 18.184, -0.1],
         [1.701, 18.04, -0.1],
         [2.089, 18.025, -0.1]]

pts = np.asarray(point, dtype=np.float64)
a = contour_intersect(mesh, pts)
print(a)

x_coords, y_coords, z = zip(*point)
plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
plt.show()

