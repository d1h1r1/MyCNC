from src import camvtk
import re

with open("../file/elephant.nc", "r") as f:
    lines = f.readlines()

txt_dist = {"X": 0.0, "Y": 0.0, "Z": 0.0, "G": ""}

line_points = []
arc_points = []


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
                line_points.append((start_point, end_point))
                # myscreen.addActor(camvtk.Line(p1=start_point, p2=end_point))
            elif "G02" in code or "G03" in code:
                center_offset = [0, 0, 0]
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                # print("start", start_point)
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
                # print("end", end_point)
                if "G02" in code:
                    txt_dist['G'] = "G02"
                    clockwise = False
                elif "G03" in code:
                    txt_dist['G'] = "G03"
                    clockwise = True
                else:
                    continue
                arc_points.append((start_point, end_point, center_offset, clockwise))
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
                    line_points.append((start_point, end_point))
                    # myscreen.addActor(camvtk.Line(p1=start_point, p2=end_point))

    myscreen.addActor(camvtk.Lines(line_points))
    myscreen.addActor(camvtk.Arcs(arc_points))
    # 添加坐标系
    camvtk.drawArrows(myscreen)
    # myscreen.addActor(camvtk.Axes())
    ren = myscreen.ren
    ren.ResetCamera()
    # 设置画面中心点
    bounds = ren.ComputeVisiblePropBounds()
    centerX = (bounds[0] + bounds[1]) / 2
    centerY = (bounds[2] + bounds[3]) / 2
    centerZ = (bounds[4] + bounds[5]) / 2
    myscreen.camera.SetFocalPoint(centerX, centerY, centerZ)

    # 设置相机位置可控制画面放缩
    distance = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
    myscreen.camera.SetPosition(centerX*1.5, (centerY - distance * 1.5)*1.5, (centerZ + distance / 2)*1.5)
    myscreen.iren.Start()


if __name__ == "__main__":
    test_gcode()
