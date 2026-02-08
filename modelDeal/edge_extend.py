import numpy as np
from shapely.geometry import Polygon, Point, LineString
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import trimesh


# 首先重新定义扇形检测扩展函数
def sector_based_extension(polygon, other_polygons, tool_radius, angle_range=60, max_extension=None):
    """
    基于扇形检测的局部扩展

    参数:
    polygon: 原始多边形 (Shapely Polygon)
    other_polygons: 同一层的其他多边形列表
    tool_radius: 刀具半径 (mm)
    angle_range: 检测扇形的角度范围 (度)
    max_extension: 最大扩展距离 (mm)

    返回:
    Polygon: 扩展后的多边形
    """
    if not polygon.is_valid or not polygon.exterior:
        return polygon

    if max_extension is None:
        max_extension = tool_radius * 3  # 默认最大扩展3倍刀具半径

    # 获取原始多边形顶点
    original_points = np.array(polygon.exterior.coords)[:-1]
    n_points = len(original_points)

    # 转换为弧度
    angle_rad = np.deg2rad(angle_range)

    # 收集所有障碍物的点（用于KDTree快速查询）
    obstacle_points = []
    for obs_poly in other_polygons:
        if obs_poly.is_valid and obs_poly != polygon:
            if obs_poly.exterior:
                points = np.array(obs_poly.exterior.coords)[:-1]
                obstacle_points.extend(points.tolist())

    # 创建KDTree（如果有障碍物）
    obstacle_kdtree = None
    if obstacle_points:
        obstacle_kdtree = KDTree(obstacle_points)

    extended_points = []

    # 对每个顶点进行处理
    for i in range(n_points):
        p_current = original_points[i]

        # 获取前后相邻点
        p_prev = original_points[(i - 1) % n_points]
        p_next = original_points[(i + 1) % n_points]

        # 计算两条边的向量
        v1 = p_current - p_prev  # 从前一点到当前点的向量
        v2 = p_next - p_current  # 从当前点到后一点的向量

        # 归一化
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm > 0:
            v1_unit = v1 / v1_norm
        else:
            v1_unit = v1

        if v2_norm > 0:
            v2_unit = v2 / v2_norm
        else:
            v2_unit = v2

        # 计算角平分线（平均方向）
        bisector = v1_unit + v2_unit
        bisector_norm = np.linalg.norm(bisector)

        if bisector_norm > 0:
            # 计算基础法线方向（垂直）
            base_normal = np.array([-bisector[1], bisector[0]])
            base_normal = base_normal / np.linalg.norm(base_normal)
        else:
            # 如果角平分线为零（直线情况），使用边的垂直方向
            tangent = v2_unit if v2_norm > 0 else v1_unit
            base_normal = np.array([-tangent[1], tangent[0]])

        # 确保法线指向外侧
        test_point = Point(p_current[0] + base_normal[0] * 0.1,
                           p_current[1] + base_normal[1] * 0.1)
        if polygon.contains(test_point):
            base_normal = -base_normal

        # 扇形检测
        best_direction = base_normal.copy()
        max_free_distance = max_extension  # 初始化为最大扩展距离

        if obstacle_kdtree and len(obstacle_points) > 0:
            # 在扇形角度范围内采样多个方向
            n_samples = 11  # 采样点数量（奇数，包含中间方向）
            sample_angles = np.linspace(-angle_rad / 2, angle_rad / 2, n_samples)

            # 评估每个方向
            for angle_offset in sample_angles:
                # 旋转基础法线
                cos_a = np.cos(angle_offset)
                sin_a = np.sin(angle_offset)

                rotated_normal = np.array([
                    base_normal[0] * cos_a - base_normal[1] * sin_a,
                    base_normal[0] * sin_a + base_normal[1] * cos_a
                ])

                # 在这个方向上查找障碍物
                # 查询当前点附近的所有障碍点
                search_radius = max_extension * 2
                indices = obstacle_kdtree.query_ball_point(p_current, search_radius)

                # 计算在这个方向上的最近障碍物距离
                min_obstacle_dist = max_extension * 2  # 初始化为大值

                for idx in indices:
                    if idx < len(obstacle_points):
                        obstacle_pt = obstacle_points[idx]

                        # 计算从当前点到障碍物的向量
                        vec_to_obstacle = np.array(obstacle_pt) - p_current
                        dist_to_obstacle = np.linalg.norm(vec_to_obstacle)

                        if dist_to_obstacle > 0:
                            # 归一化
                            vec_to_obstacle_unit = vec_to_obstacle / dist_to_obstacle

                            # 计算角度差（点积）
                            dot_product = np.dot(rotated_normal, vec_to_obstacle_unit)
                            angle_diff = np.arccos(np.clip(dot_product, -1, 1))

                            # 如果在扇形角度范围内
                            if angle_diff < angle_rad / 2:
                                # 更新最近距离
                                min_obstacle_dist = min(min_obstacle_dist, dist_to_obstacle)

                # 这个方向上的自由距离（减去安全间隙）
                safe_distance = min_obstacle_dist - tool_radius - 0.5  # 0.5mm安全余量
                safe_distance = max(0, safe_distance)  # 确保非负

                # 选择最佳方向（自由距离最大的方向）
                if safe_distance > max_free_distance:
                    max_free_distance = safe_distance
                    best_direction = rotated_normal

        # 确定扩展距离
        extension_distance = min(max_free_distance, max_extension)

        # 应用扩展
        if extension_distance > 0:
            extended_point = p_current + best_direction * extension_distance
            extended_points.append(extended_point)
        else:
            extended_points.append(p_current)

    # 创建扩展后的多边形
    if len(extended_points) >= 3:
        # 闭合多边形
        extended_points.append(extended_points[0])

        try:
            extended_polygon = Polygon(extended_points)
            if extended_polygon.is_valid:
                return extended_polygon
        except:
            pass

    # 如果扩展失败，返回原始多边形
    return polygon


