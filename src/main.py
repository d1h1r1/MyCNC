import threading
import time
from multiprocessing import Process, Value, Array
from src import camvtk
import read_gcode


class draw:
    def __init__(self, arr):
        self.flag = False
        self.num = 0
        self.arc_actors = None
        self.line_actors = None
        self.myscreen = None
        self.arr = arr

    def run(self):

        def change_color(obj, event):
            if self.arr[0]:
                print(self.num)
                self.line_actors.update_line_color(self.num, (255, 0, 0))
                self.num += 1
                self.myscreen.iren.Render()
                self.arr[0] = 0

        self.myscreen = camvtk.VTKScreen()
        line_points, arc_points = read_gcode.get_points("../file/master.nc")
        self.line_actors = camvtk.Lines(line_points)
        self.arc_actors = camvtk.Arcs(arc_points)

        self.myscreen.addActor(self.line_actors)
        self.myscreen.addActor(self.arc_actors)

        # 添加坐标系
        camvtk.drawArrows(self.myscreen)
        # 设置画面中心点
        self.myscreen.ren.ResetCamera()
        bounds = self.myscreen.ren.ComputeVisiblePropBounds()
        centerX = (bounds[0] + bounds[1]) / 2
        centerY = (bounds[2] + bounds[3]) / 2
        centerZ = (bounds[4] + bounds[5]) / 2
        self.myscreen.camera.SetFocalPoint(centerX, centerY, centerZ)

        # 设置相机位置可控制画面放缩
        distance = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
        self.myscreen.camera.SetPosition(centerX * 1.5, (centerY - distance * 1.5) * 1.5,
                                         (centerZ + distance / 2) * 1.5)  # 开始渲染

        # def change_color_callback(obj, event):
        #     threading.Thread(target=change_color, args=()).start()

        # 设置一个计时器来触发颜色更改
        # self.myscreen.iren.AddObserver('TimerEvent', change_color)
        # timer_id = self.myscreen.iren.CreateRepeatingTimer(1)  # 每隔1ms触发一次
        # myscreen.iren.AddObserver('KeyPressEvent', change_color_callback)
        # threading.Thread(target=change_color, args=()).start()
        # def trigger_custom_event():
        # self.myscreen.iren.InvokeEvent("CustomEvent")

        # 鼠标移动的时候调用，这个回调函数
        # self.myscreen.iren.AddObserver('ProgressEvent', change_color)

        self.myscreen.iren.Start()


if __name__ == "__main__":
    arr = Array('i', range(1))
    print(arr)
    obj = draw(arr)
    # threading.Thread(target=obj.run, args=()).start()
    Process(target=obj.run, args=()).start()
    # Process(target=func, args=(obj,)).start()
    # while True:
    #     arr[0] = 1
        # time.sleep(1)
    # obj.flag = True
