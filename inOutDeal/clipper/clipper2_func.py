import numpy as np
import pyclipper
import pyclipr


# 1️⃣ JoinType（连接方式）
# JoinType 控制 路径角点连接方式，也就是偏移或刀具轨迹在尖角或转角的处理方式。
# JoinType	描述	CNC / CAM 场景
# Round	在角点处做圆角	✅ CNC/激光/水刀偏移，刀具圆角，最安全
# Square	在角点做 90° 方角	❌ 适合矩形加工，或者刀具刚好矩形端
# Miter	延长边交点直到相交（尖角）	⚠ 尖角可能过长 → 适合精确 CAD，但 CNC 刀具可能碰撞

# 2️⃣ EndType（末端处理方式）
# EndType 控制 open path 的末端形状，或闭合 polygon 时对端点的处理。
# EndType	描述	CNC / CAM 场景
# Round	末端做半圆	✅ CNC / 激光，避免尖角压力
# Square	延伸端点成方角	矩形轨迹，刀具直角切割
# Butt	平直结束	最简单端点，直线末端
# Joined	自动连接端点	多段线平滑衔接
# Polygon	多边形闭合端点	偏移 polygon 必须使用

def close_paths(paths):
    """让所有返回路径首尾相同（闭合 polygon）"""
    closed = []
    for path in paths:
        if len(path) > 0:
            if not np.array_equal(path[0], path[-1]):
                path = np.vstack([path, path[0]])  # 追加首点
        closed.append(path)
    return closed


# -------- 工具函数：多边形布尔差集 --------
def clip_difference(subject_paths, clip_paths, scale=1000):
    pc = pyclipr.Clipper()
    pc.scaleFactor = scale
    pc.addPaths(subject_paths, pyclipr.Subject)
    for clip_path in clip_paths:
        area = pyclipper.Area(clip_path)
        if area > 0:
            clip_path = pyclipper.ReversePath(clip_path)
        pc.addPaths([clip_path], pyclipr.Clip)

    # 返回的是 List[List[(x,y)]]
    return close_paths(pc.execute(pyclipr.Difference, pyclipr.FillRule.NonZero))


# -------- 工具函数：offset（buffer(-step)） --------
def offset_polygon(paths, delta, scale=1000):
    po = pyclipr.ClipperOffset()
    po.scaleFactor = scale

    # 全部当成 closed polygon
    # po.addPaths(paths, pyclipr.JoinType.Round, pyclipr.EndType.Polygon)
    po.addPaths(paths, pyclipr.JoinType.Miter, pyclipr.EndType.Polygon)

    return close_paths(po.execute(delta))


# -------- 工具函数：union --------
def clip_union(paths, scale=1000):
    pc = pyclipr.Clipper()
    pc.scaleFactor = scale
    for path in paths:
        for i in path:
            pc.addPath(i, pyclipr.Subject)

    return close_paths(pc.execute(pyclipr.Union, pyclipr.FillRule.EvenOdd))
