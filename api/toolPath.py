import time
import vtk
from opencamlib import ocl
from src import camvtk
import ngc_writer
from toolpath_examples import path_algorithm


class tool_path:
    def __init__(self, file):
        self.file = None
        self.tool_diameter = 3
        self.surface = None
        self.cutter = None

    def analyze_file(self):
        self.surface = STLSurfaceSource(self.file)

    def set_tool(self, type, *args):
        pass


# 自适应避让刀路
def adaptive_path_drop_cutter(surface, cutter, paths):
    apdc = ocl.AdaptivePathDropCutter()
    # apdc = ocl.AdaptiveWaterline()
    # apdc = ocl.PathDropCutter()
    # apdc.setZ(-1)
    apdc.setSTL(surface)
    apdc.setCutter(cutter)
    apdc.setSampling(0.04)  # 最大采样或“步进”距离
    # 防止丢失STL模型的任何细节，这个数应该与最小的三角形相似或更小
    apdc.setMinSampling(0.01)  # 最小采样或“步进”距离
    # 该算法细分了工具路径的“陡峭”部分
    # 直到我们达到这个极限。

    cl_paths = []
    n_points = 0
    # print(6666666666)
    for path in paths:
        apdc.setPath(path)
        apdc.run()
        cl_points = apdc.getCLPoints()
        n_points = n_points + len(cl_points)
        cl_paths.append(cl_points)
    # print(55555555555)
    # print(cl_paths, n_points)
    return cl_paths, n_points


# 这可以是任意三角形的源
# 只要它产生一个我们可以使用的ocl.STLSurf（）
def STLSurfaceSource(filename):
    stl = camvtk.STLSurf(filename)
    polydata = stl.src.GetOutput()
    # print(polydata)
    s = ocl.STLSurf()
    camvtk.vtkPolyData2OCLSTL(polydata, s)
    return s


# 筛选单个路径
def filter_path(path, tol):
    f = ocl.LineCLFilter()
    f.setTolerance(tol)
    for p in path:
        if p.z == 0:
            continue
        p2 = ocl.CLPoint(p.x, p.y, p.z)
        f.addCLPoint(p2)
    f.run()
    return f.getCLPoints()


# 为了减少g代码的大小，我们在这里进行过滤。（这不是严格要求的，可以省略）
# 如果有过滤器的话，我们可以在这里检测到G2/G3电弧。
# 想法:
# 如果原始工具路径中有三个点（p1,p2,p3）
# 和点p2在直线p1-p3的容差范围内
# 然后我们将路径简化为（p1,p3）
def filterCLPaths(cl_paths, tolerance=0.001):
    cl_filtered_paths = []
    t_before = time.time()
    n_filtered = 0
    for cl_path in cl_paths:
        cl_filtered = filter_path(cl_path, tolerance)
        n_filtered = n_filtered + len(cl_filtered)
        cl_filtered_paths.append(cl_filtered)
    return cl_filtered_paths, n_filtered


# 使用ngc_writer并将g代码写入标准输出或文件
def write_zig_gcode_file(filename, n_triangles, t1, n1, tol, t2, n2, toolpath):
    ngc_writer.clearance_height = 20  # 安全高度
    ngc_writer.feed_height = 3  # 进刀高度
    ngc_writer.feed = 600  # 进给速度
    ngc_writer.plunge_feed = 600  # z轴进给速度
    ngc_writer.metric = True  # 公尺/英尺 flag
    # ngc_writer.comment(" OpenCAMLib %s" % ocl.version())
    # ngc_writer.comment(" STL surface: %s" % filename)
    # ngc_writer.comment("   triangles: %d" % n_triangles)
    # ngc_writer.comment(" OpenCAMLib::AdaptivePathDropCutter run took %.2f s" % t1)
    # ngc_writer.comment(" got %d raw CL-points " % n1)
    # ngc_writer.comment(" filtering to tolerance %.4f " % (tol))
    # ngc_writer.comment(" got %d filtered CL-points. Filter done in %.3f s " % (n2, t2))
    # ngc_writer.preamble()
    first = True
    # print(toolpath)
    for path in toolpath:
        if len(path) == 0:
            continue
        try:
            if first:
                ngc_writer.pen_up()
                first_pt = path[0]
                ngc_writer.xy_rapid_to(first_pt.x, first_pt.y)
                ngc_writer.pen_down(first_pt.z)
                # first = False
            for p in path[1:]:
                ngc_writer.line_to(p.x, p.y, p.z)
        except Exception as e:
            print("write gcode", e)
    # ngc_writer.postamble()  # 结束


