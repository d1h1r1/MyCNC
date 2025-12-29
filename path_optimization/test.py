from matplotlib import pyplot as plt
from shapely import Polygon, unary_union
import shapely.geometry as sg

point0 = [(12.744, 11.9), (12.632, 11.903), (12.602, 11.904), (12.566, 11.905), (12.542, 11.906), (12.501, 11.907), (12.5, 11.907), (12.48, 11.908), (11.654, 12.181), (7.153, 14.44), (6.106, 15.144), (4.688, 16.043), (3.065, 16.471), (1.388, 16.389), (-0.185, 15.805), (-1.509, 14.772), (-2.859, 13.918), (-4.382, 13.433), (-5.978, 13.348), (-7.543, 13.67), (-9.453, 14.609), (-9.974, 14.708), (-10.503, 14.666), (-11.821, 14.17), (-12.938, 13.311), (-13.755, 12.163), (-14.282, 10.575), (-14.283, 10.573), (-14.287, 10.562), (-14.442, 10.331), (-14.656, 10.152), (-14.783, 10.095), (-14.789, 10.093), (-14.821, 10.078), (-14.824, 10.076), (-14.859, 10.061), (-14.861, 10.06), (-14.897, 10.044), (-14.899, 10.044), (-14.91, 10.039), (-15.186, 10.0), (-15.447, 10.088), (-15.675, 10.244), (-15.851, 10.457), (-15.954, 10.69), (-15.954, 10.691), (-15.962, 10.709), (-16.0, 10.983), (-16.0, 16.5), (-16.0, 16.501), (-15.727, 18.572), (-14.928, 20.501), (-13.657, 22.157), (-11.999, 23.429), (-10.07, 24.228), (-8.0, 24.5), (8.862, 24.5), (8.863, 24.5), (11.02, 23.965), (12.946, 22.855), (14.492, 21.257), (15.537, 19.295), (16.0, 17.121), (16.0, 14.862), (15.874, 14.002), (15.507, 13.214), (15.059, 12.71), (14.929, 12.564), (14.189, 12.108), (13.349, 11.883), (12.805, 11.898), (12.744, 11.9)]
point1 = [(18.487, -15.261), (18.489, -15.262), (18.678, -15.364), (18.68, -15.365), (19.292, -15.696), (19.335, -15.716), (20.83, -16.0), (20.83, -24.0), (20.786, -24.0), (20.681, -24.0), (20.575, -24.0), (20.469, -24.0), (20.364, -24.0), (20.258, -24.0), (20.153, -24.0), (20.047, -24.0), (19.942, -24.0), (19.836, -24.0), (19.731, -24.0), (19.625, -24.0), (19.484, -24.0), (19.279, -24.0), (19.075, -24.0), (18.871, -24.0), (18.666, -24.0), (18.462, -24.0), (18.257, -24.0), (18.053, -24.0), (17.553, -24.0), (16.898, -24.0), (-21.0, -24.0), (-21.0, -2.5), (11.0, -2.5), (11.001, -2.5), (12.546, -2.745), (13.051, -3.003), (13.754, -3.36), (13.811, -3.389), (13.893, -3.431), (13.939, -3.455), (14.456, -3.971), (15.045, -4.561), (15.755, -5.955), (16.0, -7.5), (16.0, -11.003), (16.244, -12.537), (16.915, -13.887), (18.0, -14.999), (18.29, -15.155), (18.298, -15.159), (18.487, -15.261)]
point15 = [(-14.861, 10.06), (-14.897, 10.044), (-14.899, 10.044), (-14.91, 10.039), (-15.186, 10.0), (-15.447, 10.088), (-15.675, 10.244), (-15.851, 10.457), (-15.864, 10.487), (-15.865, 10.488), (-15.906, 10.582), (-15.954, 10.69), (-15.954, 10.691), (-15.962, 10.709), (-16.0, 10.983), (-16.0, 16.5), (-16.0, 16.501), (-16.0, 24.5), (-8.0, 24.5), (8.862, 24.5), (8.863, 24.5), (16.0, 24.5), (16.0, 17.121), (16.0, 14.862), (15.997, 14.841), (15.997, 14.841), (15.994, 14.821), (15.994, 14.819), (15.991, 14.799), (15.991, 14.798), (15.964, 14.613), (15.95, 14.518), (15.874, 14.002), (15.507, 13.214), (15.059, 12.71), (14.929, 12.564), (14.189, 12.108), (13.349, 11.883), (13.329, 11.883), (13.327, 11.883), (13.251, 11.885), (13.218, 11.886), (13.096, 11.89), (13.044, 11.891), (12.884, 11.896), (12.805, 11.898), (12.744, 11.9), (12.632, 11.903), (12.602, 11.904), (12.566, 11.905), (12.542, 11.906), (12.501, 11.907), (12.5, 11.907), (12.485, 11.908), (12.479, 11.908), (11.654, 12.181), (7.153, 14.44), (6.106, 15.144), (4.688, 16.043), (3.065, 16.471), (1.388, 16.389), (-0.185, 15.805), (-1.509, 14.772), (-2.859, 13.918), (-4.382, 13.433), (-5.978, 13.348), (-7.544, 13.67), (-9.453, 14.609), (-9.974, 14.708), (-10.503, 14.666), (-11.79, 14.182), (-12.938, 13.311), (-13.755, 12.163), (-14.282, 10.575), (-14.283, 10.573), (-14.287, 10.562), (-14.442, 10.331), (-14.656, 10.152), (-14.661, 10.15), (-14.662, 10.149), (-14.667, 10.147), (-14.668, 10.146), (-14.733, 10.117), (-14.738, 10.115), (-14.766, 10.102), (-14.783, 10.095), (-14.789, 10.093), (-14.821, 10.078), (-14.824, 10.076), (-14.859, 10.061), (-14.861, 10.06)]
point16 = [[-25.0, -30.0, 0.0], [-25.0, 30.0, 0.0], [25.0, 30.0, 0.0], [25.0, -30.0, 0.0], [-25.0, -30.0, 0.0], [-25.0, -30.0, 0.0]]


