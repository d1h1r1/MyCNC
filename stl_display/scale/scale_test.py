import time
from multiprocessing import freeze_support
import stl_scale_array
import stl_scale

if __name__ == "__main__":
    freeze_support()
    t1 = time.time()
    max_points, all_scale, detailFlag = stl_scale.get_scale("../../file/配合25凸.stl", -10)
    # print(all_scale)
    # all_scale = stl_scale_layer.get_scale("../../file/配合25凸.stl", -10)
    # z_values, all_scale = stl_scale_array1.get_scale("../../file/配合25凸.stl", -10)
    print(all_scale)
    t2 = time.time()
    print("allTime", t2-t1)