def gcode_file(toolpath):
    ngc_writer.clearance_height = 20  # 安全高度
    ngc_writer.feed_height = 3  # 进刀高度
    ngc_writer.feed = 600  # 进给速度
    ngc_writer.plunge_feed = 600  # z轴进给速度
    ngc_writer.metric = True  # 公尺/英尺 flag
    first = True
    for path in toolpath:
        try:
            if first:
                ngc_writer.pen_up()
                first_pt = path[0]
                ngc_writer.xy_rapid_to(first_pt[0], first_pt[1])
                ngc_writer.pen_down(first_pt[2])
                first = False
            for p in path[1:]:
                ngc_writer.line_to(p[0], p[1], p[2])
        except Exception as e:
            print("write gcode", e)


# 图像可视化
def vtk_visualize_parallel_finish_zig(stlfile, toolpaths):
    myscreen = camvtk.VTKScreen()
    stl = camvtk.STLSurf(stlfile)
    myscreen.addActor(stl)
    stl.SetSurface()
    stl.SetColor(camvtk.cyan)
    # myscreen.camera.SetPosition(15, 13, 7)
    # myscreen.camera.SetFocalPoint(5, 5, 0)

    rapid_height = 10  # 安全高度
    feed_height = 10   # 进给高度
    rapidColor = camvtk.pink
    XYrapidColor = camvtk.green
    plungeColor = camvtk.red
    feedColor = camvtk.yellow
    pos = ocl.Point(0, 0, 0)
    first = True
    for path in toolpaths:
        if len(path) == 0:
            continue
        try:
            first_pt = path[0]
            if first:  # 绿色球体表示开始位置
                myscreen.addActor(
                    camvtk.Sphere(center=(first_pt.x, first_pt.y, rapid_height), radius=1, color=camvtk.green))
                pos = ocl.Point(first_pt.x, first_pt.y,
                                first_pt.z)
                first = False
            # else:
                # 回到进给高度
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(first_pt.x, first_pt.y, rapid_height),
                                color=XYrapidColor))
                pos = ocl.Point(first_pt.x, first_pt.y, first_pt.z)

                # 回到进给高度
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(pos.x, pos.y, feed_height), color=rapidColor))
                # 下降到加工高度
                myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, pos.z), color=plungeColor))

            # 开始加工
            for p in path[1:]:
                myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(p.x, p.y, p.z), color=feedColor))
                pos = ocl.Point(p.x, p.y, p.z)
        except Exception as e:
            print("vtk", e)

    # 加工完成、回到安全高度
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
    myscreen.addActor(camvtk.Sphere(center=(pos.x, pos.y, rapid_height), radius=0.1, color=camvtk.red))

    camvtk.drawArrows(myscreen, center=(0, 0, 0))
    camvtk.drawOCLtext(myscreen)
    myscreen.render()
    myscreen.iren.Start()


