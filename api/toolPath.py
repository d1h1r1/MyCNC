import time
import vtk
from opencamlib import ocl
import camvtk
import path_algorithm


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
