import re

txt_dist = {"X": 0.0, "Y": 0.0, "Z": 0.0, "I": 0.0, "J": 0.0, "G": ""}

line_points = []
arc_points = []


def get_points(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        code = line.strip()
        if "X" in code or "Y" in code or "Z" in code:
            # 通过正则表达式获取所需数据
            pattern = r'([XYZIJ])([-+]?\d*\.\d+|\d+)'
            matches = re.findall(pattern, code)
            result = {match[0]: float(match[1]) for match in matches}
            # 获取数据名称列表
            keys_list = result.keys()
            # 直线运动
            if "G00" in code or "G01" in code:
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                for key in keys_list:
                    txt_dist[key] = result[key]
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if "G00" in code or "G0" in code:
                    txt_dist['G'] = "G00"
                elif "G01" in code or "G1" in code:
                    txt_dist['G'] = "G01"
                else:
                    continue
                line_points.append((start_point, end_point))
            # 圆弧运动
            elif "G02" in code or "G03" in code:
                center_offset = [0, 0, 0]
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                for key in keys_list:
                    txt_dist[key] = result[key]
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if 'I' in keys_list:
                    center_offset[0] = result['I']
                if 'J' in keys_list:
                    center_offset[1] = result['J']
                if "G02" in code or "G2" in code:
                    txt_dist['G'] = "G02"
                    clockwise = False
                elif "G03" in code or "G3" in code:
                    txt_dist['G'] = "G03"
                    clockwise = True
                else:
                    continue
                arc_points.append((start_point, end_point, center_offset, clockwise))
            # 省略运动指令名称时
            elif "G" not in code:
                before = txt_dist['G']
                center_offset = [0, 0, 0]
                start_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if 'I' in keys_list:
                    center_offset[0] = result['I']
                if 'J' in keys_list:
                    center_offset[1] = result['J']
                for key in keys_list:
                    txt_dist[key] = result[key]
                end_point = (txt_dist['X'], txt_dist['Y'], txt_dist['Z'])
                if before == "G00" or before == "G01":
                    line_points.append((start_point, end_point))
                elif before == "G02":
                    arc_points.append((start_point, end_point, center_offset, False))
                elif before == "G03":
                    arc_points.append((start_point, end_point, center_offset, True))
    return line_points, arc_points
