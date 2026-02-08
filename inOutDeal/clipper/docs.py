import numpy as np
import pyclipr

# 使用元组定义一条路径
path = [(0.0, 0.), (0, 105.1234), (100, 105.1234), (100, 0), (0, 0)]
path2 = [(1.0, 1.0), (1.0, 50), (100, 50), (100, 1.0), (1.0,1.0)]

# 创建一个偏移（offsetting）对象
po = pyclipr.ClipperOffset()

# 设置缩放因子，用于内部整数表示
po.scaleFactor = int(1000)

# 添加路径 —— 注意 endType 参数要使用 Polygon
# 在处理多边形时需要使用 addPaths —— 这是由外轮廓和内孔正确方向的路径组成的列表
po.addPaths([np.array(path)], pyclipr.JoinType.Miter, pyclipr.EndType.Polygon)

# 使用 delta 执行偏移操作
offsetSquare = po.execute(10.0)

# 创建一个布尔裁剪对象
pc = pyclipr.Clipper()
pc.scaleFactor = int(1000)

# 将路径添加到裁剪对象
# subject 和 clip 参数用于区分路径在布尔运算中的角色
# 最后一个参数标记路径是否为开放路径
pc.addPaths(offsetSquare, pyclipr.Subject)
pc.addPath(np.array(path2), pyclipr.Clip)

""" 测试多边形布尔裁剪 """
# 以下返回路径列表
out  = pc.execute(pyclipr.Intersection, pyclipr.FillRule.EvenOdd)
out2 = pc.execute(pyclipr.Union, pyclipr.FillRule.EvenOdd)
out3 = pc.execute(pyclipr.Difference, pyclipr.FillRule.EvenOdd)
out4 = pc.execute(pyclipr.Xor, pyclipr.FillRule.EvenOdd)

# 使用 execute2 会返回 PolyTree 结构，它提供路径的层次信息
# 能判断路径是外轮廓还是内孔
outB = pc.execute2(pyclipr.Intersection, pyclipr.FillRule.EvenOdd)

# 等效名称 executeTree
outB = pc.executeTree(pyclipr.Intersection, pyclipr.FillRule.EvenOdd)

""" 测试开放路径裁剪 """
# Pyclipr 可以裁剪开放路径，保持与 Clipper2 一致
pc2 = pyclipr.Clipper()
pc2.scaleFactor = int(1e5)

# 开放路径作为 subject 添加（最后参数 True）
pc2.addPath(((40,-10),(50,130)), pyclipr.Subject, True)

# 裁剪对象通常是多边形
pc2.addPaths(offsetSquare, pyclipr.Clip, False)

""" 测试带选项的开放路径裁剪返回类型 """
# returnOpenPaths=True 会返回开放路径，仅在 Intersection 最佳
outC = pc2.execute(pyclipr.Intersection, pyclipr.FillRule.NonZero)
outC2, openPathsC = pc2.execute(pyclipr.Intersection, pyclipr.FillRule.NonZero, returnOpenPaths=True)

outD = pc2.execute2(pyclipr.Intersection,  pyclipr.FillRule.NonZero)
outD2, openPathsD = pc2.execute2(pyclipr.Intersection,  pyclipr.FillRule.NonZero, returnOpenPaths=True)

# 绘制结果
pathPoly = np.array(path)

import matplotlib.pyplot as plt
plt.figure()
plt.axis('equal')

# 绘制原始多边形
plt.fill(pathPoly[:,0], pathPoly[:,1], 'b', alpha=0.1, linewidth=1.0, linestyle='dashed', edgecolor='#000')

# 绘制偏移后的多边形
plt.fill(offsetSquare[0][:, 0], offsetSquare[0][:, 1], linewidth=1.0, linestyle='dashed', edgecolor='#333', facecolor='none')

# 绘制交集结果
plt.fill(out[0][:, 0], out[0][:, 1], facecolor='#75507b')

# 绘制开放路径的交集
plt.plot(openPathsC[0][:,0], openPathsC[0][:,1], color='#222', linewidth=1.0, linestyle='dashed', marker='.', markersize=20.0)

plt.show()