def vtk_all(stlfile, toolpaths):
    myscreen = camvtk.VTKScreen()
    stl = camvtk.STLSurf(stlfile)
    myscreen.addActor(stl)
    stl.SetSurface()
    stl.SetColor(camvtk.cyan)
    # myscreen.camera.SetPosition(15, 13, 7)
    # myscreen.camera.SetFocalPoint(5, 5, 0)

    rapid_height = 10  # 安全高度
    feed_height = 10  # 进给高度
    rapidColor = camvtk.pink
    XYrapidColor = camvtk.green
    plungeColor = camvtk.red
    feedColor = camvtk.yellow
    pos = ocl.Point(0, 0, 0)
    first = True
    line_points = []
    for path in toolpaths:
        if len(path) == 0:
            continue
        try:
            first_pt = path[0]
            if first:  # 绿色球体表示开始位置
                myscreen.addActor(
                    camvtk.Sphere(center=(first_pt.x, first_pt.y, rapid_height), radius=1, color=camvtk.green))
                pos = ocl.Point(first_pt.x, first_pt.y,
                                first_pt.z)
                first = False
                # else:
                # 回到进给高度
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(first_pt.x, first_pt.y, rapid_height),
                                color=XYrapidColor))
                pos = ocl.Point(first_pt.x, first_pt.y, first_pt.z)

                # 回到进给高度
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(pos.x, pos.y, feed_height), color=rapidColor))
                # 下降到加工高度
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, pos.z), color=plungeColor))

            # 开始加工
            for p in path[1:]:
                line_points.append(((pos.x, pos.y, pos.z), (p.x, p.y, p.z)))
                pos = ocl.Point(p.x, p.y, p.z)
        except Exception as e:
            print("vtk", e)

    line_actors = camvtk.Lines(line_points)
    myscreen.addActor(line_actors)

    # 加工完成、回到安全高度
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
    myscreen.addActor(camvtk.Sphere(center=(pos.x, pos.y, rapid_height), radius=0.1, color=camvtk.red))

    camvtk.drawArrows(myscreen, center=(0, 0, 0))
    camvtk.drawOCLtext(myscreen)
    myscreen.render()
    myscreen.iren.Start()


def vtk_layer(stlfile, shared_list):
    myscreen = camvtk.VTKScreen()
    stl = camvtk.STLSurf(stlfile)
    myscreen.addActor(stl)
    stl.SetSurface()
    stl.SetColor(camvtk.cyan)
    rapid_height = 50  # 安全高度
    feed_height = 50  # 进给高度
    rapidColor = camvtk.pink
    XYrapidColor = camvtk.yellow
    plungeColor = camvtk.red
    feedColor = camvtk.green
    pos = ocl.Point(0, 0, 0)
    first = True
    line_points = []
    for path in shared_list:
        # try:
        first_pt = path[0]
        if first:  # 绿色球体表示开始位置
            myscreen.addActor(
                camvtk.Sphere(center=(first_pt[0], first_pt[1], rapid_height), radius=1, color=camvtk.green))
            pos = ocl.Point(first_pt[0], first_pt[1],
                            first_pt[2])
            first = False
            # else:
            # 回到进给高度
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(first_pt[0], first_pt[1], rapid_height),
                            color=XYrapidColor))
            pos = ocl.Point(first_pt[0], first_pt[1], first_pt[2])

            # 回到进给高度
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(pos.x, pos.y, feed_height), color=rapidColor))
            # 下降到加工高度
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, pos.z), color=plungeColor))

            # 开始加工
            for p in path[1:]:
                line_points.append(((pos.x, pos.y, pos.z), (p[0], p[1], p[2])))
                pos = ocl.Point(p[0], p[1], p[2])
        for p in path:
            line_points.append(((pos.x, pos.y, pos.z), (p[0], p[1], p[2])))
            pos = ocl.Point(p[0], p[1], p[2])
    # except Exception as e:
    #     print("vtk", e)

    line_actors = camvtk.Lines(line_points)
    myscreen.addActor(line_actors)

    # 加工完成、回到安全高度
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
    myscreen.addActor(camvtk.Sphere(center=(pos.x, pos.y, rapid_height), radius=0.1, color=camvtk.red))

    camvtk.drawArrows(myscreen, center=(0, 0, 0))
    camvtk.drawOCLtext(myscreen)
    myscreen.render()
    myscreen.iren.Start()


