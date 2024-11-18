import vtk
import datetime
import math

white = (1, 1, 1)
black = (0, 0, 0)
grey = (float(127) / 255, float(127) / 255, float(127) / 255)

red = (1, 0, 0)
pink = (float(255) / 255, float(192) / 255, float(203) / 255)
orange = (float(255) / 255, float(165) / 255, float(0) / 255)
yellow = (1, 1, 0)

green = (0, 1, 0)
lgreen = (float(150) / 255, float(255) / 255, float(150) / 255)
grass = (float(182) / 255, float(248) / 255, float(71) / 255)

blue = (0, 0, 1)
lblue = (float(125) / 255, float(191) / 255, float(255) / 255)
cyan = (0, 1, 1)
mag = (float(153) / 255, float(42) / 255, float(165) / 255)


def drawOCLtext(myscreen):
    t = Text()
    t.SetPos((myscreen.width - 200, myscreen.height - 50))
    date_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t.SetText("OpenCAMLib\n" + date_text)
    myscreen.addActor(t)


def old_drawArrows(myscreen, center=(0, 0, 0)):
    # X Y Z arrows
    arrowcenter = center
    xar = Arrow(color=red, center=arrowcenter, rotXYZ=(0, 0, 0))
    yar = Arrow(color=green, center=arrowcenter, rotXYZ=(0, 0, 90))
    zar = Arrow(color=blue, center=arrowcenter, rotXYZ=(0, -90, 0))
    myscreen.addActor(xar)
    myscreen.addActor(yar)
    myscreen.addActor(zar)


def drawArrows(myscreen, center=(0, 0, 0)):
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(20, 20, 20)
    axes.SetXAxisLabelText("")
    axes.SetYAxisLabelText("")
    axes.SetZAxisLabelText("")
    # 设置轴的颜色
    axes.GetXAxisShaftProperty().SetColor(1, 0, 0)  # 红色
    axes.GetYAxisShaftProperty().SetColor(0, 1, 0)  # 绿色
    axes.GetZAxisShaftProperty().SetColor(0, 0, 1)  # 蓝色

    myscreen.addActor(axes)


def drawCylCutter(myscreen, c, p):
    cyl = Cylinder(center=(p.x, p.y, p.z), radius=c.radius,
                   height=c.length,
                   rotXYZ=(90, 0, 0), color=grey)
    cyl.SetWireframe()
    myscreen.addActor(cyl)


def drawBallCutter(myscreen, c, p):
    cyl = Cylinder(center=(p.x, p.y, p.z + c.getRadius()), radius=c.getRadius(),
                   height=c.getLength(),
                   rotXYZ=(90, 0, 0), color=red)
    # cyl.SetWireframe()
    sph = Sphere(center=(p.x, p.y, p.z + c.getRadius()), radius=c.getRadius(), color=red)
    myscreen.addActor(cyl)
    myscreen.addActor(sph)
    acts = []
    acts.append(cyl)
    acts.append(sph)
    return acts


class VTKScreen():
    """
    a vtk render window for displaying geometry
    """

    def __init__(self, width=1280, height=720):
        """ create a screen """
        self.width = width
        self.height = height
        # 创建渲染器
        self.ren = vtk.vtkRenderer()
        # 创建窗口接收渲染器
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(self.width, self.height)

        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        interactorstyle = self.iren.GetInteractorStyle()
        interactorstyle.SetCurrentStyleToTrackballCamera()

        self.camera = vtk.vtkCamera()
        self.camera.SetClippingRange(0.01, 1000)
        self.camera.SetFocalPoint(0, 50, 0)
        self.camera.SetPosition(0, 35, 5)
        self.camera.SetViewAngle(90)
        self.camera.SetViewUp(0, 0, 1)
        self.ren.SetActiveCamera(self.camera)
        # self.iren.Initialize()

    def setAmbient(self, r, g, b):
        """ set ambient color """
        self.ren.SetAmbient(r, g, b)

    def addActor(self, actor):
        """ add an actor """
        self.ren.AddActor(actor)

    def removeActor(self, actor):
        """ remove an actor"""
        # actor.Delete()
        self.ren.RemoveActor(actor)

    def render(self):
        """ render scene"""
        self.renWin.Render()

    def GetLights(self):
        return self.ren.GetLights()

    def CreateLight(self):
        self.ren.CreateLight()

    def MakeLight(self):
        return self.ren.MakeLight()

    def AddLight(self, l):
        self.ren.AddLight(l)

    def GetActors(self):
        return self.ren.GetActors()

    def RemoveAllLights(self):
        self.ren.RemoveAllLights()

    def SetLightCollection(self, lights):
        self.ren.SetLightCollection(lights)

    def Close(self):
        self.iren.TerminateApp()


