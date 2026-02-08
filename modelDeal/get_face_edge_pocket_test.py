import numpy as np
import trimesh
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union, polygonize
import warnings

warnings.filterwarnings('ignore')


def keep_vertical_upward_faces(stl_path, min_z_normal=0.99):
    """只保留法向量垂直向上的面"""
    mesh = trimesh.load(stl_path)

    if not hasattr(mesh, 'face_normals') or mesh.face_normals is None:
        mesh.face_normals = mesh.face_normals

    mask = mesh.face_normals[:, 2] > min_z_normal

    if np.sum(mask) == 0:
        print(f"警告: 没有找到法向量z分量 > {min_z_normal}的面")
        return None

    filtered_faces = mesh.faces[mask]

    vertical_upward_mesh = trimesh.Trimesh(
        vertices=mesh.vertices,
        faces=filtered_faces,
        process=False
    )

    return vertical_upward_mesh


def get_precise_cutting_regions(mesh, target_height, tolerance=0.01):
    """
    获取指定高度的精确加工区域

    参数:
    mesh: 垂直向上的面网格
    target_height: 目标加工高度
    tolerance: 高度容差

    返回:
    List[Polygon]: 加工区域的多边形列表（每个独立区域一个多边形）
    """
    print(f"\n提取高度 {target_height:.3f} 的精确加工区域...")

    # 1. 找到该高度附近的面
    centers = mesh.triangles_center
    z_coords = centers[:, 2]

    # 找到目标高度附近的面
    height_mask = np.abs(z_coords - target_height) < tolerance
    face_indices = np.where(height_mask)[0]

    if len(face_indices) == 0:
        print(f"  警告: 在高度 {target_height:.3f} 附近没有找到面")
        return []

    print(f"  找到 {len(face_indices)} 个面在目标高度附近")

    # 2. 创建该高度层的子网格
    layer_mesh = trimesh.Trimesh(
        vertices=mesh.vertices,
        faces=mesh.faces[face_indices],
        process=False
    )

    # 3. 检测连通组件（分离不连通的区域）
    print("  检测连通区域...")
    regions = []

    try:
        # 使用trimesh的连通组件检测
        connected_meshes = layer_mesh.split(only_watertight=False)

        for comp_idx, comp_mesh in enumerate(connected_meshes):
            if len(comp_mesh.faces) == 0:
                continue

            # 为每个连通组件提取精确区域
            region_polygons = extract_precise_region_from_mesh(
                comp_mesh, target_height, comp_idx
            )

            if region_polygons:
                regions.extend(region_polygons)
                print(f"    区域 {comp_idx + 1}: 找到 {len(region_polygons)} 个多边形")

    except Exception as e:
        print(f"  连通检测失败: {e}")
        # 回退：将整个层作为一个区域
        region_polygons = extract_precise_region_from_mesh(
            layer_mesh, target_height, 0
        )
        regions.extend(region_polygons)

    return regions


def extract_precise_region_from_mesh(mesh, target_height, region_id):
    """
    从网格中提取精确的加工区域多边形
    """
    # 方法1: 使用水平截面
    try:
        # 创建与目标高度平行的截面
        section = mesh.section(
            plane_normal=[0, 0, 1],
            plane_origin=[0, 0, target_height]
        )

        if section is not None and len(section.entities) > 0:
            # 转换为2D多边形
            try:
                section_2d, transform = section.to_planar()
                if section_2d is not None:
                    polygons = []

                    # 提取所有多边形
                    for polygon in section_2d.polygons_full:
                        if polygon.is_valid and polygon.area > 1e-10:
                            polygons.append(polygon)

                    if polygons:
                        print(f"      区域 {region_id + 1}: 截面法成功，找到 {len(polygons)} 个多边形")
                        return polygons
            except:
                pass
    except:
        pass

    # 方法2: 使用面片投影（更精确，适合CAM加工）
    print(f"      区域 {region_id + 1}: 使用面片投影法...")
    return extract_region_by_triangle_projection(mesh, target_height)


