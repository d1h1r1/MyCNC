from shapely.geometry import LineString
import matplotlib.pyplot as plt

# 创建一条曲线
# line = LineString([(0, 0), (1, 2), (2, 3), (4, 2), (5, 0)])
line = LineString([(0, 0), (2, 2), (2, 4), (0, 4), (0, 0)])
# 向外扩展 0.5 的距离
buffered_out = line.buffer(0.5)

# 向内扩展 -0.2 的距离（如果是负数，需要注意是否仍然有效）
buffered_in = line.buffer(-0.2)

# 可视化
fig, ax = plt.subplots()
ax.plot(*line.xy, 'k-', label="Original Line")  # 原始线
ax.fill(*buffered_out.exterior.xy, color='blue', alpha=0.5, label="Outer Buffer")  # 外扩区域
if buffered_in.is_empty:
    print("Inner buffer is empty")  # 负数过大会导致空区域
else:
    ax.fill(*buffered_in.exterior.xy, color='red', alpha=0.5, label="Inner Buffer")  # 内扩区域

ax.legend()
plt.show()