class CamvtkActor(vtk.vtkActor):
    """ base class for actors"""

    def __init__(self):
        """ do nothing"""
        pass

    def Delete(self):
        self.Delete()

    def SetColor(self, color):
        """ set color of actor"""
        self.GetProperty().SetColor(color)

    def SetOpacity(self, op=0.5):
        """ set opacity of actor, 0 is see-thru (invisible)"""
        self.GetProperty().SetOpacity(op)

    def SetWireframe(self):
        """ set surface to wireframe"""
        self.GetProperty().SetRepresentationToWireframe()

    def SetSurface(self):
        """ set surface rendering on"""
        self.GetProperty().SetRepresentationToSurface()

    def SetPoints(self):
        """ render only points"""
        self.GetProperty().SetRepresentationToPoints()

    def SetFlat(self):
        """ set flat shading"""
        self.GetProperty().SetInterpolationToFlat()

    def SetGouraud(self):
        """ set gouraud shading"""
        self.GetProperty().SetInterpolationToGouraud()

    def SetPhong(self):
        """ set phong shading"""
        self.GetProperty().SetInterpolationToPhong()

    # possible TODOs
    # specular
    # diffuse
    # ambient


class Cone(CamvtkActor):
    """ a cone"""

    def __init__(self, center=(-2, 0, 0), radius=1, angle=45, height=0.4, color=(1, 1, 0), resolution=60):
        """ cone"""
        self.src = vtk.vtkConeSource()
        self.src.SetResolution(resolution)
        self.src.SetRadius(radius)
        # self.src.SetAngle( angle )
        self.src.SetHeight(height)
        # self.src.SetCenter(center)

        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2] - self.src.GetHeight() / 2)
        # transform.RotateX(rotXYZ[0])
        transform.RotateY(-90)
        # transform.RotateZ(rotXYZ[2])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(transformFilter.GetOutput())

        # self.mapper = vtk.vtkPolyDataMapper()
        # self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Sphere(CamvtkActor):
    """ a sphere"""

    def __init__(self, radius=1, resolution=20, center=(0, 2, 0),
                 color=(1, 0, 0)):
        """ create sphere"""
        self.src = vtk.vtkSphereSource()
        self.src.SetRadius(radius)
        self.src.SetCenter(center)
        self.src.SetThetaResolution(resolution)
        self.src.SetPhiResolution(resolution)
        self.src.Update()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Cube(CamvtkActor):
    """ a cube"""

    def __init__(self, center=(2, 2, 0), length=1, color=(0, 1, 0)):
        """ create cube"""
        self.src = vtk.vtkCubeSource()
        self.src.SetCenter(center)
        self.src.SetXLength(length)
        self.src.SetYLength(length)
        self.src.SetZLength(length)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Cylinder(CamvtkActor):
    """ cylinder """

    def __init__(self, center=(0, -2, 0), radius=0.5, height=2, color=(0, 1, 1),
                 rotXYZ=(0, 0, 0), resolution=50):
        """ cylinder """
        self.src = vtk.vtkCylinderSource()
        self.src.SetCenter(0, 0, 0)
        self.src.SetHeight(height)
        self.src.SetRadius(radius)
        self.src.SetResolution(resolution)
        # SetResolution
        # SetCapping(int)
        # CappingOn() CappingOff()

        # this transform rotates the cylinder so it is vertical
        # and then translates the lower tip to the center point
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2] + height / 2)
        transform.RotateX(rotXYZ[0])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        # self.mapper.SetInput(self.src.GetOutput())
        self.mapper.SetInputData(transformFilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Line(CamvtkActor):
    """ line """

    def __init__(self, p1=(0, 0, 0), p2=(1, 1, 1), color=(0, 1, 1)):
        """ line """
        self.src = vtk.vtkLineSource()
        self.src.SetPoint1(p1)
        self.src.SetPoint2(p2)
        self.src.Update()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Lines(CamvtkActor):
    """ lines """

    def __init__(self, points, color=(0, 255, 255)):
        """ line """
        self.append_filter = vtk.vtkAppendPolyData()
        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        self.colors.SetName("Colors")
        self.line_sources = []

        for p1, p2 in points:
            line_source = vtk.vtkLineSource()
            line_source.SetPoint1(p1)
            line_source.SetPoint2(p2)
            line_source.Update()
            self.line_sources.append(line_source)
            # 为每段线段添加颜色
            num_points = line_source.GetOutput().GetNumberOfPoints()
            for _ in range(num_points):
                self.colors.InsertNextTuple(color)
            self.append_filter.AddInputData(line_source.GetOutput())

        self.append_filter.Update()

        output = self.append_filter.GetOutput()
        output.GetPointData().SetScalars(self.colors)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.append_filter.GetOutput())
        self.SetMapper(self.mapper)
        # self.SetColor(color)

    def update_line_color(self, index, new_color):
        """ 更新指定线段的颜色 """
        if index < 0 or index >= len(self.line_sources):
            print("索引超出范围")
            return

        line_source = self.line_sources[index]
        num_points = line_source.GetOutput().GetNumberOfPoints()

        # 更新颜色数组
        start_idx = sum(self.line_sources[i].GetOutput().GetNumberOfPoints() for i in range(index))
        for i in range(num_points):
            self.colors.SetTuple(start_idx + i, new_color)

        self.colors.Modified()
        self.append_filter.Update()


