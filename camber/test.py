# 生成内部偏移刀路
@cam_ns.route("/pocketPath")
@cam_ns.expect(pocketPath_parser)
class pocketPath(Resource):
    def post(self):
        """
        生成内部偏移刀路
        """
        if 'file' in request.files:
            file = request.files['file']
            file_name = file.filename
            # 判断是否为stp或者step文件
            extensions_name = file_name[file_name.rfind(".") + 1:]
            if extensions_name.lower() != 'stl':
                return {'message': 'Unsupported file type! Only stl files are allowed.'}, 400
            # 获取参数
            params_dist = request.form.to_dict()
            # print(params_dist)
            if params_dist.get("zPer"):
                zPer = float(params_dist.get("zPer"))
            else:
                return {'message': 'please input zPer'}, 400
            if params_dist.get("feed"):
                feed = float(params_dist.get("feed"))
            else:
                return {'message': 'please input feed'}, 400
            if params_dist.get("plungeFeed"):
                plungeFeed = float(params_dist.get("plungeFeed"))
            else:
                return {'message': 'please input plungeFeed'}, 400
            if params_dist.get("spindleSpeed"):
                spindleSpeed = float(params_dist.get("spindleSpeed"))
            else:
                return {'message': 'please input spindleSpeed'}, 400
            if params_dist.get("zDepth"):
                zDepth = float(params_dist.get("zDepth"))
            else:
                return {'message': 'please input zDepth'}, 400
            if params_dist.get("toolNum"):
                toolNum = int(params_dist.get("toolNum"))
            else:
                toolNum = None
            if params_dist.get("tiltAngle"):
                tiltAngle = float(params_dist.get("tiltAngle"))
            else:
                return {'message': 'please input tiltAngle'}, 400
            if params_dist.get("materialDepth"):
                materialDepth = float(params_dist.get("materialDepth"))
            else:
                return {'message': 'please input materialDepth'}, 400
            if params_dist.get("tabLength"):
                tabLength = float(params_dist.get("tabLength"))
            else:
                return {'message': 'please input tabLength'}, 400
            if params_dist.get("tabHigh"):
                tabHigh = float(params_dist.get("tabHigh"))
            else:
                return {'message': 'please input tabHigh'}, 400
            if params_dist.get("tabNum"):
                tabNum = float(params_dist.get("tabNum"))
            else:
                return {'message': 'please input tabNum'}, 400
            if params_dist.get("stepOver"):
                stepOver = float(params_dist.get("stepOver"))
            else:
                return {'message': 'please input stepOver'}, 400
            if params_dist.get("toolType"):
                toolType = params_dist.get("toolType")
                if toolType.lower() not in ['endmill', 'ball', 'cone']:
                    return {'message': 'Unsupported tool type! Only endmil ,ball, cone are allowed.'}, 400
                if toolType == "cone":
                    if params_dist.get("angle"):
                        angle = float(params_dist.get("angle"))
                    else:
                        return {'message': 'please input angle'}, 400
                else:
                    angle = 180
            else:
                return {'message': 'please input toolType'}, 400
            if params_dist.get("diameter"):
                diameter = float(params_dist.get("diameter"))
            else:
                return {'message': 'please input diameter'}, 400
            s = time.time()
            logging.debug(f'start time: {s}')
            if not os.path.exists('../file'):
                os.makedirs('../file')
            # 删除之前保存的文件
            folder_path = os.path.join(os.getcwd(), '../file')
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # 下载上传的文件，进行转换
            save_path = os.path.join(os.getcwd(), '../file', file_name)
            # 保存文件
            file.save(save_path)
            # 获取最大外轮廓
            max_area_point, all_scale, detailFlag = stl_scale.get_scale(save_path, materialDepth)
            # print(detailFlag)
            # # 计算切割层数
            if not detailFlag:
                layer = abs(zDepth / zPer)
                num_items = math.ceil(layer)

                # 使用多进程刀路计算
                processes_num = 4
                if processes_num > num_items:
                    processes_num = num_items
                toolpaths = []
                # 进程池
                with multiprocessing.Pool(processes=processes_num) as pool:
                    with multiprocessing.Manager() as manager:
                        # 共享字典数据
                        shared_dict = manager.dict()
                        # 生成刀路
                        pool.starmap(toolPath.tool_layer, [[processes_num, zDepth, zPer,
                                                            stepOver, save_path, toolType,
                                                            diameter, angle, num, max_area_point,
                                                            shared_dict, materialDepth, tabHigh, tabNum, tabLength,
                                                            tiltAngle] for num in range(processes_num)])
                        for i in range(processes_num):
                            toolpaths.append(shared_dict[i])
                s1 = time.time()
                logging.debug(f'pocket_end time: {s1} use time: {s1 - s}')
                # 将刀路点云转为gcode

                toolPath.write_zig_gcode_file(3, 3, feed, plungeFeed, spindleSpeed, toolpaths, toolNum, startFlag=True,
                                              endFlag=True)
            # 是否需要二次精加工
            if detailFlag:
                surface = toolPath.STLSurfaceSource(save_path)
                if toolType == "endmill":
                    cutter = ocl.CylCutter(diameter, 10)  # 平底刀
                elif toolType == "ball":
                    cutter = ocl.BallCutter(diameter, 10)  # 球刀
                elif toolType == "cone":
                    cutter = ocl.ConeCutter(diameter, angle, 10)  # 锥形刀
                t1 = time.time()
                try:
                    allPath, maxPath = stl_scale.scalePocket(all_scale, max_area_point, save_path)
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                t2 = time.time()
                print("scalePocket", t2 - t1)
                topValue = -999
                for j in allPath:
                    if j[1][0] > topValue:
                        topValue = j[1][0]
                topValue += 0.1
                if topValue < 0:
                    print("faceCut", topValue)
                    try:
                        allToolPath = path_algorithm.faceCut(allPath[maxPath][0], topValue, zPer, tiltAngle, diameter,
                                                             stepOver)
                        (raw_toolpath, n_raw) = toolPath.adaptive_path_drop_cutter(surface, cutter, allToolPath)
                        (toolpaths, n_filtered) = toolPath.filterCLPaths(raw_toolpath, tolerance=0.001)
                        toolPath.write_zig_gcode_file(3, 3, feed, plungeFeed, spindleSpeed, toolpaths, toolNum,
                                                      startFlag=True,
                                                      endFlag=False)
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                if toolType == "endmill":
                    cutter = ocl.CylCutter(diameter + diameter * 0.05, 10)  # 平底刀
                elif toolType == "ball":
                    cutter = ocl.BallCutter(diameter + diameter * 0.05, 10)  # 球刀
                elif toolType == "cone":
                    cutter = ocl.ConeCutter(diameter + diameter * 0.05, angle, 10)  # 锥形刀
                # 粗加工
                try:
                    allToolPath = path_algorithm.pocket(allPath, maxPath, diameter, zPer, tiltAngle, zDepth, stepOver,
                                                        tabHigh, tabNum, tabLength, materialDepth, topValue)
                    # 生成gcode
                    for j in range(len(allToolPath)):
                        (raw_toolpath, n_raw) = toolPath.adaptive_path_drop_cutter(surface, cutter, allToolPath[j])
                        (toolpaths, n_filtered) = toolPath.filterCLPaths(raw_toolpath, tolerance=0.001)
                        if topValue == 0 and j == 0:
                            startFlag = True
                        else:
                            startFlag = False
                        # print(111, toolpaths)
                        toolPath.write_zig_gcode_file(3, 3, feed, plungeFeed, spindleSpeed, toolpaths, toolNum,
                                                      startFlag=startFlag,
                                                      endFlag=False)
                except Exception as e:
                    print(e)
                    traceback.print_exc()

                if toolType == "endmill":
                    cutter = ocl.CylCutter(diameter * 0.95, 10)  # 平底刀
                elif toolType == "ball":
                    cutter = ocl.BallCutter(diameter * 0.95, 10)  # 球刀
                elif toolType == "cone":
                    cutter = ocl.ConeCutter(diameter * 0.95, angle, 10)  # 锥形刀
                try:
                    # 二次精加工
                    allToolPath = path_algorithm.detailPocketPlus(allPath, diameter, zPer, tiltAngle, zDepth, maxPath,
                                                                  topValue, materialDepth, tabHigh, tabNum, tabLength)
                    # 生成gcode
                    for j in range(len(allToolPath)):
                        # print(222)
                        (raw_toolpath, n_raw) = toolPath.adaptive_path_drop_cutter(surface, cutter, allToolPath[j])
                        (toolpaths, n_filtered) = toolPath.filterCLPaths(raw_toolpath, tolerance=0.001)
                        # print(222, toolpaths)
                        if not toolpaths:
                            continue
                        # 将有避让的刀路删除
                        z = round(toolpaths[0][1].z, 3)
                        zFlag = False
                        for path in toolpaths:
                            for p in path[1:]:
                                pz = round(p.z, 3)
                                if abs(pz - z) > 0.1 and abs(pz - z) != tabHigh:
                                    zFlag = True
                                    continue
                            if zFlag:
                                continue
                        if zFlag:
                            continue
                        if j == len(allToolPath) - 1:
                            endFlag = True
                        else:
                            endFlag = False
                        toolPath.write_zig_gcode_file(3, 3, feed * 0.5, plungeFeed, spindleSpeed, toolpaths, toolNum,
                                                      startFlag=False,
                                                      endFlag=endFlag)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
            s2 = time.time()
            logging.debug(f'pocketDetail_end time: {s2} use time: {s2 - s}')
            # 保存文件
            send_path = os.path.join(os.getcwd(), '../file/test.nc')
            # 返回gcode文件
            return send_file(send_path, as_attachment=True)

        # 如果没有文件上传，返回错误
        return {'message': 'No file uploaded'}, 400



