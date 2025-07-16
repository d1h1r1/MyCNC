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

def cutCamber(allPath, diameter, zPer, zDepth, stepOver):
    allToolPath = []
    allToolPathDepth = []

    for pathIdx, pathPoints in enumerate(allPath):
        depth = pathPoints[1]
        outer = Polygon(pathPoints[0][1])
        hole = Polygon(pathPoints[0][0])
        holes_union = unary_union(hole)
        cut_polygon = outer.difference(holes_union)

        if not cut_polygon:
            continue

        if isinstance(cut_polygon, sg.MultiPolygon):
            pocketType = 1
        else:
            if cut_polygon.interiors:
                pocketType = 0
            else:
                pocketType = 1
        outBuffer = diameter*0.4
        if pocketType:
            # 外减内为一个区域，区域放大
            holes_union = unary_union(hole)
            cut_polygon = outer.difference(holes_union)
            cut_polygon = cut_polygon.buffer(outBuffer, resolution=128, quad_segs=128)
        else:
            # 外减内为一个环，直接最外围到内
            outBuffer = diameter*0.4
            cut_polygon = Polygon(pathPoints[0][1]).buffer(outBuffer, resolution=128, quad_segs=128)
            # hole = Polygon(pathPoints[0][0]).buffer(inBuffer, resolution=128, quad_segs=128)
            # holes_union = unary_union(hole)

        # 保存当前深度
        allToolPathDepth.append([depth[0], depth[1]])

        # 初始化图像
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.set_title(f'All Buffer Layers, Z={depth[1]:.2f}')

        # 多层 buffer 可视化
        current_polygon = cut_polygon
        step_idx = 0
        colors = plt.cm.viridis_r  # 颜色渐变

        while not current_polygon.is_empty and current_polygon.area > 0.01:
            polygons = current_polygon.geoms if isinstance(current_polygon, MultiPolygon) else [current_polygon]

            for poly in polygons:
                if poly.is_empty or poly.area <= 0.01:
                    continue
                coords = list(poly.exterior.coords)
                x_coords, y_coords = zip(*coords)
                ax.plot(x_coords, y_coords, '-', color=colors(step_idx * 0.1), label=f'Step {step_idx}')

            # 缩放一层
            # if pocketType:
            #     current_polygon = current_polygon.buffer(-stepOver, resolution=128, quad_segs=128)
            # else:
            #     outer = outer.buffer(-stepOver, resolution=128, quad_segs=128)
            #     current_polygon = outer.difference(holes_union)
            current_polygon = current_polygon.buffer(-stepOver, resolution=128, quad_segs=128)
            step_idx += 1

        ax.legend()
        plt.show()

    return allToolPath, allToolPathDepth


with open("point.json") as f:
    data = json.load(f)

cutCamber(data, 6, 1, -20, 1)
