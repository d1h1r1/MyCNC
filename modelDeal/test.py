from collections import defaultdict

layer_map = defaultdict(list, {
    -0.2: [[-0.2, -7.000000000000001], [0]],
    -7.1000000000000005: [[-7.1000000000000005, -7.5], [0, 1, 2]],
    -7.5: [[-7.5, -7.5], [0, 1, 2]],
    -7.6000000000000005: [[-7.6000000000000005, -9.8], [0, 3, 4]],
    -9.9: [[-9.9, -10.000000000000002], [0, 3, 4]],
    -10.100000000000001: [[-10.100000000000001, -15.0], [3, 4, 5]],
    -15.0: [[-15.0, -15.0], [3, 4, 5]],
    -15.100000000000001: [[-15.100000000000001, -17.0], [6]],
    -17.0: [[], []]
})

# 获取每个索引的所有高度范围
index_ranges = defaultdict(list)
for key in layer_map:
    height_range, indices = layer_map[key]
    if height_range and indices:
        start, end = height_range
        for index in indices:
            index_ranges[index].append((start, end))


# 合并范围（允许接近的范围合并，设置一个很小的阈值）
def merge_ranges(ranges, threshold=0.2):  # 如果两个范围的间隙 <= threshold，就合并
    if not ranges:
        return []
    ranges = sorted(ranges)
    merged = [list(ranges[0])]
    for current_start, current_end in ranges[1:]:
        last_start, last_end = merged[-1]
        if current_start <= last_end + threshold:  # 允许接近的范围合并
            new_start = min(last_start, current_start)
            new_end = max(last_end, current_end)
            merged[-1] = [new_start, new_end]
        else:
            merged.append([current_start, current_end])
    return merged


# 合并每个索引的范围
for index in index_ranges:
    index_ranges[index] = merge_ranges(index_ranges[index])

# 计算每个索引的最低点和最高点
index_min_max = {}
for index in index_ranges:
    all_heights = []
    for start, end in index_ranges[index]:
        all_heights.extend([start, end])
    min_height = min(all_heights)  # 最低点
    max_height = max(all_heights)  # 最高点
    index_min_max[index] = (min_height, max_height)

# 输出结果
for index in sorted(index_min_max.keys()):
    min_h, max_h = index_min_max[index]
    print(f"索引 {index}: 最低点 = {min_h}, 最高点 = {max_h}")
