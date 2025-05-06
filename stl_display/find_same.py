from shapely.geometry import Polygon
from shapely.ops import unary_union


def merge_similar_contours(contours, similarity_threshold=0.8):
    """
    将相似的轮廓进行合并
    :param contours: 轮廓列表，每个轮廓是 [(x1, y1), (x2, y2), ...]
    :param similarity_threshold: 形状相似度阈值（0~1），大于此值的轮廓会被合并
    :return: 合并后的轮廓列表
    """
    merged_contours = []
    used = set()

    for i, contour1 in enumerate(contours):
        if i in used:
            continue  # 该轮廓已合并，跳过

        poly1 = Polygon(contour1)
        group = [poly1]  # 存放相似的轮廓

        for j, contour2 in enumerate(contours):
            if i != j and j not in used:
                poly2 = Polygon(contour2)
                # 计算 Jaccard 相似度
                intersection = poly1.intersection(poly2).area
                union = poly1.union(poly2).area
                similarity = intersection / union if union > 0 else 0

                if similarity > similarity_threshold:
                    group.append(poly2)
                    used.add(j)

        # 合并相似轮廓
        merged_contours.append(unary_union(group))
        used.add(i)

    return [list(poly.exterior.coords) for poly in merged_contours]  # 转换为点坐标


def jaccard_similarity(contour1, contour2):
    """
    计算两个轮廓的 Jaccard 相似度
    :param contour1: 轮廓 1，格式 [(x1, y1), (x2, y2), ...]
    :param contour2: 轮廓 2，格式 [(x1, y1), (x2, y2), ...]
    :return: 相似度（0~1），1 表示完全相同
    """
    poly1 = Polygon(contour1)
    poly2 = Polygon(contour2)

    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area

    return intersection / union if union != 0 else 0


# 测试数据：两层相似的轮廓
contours = [
    [(0, 0), (10, 0.2), (10, 10), (0, 10)],  # 轮廓1
    [(0, 0.1), (10, 0), (11, 10), (0, 10)],  # 轮廓2（与1相似）
    [(20, 20), (30, 20), (30, 30), (20, 30)]  # 轮廓3（不同）
]

# merged = merge_similar_contours(contours, similarity_threshold=0.9)
# print("合并后的轮廓:", merged)
# print(len(merged))
flag = jaccard_similarity(contours[0], contours[1])
print(flag)