point00 = [(-43.089, 34.359), (-43.084, 34.36), (-42.674, 34.474), (-41.957, 34.701), (-41.311, 34.958), (-40.759, 35.213), (-40.531, 35.325), (-39.847, 35.699), (-39.831, 35.707), (-39.811, 35.72), (-39.24, 36.09), (-38.841, 36.38), (-38.553, 36.598), (-37.941, 37.109), (-37.512, 37.519), (-37.109, 37.941), (-36.575, 38.578), (-36.555, 38.603), (-36.554, 38.605), (-36.554, 38.605), (-36.554, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.605), (-36.553, 38.606), (-36.089, 39.242), (-35.72, 39.811), (-35.705, 39.835), (-35.301, 40.572), (-35.259, 40.656), (-34.913, 41.408), (-34.701, 41.957), (-34.478, 42.659), (-34.351, 43.126), (-34.183, 43.943), (-34.178, 43.967), (-34.058, 44.822), (-34.014, 45.411), (-34.0, 46.0), (-34.0, 50.0), (34.0, 50.0), (34.0, 46.0), (34.014, 45.411), (34.058, 44.822), (34.176, 43.985), (34.189, 43.912), (34.359, 43.089), (34.36, 43.084), (34.474, 42.674), (34.701, 41.957), (34.958, 41.311), (35.213, 40.759), (35.325, 40.531), (35.699, 39.847), (35.707, 39.831), (35.72, 39.811), (36.09, 39.24), (36.38, 38.841), (36.598, 38.553), (37.109, 37.941), (37.519, 37.512), (37.941, 37.109), (38.5, 36.638), (38.839, 36.382), (39.239, 36.09), (39.831, 35.707), (40.572, 35.301), (40.656, 35.259), (41.408, 34.913), (41.957, 34.701), (42.659, 34.478), (43.126, 34.351), (43.943, 34.183), (43.967, 34.178), (44.822, 34.058), (45.411, 34.014), (46.0, 34.0), (50.0, 34.0), (50.0, -34.0), (46.0, -34.0), (45.411, -34.014), (44.822, -34.058), (43.967, -34.178), (43.943, -34.183), (43.126, -34.351), (42.659, -34.478), (41.957, -34.701), (41.408, -34.913), (40.656, -35.259), (40.572, -35.301), (39.831, -35.707), (39.245, -36.086), (38.707, -36.478), (38.52, -36.622), (37.941, -37.109), (37.503, -37.527), (37.109, -37.941), (36.638, -38.5), (36.382, -38.839), (36.09, -39.239), (35.707, -39.831), (35.304, -40.567), (35.256, -40.663), (34.913, -41.408), (34.701, -41.957), (34.48, -42.653), (34.347, -43.145), (34.183, -43.943), (34.178, -43.967), (34.069, -44.749), (34.014, -45.411), (34.0, -46.0), (34.0, -50.0), (-34.0, -50.0), (-34.0, -46.0), (-34.014, -45.411), (-34.058, -44.822), (-34.176, -43.985), (-34.189, -43.912), (-34.359, -43.089), (-34.36, -43.084), (-34.474, -42.674), (-34.701, -41.957), (-34.958, -41.311), (-35.213, -40.759), (-35.325, -40.531), (-35.699, -39.847), (-35.707, -39.831), (-35.72, -39.811), (-36.09, -39.24), (-36.38, -38.841), (-36.598, -38.553), (-37.105, -37.946), (-37.247, -37.797), (-37.519, -37.512), (-37.803, -37.241), (-37.946, -37.105), (-38.553, -36.598), (-38.841, -36.38), (-39.24, -36.09), (-39.811, -35.72), (-39.835, -35.705), (-40.516, -35.332), (-40.805, -35.191), (-41.307, -34.959), (-41.957, -34.701), (-42.674, -34.474), (-43.084, -34.36), (-43.089, -34.359), (-43.928, -34.186), (-43.977, -34.177), (-44.822, -34.058), (-45.411, -34.014), (-46.0, -34.0), (-50.0, -34.0), (-50.0, 34.0), (-46.0, 34.0), (-45.411, 34.014), (-44.822, 34.058), (-43.977, 34.177), (-43.928, 34.186), (-43.089, 34.359)]
point19 = [[-34.0, 50.0, 0.0], [34.0, 50.0, 0.0], [50.0, 50.0, 0.0], [50.0, 34.0, 0.0], [50.0, -34.0, 0.0], [50.0, -50.0, 0.0], [34.0, -50.0, 0.0], [-34.0, -50.0, 0.0], [-50.0, -50.0, 0.0], [-50.0, -34.0, 0.0], [-50.0, 34.0, 0.0], [-50.0, 50.0, 0.0], [-34.0, 50.0, 0.0]]