def extract_region_by_triangle_projection(mesh, target_height):
    """
    通过三角形投影和合并获取精确区域
    这是CAM加工最常用的方法
    """
    # 收集所有多边形的线段
    all_segments = []

    for face in mesh.faces:
        triangle = [
            mesh.vertices[face[0]],
            mesh.vertices[face[1]],
            mesh.vertices[face[2]]
        ]

        # 处理三角形与平面的关系
        segments = process_triangle_for_contour(triangle, target_height)
        all_segments.extend(segments)

    if not all_segments:
        return []

    # 从线段构建多边形
    try:
        polygons = list(polygonize(all_segments))
    except:
        # 如果polygonize失败，使用备用方法
        polygons = []
        try:
            merged = unary_union(all_segments)
            if merged.geom_type == 'Polygon':
                polygons = [merged]
            elif merged.geom_type == 'MultiPolygon':
                polygons = list(merged.geoms)
            elif merged.geom_type == 'GeometryCollection':
                # 从集合中提取多边形
                for geom in merged.geoms:
                    if geom.geom_type == 'Polygon':
                        polygons.append(geom)
        except:
            return []

    # 过滤有效多边形
    valid_polygons = []
    for poly in polygons:
        if poly.is_valid and poly.area > 1e-10:
            valid_polygons.append(poly)

    return valid_polygons


def process_triangle_for_contour(triangle_vertices, target_height):
    """
    处理单个三角形，返回与目标高度相关的轮廓线段
    """
    points = np.array(triangle_vertices)
    z_vals = points[:, 2]
    max_z = max(z_vals)
    min_z = min(z_vals)

    segments = []

    # 情况1: 整个三角形在平面上方
    if min_z > target_height:
        # 投影到XY平面，添加三角形的三条边
        for i in range(3):
            j = (i + 1) % 3
            p1 = points[i, :2]
            p2 = points[j, :2]
            segments.append(LineString([p1, p2]))

    # 情况2: 三角形与平面相交
    elif max_z > target_height and min_z < target_height:
        # 找出与平面相交的边
        intersection_points = []

        for i in range(3):
            j = (i + 1) % 3
            p1 = points[i]
            p2 = points[j]
            z1 = p1[2]
            z2 = p2[2]

            # 如果线段与平面相交
            if (z1 - target_height) * (z2 - target_height) < 0:
                # 计算交点
                t = (target_height - z1) / (z2 - z1)
                x = p1[0] + t * (p2[0] - p1[0])
                y = p1[1] + t * (p2[1] - p1[1])
                intersection_points.append((x, y))

        # 如果有2个交点，添加线段
        if len(intersection_points) == 2:
            segments.append(LineString(intersection_points))

    return segments


def get_all_cutting_heights(mesh, min_distance=1.0):
    """
    获取所有需要加工的高度

    参数:
    mesh: 垂直向上的面网格
    min_distance: 最小加工层高

    返回:
    List[float]: 加工高度列表
    """
    centers = mesh.triangles_center
    z_coords = centers[:, 2]

    # 获取唯一高度（排序）
    unique_z = np.unique(z_coords)

    # 按最小距离筛选高度
    cutting_heights = []
    current_height = None

    for z in sorted(unique_z):
        if current_height is None or abs(z - current_height) >= min_distance:
            cutting_heights.append(z)
            current_height = z

    print(f"找到 {len(cutting_heights)} 个加工高度:")
    for i, height in enumerate(cutting_heights):
        # 统计该高度的面数
        mask = np.abs(z_coords - height) < 0.01
        face_count = np.sum(mask)
        print(f"  高度 {i + 1}: {height:.3f} ({face_count} 个面)")

    return cutting_heights


def generate_cam_path(region_polygons, tool_diameter=10.0, stepover=0.5):
    """
    为加工区域生成CAM路径

    参数:
    region_polygons: 加工区域多边形列表
    tool_diameter: 刀具直径 (mm)
    stepover: 步距比例 (0.0-1.0)

    返回:
    Dict: 包含路径信息的字典
    """
    tool_radius = tool_diameter / 2.0
    step_distance = tool_diameter * stepover

    all_paths = []

    for poly_idx, polygon in enumerate(region_polygons):
        if not polygon.is_valid or polygon.area < 1e-10:
            continue

        # 1. 外轮廓偏移（粗加工）
        try:
            # 偏移一个刀具半径（加工到轮廓）
            offset_polygon = polygon.buffer(-tool_radius)

            if offset_polygon.is_empty:
                # 区域太小，无法加工
                continue

            path_info = {
                'region_id': poly_idx,
                'outer_contour': list(polygon.exterior.coords),
                'machining_area': offset_polygon,
                'area': polygon.area,
                'offset_area': offset_polygon.area if hasattr(offset_polygon, 'area') else 0
            }

            # 2. 生成平行线路径（精加工）
            if offset_polygon.area > 0:
                # 获取区域边界
                bounds = offset_polygon.bounds  # (min_x, min_y, max_x, max_y)

                # 生成平行线
                scan_lines = []
                x_start = bounds[0]
                x_end = bounds[2]
                y_start = bounds[1]
                y_end = bounds[3]

                # 简单示例：生成X方向的平行线
                current_y = y_start
                while current_y <= y_end:
                    # 创建水平线
                    line = LineString([(x_start, current_y), (x_end, current_y)])

                    # 计算与多边形的交点
                    intersection = line.intersection(offset_polygon)

                    if not intersection.is_empty:
                        if intersection.geom_type == 'MultiLineString':
                            for line_seg in intersection.geoms:
                                if line_seg.length > 0:
                                    scan_lines.append(list(line_seg.coords))
                        elif intersection.geom_type == 'LineString':
                            scan_lines.append(list(intersection.coords))

                    current_y += step_distance

                path_info['scan_lines'] = scan_lines

            all_paths.append(path_info)

        except Exception as e:
            print(f"  生成区域 {poly_idx + 1} 的路径时出错: {e}")

    return all_paths


