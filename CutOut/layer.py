# data = {0: [2], 2: [], 4: [0, 2], 6: [0, 2, 4]}
data = {0: [49, 56, 57], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [50, 51, 52, 53, 54, 55, 58, 59, 60, 61], 49: [], 50: [], 51: [], 52: [], 53: [], 54: [], 55: [], 56: [], 57: [], 58: [], 59: [], 60: [], 61: []}


# 构建一个函数，判断某个节点是否间接包含另一个节点
def is_descendant(parent, target):
    if target in data.get(parent, []):
        return True
    for child in data.get(parent, []):
        if is_descendant(child, target):
            return True
    return False


# 清理每个节点中被其他子节点间接包含的项
def clean_children(node):
    children = data.get(node, [])
    cleaned = []
    for i, c in enumerate(children):
        if not any(is_descendant(other, c) for j, other in enumerate(children) if j != i):
            cleaned.append(c)
    return cleaned


# 构建简化后的树结构
def build_actual_tree(node):
    children = clean_children(node)
    return {node: [build_actual_tree(child) for child in children]}


# 找最外层节点（没有被其他人包含）
all_nodes = set(data.keys())
contained_nodes = set()
for v in data.values():
    contained_nodes.update(v)
top_level_nodes = all_nodes - contained_nodes


# 打印树结构
def print_tree(tree, indent=""):
    for node, children in tree.items():
        print(indent + str(node))
        for child in children:
            print_tree(child, indent + "    ")


# 构建并打印实际嵌套结构
for top in top_level_nodes:
    actual_tree = build_actual_tree(top)
    print_tree(actual_tree)
