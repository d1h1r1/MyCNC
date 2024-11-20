# simple parallel finish toolpath example
# Anders Wallin 2014-02-23

import time

from opencamlib import ocl, camvtk
import ngc_writer  # G-code output is produced by this module
import math
import shapely.affinity as sa
import shapely.geometry as sg
from shapely.affinity import scale


# 创建一个简单的“Zig”图案，我们只在一个方向上切割。
# 第一行在ymin
# 最后一行是ymax
def YdirectionZigPath(xmin, xmax, ymin, ymax, Ny):
    paths = []
    dy = float(ymax - ymin) / (Ny - 1)  # the y step-over
    for n in range(0, Ny):
        path = ocl.Path()
        y = ymin + n * dy  # current y-coordinate
        if n == Ny - 1:
            assert (y == ymax)
        elif n == 0:
            assert (y == ymin)
        p1 = ocl.Point(xmin, y, 0)  # start-point of line
        p2 = ocl.Point(xmax, y, 0)  # end-point of line
        l = ocl.Line(p1, p2)  # line-object
        path.append(l)  # add the line to the path
        paths.append(path)
    return paths


# 双向锯齿
def YdirectionAlternatingZigPath(xmin, xmax, ymin, ymax, Ny):
    paths = []
    dy = float(ymax - ymin) / (Ny - 1)  # y 步长
    for n in range(0, Ny):
        path = ocl.Path()
        y = ymin + n * dy  # 当前 y 坐标
        if (n == Ny - 1):
            assert (y == ymax)
        elif (n == 0):
            assert (y == ymin)
        p1 = ocl.Point(xmin, y, 0)  # 起始点
        p2 = ocl.Point(xmax, y, 0)  # 结束点

        if n % 2 == 0:  # 偶数行从左到右
            l = ocl.Line(p1, p2)
        else:  # 奇数行从右到左
            l = ocl.Line(p2, p1)

        path.append(l)
        paths.append(path)
    return paths


"""
螺旋路径1
这种路径适用于需要处理圆形区域的情况，像是孔的加工或者从外向内的轮廓铣削。
turns: 螺旋的圈数。
segments: 每圈的分段数，总分段数为 turns * segments。
从内到外
"""


def spiralPath(xmin, xmax, ymin, ymax, turns, segments):
    center_x = (xmin + xmax) / 2
    center_y = (ymin + ymax) / 2
    max_radius = min((xmax - xmin) / 2, (ymax - ymin) / 2)
    total_segments = turns * segments
    angle_step = 2 * math.pi / segments  # 每个分段的角度增量
    radius_step = max_radius / total_segments  # 每个分段的半径增量
    paths = []  # 存储路径点
    for i in range(total_segments):
        path = ocl.Path()
        angle = i * angle_step  # 当前角度
        radius = i * radius_step  # 当前半径
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        p = ocl.Point(x, y)
        if i > 0:  # 从第二个点开始创建线段
            l = ocl.Line(prev_p, p)
            path.append(l)
        prev_p = p
        paths.append(path)
    return paths


"""
螺旋路径2
center_x:螺旋路径的中心 X 坐标
center_y:螺旋路径的中心 Y 坐标。
radius:螺旋的最大半径，定义路径的覆盖范围。
z_depth:刀具的切削深度（Z 轴位置）。
num_turns:螺旋的圈数，即路径从外到内的次数。
step_over:刀具每圈之间的间隔，用于控制路径密度（通常小于刀具直径）。
从外到内
"""


def SpiralPath(center_x, center_y, radius, z_depth, num_turns, step_over):
    paths = []
    theta_step = 2 * math.pi / 100  # 控制圆滑度（100 步每圈）
    for turn in range(num_turns):
        path = ocl.Path()
        for i in range(101):  # 101 点构成一圈
            theta = i * theta_step + turn * 2 * math.pi
            r = radius - turn * step_over  # 半径逐渐减小
            if r <= 0:  # 超出半径范围
                break
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            z = z_depth
            p = ocl.Point(x, y, z)
            if i > 0:  # 从第二个点开始创建线段
                l = ocl.Line(prev_p, p)
                path.append(l)
            prev_p = p
        paths.append(path)
    return paths


"""
从中心开始的螺旋路径
"""


