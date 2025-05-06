import re
import math

# 假设 CNC 机器的最大加速度（mm/s²）
ACCELERATION = 500  # 可根据你的 CNC 机器调整
maxSpeed = 2500


def parse_gcode(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    commands = []
    x, y, z, f = 0, 0, 0, 2500  # 初始位置和默认进给速度
    for line in lines:
        line = line.strip()
        if line.startswith('G0') or line.startswith('G1') or line.startswith('G2') or line.startswith('G3'):
            new_x = re.search(r'X([\d\.\-]+)', line)
            new_y = re.search(r'Y([\d\.\-]+)', line)
            new_z = re.search(r'Z([\d\.\-]+)', line)
            new_f = re.search(r'F([\d\.\-]+)', line)
            i = re.search(r'I([\d\.\-]+)', line)
            j = re.search(r'J([\d\.\-]+)', line)
            new_x = float(new_x.group(1)) if new_x else x
            new_y = float(new_y.group(1)) if new_y else y
            new_z = float(new_z.group(1)) if new_z else z
            if line.startswith('G0'):
                new_f = maxSpeed
            else:
                if new_f:
                    new_f = float(new_f.group(1))
                else:
                    new_f = f

            if line.startswith('G1') or line.startswith('G0'):
                # 直线长度计算
                dist = math.sqrt((new_x - x) ** 2 + (new_y - y) ** 2 + (new_z - z) ** 2)
            elif line.startswith('G2') or line.startswith('G3'):
                # 圆弧长度计算
                if i and j:
                    center_x = x + float(i.group(1))
                    center_y = y + float(j.group(1))
                    radius = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    theta = math.atan2(new_y - center_y, new_x - center_x) - math.atan2(y - center_y, x - center_x)
                    if line.startswith('G2') and theta < 0:
                        theta += 2 * math.pi
                    if line.startswith('G3') and theta > 0:
                        theta -= 2 * math.pi
                    arc_length = abs(theta) * radius
                    dist = arc_length
                else:
                    dist = 0

            commands.append((line, dist, new_f))
            x, y, z, f = new_x, new_y, new_z, new_f

    return commands


def calculate_time_with_acceleration(commands):
    total_time = 0
    for _, dist, feed in commands:
        if feed > 0:
            # 进给速度从 mm/min 转换为 mm/s
            F_mm_s = feed / 60.0

            # 计算加速和减速时间
            t_acc = F_mm_s / ACCELERATION  # 加速时间
            d_acc = 0.5 * ACCELERATION * (t_acc ** 2)  # 加速段的位移
            d_dec = d_acc  # 减速段位移相同
            t_dec = t_acc  # 减速时间相同

            if dist >= (d_acc + d_dec):
                # 如果距离足够长，中间有匀速段
                d_uniform = dist - (d_acc + d_dec)
                t_uniform = d_uniform / F_mm_s
                total_time += (t_acc + t_uniform + t_dec)
            else:
                # 如果距离很短，无法达到最大速度，使用匀加速运动公式
                t_total = math.sqrt(2 * dist / ACCELERATION)
                total_time += t_total

    return format_time(total_time)


def format_time(seconds):
    """ 将秒转换为 小时:分钟:秒 """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours} 小时 {minutes} 分钟 {secs} 秒"


# 示例调用
gcode_file = '3.8use.nc'
commands = parse_gcode(gcode_file)
processing_time = calculate_time_with_acceleration(commands)

print(f"预计加工时间（考虑加速度）: {processing_time}")