def create_test_polygons():
    """
    创建测试多边形：一个小面旁边有一个大障碍物
    """
    # 1. 小面（需要加工的区域）
    small_polygon = Polygon([
        (0, 0), (10, 0), (10, 5), (0, 5)
    ])

    # 2. 大障碍物（紧挨着小面右边）
    obstacle_polygon = Polygon([
        (10, -5), (30, -5), (30, 10), (10, 10)
    ])

    # 3. 另一个障碍物（在小面左边，但有一定距离）
    left_obstacle = Polygon([
        (-15, 0), (-5, 0), (-5, 5), (-15, 5)
    ])

    # 4. 开放区域（小面上方）
    top_open_area = Polygon([
        (0, 5), (10, 5), (10, 15), (0, 15)
    ])

    return {
        'small_polygon': small_polygon,
        'right_obstacle': obstacle_polygon,
        'left_obstacle': left_obstacle,
        'top_open_area': top_open_area,
        'all_polygons': [small_polygon, obstacle_polygon, left_obstacle, top_open_area]
    }


def visualize_sector_extension(polygon, other_polygons, tool_radius, angle_range=60, max_extension=None):
    """
    可视化扇形检测扩展过程
    """
    if max_extension is None:
        max_extension = tool_radius * 3

    # 执行扇形检测扩展
    extended_polygon = sector_based_extension(
        polygon, other_polygons, tool_radius, angle_range, max_extension
    )

    # 计算加工区域
    machining_area = extended_polygon.buffer(-tool_radius)

    # 创建可视化图形
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # 子图1：原始布局
    ax1 = axes[0, 0]

    # 绘制原始多边形
    if polygon.is_valid:
        x, y = polygon.exterior.xy
        ax1.plot(x, y, 'b-', linewidth=3, label='加工轮廓')
        ax1.fill(x, y, 'blue', alpha=0.2)

    # 绘制障碍物
    for i, obs_poly in enumerate(other_polygons):
        if obs_poly.is_valid:
            x, y = obs_poly.exterior.xy
            color = 'red' if i == 0 else 'orange'
            label = '右侧障碍物' if i == 0 else '其他障碍物'
            ax1.plot(x, y, '-', color=color, linewidth=2, alpha=0.7, label=label)
            ax1.fill(x, y, color, alpha=0.1)

    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_title('原始布局')
    ax1.axis('equal')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')

    # 子图2：扇形检测分析
    ax2 = axes[0, 1]

    # 绘制原始多边形
    if polygon.is_valid:
        x, y = polygon.exterior.xy
        ax2.plot(x, y, 'b-', linewidth=1, alpha=0.3)

    # 绘制顶点和扇形
    original_points = np.array(polygon.exterior.coords)[:-1]

    for i, point in enumerate(original_points):
        # 绘制顶点
        ax2.plot(point[0], point[1], 'bo', markersize=8, alpha=0.5)

        # 获取前后点计算法线
        p_prev = original_points[(i - 1) % len(original_points)]
        p_next = original_points[(i + 1) % len(original_points)]

        v1 = point - p_prev
        v2 = p_next - point

        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm > 0 and v2_norm > 0:
            v1_unit = v1 / v1_norm
            v2_unit = v2 / v2_norm

            # 计算基础法线
            bisector = v1_unit + v2_unit
            if np.linalg.norm(bisector) > 0:
                base_normal = np.array([-bisector[1], bisector[0]])
                base_normal = base_normal / np.linalg.norm(base_normal)

                # 检查方向
                test_pt = Point(point[0] + base_normal[0] * 0.1, point[1] + base_normal[1] * 0.1)
                temp_poly = Polygon(original_points)
                if temp_poly.contains(test_pt):
                    base_normal = -base_normal

                # 绘制扇形
                angles = np.linspace(-angle_range / 2, angle_range / 2, 5)
                for angle in angles:
                    angle_rad = np.deg2rad(angle)
                    cos_a = np.cos(angle_rad)
                    sin_a = np.sin(angle_rad)

                    direction = np.array([
                        base_normal[0] * cos_a - base_normal[1] * sin_a,
                        base_normal[0] * sin_a + base_normal[1] * cos_a
                    ])

                    # 绘制扇形线
                    end_x = point[0] + direction[0] * max_extension
                    end_y = point[1] + direction[1] * max_extension
                    ax2.plot([point[0], end_x], [point[1], end_y],
                             'g-', linewidth=0.5, alpha=0.3)

    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_title(f'扇形检测 (角度范围: ±{angle_range / 2}°)')
    ax2.axis('equal')
    ax2.grid(True, alpha=0.3)

    # 子图3：扩展结果
    ax3 = axes[0, 2]

    # 绘制原始多边形
    if polygon.is_valid:
        x, y = polygon.exterior.xy
        ax3.plot(x, y, 'b-', linewidth=2, alpha=0.5, label='原始轮廓')

    # 绘制扩展多边形
    if extended_polygon.is_valid:
        x, y = extended_polygon.exterior.xy
        ax3.plot(x, y, 'g-', linewidth=3, label='扩展轮廓')
        ax3.fill(x, y, 'green', alpha=0.2)

    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    ax3.set_title('扩展结果')
    ax3.axis('equal')
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    # 子图4：加工区域
    ax4 = axes[1, 0]

    # 绘制原始多边形
    if polygon.is_valid:
        x, y = polygon.exterior.xy
        ax4.plot(x, y, 'b-', linewidth=1, alpha=0.3)

    # 绘制加工区域
    if machining_area.is_valid:
        if machining_area.geom_type == 'Polygon':
            areas = [machining_area]
        elif machining_area.geom_type == 'MultiPolygon':
            areas = list(machining_area.geoms)
        else:
            areas = []

        for area in areas:
            if area.is_valid:
                x, y = area.exterior.xy
                ax4.plot(x, y, 'orange', linewidth=2, label='加工区域')
                ax4.fill(x, y, 'orange', alpha=0.3)

    ax4.set_xlabel('X (mm)')
    ax4.set_ylabel('Y (mm)')
    ax4.set_title('最终加工区域')
    ax4.axis('equal')
    ax4.grid(True, alpha=0.3)
    ax4.legend()

    # 子图5：刀具路径示例
    ax5 = axes[1, 1]

    # 绘制加工区域
    if machining_area.is_valid and machining_area.geom_type == 'Polygon':
        boundary = machining_area.exterior

        # 沿边界采样点
        sample_distance = tool_radius * 1.5
        n_samples = max(5, int(boundary.length / sample_distance))

        for i in range(n_samples):
            dist = i * sample_distance
            point = boundary.interpolate(dist)

            # 绘制刀具
            tool_circle = plt.Circle((point.x, point.y), tool_radius,
                                     color='red', alpha=0.15, ec='red', linewidth=0.5)
            ax5.add_patch(tool_circle)
            ax5.plot(point.x, point.y, 'r.', markersize=3)

    # 绘制原始轮廓作为参考
    if polygon.is_valid:
        x, y = polygon.exterior.xy
        ax5.plot(x, y, 'b-', linewidth=1, alpha=0.5, label='原始轮廓')

    ax5.set_xlabel('X (mm)')
    ax5.set_ylabel('Y (mm)')
    ax5.set_title(f'刀具路径示例 (刀具半径: {tool_radius}mm)')
    ax5.axis('equal')
    ax5.grid(True, alpha=0.3)
    ax5.legend()

    # 子图6：信息面板
    ax6 = axes[1, 2]
    ax6.axis('off')

    # 计算统计信息
    original_area = polygon.area
    extended_area = extended_polygon.area
    machining_area_val = machining_area.area if machining_area.is_valid else 0

    normal_machining_possible = not polygon.buffer(-tool_radius).is_empty
    extended_machining_possible = not machining_area.is_empty

    info_text = f"""
    扇形检测扩展分析

    刀具半径: {tool_radius:.1f} mm
    检测角度: ±{angle_range / 2:.0f}°
    最大扩展: {max_extension:.1f} mm

    面积统计:
      原始轮廓: {original_area:.1f} mm²
      扩展轮廓: {extended_area:.1f} mm²
      加工区域: {machining_area_val:.1f} mm²
      扩展比例: {extended_area / original_area:.1f}x

    加工可行性:
      正常加工: {'✓ 可行' if normal_machining_possible else '✗ 不可行'}
      扩展加工: {'✓ 可行' if extended_machining_possible else '✗ 不可行'}

    扩展效果:
      {get_extension_effect_description(original_area, extended_area,
                                        normal_machining_possible, extended_machining_possible)}
    """

    ax6.text(0.05, 0.95, info_text, transform=ax6.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle('基于扇形检测的局部扩展加工', fontsize=14)
    plt.tight_layout()
    plt.show()

    return extended_polygon, machining_area


def get_extension_effect_description(original_area, extended_area,
                                     normal_possible, extended_possible):
    """获取扩展效果描述"""
    extension_ratio = extended_area / original_area if original_area > 0 else 1

    if not normal_possible and extended_possible:
        if extension_ratio < 1.5:
            return "小范围扩展，主要向上方开放空间延伸"
        elif extension_ratio < 2.5:
            return "中等范围扩展，充分利用开放空间"
        else:
            return "大范围扩展，显著增加加工区域"
    elif normal_possible:
        return "无需扩展，刀具可直接进入"
    else:
        return "即使扩展也无法加工，需要更小刀具"


def apply_sector_extension_to_real_data(mesh, clusters, tool_diameter=6.0):
    """
    将扇形检测扩展应用到实际数据

    参数:
    mesh: 网格数据
    clusters: 聚类结果（每个高度层的面）
    tool_diameter: 刀具直径
    """
    tool_radius = tool_diameter / 2

    print("=" * 60)
    print("扇形检测扩展加工分析")
    print("=" * 60)

    # 遍历每个高度层
    for layer_idx, cluster in enumerate(clusters):
        print(f"\n处理第 {layer_idx + 1} 层:")
        print(f"  高度: {cluster.get('height', 0):.2f} mm")
        print(f"  面数: {len(cluster.get('faces', []))}")

        # 提取该层的所有轮廓多边形
        layer_polygons = extract_polygons_from_cluster(mesh, cluster)

        if len(layer_polygons) == 0:
            print("  没有提取到有效轮廓")
            continue

        print(f"  提取到 {len(layer_polygons)} 个轮廓")

        # 对每个轮廓应用扇形检测扩展
        for poly_idx, polygon in enumerate(layer_polygons):
            print(f"\n  分析轮廓 {poly_idx + 1}:")
            print(f"    面积: {polygon.area:.2f} mm²")

            # 其他轮廓作为障碍物
            other_polygons = [p for j, p in enumerate(layer_polygons) if j != poly_idx]

            # 检查正常加工是否可行
            normal_machining_area = polygon.buffer(-tool_radius)
            can_machine_normal = not normal_machining_area.is_empty

            if can_machine_normal:
                print("    ✓ 可以正常加工")
                continue

            print("    ✗ 无法正常加工，尝试扇形检测扩展...")

            # 应用扇形检测扩展
            extended_polygon = sector_based_extension(
                polygon, other_polygons, tool_radius,
                angle_range=60, max_extension=tool_radius * 3
            )

            # 检查扩展后是否可以加工
            machining_area = extended_polygon.buffer(-tool_radius)
            can_machine_extended = not machining_area.is_empty

            if can_machine_extended:
                extension_ratio = extended_polygon.area / polygon.area
                print(f"    ✓ 扩展加工可行 (扩展 {extension_ratio:.1f} 倍)")

                # 可视化这个轮廓的扩展结果
                print("    生成扩展分析图...")
                visualize_sector_extension(
                    polygon, other_polygons, tool_radius,
                    angle_range=60, max_extension=tool_radius * 3
                )
            else:
                print("    ✗ 即使扩展也无法加工，需要更小刀具")

        # 只处理第一层作为示例
        if layer_idx == 0:
            break


def extract_polygons_from_cluster(mesh, cluster):
    """
    从聚类中提取多边形轮廓
    简化版本，实际使用时需要根据你的数据结构调整
    """
    polygons = []

    # 假设cluster中有face_indices
    face_indices = cluster.get('faces', [])
    if len(face_indices) == 0:
        return polygons

    # 创建该层的子网格
    layer_mesh = trimesh.Trimesh(
        vertices=mesh.vertices,
        faces=mesh.faces[face_indices],
        process=False
    )

    try:
        # 检测连通组件
        connected_components = layer_mesh.split(only_watertight=False)

        for comp in connected_components:
            if len(comp.faces) > 0:
                # 提取轮廓（简化方法）
                # 获取所有顶点并创建凸包
                points_2d = comp.vertices[:, :2]

                if len(points_2d) >= 3:
                    from scipy.spatial import ConvexHull
                    hull = ConvexHull(points_2d)
                    hull_points = points_2d[hull.vertices]

                    # 创建多边形
                    polygon = Polygon(hull_points)
                    if polygon.is_valid and polygon.area > 1e-10:
                        polygons.append(polygon)
    except:
        pass

    return polygons


def sector_extension_demo():
    """
    扇形检测扩展的完整演示
    """
    print("扇形检测扩展演示")
    print("=" * 60)

    # 1. 创建测试场景
    print("1. 创建测试场景...")
    test_data = create_test_polygons()

    small_poly = test_data['small_polygon']
    right_obstacle = test_data['right_obstacle']
    left_obstacle = test_data['left_obstacle']

    print(f"   小面面积: {small_poly.area:.1f} mm²")
    print(f"   右侧障碍物距离: {10.0} mm (紧贴)")
    print(f"   左侧障碍物距离: {5.0} mm")
    print(f"   上方开放空间: 可用")

    # 2. 设置刀具参数
    tool_diameter = 6.0
    tool_radius = tool_diameter / 2

    print(f"\n2. 设置加工参数:")
    print(f"   刀具直径: {tool_diameter} mm")
    print(f"   刀具半径: {tool_radius} mm")

    # 3. 检查正常加工可行性
    print(f"\n3. 检查正常加工可行性:")
    normal_area = small_poly.buffer(-tool_radius)
    can_normal = not normal_area.is_empty
    print(f"   正常加工: {'可行' if can_normal else '不可行'}")

    if can_normal:
        print("   刀具可以直接进入，无需扩展")
        return

    # 4. 应用扇形检测扩展
    print(f"\n4. 应用扇形检测扩展:")
    print(f"   检测角度: ±30°")
    print(f"   最大扩展距离: {tool_radius * 3:.1f} mm")

    # 其他多边形作为障碍物
    other_polygons = [right_obstacle, left_obstacle]

    # 5. 可视化扩展过程
    print(f"\n5. 生成扩展分析图...")
    extended_poly, machining_area = visualize_sector_extension(
        small_poly, other_polygons, tool_radius,
        angle_range=60, max_extension=tool_radius * 3
    )

    # 6. 输出结果
    print(f"\n6. 扩展结果:")
    print(f"   原始面积: {small_poly.area:.1f} mm²")
    print(f"   扩展后面积: {extended_poly.area:.1f} mm²")
    print(f"   扩展比例: {extended_poly.area / small_poly.area:.1f}x")
    print(f"   加工区域面积: {machining_area.area:.1f} mm²")

    if not machining_area.is_empty:
        print(f"   ✅ 扩展加工成功!")
        print(f"   刀具可以部分悬空加工小面")
    else:
        print(f"   ❌ 扩展加工失败")
        print(f"   需要更小直径的刀具")

    print("\n" + "=" * 60)
    print("演示完成")


# 运行演示
if __name__ == "__main__":
    # 运行扇形检测扩展演示
    sector_extension_demo()

    # 如果你有实际数据，可以取消注释下面的代码
    # stl_file = "test.stl"
    # mesh = trimesh.load(stl_file)

    # # 提取垂直向上的面并聚类
    # vertical_mesh = keep_vertical_upward_faces(mesh)  # 需要定义这个函数
    # clusters = cluster_faces_by_height(vertical_mesh)  # 需要定义这个函数

    # # 应用扇形检测扩展
    # apply_sector_extension_to_real_data(vertical_mesh, clusters, tool_diameter=6.0)