def tool_layer(processes_num, z_depth, z_per, step_over, save_path, tool_type, diameter, angle, num, max_area_point,
               shared_dict, material_depth, prop_depth, tabNum, tabLength, tiltAngle):
    if tool_type == "endmill":
        cutter = ocl.CylCutter(diameter + 0.1, 10)  # 平底刀
    elif tool_type == "ball":
        cutter = ocl.BallCutter(diameter + 0.1, 10)  # 球刀
    elif tool_type == "cone":
        cutter = ocl.ConeCutter(diameter + 0.1, angle, 10)  # 锥形刀
    surface = toolPath.STLSurfaceSource(save_path)
    layer = abs(z_depth / z_per)
    num_items = math.ceil(layer)
    distribution = distribute_evenly(num_items, processes_num)
    all_layer_num = 0
    for i in range(num):
        all_layer_num += distribution[i]
    start_depth = all_layer_num * z_per
    # print(num, distribution[num], start_depth)
    logging.debug(f"time: {time.time()}, num: {num}, per: {distribution[num]}, start_depth: {start_depth}")
    layer_paths = path_algorithm.OffsetPath_process(max_area_point, diameter, z_depth, z_per, step_over, start_depth,
                                                    distribution[num], material_depth, prop_depth, tabNum, tabLength,
                                                    tiltAngle)  # 轮廓内部切割路径
    (raw_toolpath, n_raw) = adaptive_path_drop_cutter(surface, cutter, layer_paths)
    (toolpaths, n_filtered) = filterCLPaths(raw_toolpath, tolerance=0.001)
    toolpaths_list = []
    # print(num)
    first = True
    # 设置抬刀
    for path in toolpaths:
        if len(path) == 0:
            continue
        if first:
            first_pt = path[0]
            toolpaths_list.append([3])
            toolpaths_list.append((first_pt.x, first_pt.y))
            toolpaths_list.append([first_pt.z])
            # first = False
        for p in path[1:]:
            toolpaths_list.append((p.x, p.y, p.z))
            # toolpaths_list.append({"x": first_pt.x, "y": first_pt.y, "z": first_pt.z})
    shared_dict[num] = toolpaths_list



