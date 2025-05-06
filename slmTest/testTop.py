import shapely.geometry as sg
import pyslm.visualise
from matplotlib import pyplot as plt


def get_scale(path):
    solidPart = pyslm.Part('stl')
    solidPart.setGeometry(path)
    all_scale = {}
    max_area = 0
    max_points = []
    max_num = 0
    geomSlice = solidPart.getVectorSlice(-1)
    a = solidPart.getProjectedHull()
    print(a)
    for i in a:
        x_coords, y_coords = i[0], i[1]
        plt.plot(x_coords, y_coords, '-o', markersize=1, label='Points Path')
    plt.show()
    # print(geomSlice)


get_scale("../file/灵巧手末端.STL")

# test_all_scale()