def spiralOutPath(xmin, xmax, ymin, ymax, layers):
    paths = []
    center_x = (xmin + xmax) / 2
    center_y = (ymin + ymax) / 2
    radius_step = min(xmax - xmin, ymax - ymin) / (2 * layers)
    for i in range(layers):
        path = ocl.Path()
        radius = radius_step * (i + 1)
        # path = []
        for angle in range(0, 360, 5):  # 每 5 度
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            p = ocl.Point(x, y, 0)
            if i > 0:  # 从第二个点开始创建线段
                l = ocl.Line(prev_p, p)
                path.append(l)
            prev_p = p
        paths.append(path)
    return paths


"""
平行偏移路径
polygon:描述初始区域的多边形顶点，表示要加工的封闭区域。
step_over:每次偏移的距离（通常小于刀具直径），控制路径的密集程度
"""


def OffsetPath(polygon, step_over):
    original_polygon = sg.Polygon(polygon)  # 输入多边形
    paths = []
    current_polygon = original_polygon
    while not current_polygon.is_empty and current_polygon.area > 0:
        path = ocl.Path()
        coords = list(current_polygon.exterior.coords)  # 提取当前多边形外边界点
        for i in range(len(coords) - 1):  # 创建线段
            p1 = ocl.Point(*coords[i], 0)
            p2 = ocl.Point(*coords[i + 1], 0)
            l = ocl.Line(p1, p2)
            path.append(l)
        paths.append(path)
        # 偏移当前多边形
        current_polygon = current_polygon.buffer(-step_over, resolution=16)
    return paths


"""
曲线跟随
curve_points: 曲线点列表（例如从矢量文件中读取）。
z_depth: 切削深度。
"""


def ContourPath(curve_points, z_depth):
    path = ocl.Path()
    for i in range(len(curve_points) - 1):
        p1 = ocl.Point(*curve_points[i], z_depth)
        p2 = ocl.Point(*curve_points[i + 1], z_depth)
        l = ocl.Line(p1, p2)
        path.append(l)
    return [path]


"""
混合路径 (Adaptive Clearing)
自适应清除路径会智能调整切削区域，保持恒定刀具负载，适合高效粗加工。

实现思路： 自适应路径需要不断计算刀具干涉和剩余材料区域，以下是一个简化版思路：

初始化加工区域为一个多边形。
刀具按固定步进（步距和深度）逐步侵入区域。
通过布尔运算计算剩余未加工区域。
根据未加工区域继续生成路径。

initial_region:初始加工区域，定义要清除的几何形状。
tool_diameter:刀具直径，用于计算路径与材料的干涉和刀具负载。
step_over:刀具之间的侧向重叠距离，影响路径密度。
max_depth:最大切削深度，用于控制单次加工的材料移除量。
"""


def AdaptivePath(initial_region, tool_diameter, step_over, max_depth):
    def generate_one_pass(region, tool_diameter, step_over, max_depth):
        # 确定步距：根据刀具直径和步进比例
        step_distance = tool_diameter * step_over
        current_region = region

        # 定义路径存储
        pass_path = []

        # 在区域内生成步进切割路径
        while current_region.area > 1:
            print(1, current_region.area)
            # 获取区域的边界
            boundary = current_region.exterior
            # 缩小区域以模拟刀具轨迹
            offset_region = sa.scale(boundary, xfact=(1 - step_over), yfact=(1 - step_over))
            # 更新路径
            # print(offset_region.area)
            pass_path.append(offset_region)
            # 减去切割过的部分
            current_region = sg.Polygon(offset_region)
            print(2, current_region.area)

        return pass_path

    def calculate_remaining_area(region, path, tool_diameter):
        # 将路径转换为多边形刀具区域
        tool_path = sg.Polygon(path)

        # 缩小刀具区域以模拟实际切割效果
        cut_area = tool_path.buffer(tool_diameter / 2.0)

        # 从当前区域中减去切割区域
        remaining_region = region.difference(cut_area)

        return remaining_region

    region = sg.Polygon(initial_region)
    paths = []
    # while region.area > 0:
    print(region.area)
    path = generate_one_pass(region, tool_diameter, step_over, max_depth)
    # paths.append(path)
    region = calculate_remaining_area(region, path, tool_diameter)
    print(region.area)
    # print(region.area)
    return paths


def pocket(region_points, step_over, max_depth):
    # 创建区域
    region = ocl.Path()
    for point in region_points:
        p1 = ocl.Point(point[0], 0)
        p2 = ocl.Point(point[1], 0)
        l = ocl.Line(p1, p2)
        region.append(l)

    # 创建 Pocket
    zigzag = ocl.ZigZag()
    zigzag.setOrigin(region)
    # zigzag.setBounds(xmin, xmax, ymin, ymax)
    zigzag.setStepover(step_over)
    zigzag.setZ(max_depth)

    # 生成路径
    paths = zigzag.getPaths()
    return paths


