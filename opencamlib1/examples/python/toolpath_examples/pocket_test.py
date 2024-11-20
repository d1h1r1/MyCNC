import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString


def generate_ring_lines(polygon_points, center, num_rings=10, num_segments=100):
    """
    生成围绕中心点的环形覆盖线条

    参数：
    - polygon_points: 多边形顶点列表 [(x1, y1), (x2, y2), ...]
    - center: 旋转中心 (cx, cy)
    - num_rings: 环的数量
    - num_segments: 每个环分割的线段数量

    返回：
    - lines: 裁剪后覆盖区域的线条
    """
    # 创建多边形
    poly = Polygon(polygon_points)

    # 存储裁剪后的线条
    lines = []

    # 半径增量
    max_radius = max([np.linalg.norm([x - center[0], y - center[1]]) for x, y in polygon_points])
    radius_step = max_radius / num_rings

    # 生成每个环的线条
    for ring in range(1, num_rings + 1):
        radius = ring * radius_step
        points = []

        # 在环上均匀生成点
        for i in range(num_segments + 1):
            angle = 2 * np.pi * i / num_segments
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            points.append((x, y))

        # 将点连成闭合环
        ring_line = LineString(points)

        # 裁剪环与多边形的交集
        clipped_line = ring_line.intersection(poly)

        if not clipped_line.is_empty:
            if isinstance(clipped_line, LineString):
                # 单条线段
                lines.append(clipped_line)
            elif isinstance(clipped_line, MultiLineString):
                # 多条线段，展开添加
                lines.extend(clipped_line.geoms)

    return lines


# 示例：定义多边形和中心
polygon_points = [(1, 1), (5, 1), (4, 4), (2, 5), (1, 4)]
center = (3, 3)

# 生成环形线条
lines = generate_ring_lines(polygon_points, center, num_rings=20, num_segments=200)

# 可视化
plt.figure(figsize=(6, 6))

# 绘制多边形
poly_patch = plt.Polygon(polygon_points, closed=True, fill=None, edgecolor='black')
plt.gca().add_patch(poly_patch)

# 绘制环形线条
for line in lines:
    x, y = line.xy
    plt.plot(x, y, 'b-', linewidth=0.5)

# 绘制旋转中心
plt.scatter([center[0]], [center[1]], color='red', label="旋转中心")

plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()
