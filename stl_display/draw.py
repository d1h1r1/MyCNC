import vtk

from src import camvtk
from opencamlib import ocl
from svgpathtools import svg2paths, Arc, Line

svg_file = '../file/phone.svg'
paths, attributes = svg2paths(svg_file)

myscreen = camvtk.VTKScreen()
flag = False
pos = ocl.Point(0, 0, 0)
for path in paths:
    for segment in path:
        if isinstance(segment, Arc):
            print("arc", segment)
            if segment.sweep:
                if flag:
                    myscreen.addActor(
                        camvtk.Line(p1=(pos.x, pos.y, 0),
                                    p2=(segment.start.real, segment.start.imag, 0)))
                myscreen.addActor(
                    camvtk.Arc(center_offset=(segment.radius.real, segment.radius.imag, 0),
                               start_point=(segment.start.real, segment.start.imag, 0),
                               end_point=(segment.end.real, segment.end.imag, 0), color=(0, 1, 1),
                               clockwise=True))
                pos = ocl.Point(segment.end.real, segment.end.imag, 0)
            else:
                if flag:
                    myscreen.addActor(
                        camvtk.Line(p1=(pos.x, pos.y, 0),
                                    p2=(segment.start.real, segment.start.imag, 0)))
                myscreen.addActor(
                    camvtk.Arc(center_offset=(segment.radius.real, segment.radius.imag, 0),
                               start_point=(segment.start.real, segment.start.imag, 0),
                               end_point=(segment.end.real, segment.end.imag, 0), color=(0, 1, 1),
                               clockwise=False))
                pos = ocl.Point(segment.end.real, segment.end.imag, 0)
        elif isinstance(segment, Line):
            if flag:
                myscreen.addActor(
                    camvtk.Line(p1=(pos.x, pos.y, 0),
                                p2=(segment.start.real, segment.start.imag, 0)))
            myscreen.addActor(
                camvtk.Line(p1=(segment.start.real, segment.start.imag, 0), p2=(segment.end.real, segment.end.imag, 0)))
            pos = ocl.Point(segment.end.real, segment.end.imag, 0)
            print("line", segment)
            # continue
        else:
            continue
        flag = True
        # print(i.start)
        # start_points = np.array([[segment.start.real, segment.start.imag] for segment in path])
        # print(start_points)
        # end_points = np.array([[segment.end.real, segment.end.imag] for segment in path])
        # print(end_points)
        print("=================================================")

# 加工完成、回到安全高度
# myscreen.ren.GetActiveCamera().SetPosition(0, 0, 1)  # 正对屏幕
# myscreen.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)  # 聚焦原点
# myscreen.ren.GetActiveCamera().SetViewUp(0, 1, 0)  # 设置上方向


myscreen.render()
myscreen.iren.Start()