# run the actual drop-cutter algorithm
def adaptive_path_drop_cutter(surface, cutter, paths):
    apdc = ocl.AdaptivePathDropCutter()
    # apdc = ocl.AdaptiveWaterline()
    # apdc = ocl.PathDropCutter()
    # apdc.setZ(-1)
    apdc.setSTL(surface)
    apdc.setCutter(cutter)
    # apdc.setSampling(0.04)  # maximum sampling or "step-forward" distance
    # should be set so that we don't loose any detail of the STL model
    # i.e. this number should be similar or smaller than the smallest triangle
    # apdc.setMinSampling(0.01)  # minimum sampling or step-forward distance
    # the algorithm subdivides "steep" portions of the toolpath
    # until we reach this limit.
    # 0.0008
    cl_paths = []
    n_points = 0
    for path in paths:
        apdc.setPath(path)
        apdc.run()
        cl_points = apdc.getCLPoints()
        n_points = n_points + len(cl_points)
        cl_paths.append(cl_points)
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
        cl_filtered = filter_path(cl_path, tol)

        n_filtered = n_filtered + len(cl_filtered)
        cl_filtered_paths.append(cl_filtered)
    return (cl_filtered_paths, n_filtered)


# 使用ngc_writer并将g代码写入标准输出或文件
def write_zig_gcode_file(filename, n_triangles, t1, n1, tol, t2, n2, toolpath):
    ngc_writer.clearance_height = 5  # XY rapids at this height
    ngc_writer.feed_height = 3  # use z plunge-feed below this height
    ngc_writer.feed = 200  # feedrate
    ngc_writer.plunge_feed = 100  # plunge feedrate
    ngc_writer.metric = False  # metric/inch flag
    ngc_writer.comment(" OpenCAMLib %s" % ocl.version())  # git version-tag
    # it is probably useful to include this in all g-code output, so that bugs/problems can be tracked

    ngc_writer.comment(" STL surface: %s" % filename)
    ngc_writer.comment("   triangles: %d" % n_triangles)
    ngc_writer.comment(" OpenCAMLib::AdaptivePathDropCutter run took %.2f s" % t1)
    ngc_writer.comment(" got %d raw CL-points " % n1)
    ngc_writer.comment(" filtering to tolerance %.4f " % (tol))
    ngc_writer.comment(" got %d filtered CL-points. Filter done in %.3f s " % (n2, t2))
    ngc_writer.preamble()
    # a "Zig" or one-way parallel finish path
    # 1) lift to clearance height
    # 2) XY rapid to start of path
    # 3) plunge to correct z-depth
    # 4) feed along path until end 
    for path in toolpath:
        try:
            ngc_writer.pen_up()
            first_pt = path[0]
            ngc_writer.xy_rapid_to(first_pt.x, first_pt.y)
            ngc_writer.pen_down(first_pt.z)
            for p in path[1:]:
                ngc_writer.line_to(p.x, p.y, p.z)
        except:
            pass
    ngc_writer.postamble()  # end of program