outer = Polygon(point16)
# outer = Polygon(point19)
outOffset = stepOver = 3
outer = outer.buffer(outOffset)

allHole = []
# hole1 = Polygon(point1)
# hole1 = hole1.buffer(outOffset)
# allHole.append(hole1)

hole0 = Polygon(point0)
hole0 = hole0.buffer(outOffset)
allHole.append(hole0)


def process_polygon(poly, shrink_step, min_area=1.0):
    """
    递归处理 Polygon / MultiPolygon / GeometryCollection
    每次收缩后返回所有有效 Polygon
    """
    results = []

    if poly.is_empty:
        return results

    if isinstance(poly, sg.Polygon):
        if poly.area < min_area:
            return results
        results.append(poly)
        shrunk = poly.buffer(shrink_step)
        if not shrunk.is_empty:
            results += process_polygon(shrunk, shrink_step, min_area)

    elif isinstance(poly, (sg.MultiPolygon, sg.GeometryCollection)):
        for g in poly.geoms:
            if isinstance(g, sg.Polygon) and g.area > min_area:
                results += process_polygon(g, shrink_step, min_area)

    return results


def func1():
    current_out = outer
    # 将所有内轮廓合并成一个 geometry（组合）
    holes_union = unary_union(allHole)
    # 差集区域（可加工区域）
    cut_polygon = outer.difference(holes_union, 0.001)
    current_polygon = cut_polygon
    firstFlag = True
    while not current_polygon.is_empty and current_polygon.area > 1:
        if firstFlag:
            firstFlag = False
        else:
            current_out = current_out.buffer(-stepOver)  # 向内收缩

        holes_union = unary_union(allHole)
        current_polygon = current_out.difference(holes_union, 0.001)

        if isinstance(current_polygon, sg.MultiPolygon):
            polygons = list(current_polygon.geoms)
        elif isinstance(current_polygon, sg.GeometryCollection):
            polygons = []
            for g in current_polygon.geoms:
                if g.geom_type == 'Polygon' and g.area > 0.1:
                    polygons.append(g)
        else:
            polygons = [current_polygon]

        # 一次性处理所有polygon并继续 offset
        merged_poly = unary_union(polygons)
        # 在这里做递归向内 offset
        inner_polys = process_polygon(merged_poly, -stepOver, min_area=1.0)
        for poly in inner_polys:
            if poly.is_empty or poly.area <= 1:
                continue

            coords = list(poly.exterior.coords)
            x_coords, y_coords = zip(*coords)
            plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')

            hole = Polygon(coords)
            # ✅ 记录为避让区域（防止重复切）
            allHole.append(hole)
    plt.show()