def visualize_cam_regions(cutting_data):
    """
    可视化加工区域和路径
    """
    if not cutting_data:
        print("没有加工数据可显示")
        return

    print(f"\n可视化 {len(cutting_data)} 个加工层...")

    # 计算需要多少个子图
    num_layers = len(cutting_data)
    cols = min(3, num_layers)
    rows = (num_layers + cols - 1) // cols

    fig = plt.figure(figsize=(5 * cols, 5 * rows))

    for layer_idx, layer_data in enumerate(cutting_data):
        height = layer_data['height']
        regions = layer_data['regions']
        cam_paths = layer_data.get('cam_paths', [])

        ax = fig.add_subplot(rows, cols, layer_idx + 1)

        # 绘制加工区域
        for region_idx, region in enumerate(regions):
            if region.is_valid:
                # 绘制区域边界
                x, y = region.exterior.xy
                ax.plot(x, y, 'b-', linewidth=2, alpha=0.8)

                # 填充区域
                ax.fill(x, y, 'blue', alpha=0.2)

                # 标记区域编号
                centroid = region.centroid
                ax.text(centroid.x, centroid.y, f'R{region_idx + 1}',
                        fontsize=10, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

        # 绘制CAM路径（如果存在）
        for path_info in cam_paths:
            # 绘制外轮廓
            if 'outer_contour' in path_info:
                contour = np.array(path_info['outer_contour'])
                ax.plot(contour[:, 0], contour[:, 1], 'r--', linewidth=1, alpha=0.5)

            # 绘制平行线路径
            if 'scan_lines' in path_info:
                for line_coords in path_info['scan_lines']:
                    line_array = np.array(line_coords)
                    ax.plot(line_array[:, 0], line_array[:, 1], 'g-', linewidth=0.5, alpha=0.6)

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title(f'加工层 {layer_idx + 1}\n高度: {height:.3f}mm\n区域数: {len(regions)}')
        ax.axis('equal')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def export_cam_data(cutting_data, output_dir="cam_output"):
    """
    导出CAM加工数据
    """
    import os
    import json
    import csv

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n导出CAM数据到目录: {output_dir}")

    # 1. 导出JSON格式的总数据
    json_data = []

    for layer_idx, layer_data in enumerate(cutting_data):
        height = layer_data['height']
        regions = layer_data['regions']

        layer_info = {
            'layer_index': layer_idx,
            'height_mm': float(height),
            'region_count': len(regions),
            'regions': []
        }

        for region_idx, region in enumerate(regions):
            if region.is_valid:
                # 获取多边形坐标
                if region.geom_type == 'Polygon':
                    exterior = list(region.exterior.coords)
                    interiors = [list(interior.coords) for interior in region.interiors] if region.interiors else []

                    region_info = {
                        'region_index': region_idx,
                        'area_mm2': float(region.area),
                        'perimeter_mm': float(region.length),
                        'centroid': [float(region.centroid.x), float(region.centroid.y)],
                        'exterior_points': exterior,
                        'interior_holes': interiors
                    }

                    layer_info['regions'].append(region_info)

        json_data.append(layer_info)

    # 保存JSON文件
    json_file = os.path.join(output_dir, "cam_layers.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"  JSON数据已保存: {json_file}")

    # 2. 为每个层导出CSV文件
    for layer_idx, layer_data in enumerate(cutting_data):
        height = layer_data['height']
        regions = layer_data['regions']

        csv_file = os.path.join(output_dir, f"layer_{layer_idx + 1}_height_{height:.3f}.csv")

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # 写入头部
            writer.writerow(['region_id', 'point_id', 'x_mm', 'y_mm', 'z_mm'])

            # 写入数据
            point_id = 0
            for region_idx, region in enumerate(regions):
                if region.is_valid:
                    # 外轮廓
                    for coord in region.exterior.coords:
                        writer.writerow([region_idx, point_id, coord[0], coord[1], height])
                        point_id += 1

                    # 内孔（如果有）
                    if region.interiors:
                        for hole_idx, interior in enumerate(region.interiors):
                            for coord in interior.coords:
                                writer.writerow([f'{region_idx}_hole{hole_idx}', point_id, coord[0], coord[1], height])
                                point_id += 1

        print(f"  层 {layer_idx + 1} CSV已保存: {os.path.basename(csv_file)}")

    # 3. 导出G代码示例（简单版本）
    gcode_file = os.path.join(output_dir, "sample_gcode.nc")
    generate_sample_gcode(cutting_data, gcode_file)

    print(f"  示例G代码已保存: {gcode_file}")

    return output_dir


def generate_sample_gcode(cutting_data, output_file, feed_rate=1000, plunge_rate=300):
    """
    生成示例G代码
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("; CAM加工G代码 - 自动生成\n")
        f.write("; 刀具直径: 10mm\n")
        f.write("; 安全高度: 50mm\n\n")

        f.write("G90 ; 绝对坐标\n")
        f.write("G21 ; 毫米模式\n")
        f.write("G17 ; XY平面\n")
        f.write("G40 ; 取消刀具半径补偿\n")
        f.write("G49 ; 取消刀具长度补偿\n")
        f.write("G80 ; 取消固定循环\n")
        f.write("G94 ; 每分钟进给\n\n")

        f.write("; 快速移动到安全高度\n")
        f.write("G0 Z50.000\n\n")

        for layer_idx, layer_data in enumerate(cutting_data):
            height = layer_data['height']
            regions = layer_data['regions']

            f.write(f"; 第{layer_idx + 1}层 - 加工高度: {height:.3f}mm\n")

            for region_idx, region in enumerate(regions):
                if region.is_valid:
                    f.write(f"; 区域 {region_idx + 1}\n")

                    # 移动到起点
                    first_point = region.exterior.coords[0]
                    f.write(f"G0 X{first_point[0]:.3f} Y{first_point[1]:.3f}\n")
                    f.write(f"G0 Z{height + 5:.3f} ; 接近高度\n")
                    f.write(f"G1 Z{height:.3f} F{plunge_rate} ; 下刀\n")

                    # 加工轮廓
                    f.write(f"G1 X{first_point[0]:.3f} Y{first_point[1]:.3f} F{feed_rate}\n")

                    for i in range(1, len(region.exterior.coords)):
                        point = region.exterior.coords[i]
                        f.write(f"G1 X{point[0]:.3f} Y{point[1]:.3f}\n")

                    # 回到起点
                    f.write(f"G1 X{first_point[0]:.3f} Y{first_point[1]:.3f}\n")

                    # 抬刀
                    f.write(f"G0 Z{height + 5:.3f}\n")
                    f.write("G0 Z50.000 ; 安全高度\n\n")

        f.write("; 程序结束\n")
        f.write("M30\n")


def main_cam_processing(stl_path="test.stl", min_layer_distance=1.0):
    """
    主函数：CAM加工区域处理
    """
    print("=" * 60)
    print("CAM加工区域提取")
    print("=" * 60)

    # 1. 提取垂直向上的面
    print("\n1. 提取垂直向上的面...")
    mesh = keep_vertical_upward_faces(stl_path)

    if mesh is None:
        print("错误: 没有找到垂直向上的面！")
        return []

    print(f"  找到 {len(mesh.faces)} 个垂直向上的面")

    # 2. 获取所有加工高度
    print("\n2. 确定加工高度...")
    cutting_heights = get_all_cutting_heights(mesh, min_layer_distance)

    if not cutting_heights:
        print("错误: 没有找到加工高度！")
        return []

    # 3. 为每个高度提取精确加工区域
    print("\n3. 提取精确加工区域...")
    all_cutting_data = []

    for height_idx, target_height in enumerate(cutting_heights):
        print(f"\n  处理高度 {height_idx + 1}/{len(cutting_heights)}: {target_height:.3f}")

        # 获取该高度的精确加工区域
        regions = get_precise_cutting_regions(mesh, target_height)

        if regions:
            print(f"  成功提取 {len(regions)} 个加工区域")

            # 计算总面积
            total_area = sum(region.area for region in regions if region.is_valid)

            cutting_data = {
                'height': target_height,
                'regions': regions,
                'region_count': len(regions),
                'total_area': total_area
            }

            # 可选：生成CAM路径
            if len(regions) > 0:
                cam_paths = generate_cam_path(regions)
                cutting_data['cam_paths'] = cam_paths
                print(f"  生成了 {len(cam_paths)} 个加工路径")

            all_cutting_data.append(cutting_data)
        else:
            print(f"  警告: 高度 {target_height:.3f} 没有找到加工区域")

    if not all_cutting_data:
        print("\n错误: 没有提取到任何加工数据！")
        return []

    print(f"\n成功处理 {len(all_cutting_data)} 个加工层")

    # 4. 可视化
    print("\n4. 可视化加工区域...")
    visualize_cam_regions(all_cutting_data)

    # 5. 导出数据
    print("\n5. 导出CAM加工数据...")
    export_dir = export_cam_data(all_cutting_data)

    # 6. 打印摘要
    print("\n" + "=" * 60)
    print("CAM数据处理完成")
    print("=" * 60)

    total_regions = sum(data['region_count'] for data in all_cutting_data)
    total_area = sum(data['total_area'] for data in all_cutting_data)

    print(f"\n加工摘要:")
    print(f"  加工层数: {len(all_cutting_data)}")
    print(f"  总区域数: {total_regions}")
    print(f"  总面积: {total_area:.2f} mm²")

    print(f"\n每层详情:")
    for i, data in enumerate(all_cutting_data):
        print(f"  层 {i + 1}: 高度={data['height']:.3f}mm, "
              f"区域={data['region_count']}, "
              f"面积={data['total_area']:.1f}mm²")

    print(f"\n数据已导出到: {export_dir}")
    print("=" * 60)

    return all_cutting_data


def test_single_height(stl_path="test.stl", target_height=10.0):
    """
    测试单个高度的加工区域提取
    """
    print(f"测试单个高度: {target_height}mm")

    mesh = keep_vertical_upward_faces(stl_path)
    if mesh is None:
        return

    regions = get_precise_cutting_regions(mesh, target_height)

    if regions:
        print(f"找到 {len(regions)} 个加工区域")

        # 绘制结果
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # 子图1: 区域显示
        ax1 = axes[0]
        for i, region in enumerate(regions):
            if region.is_valid:
                x, y = region.exterior.xy
                ax1.plot(x, y, linewidth=2, label=f'区域 {i + 1}')
                ax1.fill(x, y, alpha=0.2)

                # 标记质心
                centroid = region.centroid
                ax1.plot(centroid.x, centroid.y, 'ro')
                ax1.text(centroid.x, centroid.y, f'R{i + 1}',
                         fontsize=10, ha='center', va='center')

        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_title(f'加工高度: {target_height}mm')
        ax1.axis('equal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 子图2: 区域统计
        ax2 = axes[1]
        areas = [region.area for region in regions if region.is_valid]
        perimeters = [region.length for region in regions if region.is_valid]

        x_pos = np.arange(len(areas))

        ax2.bar(x_pos - 0.2, areas, 0.4, label='面积 (mm²)', alpha=0.7)
        ax2.bar(x_pos + 0.2, perimeters, 0.4, label='周长 (mm)', alpha=0.7)

        ax2.set_xlabel('区域编号')
        ax2.set_ylabel('数值')
        ax2.set_title('区域几何属性')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f'R{i + 1}' for i in range(len(areas))])
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.show()
    else:
        print("没有找到加工区域")


if __name__ == '__main__':
    stl_file = "test.stl"

    # 方法1: 完整处理所有加工层
    print("方法1: 完整CAM处理流程")
    print("-" * 40)
    cam_data = main_cam_processing(stl_file, min_layer_distance=1.0)

    # 方法2: 测试单个高度
    # print("\n\n方法2: 测试单个高度")
    # print("-" * 40)
    # test_single_height(stl_file, target_height=10.0)  # 修改为你需要的高度