# 图像可视化
def vtk_visualize_parallel_finish_zig(stlfile, toolpaths):
    myscreen = camvtk.VTKScreen()
    stl = camvtk.STLSurf(stlfile)
    myscreen.addActor(stl)
    stl.SetSurface()  # try also SetWireframe()
    stl.SetColor(camvtk.cyan)
    myscreen.camera.SetPosition(15, 13, 7)
    myscreen.camera.SetFocalPoint(5, 5, 0)

    rapid_height = 5  # XY rapids at this height
    feed_height = 3
    rapidColor = camvtk.pink
    XYrapidColor = camvtk.green
    plungeColor = camvtk.red
    feedColor = camvtk.yellow
    # zig path algorithm:
    # 1) lift to clearance height
    # 2) XY rapid to start of path
    # 3) plunge to correct z-depth
    # 4) feed along path until end
    pos = ocl.Point(0, 0, 0)  # keep track of the current position of the tool
    first = True
    for path in toolpaths:
        try:
            first_pt = path[0]
            if first:  # green sphere at path start
                myscreen.addActor(
                    camvtk.Sphere(center=(first_pt.x, first_pt.y, rapid_height), radius=0.1, color=camvtk.green))
                pos = ocl.Point(first_pt.x, first_pt.y,
                                first_pt.z)  # at start of program, assume we have already a rapid move here
                first = False
            else:  # not the very first move
                # retract up to rapid_height
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
                # XY rapid into position
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(first_pt.x, first_pt.y, rapid_height),
                                color=XYrapidColor))
                pos = ocl.Point(first_pt.x, first_pt.y, first_pt.z)

            # rapid down to the feed_height
            myscreen.addActor(
                camvtk.Line(p1=(pos.x, pos.y, rapid_height), p2=(pos.x, pos.y, feed_height), color=rapidColor))
            # feed down to CL
            myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, pos.z), color=plungeColor))

            # feed along the path
            for p in path[1:]:
                # print(p)
                myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(p.x, p.y, p.z), color=feedColor))
                pos = ocl.Point(p.x, p.y, p.z)
        except:
            pass

    # END retract up to rapid_height
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, pos.z), p2=(pos.x, pos.y, feed_height), color=plungeColor))
    myscreen.addActor(camvtk.Line(p1=(pos.x, pos.y, feed_height), p2=(pos.x, pos.y, rapid_height), color=rapidColor))
    myscreen.addActor(camvtk.Sphere(center=(pos.x, pos.y, rapid_height), radius=0.1, color=camvtk.red))

    camvtk.drawArrows(myscreen, center=(-0.5, -0.5, -0.5))  # XYZ coordinate arrows
    camvtk.drawOCLtext(myscreen)
    myscreen.render()
    myscreen.iren.Start()


if __name__ == "__main__":
    # stlfile = "guanyuplat.STL"
    stlfile = "elephant.stl"
    surface = STLSurfaceSource(stlfile)

    # choose a cutter for the operation:
    # http://www.anderswallin.net/2011/08/opencamlib-cutter-shapes/
    diameter = 3
    length = 20
    # cutter = ocl.BallCutter(diameter, length)
    cutter = ocl.CylCutter(diameter, length)
    # corner_radius = 0.05
    # cutter = ocl.BullCutter(diameter, corner_radius, length)
    # angle = math.pi/4
    # cutter = ocl.ConeCutter(diameter, angle, length)
    # cutter = cutter.offsetCutter( 0.4 )

    # toolpath is contained in this simple box
    ymin = 0
    ymax = 150
    xmin = 0
    xmax = 100
    Ny = 50  # number of lines in the y-direction

    paths = YdirectionZigPath(xmin, xmax, ymin, ymax, Ny)  # 单向锯齿
    # paths = YdirectionAlternatingZigPath(xmin, xmax, ymin, ymax, Ny)  # 双向锯齿
    # paths = spiralPath(xmin, xmax, ymin, ymax, 2, 20)  # 螺旋路径1，从内到外
    # paths = SpiralPath(50, 100, 50, 2, 10, 5)  # 螺旋路径2，从外向内
    # paths = OffsetPath([(40, 40), (60, 60), (61, 133), (50, 148), (37, 130)], 3)  # 平行偏移路径
    # paths = ContourPath([(45, 50), (60, 60), (61, 133), (50, 130), (45, 120), (45, 50)], 0)  # 曲线跟随
    # paths = AdaptivePath([(40, 40), (60, 60), (61, 133), (50, 148), (37, 130)], 3, 0.5, 1)  # 自适应混合路径
    # paths = spiralOutPath(xmin, xmax, ymin, ymax, 3)  # 从外向内

    # cutter_diameter = 3.0
    # step_over = 5.0
    # max_depth = 5.0
    # region_points = [
    #     (0.0, 0.0),
    #     (50.0, 0.0),
    #     (50.0, 50.0),
    #     (0.0, 50.0),
    # ]
    # paths = pocket(region_points, step_over, max_depth)

    # now project onto the STL surface
    t_before = time.time()

    (raw_toolpath, n_raw) = adaptive_path_drop_cutter(surface, cutter, paths)
    t1 = time.time()

    # filter raw toolpath to reduce size
    tol = 0.001
    (toolpaths, n_filtered) = filterCLPaths(raw_toolpath, tolerance=0.001)
    t2 = time.time() - t_before

    # output a g-code file
    write_zig_gcode_file(stlfile, surface.size(), t1, n_raw, tol, t2, n_filtered, toolpaths)
    # and/or visualize with VTK
    vtk_visualize_parallel_finish_zig(stlfile, toolpaths)