def func2():
    current_out = outer
    # 将所有内轮廓合并成一个 geometry（组合）
    holes_union = unary_union(allHole)
    # 差集区域（可加工区域）
    cut_polygon = outer.difference(holes_union, 0.001)
    current_polygon = cut_polygon
    firstFlag = True
    while not current_polygon.is_empty and current_polygon.area > 0.01:
        if firstFlag:
            firstFlag = False
        else:
            current_out = current_out.buffer(-outOffset)  # 向内收缩
        # 差集区域（可加工区域）
        current_polygon = current_out.difference(holes_union, 0.001)
        if isinstance(current_polygon, sg.MultiPolygon):
            polygons = list(current_polygon.geoms)
        elif isinstance(current_polygon, sg.GeometryCollection):
            polygons = []
            for g in current_polygon.geoms:
                if g.geom_type == 'Polygon' and g.area > 1:
                    polygons.append(g)
        else:
            polygons = [current_polygon]
        for poly in polygons:
            if poly.is_empty or poly.area <= 1:
                continue
            coords = list(poly.exterior.coords)  # 提取外边界点
            x_coords, y_coords = zip(*coords)
            plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
    plt.show()


def process_polygon(poly, shrink_step, min_area=1.0):
    """
    递归处理 Polygon / MultiPolygon / GeometryCollection
    对每个Polygon单独进行偏移处理
    """
    results = []

    if poly.is_empty:
        return results

    if isinstance(poly, sg.Polygon):
        if poly.area < min_area:
            return results
        results.append(poly)
        shrunk = poly.buffer(shrink_step)
        if not shrunk.is_empty:
            results += process_polygon(shrunk, shrink_step, min_area)

    elif isinstance(poly, (sg.MultiPolygon, sg.GeometryCollection)):
        # 关键修改：对每个子Polygon分别递归处理
        for g in poly.geoms:
            if isinstance(g, sg.Polygon) and g.area > min_area:
                # 对每个子Polygon单独进行递归偏移
                sub_results = process_polygon(g, shrink_step, min_area)
                results.extend(sub_results)

    return results


def func1_improved():
    current_out = outer
    # 将所有内轮廓合并成一个 geometry（组合）
    holes_union = unary_union(allHole)
    # 差集区域（可加工区域）
    cut_polygon = outer.difference(holes_union, 0.001)
    current_polygon = cut_polygon
    firstFlag = True

    while not current_polygon.is_empty and current_polygon.area > 1:
        if firstFlag:
            firstFlag = False
        else:
            current_out = current_out.buffer(-stepOver)  # 向内收缩

        holes_union = unary_union(allHole)
        current_polygon = current_out.difference(holes_union, 0.001)

        if current_polygon.is_empty:
            break

        # 关键修改：对MultiPolygon中的每个Polygon分别处理
        if isinstance(current_polygon, sg.MultiPolygon):
            # 对每个子Polygon单独进行递归偏移
            all_inner_polys = []
            for poly in current_polygon.geoms:
                if isinstance(poly, sg.Polygon) and poly.area > 1:
                    # 对单个Polygon进行递归偏移
                    inner_polys = process_polygon(poly, -stepOver, min_area=1.0)
                    all_inner_polys.extend(inner_polys)

            # 绘制所有处理后的多边形
            for poly in all_inner_polys:
                if poly.is_empty or poly.area <= 1:
                    continue
                coords = list(poly.exterior.coords)
                x_coords, y_coords = zip(*coords)
                plt.plot(x_coords, y_coords, '-o', markersize=1, linewidth=1)

                # 添加到避让区域
                hole = Polygon(coords)
                allHole.append(hole)
                # plt.axis('equal')
                # plt.show()
        elif isinstance(current_polygon, sg.GeometryCollection):
            polygons = []
            for g in current_polygon.geoms:
                if g.geom_type == 'Polygon' and g.area > 1:
                    polygons.append(g)
            # 对每个有效的Polygon分别处理
            for poly in polygons:
                inner_polys = process_polygon(poly, -stepOver, min_area=1.0)
                for inner_poly in inner_polys:
                    if inner_poly.is_empty or inner_poly.area <= 1:
                        continue
                    coords = list(inner_poly.exterior.coords)
                    x_coords, y_coords = zip(*coords)
                    plt.plot(x_coords, y_coords, '-o', markersize=1, linewidth=1)

                    hole = Polygon(coords)
                    allHole.append(hole)
                    # plt.axis('equal')
                    # plt.show()
        else:  # 单个Polygon
            inner_polys = process_polygon(current_polygon, -stepOver, min_area=1.0)
            for poly in inner_polys:
                if poly.is_empty or poly.area <= 1:
                    continue
                coords = list(poly.exterior.coords)
                x_coords, y_coords = zip(*coords)
                plt.plot(x_coords, y_coords, '-o', markersize=1, linewidth=1)

                hole = Polygon(coords)
                allHole.append(hole)

                # plt.axis('equal')
                # plt.show()
    plt.axis('equal')
    plt.show()


# 使用改进的版本
func1_improved()

