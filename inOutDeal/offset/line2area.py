from shapely.geometry import LineString, Polygon, LinearRing
from shapely.ops import unary_union
import matplotlib.pyplot as plt


def get_tool_path_ring(line_start, line_end, tool_diameter, contour_offset=0.0):
    """
    获取刀具沿线段行走扫掠的环状区域（空心槽）

    参数:
    - line_start: 线段起点 (x, y)
    - line_end: 线段终点 (x, y)
    - tool_diameter: 刀具直径
    - contour_offset: 轮廓偏移量（正值为向外扩展，负值为向内收缩）

    返回:
    - Polygon: 环状区域（空心区域）
    - LineString: 原始线段
    """
    # 1. 创建原始线段
    line = LineString([line_start, line_end])
    tool_radius = tool_diameter / 2.0

    # 2. 计算外轮廓和内轮廓
    # 外轮廓：原始路径向外偏移（刀具半径 + 轮廓偏移）
    outer_offset = tool_radius + contour_offset
    # 内轮廓：原始路径向内偏移（轮廓偏移 - 刀具半径）
    inner_offset = contour_offset - tool_radius

    # 3. 创建外轮廓和内轮廓的缓冲区
    outer_polygon = line.buffer(
        outer_offset,
        cap_style='round',
        join_style='round'
    )

    inner_polygon = line.buffer(
        abs(inner_offset) if inner_offset < 0 else inner_offset,
        cap_style='round',
        join_style='round'
    )

    # 4. 计算环状区域（外轮廓减去内轮廓）
    if inner_offset >= 0:
        # 如果内轮廓偏移为正或零，直接计算差集
        ring_polygon = outer_polygon.difference(inner_polygon)
    else:
        # 如果内轮廓偏移为负，需要处理特殊情况
        ring_polygon = outer_polygon

    return ring_polygon, line


def get_contour_cutting_ring(contour_coords, tool_diameter, is_closed=True):
    """
    获取沿闭合轮廓切割的环状区域

    参数:
    - contour_coords: 轮廓顶点坐标列表 [(x1,y1), (x2,y2), ...]
    - tool_diameter: 刀具直径
    - is_closed: 轮廓是否闭合

    返回:
    - Polygon: 环状切割区域
    - LinearRing/LineString: 原始轮廓
    """
    # 创建原始轮廓
    if is_closed and len(contour_coords) > 2:
        contour = LinearRing(contour_coords)
    else:
        contour = LineString(contour_coords)

    tool_radius = tool_diameter / 2.0

    # 创建外轮廓（向外偏移刀具半径）
    outer_polygon = contour.buffer(
        tool_radius,
        cap_style='round' if not is_closed else 'flat',
        join_style='round'
    )

    # 创建内轮廓（向内偏移刀具半径）
    inner_polygon = contour.buffer(
        -tool_radius,
        cap_style='round' if not is_closed else 'flat',
        join_style='round'
    )

    # 计算环状区域（外轮廓减去内轮廓）
    # 注意：对于非闭合线段，内轮廓可能为空
    if inner_polygon.is_empty:
        ring_polygon = outer_polygon
    else:
        ring_polygon = outer_polygon.difference(inner_polygon)

    return ring_polygon, contour


