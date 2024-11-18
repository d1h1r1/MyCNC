from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src import camvtk
import read_gcode


class myMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()

        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.myscreen = camvtk.VTKScreen()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.myscreen.ren)
        self.myscreen.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        interactorstyle = self.myscreen.iren.GetInteractorStyle()
        interactorstyle.SetCurrentStyleToTrackballCamera()

        line_points, arc_points = read_gcode.get_points("../file/elephant.nc")
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

        # self.myscreen.iren.Start()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()
        self.myscreen.iren.Start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myMainWindow()
    sys.exit(app.exec_())
