from OCC.Core.BRep import BRep_Tool
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopoDS import TopoDS_Shape
# from OCC.Core.BRepTools import breptools_Write
from OCC.Display.SimpleGui import init_display

# 读取STEP文件
step_reader = STEPControl_Reader()
status = step_reader.ReadFile("../file/多功能钥匙扣.STEP")
if status != 1:
    raise ValueError("Failed to read STEP file")
step_reader.TransferRoots()
shape = step_reader.Shape()  # 获取几何形状

# 提取所有边（轮廓）
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE

edge_explorer = TopExp_Explorer(shape, TopAbs_EDGE)
edges = []
while edge_explorer.More():
    edge = TopoDS_Shape(edge_explorer.Current())
    edges.append(edge)
    curve = BRep_Tool.Curve(edge)
    print(curve)
    edge_explorer.Next()

print(f"Extracted {len(edges)} edges")

# 可视化（可选）
display, start_display, add_menu, add_function = init_display()
display.DisplayShape(shape, update=True)
start_display()