def tool_threading(radius, shared_dict):
    # stlfile = "../file/coin_half.stl"
    diameter = 3
    length = 50
    simplify_file = 'simplified_model.stl'
    surface = STLSurfaceSource(simplify_file)
    cutter = ocl.CylCutter(diameter, length)          # 平底刀
    # radius = 1
    paths = path_algorithm.SpiralPath(0, 0, -3, radius, 1)  # 螺旋路径1，从内到外
    (raw_toolpath, n_raw) = adaptive_path_drop_cutter(surface, cutter, paths)
    (toolpaths, n_filtered) = filterCLPaths(raw_toolpath, tolerance=0.001)
    toolpaths_list = []
    print(radius)
    for path in toolpaths:
        if len(path) == 0:
            continue
        for first_pt in path:
            toolpaths_list.append((first_pt.x, first_pt.y, first_pt.z))
            # toolpaths_list.append({"x": first_pt.x, "y": first_pt.y, "z": first_pt.z})
    shared_dict[radius] = toolpaths_list


def tool_layer(radius, num, processes_num, shared_dict):
    # stlfile = "../file/coin_half.stl"
    diameter = 1.5
    length = 8
    simplify_file = 'simplified_model.stl'
    surface = STLSurfaceSource(simplify_file)
    # angle = math.pi / 6
    # cutter = ocl.ConeCutter(diameter, angle, length)  # 锥形刀
    cutter = ocl.CylCutter(diameter, length)          # 平底刀

    min_radius = radius * ((num - 1) / processes_num)
    max_radius = radius * (num / processes_num)
    # print("num1", ((num - 1) / processes_num))
    # print("num2", (num / processes_num))
    # print("min_radius", min_radius)
    # print("max_radius", max_radius)
    paths = path_algorithm.SpiralPathPart(0, 0, -10, min_radius, max_radius, 0.5, 1)  # 螺旋路径1，从内到外
    (raw_toolpath, n_raw) = adaptive_path_drop_cutter(surface, cutter, paths)
    (toolpaths, n_filtered) = filterCLPaths(raw_toolpath, tolerance=0.001)
    toolpaths_list = []
    # print(num)
    for path in toolpaths:
        if len(path) == 0:
            continue
        for first_pt in path:
            toolpaths_list.append((first_pt.x, first_pt.y, first_pt.z))
            # toolpaths_list.append({"x": first_pt.x, "y": first_pt.y, "z": first_pt.z})
    shared_dict[num] = toolpaths_list
    # print(shared_dict)


def simplify_stl_quadratic(input_file, output_file, target_reduction=0.5):
    # 读取 STL 文件
    reader = vtk.vtkSTLReader()
    reader.SetFileName(input_file)
    reader.Update()

    # 获取输入的 polydata
    polydata = reader.GetOutput()

    # 创建 vtkQuadricDecimation 对象来进行简化
    decimator = vtk.vtkQuadricDecimation()
    decimator.SetInputData(polydata)
    decimator.SetTargetReduction(target_reduction)  # 设置简化目标：0.5表示减少50%面数
    decimator.Update()

    # 获取简化后的 polydata
    simplified_polydata = decimator.GetOutput()

    # 使用 STL writer 将简化后的数据保存为 STL 文件
    writer = vtk.vtkSTLWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(simplified_polydata)
    writer.Write()


def get_tool_path(stlfile):

    center_x = 0
    center_y = 0
    z_depth = -10
    layer = 1
    step_over = 1
    diameter = 3
    length = 8
    max_radius = 75
    # 示例：简化 STL 文件
    simplify_file = 'file/simplified_model.stl'
    simplify_stl_quadratic(stlfile, simplify_file, target_reduction=0.1)
    surface = STLSurfaceSource(simplify_file)
    cutter = ocl.CylCutter(diameter, length)  # 平底刀
    paths = path_algorithm.SpiralPathOut(center_x, center_y, z_depth, max_radius, step_over, layer)  # 螺旋路径1，从内到外

    (raw_toolpath, n_raw) = adaptive_path_drop_cutter(surface, cutter, paths)
    (toolpaths, n_filtered) = filterCLPaths(raw_toolpath, tolerance=0.001)
    path_list = []
    for path in toolpaths:
        if len(path) == 0:
            continue
        for p in path:
            # print(p.x, p.y, p.z)
            path_list.append([p.x, p.y, p.z])
    return path_list


if __name__ == "__main__":
    stlfile = "../file/Throwing.stl"
    path_list = get_tool_path(stlfile)
    print(path_list)