# 示例：生成矩形环状区域
def create_rectangle_ring_example():
    """创建矩形环状切割区域的示例"""
    # 矩形轮廓坐标（闭合）
    rectangle_coords = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
    tool_diameter = 1.0

    # 获取环状区域
    ring_polygon, contour = get_contour_cutting_ring(rectangle_coords, tool_diameter)

    # 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：显示内外轮廓
    ax1.set_title('内外轮廓示意图')

    # 绘制原始轮廓
    if hasattr(contour, 'xy'):
        ax1.plot(*contour.xy, 'r-', linewidth=3, label='刀具中心路径')
    else:
        x, y = contour.coords.xy
        ax1.plot(x, y, 'r-', linewidth=3, label='刀具中心路径')

    # 计算并绘制外轮廓
    outer = contour.buffer(tool_diameter / 2, cap_style='flat', join_style='round')
    x_outer, y_outer = outer.exterior.xy
    ax1.plot(x_outer, y_outer, 'b--', linewidth=2, label='外轮廓')

    # 计算并绘制内轮廓
    inner = contour.buffer(-tool_diameter / 2, cap_style='flat', join_style='round')
    if not inner.is_empty:
        x_inner, y_inner = inner.exterior.xy
        ax1.plot(x_inner, y_inner, 'g--', linewidth=2, label='内轮廓')

    ax1.legend()
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)

    # 右图：显示环状区域
    ax2.set_title(f'环状切割区域 (刀具直径: {tool_diameter})')

    # 绘制环状区域
    if ring_polygon.geom_type == 'Polygon':
        # 绘制外边界
        x_ring, y_ring = ring_polygon.exterior.xy
        ax2.fill(x_ring, y_ring, alpha=0.3, fc='lightblue', ec='blue', linewidth=2)

        # 如果有内孔，绘制内边界
        for interior in ring_polygon.interiors:
            xi, yi = interior.coords.xy
            ax2.fill(xi, yi, fc='white', ec='red', linewidth=1)
    elif ring_polygon.geom_type == 'MultiPolygon':
        # 处理多个多边形的情况
        for poly in ring_polygon.geoms:
            x_ring, y_ring = poly.exterior.xy
            ax2.fill(x_ring, y_ring, alpha=0.3, fc='lightblue', ec='blue', linewidth=2)
            for interior in poly.interiors:
                xi, yi = interior.coords.xy
                ax2.fill(xi, yi, fc='white', ec='red', linewidth=1)

    # 绘制原始轮廓
    if hasattr(contour, 'xy'):
        ax2.plot(*contour.xy, 'r-', linewidth=2, label='刀具路径')
    else:
        x, y = contour.coords.xy
        ax2.plot(x, y, 'r-', linewidth=2, label='刀具路径')

    ax2.legend()
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 输出信息
    print("=" * 60)
    print("环状区域信息:")
    print(f"刀具直径: {tool_diameter}")
    print(f"环状区域面积: {ring_polygon.area:.4f}")
    print(f"环状区域外周长: {ring_polygon.exterior.length:.4f}")
    if ring_polygon.interiors:
        print(f"环状区域内周长: {ring_polygon.interiors[0].length:.4f}")
    print(f"材料去除宽度: {tool_diameter}")

    return ring_polygon, contour


# 示例：生成单个线段的环状区域
def create_single_line_ring_example():
    """创建单线段环状区域的示例"""
    line_start = (0, 0)
    line_end = (10, 5)
    tool_diameter = 2.0

    # 获取环状区域
    ring_polygon, line = get_tool_path_ring(line_start, line_end, tool_diameter)

    # 可视化
    fig, ax = plt.subplots(figsize=(10, 8))

    # 绘制环状区域
    if ring_polygon.geom_type == 'Polygon':
        x_ring, y_ring = ring_polygon.exterior.xy
        ax.fill(x_ring, y_ring, alpha=0.3, fc='lightblue', ec='blue', linewidth=2)
    elif ring_polygon.geom_type == 'MultiPolygon':
        for poly in ring_polygon.geoms:
            x_ring, y_ring = poly.exterior.xy
            ax.fill(x_ring, y_ring, alpha=0.3, fc='lightblue', ec='blue', linewidth=2)

    # 绘制原始线段
    ax.plot(*line.xy, 'r-', linewidth=3, label='刀具中心路径')

    # 标记起点和终点
    ax.plot(line_start[0], line_start[1], 'ro', markersize=8, label='起点')
    ax.plot(line_end[0], line_end[1], 'go', markersize=8, label='终点')

    ax.set_title(f'线段环状切割区域 (刀具直径: {tool_diameter})')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()

    print("\n" + "=" * 60)
    print("单线段环状区域信息:")
    print(f"线段: {line_start} -> {line_end}")
    print(f"刀具直径: {tool_diameter}")
    print(f"环状区域面积: {ring_polygon.area:.4f}")

    return ring_polygon, line


if __name__ == "__main__":
    # 运行示例
    print("示例1: 矩形环状切割区域")
    ring1, contour1 = create_rectangle_ring_example()

    # print("\n\n示例2: 单线段环状切割区域")
    # ring2, line2 = create_single_line_ring_example()

    plt.show()