import multiprocessing
import threading
import time
import pyslm.visualise
import shapely.geometry as sg


# z_depth = 10
# for i in range(abs(z_depth * 100)):
#     # 设置切片层位置
#     z = -0.01 * i
#     # 在Z方向切割物体并得到边界
#
#     geomSlice = solidPart.getVectorSlice(z)
#     for path in geomSlice:
#         point = []
#         for j in path:
#             point.append([j[0], j[1]])


def cut_layer_process(z, shared_dict):
    depth = -0.1 * z
    # print(depth)
    solidPart = pyslm.Part('Throwing')
    solidPart.setGeometry('../file/Throwing.stl')
    geomSlice = solidPart.getVectorSlice(depth)
    path_area = []
    for path in geomSlice:
        point = []
        for j in path:
            point.append([j[0], j[1]])
        polygon_area = sg.Polygon(point).area
        path_area.append([polygon_area, path])
    shared_dict[z] = path_area


# 导入部件并将几何形状设置为STL文件（frameGuide.stl）
solidPart = pyslm.Part('Throwing')
solidPart.setGeometry('../file/Throwing.stl')

max = 0
max_points = [0]


def cut_layer(z):
    global max
    geomSlice = solidPart.getVectorSlice(z)
    for path in geomSlice:
        point = []
        for j in path:
            point.append([j[0], j[1]])
        polygon_area = sg.Polygon(point).area
        if polygon_area > max:
            max = polygon_area
            max_points[0] = point
        # print(polygon_area)


t1 = time.time()
z_depth = 10
for i in range(abs(z_depth * 10)):
    # 设置切片层位置
    z = -0.1 * i
    # 在Z方向切割物体并得到边界
    cut_layer(z)
    # threading.Thread(target=cut_layer, args=(z,)).start()
print(max)
t2 = time.time()
print(t2 - t1)


# print(max)
# t2 = time.time()
# print(t2 - t1)

def processCode(z_depth):
    processes_num = 1
    toolpaths = []
    layer = int(abs(z_depth * 10))
    # 进程池
    with multiprocessing.Pool(processes=processes_num) as pool:
        with multiprocessing.Manager() as manager:
            # 共享字典数据
            shared_dict = manager.dict()
            # 生成刀路
            pool.starmap(cut_layer_process, [[num, shared_dict] for num in range(layer)])
            for i in range(layer):
                toolpaths.append(shared_dict[i])

    # print(toolpaths)

# 运行 Flask 应用
# if __name__ == '__main__':
# from multiprocessing import freeze_support
# freeze_support()  # 用于 PyInstaller 等工具打包多进程
# t1 = time.time()
# processCode(-10)
# t2 = time.time()
# print(t2 - t1)