class Tube(CamvtkActor):
    """ line with tube filter"""

    def __init__(self, p1=(0, 0, 0), p2=(1, 1, 1), radius=0.1, color=(0, 1, 1)):
        self.src = vtk.vtkLineSource()
        self.src.SetPoint1(p1)
        self.src.SetPoint2(p2)

        self.tubefilter = vtk.vtkTubeFilter()
        self.tubefilter.SetInputData(self.src.GetOutput())
        self.tubefilter.SetRadius(radius)
        self.tubefilter.SetNumberOfSides(30)
        self.tubefilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.tubefilter.GetOutputPort())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Circle(CamvtkActor):
    """ circle"""

    def __init__(self, center=(0, 0, 0), radius=1, color=(0, 1, 1), resolution=50):
        """ create circle """
        lines = vtk.vtkCellArray()
        id = 0
        points = vtk.vtkPoints()
        for n in range(0, resolution):
            line = vtk.vtkLine()
            angle1 = (float(n) / (float(resolution))) * 2 * math.pi
            angle2 = (float(n + 1) / (float(resolution))) * 2 * math.pi
            p1 = (center[0] + radius * math.cos(angle1), center[1] + radius * math.sin(angle1), center[2])
            p2 = (center[0] + radius * math.cos(angle2), center[1] + radius * math.sin(angle2), center[2])
            points.InsertNextPoint(p1)
            points.InsertNextPoint(p2)
            line.GetPointIds().SetId(0, id)
            id = id + 1
            line.GetPointIds().SetId(1, id)
            id = id + 1
            lines.InsertNextCell(line)

        self.pdata = vtk.vtkPolyData()
        self.pdata.SetPoints(points)
        self.pdata.SetLines(lines)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.pdata)
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Arc(CamvtkActor):
    """ circle"""

    def __init__(self, center_offset=(0, 0, 0), start_point=(0, 0, 0), end_point=(0, 0, 0), color=(0, 1, 1),
                 clockwise=True):
        """ create circle """

        def calculate_angle(center, point):
            """
            计算给定点相对于圆心的角度
            """
            dx = point[0] - center[0]
            dy = point[1] - center[1]
            return math.atan2(dy, dx)

        def create_arc(center, radius, start_angle, end_angle, num_points=100, clockwise=True):
            """
            创建圆弧，顺时针或逆时针
            """
            points = vtk.vtkPoints()
            if not clockwise:
                if end_angle < start_angle:
                    end_angle += 2 * vtk.vtkMath.Pi()
            else:
                if start_angle < end_angle:
                    start_angle += 2 * vtk.vtkMath.Pi()

            for i in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * (i / num_points)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.InsertNextPoint(x, y, center[2])
            return points

        radius = math.sqrt(center_offset[0] ** 2 + center_offset[1] ** 2)
        center = (
            start_point[0] + center_offset[0], start_point[1] + center_offset[1], start_point[2] + center_offset[2])

        # 计算起始点和终止点相对于圆心的角度
        start_angle = calculate_angle(center, start_point)  # 起始角度
        end_angle = calculate_angle(center, end_point)  # 终止角度

        points = create_arc(center, radius, end_angle, start_angle, clockwise=clockwise)

        # 创建圆弧polyline
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(points.GetNumberOfPoints())
        for i in range(points.GetNumberOfPoints()):
            lines.InsertCellPoint(i)

        self.pdata = vtk.vtkPolyData()
        self.pdata.SetPoints(points)
        self.pdata.SetLines(lines)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.pdata)
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Arcs(CamvtkActor):
    """ circle"""

    def __init__(self, points, color=(0, 1, 1)):
        """ create circle """

        def calculate_angle(center, point):
            """
            计算给定点相对于圆心的角度
            """
            dx = point[0] - center[0]
            dy = point[1] - center[1]
            return math.atan2(dy, dx)

        def create_arc(center, radius, start_angle, end_angle, num_points=100, clockwise=True):
            """
            创建圆弧，顺时针或逆时针
            """
            points = vtk.vtkPoints()
            if not clockwise:
                if end_angle < start_angle:
                    end_angle += 2 * vtk.vtkMath.Pi()
            else:
                if start_angle < end_angle:
                    start_angle += 2 * vtk.vtkMath.Pi()

            for i in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * (i / num_points)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.InsertNextPoint(x, y, center[2])  # z = center[2]保持不变
            return points

        self.append_filter = vtk.vtkAppendPolyData()
        for start_point, end_point, center_offset, clockwise in points:
            radius = math.sqrt(center_offset[0] ** 2 + center_offset[1] ** 2)
            center = (
                start_point[0] + center_offset[0], start_point[1] + center_offset[1], start_point[2] + center_offset[2])

            # 计算起始点和终止点相对于圆心的角度
            start_angle = calculate_angle(center, start_point)  # 起始角度
            end_angle = calculate_angle(center, end_point)  # 终止角度

            points = create_arc(center, radius, end_angle, start_angle, clockwise=clockwise)

            # 创建圆弧polyline
            lines = vtk.vtkCellArray()
            lines.InsertNextCell(points.GetNumberOfPoints())
            for i in range(points.GetNumberOfPoints()):
                lines.InsertCellPoint(i)

            self.pdata = vtk.vtkPolyData()
            self.pdata.SetPoints(points)
            self.pdata.SetLines(lines)
            self.append_filter.AddInputData(self.pdata)

        self.append_filter.Update()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.append_filter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Tube(CamvtkActor):
    """ a Tube is a line with thickness"""

    def __init__(self, p1=(0, 0, 0), p2=(1, 1, 1), radius=0.2, color=(0, 1, 1)):
        """ tube"""
        points = vtk.vtkPoints()
        points.InsertNextPoint(p1)
        points.InsertNextPoint(p2)
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 1)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line)
        self.pdata = vtk.vtkPolyData()
        self.pdata.SetPoints(points)
        self.pdata.SetLines(lines)

        tubefilter = vtk.vtkTubeFilter()
        tubefilter.SetInputData(self.pdata)
        tubefilter.SetRadius(radius)
        tubefilter.SetNumberOfSides(50)
        tubefilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(tubefilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Point(CamvtkActor):
    """ point"""

    def __init__(self, center=(0, 0, 0), color=(1, 2, 3)):
        """ create point """
        self.src = vtk.vtkPointSource()
        self.src.SetCenter(center)
        self.src.SetRadius(0)
        self.src.SetNumberOfPoints(1)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Arrow(CamvtkActor):
    """ arrow """

    def __init__(self, center=(0, 0, 0), color=(0, 0, 1), rotXYZ=(0, 0, 0)):
        """ arrow """
        self.src = vtk.vtkArrowSource()
        # self.src.SetCenter(center)
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2])
        transform.RotateX(rotXYZ[0])
        transform.RotateY(rotXYZ[1])
        transform.RotateZ(rotXYZ[2])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(transformFilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Text(vtk.vtkTextActor):
    """ 2D text, HUD-type"""

    def __init__(self, text="text", size=18, color=(1, 1, 1), pos=(100, 100)):
        """create text"""
        self.SetText(text)
        self.properties = self.GetTextProperty()
        self.properties.SetFontFamilyToArial()
        self.properties.SetFontSize(size)

        self.SetColor(color)
        self.SetPos(pos)

    def SetColor(self, color):
        """ set color of text """
        self.properties.SetColor(color)

    def SetPos(self, pos):
        """ set position on screen """
        self.SetDisplayPosition(pos[0], pos[1])

    def SetText(self, text):
        """ set text to be displayed """
        self.SetInput(text)

    def SetSize(self, size):
        self.properties.SetFontSize(size)


class Text3D(vtk.vtkFollower):
    """ 3D text rendered in the scene"""

    def __init__(self, color=(1, 1, 1), center=(0, 0, 0), text="hello", scale=1, camera=[]):
        """ create text """
        self.src = vtk.vtkVectorText()
        self.SetText(text)
        # self.SetCamera(camera)
        transform = vtk.vtkTransform()

        transform.Translate(center[0], center[1], center[2])
        transform.Scale(scale, scale, scale)
        # transform.RotateY(90)
        # transform2 = vtk.vtkTransform()
        # transform.Concatenate(transform2)
        # transformFilter=vtk.vtkTransformPolyDataFilter()
        # transformFilter.SetTransform(transform)
        # transformFilter.SetInputConnection(self.src.GetOutputPort())
        # transformFilter.Update()

        # follower = vtk.vtkFollower()
        # follower.SetMapper

        self.SetUserTransform(transform)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.src.GetOutputPort())
        self.SetMapper(self.mapper)
        self.SetColor(color)

    def SetText(self, text):
        """ set text to be displayed"""
        self.src.SetText(text)

    def SetColor(self, color):
        """ set color of text"""
        self.GetProperty().SetColor(color)


