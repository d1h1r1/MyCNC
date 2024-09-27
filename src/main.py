import threading
import time

from src import camvtk
import read_gcode


def test_gcode():
    i = [0]

    def change_color():
        i[0] += 1
        print(i[0])
        line_actors.update_line_color(i[0], (255, 0, 0))
        myscreen.iren.Render()

    # 创建渲染器、渲染窗口和交互器
    myscreen = camvtk.VTKScreen()
    line_points, arc_points = read_gcode.get_points("../file/elephant.nc")
    line_actors = camvtk.Lines(line_points)
    arc_actors = camvtk.Arcs(arc_points)
    myscreen.addActor(line_actors)
    myscreen.addActor(arc_actors)

    # 添加坐标系
    camvtk.drawArrows(myscreen)
    # 设置画面中心点
    myscreen.ren.ResetCamera()
    bounds = myscreen.ren.ComputeVisiblePropBounds()
    centerX = (bounds[0] + bounds[1]) / 2
    centerY = (bounds[2] + bounds[3]) / 2
    centerZ = (bounds[4] + bounds[5]) / 2
    myscreen.camera.SetFocalPoint(centerX, centerY, centerZ)

    # 设置相机位置可控制画面放缩
    distance = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
    myscreen.camera.SetPosition(centerX * 1.5, (centerY - distance * 1.5) * 1.5, (centerZ + distance / 2) * 1.5)  # 开始渲染

    # def change_color_callback(obj, event):
    #     threading.Thread(target=change_color, args=()).start()

    # 设置一个计时器来触发颜色更改
    # myscreen.iren.AddObserver('TimerEvent', change_color_callback)
    # timer_id = myscreen.iren.CreateRepeatingTimer(1000)  # 每隔1秒触发一次
    # myscreen.iren.AddObserver('KeyPressEvent', change_color_callback)
    # threading.Thread(target=change_color, args=()).start()
    myscreen.iren.Start()


if __name__ == "__main__":
    threading.Thread(target=test_gcode, args=()).start()
