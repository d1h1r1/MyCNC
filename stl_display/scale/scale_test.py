import time
from multiprocessing import freeze_support

import numpy as np
from matplotlib import pyplot as plt

import stl_scale
import stl_scale_layer
import stl_scale_array
import stl_scale_array1
import test1


if __name__ == "__main__":
    freeze_support()
    # import shapely
    #
    # print(shapely.__version__)

    t1 = time.time()
    max_points, all_scale, detailFlag = stl_scale.get_scale("../../file/配合25凸.stl", -10)
    # print(all_scale)
    # all_scale = stl_scale_layer.get_scale("../../file/配合25凸.stl", -10)
    # z_values, all_scale = stl_scale_array1.get_scale("../../file/配合25凸.stl", -10)
    print(all_scale)
    # plot_2d_slices(all_scale)
    # plot_3d_stacked(all_contours)
    t2 = time.time()
    # print(all_scale)
    print("allTime", t2-t1)