"""
平行偏移路径（多进程）从外到内
polygon:描述初始区域的多边形顶点，表示要加工的封闭区域。
step_over:每次偏移的距离（通常小于刀具直径），控制路径的密集程度
"""


def OffsetPath_process(polygon, diameter, z_depth, z_per, step_over, start_depth, layer, material_depth, prop_depth,
                       tabNum, tabLength, tiltAngle):
    cap_style = 2  # 1 (round), 2 (flat), 3 (square)
    join_style = 2  # 1 (round), 2 (mitre), and 3 (bevel)
    mitre_limit = 5  # 默认是 5

    original_polygon = sg.Polygon(polygon)  # 输入多边形
    cut_polygon = original_polygon.buffer(diameter * 0.5 + 0.1, resolution=64, cap_style=cap_style,
                                          join_style=join_style, mitre_limit=mitre_limit)
    paths = []
    slant_points = []
    # 计算斜线下刀需要底边长度
    slant_length = z_per / math.tan(math.radians(tiltAngle))
    for j in range(1, layer + 1):
        zValue = 0
        slantFlag = True
        first_path = True
        first_zplus = False
        prop_flag = False  # 是否避让中
        flag = True

        current_polygon = cut_polygon
        z = -start_depth - j * z_per  # 当前z轴
        if z < z_depth:
            zValue = abs(z_depth - (z + z_per))
            if zValue < 0.1:
                slantFlag = False
            z = z_depth
        try:
            while not current_polygon.is_empty and current_polygon.area > 0:
                # 如果是 MultiPolygon，遍历每个 Polygon
                if isinstance(current_polygon, sg.MultiPolygon):
                    polygons = list(current_polygon.geoms)
                else:
                    polygons = [current_polygon]
                for poly in polygons:
                    if poly.is_empty or poly.area <= 0:
                        continue
                    # 创建刀路组
                    path = ocl.Path()
                    coords = list(poly.exterior.coords)  # 提取外边界点
                    # 添加支撑点云
                    if flag and tabNum != 0:
                        # 添加支撑点云
                        coords = pointRound(coords)
                        coords = remove_repeat(coords)
                        coords = get_prop_points(coords, tabLength, tabNum)
                        # print(coords)
                        flag = False
                    # 将点云转成2位数据
                    all_points = []
                    for points in coords:
                        if len(points) == 2:
                            all_points.append(points)
                        elif len(points) == 3:
                            all_points.append((points[0], points[1]))
                    # 将外轮廓点云组成一个多边形封闭曲线进行处理
                    polygon = sg.Polygon(all_points)
                    # 获取多边形的边界
                    boundary = polygon.boundary
                    length = boundary.length
                    slantPercentage = slant_length / length
                    if slantPercentage >= 1:
                        slantPercentage = 0.5
                    # 循环判断点云中的点
                    for i in range(len(coords) - 1):  # 创建线段
                        # 第一圈切外边
                        if first_path and slantFlag:
                            point = Point(coords[i][0], coords[i][1])
                            # 计算该点在周长上的位置
                            projected_length = boundary.project(point)  # 点在周长上的投影长度
                            percentage = projected_length / length  # 计算百分比
                            # 点位超过斜坡时
                            if percentage > slantPercentage:
                                # 如果第一次超过，开始画斜线刀路
                                if not first_zplus:
                                    # print(coords[i])
                                    first_zplus = True
                                    slant_points = []
                                    # 斜坡点位拆为50个点
                                    for k in range(0, 50):
                                        # 根据百分比截取线段，获取截断除的点
                                        x1, y1 = boundary.interpolate(slantPercentage / 50 * k,
                                                                      normalized=True).coords[0]
                                        slant_points.append([x1, y1])
                                        x2, y2 = boundary.interpolate(slantPercentage / 50 * (k + 1),
                                                                      normalized=True).coords[
                                            0]
                                        if zValue != 0:
                                            slant_zPer = zValue
                                        else:
                                            slant_zPer = z_per
                                        slantZStart = z + slant_zPer / 50 * (50 - k)
                                        slantZEnd = z + slant_zPer / 50 * (50 - (k + 1))
                                        p1 = ocl.Point(x1, y1, slantZStart)
                                        p2 = ocl.Point(x2, y2, slantZEnd)
                                        l = ocl.Line(p1, p2)
                                        path.append(l)

                                    # 斜坡绘制完后连接斜坡结束与普通刀路开始
                                    p1 = ocl.Point(x2, y2, slantZEnd)
                                    p2 = ocl.Point(coords[i][0], coords[i][1], slantZEnd)
                                    l = ocl.Line(p1, p2)
                                    path.append(l)
                                    # 如果超过支撑长度的点刚好是支撑抬刀，进行抬刀
                                    if len(coords[i]) == 3 and z <= material_depth + prop_depth:
                                        # 抬刀
                                        prop_flag = True
                                        p1 = ocl.Point(coords[i][0], coords[i][1], z)
                                        p2 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                        l = ocl.Line(p1, p2)
                                        path.append(l)
                                else:
                                    # 后续长度超过斜坡，开始普通刀路
                                    if len(coords[i]) == 3 and z <= material_depth + prop_depth:
                                        # 下刀
                                        if coords[i][2] == 0:
                                            p1 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                            p2 = ocl.Point(coords[i][0], coords[i][1], z)
                                            l = ocl.Line(p1, p2)
                                            path.append(l)
                                            prop_flag = False
                                        else:
                                            # 抬刀
                                            prop_flag = True
                                            p1 = ocl.Point(coords[i][0], coords[i][1], z)
                                            p2 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                            l = ocl.Line(p1, p2)
                                            path.append(l)
                                    else:
                                        # 是否正在抬刀
                                        if prop_flag:
                                            p1 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                            p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1],
                                                           material_depth + prop_depth)
                                            l = ocl.Line(p1, p2)
                                            path.append(l)
                                        else:
                                            p1 = ocl.Point(coords[i][0], coords[i][1], z)
                                            p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1], z)
                                            l = ocl.Line(p1, p2)
                                            path.append(l)
                        else:
                            # 不是第一圈，开始普通刀路
                            if len(coords[i]) == 3 and z <= material_depth + prop_depth:
                                # 下刀
                                if coords[i][2] == 0:
                                    p1 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                    p2 = ocl.Point(coords[i][0], coords[i][1], z)
                                    l = ocl.Line(p1, p2)
                                    path.append(l)
                                    prop_flag = False
                                else:
                                    # 抬刀
                                    prop_flag = True
                                    p1 = ocl.Point(coords[i][0], coords[i][1], z)
                                    p2 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                    l = ocl.Line(p1, p2)
                                    path.append(l)
                            else:
                                # 是否正在抬刀
                                if prop_flag:
                                    p1 = ocl.Point(coords[i][0], coords[i][1], material_depth + prop_depth)
                                    p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1],
                                                   material_depth + prop_depth)
                                    l = ocl.Line(p1, p2)
                                    path.append(l)
                                else:
                                    p1 = ocl.Point(coords[i][0], coords[i][1], z)
                                    p2 = ocl.Point(coords[i + 1][0], coords[i + 1][1], z)
                                    l = ocl.Line(p1, p2)
                                    path.append(l)
                    if first_path and z == z_depth and slantFlag:
                        for i in range(len(slant_points) - 1):  # 创建线段
                            p1 = ocl.Point(slant_points[i][0], slant_points[i][1], z)
                            p2 = ocl.Point(slant_points[i + 1][0], slant_points[i + 1][1], z)
                            l = ocl.Line(p1, p2)
                            path.append(l)
                    first_path = False
                    paths.append(path)
                # 偏移当前多边形
                current_polygon = current_polygon.buffer(-step_over, resolution=16)
        except Exception as e:
            print(f"Error: {e}")
    return paths
