from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS_Face

# 加载 STEP 文件
reader = STEPControl_Reader()
status = reader.ReadFile("../file/myhand.step")

if status == 1:
    raise Exception("无法读取 STEP 文件")

reader.TransferRoots()
shape = reader.Shape()

# 提取所有面
explorer = TopExp_Explorer(shape, TopAbs_FACE)

faces = []
while explorer.More():
    face = TopoDS_Face(explorer.Current())  # 直接构造，无需 DownCast
    faces.append(face)
    explorer.Next()

print(f"提取到的面数量：{len(faces)}")
