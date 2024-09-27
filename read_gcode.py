import re

with open("file/4.nc", "r") as f:
    lines = f.readlines()

txt_dist = {"X": 0, "Y": 0, "Z": 0, "G": ""}

for line in lines:
    code = line.strip()
    code_list = code.split()
    if "X" in code or "Y" in code or "Z" in code:
        pattern = r'([XYZIJ])([-+]?\d*\.\d+|\d+)'
        matches = re.findall(pattern, code)
        result = {match[0]: float(match[1]) for match in matches}
        keys_list = result.keys()
        if "G00" in code or "G01" in code:
            if 'X' in keys_list:
                txt_dist['X'] = result['X']
            if 'Y' in keys_list:
                txt_dist['Y'] = result['Y']
            if 'Z' in keys_list:
                txt_dist['Z'] = result['Z']
            if "G00" in code:
                txt_dist['G'] = "G00"
            elif "G01" in code:
                txt_dist['G'] = "G01"
        elif "G02" in code or "G03" in code:
            center_offset = [0, 0, 0]
            start_X, start_Y, start_Z = txt_dist['X'], txt_dist['Y'], txt_dist['Z']
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
            end_X, end_Y, end_Z = txt_dist['X'], txt_dist['Y'], txt_dist['Z']
            if "G02" in code:
                txt_dist['G'] = "G02"
                clockwise = True
            elif "G03" in code:
                txt_dist['G'] = "G03"
                clockwise = False
        elif "G" not in code:
            G = txt_dist['G']
            if 'X' in keys_list:
                txt_dist['X'] = result['X']
            if 'Y' in keys_list:
                txt_dist['Y'] = result['Y']
            if 'Z' in keys_list:
                txt_dist['Z'] = result['Z']
