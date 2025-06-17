def check_a_axis_increasing(gcode_file):
    """
    检查Gcode文件中的A轴值是否一直在增加

    参数:
        gcode_file (str): Gcode文件路径

    返回:
        bool: True表示A轴一直在增加，False表示有减小的情况
        str: 结果描述信息
        list: 所有A轴值的列表（用于调试或进一步分析）
    """
    try:
        with open(gcode_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return False, f"错误：文件 {gcode_file} 未找到", []
    except Exception as e:
        return False, f"读取文件时出错: {str(e)}", []

    a_values = []
    previous_a = None
    line_number = 0
    decreasing_points = []

    for line in lines:
        line_number += 1
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('('):
            continue  # 跳过注释和空行

        # 查找A轴参数
        a_index = line.find('A')
        if a_index != -1:
            try:
                # 提取A值部分
                a_part = line[a_index:]
                # 去除A后面可能的空格
                a_value_str = a_part[1:].replace(' ', '')
                # 找到第一个非数字字符（F, ;等）
                for i, c in enumerate(a_value_str):
                    if not (c.isdigit() or c == '.' or c == '-'):
                        a_value_str = a_value_str[:i]
                        break

                current_a = float(a_value_str)
                a_values.append(current_a)

                # 检查是否比前一个值小
                if previous_a is not None and current_a < previous_a:
                    if abs(previous_a - current_a) > 10:
                        print(abs(previous_a - current_a))
                        decreasing_points.append(
                            f"行 {line_number}: A从 {previous_a} 减小到 {current_a} - '{line.strip()}'"
                        )

                previous_a = current_a
            except (IndexError, ValueError) as e:
                continue  # 跳过格式错误的行

    if not a_values:
        return True, "文件中未找到A轴移动指令", []

    if decreasing_points:
        message = (f"检测到 {len(decreasing_points)} 处A轴减小情况:\n" +
                   "\n".join(decreasing_points) + \
                   f"\n\nA轴值范围: {min(a_values)} 到 {max(a_values)}")
        return False, message, a_values

    return True, (f"A轴一直在增加，共检测到 {len(a_values)} 个A轴移动指令\n" +
                  f"起始值: {a_values[0]}, 结束值: {a_values[-1]}\n" +
                  f"总增加量: {a_values[-1] - a_values[0]}"), a_values


if __name__ == "__main__":
    result, message, a_values = check_a_axis_increasing("250604精2.nc")

    print("\n检查结果:")
    print(message)

    # 如果需要，可以打印所有A值用于调试
    debug = False
    if debug and a_values:
        print("\n所有A值:", a_values)

    print(f"\n总结: A轴{'一直增加' if result else '有减小的情况'}")