import json

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import shapely.geometry as sg
import numpy as np

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import shapely.geometry as sg

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import shapely.geometry as sg


def cutCamber(allPath, diameter, zPer, zDepth, stepOver,
              ring_cut=True, outBuffer=5, inBuffer=-1.0,
              show_plot=True):
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import unary_union
    import shapely.geometry as sg

    allToolPath = []
    allToolPathDepth = []

    # === 收集所有层的轮廓用于统一绘图 ===
    allContours = []  # 每一层是 [(x_list, y_list, step, pathIdx)]

    for pathIdx, pathPoints in enumerate(allPath):
        depth = pathPoints[1]
        outer = Polygon(pathPoints[0][1])  # 外圈
        hole = Polygon(pathPoints[0][0])   # 内圈

        # === 环形区域处理 ===
        if ring_cut:
            outer_buffered = outer.buffer(outBuffer, resolution=128, quad_segs=128)
            hole_buffered = unary_union(hole).buffer(inBuffer, resolution=128, quad_segs=128)
            cut_polygon = outer_buffered.difference(hole_buffered)
        else:
            cut_polygon = outer.difference(unary_union(hole))

        if cut_polygon.is_empty:
            continue

        allToolPathDepth.append([depth[0], depth[1]])

        # === 蚕食式 buffer，记录每一层轮廓 ===
        current_polygon = cut_polygon
        step_idx = 0
        while not current_polygon.is_empty and current_polygon.area > 0.01:
            polygons = current_polygon.geoms if isinstance(current_polygon, MultiPolygon) else [current_polygon]
            for poly in polygons:
                if poly.is_empty or poly.area <= 0.01:
                    continue
                coords = list(poly.exterior.coords)
                x, y = zip(*coords)
                allContours.append((x, y, step_idx, pathIdx))
            current_polygon = current_polygon.buffer(-stepOver, resolution=128, quad_segs=128)
            step_idx += 1

    # === 一次性绘图 ===
    if show_plot:
        import matplotlib.cm as cm
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.set_title('All Cut Paths (buffered inwards)')

        color_map = cm.get_cmap("tab10")  # 用不同颜色区分 pathIdx

        for x, y, step, pathIdx in allContours:
            color = color_map(pathIdx % 10)
            ax.plot(x, y, '-', linewidth=1.0, color=color,
                    alpha=max(0.3, 1 - step * 0.1))  # 深层更浅

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True)
        plt.show()

    return allToolPath, allToolPathDepth




with open("point.json") as f:
    data = json.load(f)

cutCamber(data, 6, 1, -20, 1)