class Axes(vtk.vtkActor):
    """ axes (x,y,z) """

    def __init__(self, center=(0, 0, 0), color=(0, 0, 1)):
        """ create axes """
        self.src = vtk.vtkAxes()
        # self.src.SetCenter(center)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)

        self.SetColor(color)
        self.SetOrigin(center)
        # SetScaleFactor(double)
        # GetOrigin

    def SetColor(self, color):
        self.GetProperty().SetColor(color)

    def SetOrigin(self, center=(0, 0, 0)):
        self.src.SetOrigin(center[0], center[1], center[2])


class Toroid(CamvtkActor):
    def __init__(self, r1=1, r2=0.25, center=(0, 0, 0), rotXYZ=(0, 0, 0), color=(1, 0, 0)):
        self.parfun = vtk.vtkParametricSuperToroid()
        self.parfun.SetRingRadius(r1)
        self.parfun.SetCrossSectionRadius(r2)
        self.parfun.SetN1(1)
        self.parfun.SetN2(1)

        self.src = vtk.vtkParametricFunctionSource()
        self.src.SetParametricFunction(self.parfun)

        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2])
        transform.RotateX(rotXYZ[0])
        transform.RotateY(rotXYZ[1])
        transform.RotateZ(rotXYZ[2])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(transformFilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


"""
class TrilistReader(vtk.vtkPolyDataAlgorithm):
    def __init__(self, triangleList):
        vtk.vtkPolyDataAlgorithm.__init__(self)
        self.FileName = None
        self.SetNumberOfInputPorts(0)
        self.SetNumberOfOutputPorts(1)

    def FillOutputPortInfornmation(self, port, info):
        if port == 0:
            info.Set( vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkPolyData")
            return 1
        return 0

    def RequestData(self, request, inputVector, outputVector):
        outInfo = outputVector.GetInformationObject(0)
        output = outInfo.Get( vtk.vtkDataObject.DATA_OBJECT() )
        polydata = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        points.InsertNextPoint(0,0,0)
        polydata.SetPoints(points)

        output.ShallowCopy(polydata)
        return 1
"""


class STLSurf(CamvtkActor):
    def __init__(self, filename=None, triangleList=[], color=(1, 1, 1)):
        self.src = []
        if filename is None:
            points = vtk.vtkPoints()
            triangles = vtk.vtkCellArray()
            n = 0
            for t in triangleList:
                triangle = vtk.vtkTriangle()
                for p in t.getPoints():
                    points.InsertNextPoint(p.x, p.y, p.z)
                triangle.GetPointIds().SetId(0, n)
                n = n + 1
                triangle.GetPointIds().SetId(1, n)
                n = n + 1
                triangle.GetPointIds().SetId(2, n)
                n = n + 1
                triangles.InsertNextCell(triangle)
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(triangles)
            polydata.Modified()
            # polydata.Update() # gives error on vtk6
            self.src = polydata
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInputData(self.src)
            self.SetMapper(self.mapper)

        else:  # a filename was specified
            self.src = vtk.vtkSTLReader()
            self.src.SetFileName(filename)
            self.src.Update()
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInputData(self.src.GetOutput())
            self.SetMapper(self.mapper)

        self.SetColor(color)
        # SetScaleFactor(double)
        # GetOrigin


class PointCloud(CamvtkActor):
    def __init__(self, pointlist=[]):
        points = vtk.vtkPoints()
        cellArr = vtk.vtkCellArray()
        # Colors = vtk.vtkUnsignedCharArray()
        # Colors.SetNumberOfComponents(3)
        # Colors.SetName("Colors")

        n = 0
        for p in pointlist:
            vert = vtk.vtkVertex()
            points.InsertNextPoint(p.x, p.y, p.z)
            vert.GetPointIds().SetId(0, n)
            cellArr.InsertNextCell(vert)
            # col = clColor(p.cc())
            # Colors.InsertNextTuple3( float(255)*col[0], float(255)*col[1], float(255)*col[2] )
            n = n + 1

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts(cellArr)
        # polydata.GetPointData().SetScalars(Colors)

        polydata.Modified()
        # polydata.Update() # https://www.vtk.org/Wiki/VTK/VTK_6_Migration/Removal_of_Update
        self.src = polydata
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src)
        self.SetMapper(self.mapper)
        # self.SetColor(color)


class Plane(CamvtkActor):
    def __init__(self, center=(0, 0, 0), color=(0, 0, 1)):
        self.src = vtk.vtkPlaneSource()
        # self.src.SetCenter(center)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.src.GetOutput())
        self.SetMapper(self.mapper)

        self.SetColor(color)
        self.SetOrigin(center)
        # SetScaleFactor(double)
        # GetOrigin
