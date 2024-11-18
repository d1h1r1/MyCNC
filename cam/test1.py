import numpy as np
from stl import mesh
import matplotlib.pyplot as plt


class ToolpathGenerator:
    def __init__(self, stl_file, slice_height=1.0):
        """初始化刀路生成器"""
        # 读取 STL 文件
        self.model = mesh.Mesh.from_file(stl_file)
        self.slice_height = slice_height
        self.toolpaths = []  # 保存生成的刀路

    def generate_toolpath(self):
        """生成刀路"""
        # 获取模型的 Z 高度范围
        vertices = self.model.vectors.reshape(-1, 3)
        z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()

        # 按切片高度划分层
        slices = np.arange(z_min, z_max, self.slice_height)

        for z in slices:
            # 提取当前 Z 平面的轮廓
            slice_edges = self._get_slice_edges(z)
            if slice_edges:
                # 将边转化为点集（可以进一步连接为线段）
                slice_points = [point for edge in slice_edges for point in edge]
                self.toolpaths.append(slice_points)

    def _get_slice_edges(self, z):
        """获取某个 Z 切片与模型的交线"""
        edges = []
        for triangle in self.model.vectors:
            # 检查三角形与 Z 平面的交点
            intersect_points = self._intersect_triangle_with_plane(triangle, z)
            if len(intersect_points) == 2:  # 只有两点才能形成一条边
                edges.append(intersect_points)
        return edges

    def _intersect_triangle_with_plane(self, triangle, z):
        """计算三角形与平面 Z = z 的交点"""
        intersect_points = []
        for i in range(3):
            p1 = triangle[i]
            p2 = triangle[(i + 1) % 3]
            if (p1[2] <= z <= p2[2]) or (p2[2] <= z <= p1[2]):
                # 线性插值计算交点
                t = (z - p1[2]) / (p2[2] - p1[2])
                intersection = p1 + t * (p2 - p1)
                intersect_points.append(intersection[:2])  # 仅返回 X, Y 坐标
        return intersect_points

    def save_toolpath(self, file_name):
        """将刀路保存为文件（示例：简单保存为 CSV）"""
        with open(file_name, "w") as f:
            for layer_index, layer_points in enumerate(self.toolpaths):
                f.write(f"# Layer {layer_index}\n")
                for point in layer_points:
                    f.write(f"{point[0]},{point[1]}\n")

    def plot_toolpath(self):
        """绘制刀路"""
        plt.figure(figsize=(8, 6))
        for layer_index, layer_points in enumerate(self.toolpaths):
            if len(layer_points) > 0:
                points = np.array(layer_points)
                plt.scatter(points[:, 0], points[:, 1], label=f"Layer {layer_index}")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Generated Toolpath")
        plt.legend()
        plt.show()


# 示例使用
if __name__ == "__main__":
    stl_file = "../file/elephant.STL"  # 替换为实际的 STL 文件路径
    generator = ToolpathGenerator(stl_file, slice_height=1.0)
    generator.generate_toolpath()
    generator.save_toolpath("toolpath.csv")  # 将刀路保存为 CSV
    generator.plot_toolpath()  # 可视化刀路
