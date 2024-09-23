import camvtk
import re

with open("4.txt", "r") as f:
    lines = f.readlines()

txt_dist = {"X": 0.0, "Y": 0.0, "Z": 0.0, "G": ""}


def test_gcode():
    myscreen = camvtk.VTKScreen()
    for line in lines:
        code = line.strip()
        if "X" in code or "Y" in code or "Z" in code:
            pattern = r'([XYZIJ])([-+]?\d*\.\d+|\d+)'
            matches = re.findall(pattern, code)
            result = {match[0]: float(match[1]) for match in matches}
            keys_list = result.keys()
            if "G00" in code or "G01" in code:
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if 'X' in keys_list:
                    txt_dist['X'] = result['X']
                if 'Y' in keys_list:
                    txt_dist['Y'] = result['Y']
                if 'Z' in keys_list:
                    txt_dist['Z'] = result['Z']
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if "G00" in code:
                    txt_dist['G'] = "G00"
                elif "G01" in code:
                    txt_dist['G'] = "G01"
                myscreen.addActor(camvtk.Line(p1=start_point, p2=end_point))
            elif "G02" in code or "G03" in code:
                center_offset = [0, 0, 0]
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                print("start", start_point)
                if 'X' in keys_list:
                    txt_dist['X'] = result['X']
                if 'Y' in keys_list:
                    txt_dist['Y'] = result['Y']
                if 'Z' in keys_list:
                    txt_dist['Z'] = result['Z']
                if 'I' in keys_list:
                    center_offset[0] = result['I']
                if 'J' in keys_list:
                    center_offset[1] = result['J']
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                print("end", end_point)
                if "G02" in code:
                    txt_dist['G'] = "G02"
                    clockwise = False
                elif "G03" in code:
                    txt_dist['G'] = "G03"
                    clockwise = True
                myscreen.addActor(
                    camvtk.Arc(start_point=start_point, end_point=end_point,
                               center_offset=center_offset,
                               clockwise=clockwise))
            elif "G" not in code:
                before = txt_dist['G']
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if 'X' in keys_list:
                    txt_dist['X'] = result['X']
                if 'Y' in keys_list:
                    txt_dist['Y'] = result['Y']
                if 'Z' in keys_list:
                    txt_dist['Z'] = result['Z']
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if before == "G00" or before == "G01":
                    myscreen.addActor(camvtk.Line(p1=start_point, p2=end_point))
    myscreen.iren.Start()

def vtk_visualize_parallel_finish_zig():
    myscreen = camvtk.VTKScreen()
    # myscreen.camera.SetPosition(15, 13, 7)
    # myscreen.camera.SetFocalPoint(5, 5, 0)

    # myscreen.addActor(camvtk.Sphere(center=(1, 2, 0), radius=0.1, color=camvtk.red))
    # myscreen.addActor(camvtk.Line(p1=(0, 0, 0), p2=(1, 1, 0), color=plungeColor))
    I = 1.375  # X 方向偏移
    J = 2.945  # Y 方向偏移
    center_offset = [I, J, 0]  # 圆心相对起点的偏移
    myscreen.addActor(
        camvtk.Arc(end_point=(80.0, -15.0, 0.0), start_point=(81.348, -15.696, 0.0), center_offset=center_offset,
                   clockwise=False))
    camvtk.drawArrows(myscreen, center=(-0.5, -0.5, -0.5))  # XYZ coordinate arrows
    # camvtk.drawOCLtext(myscreen)
    # myscreen.render()
    myscreen.iren.Start()


if __name__ == "__main__":
    # vtk_visualize_parallel_finish_zig()
    test_gcode()
