# data = {
#     0: [49, 56, 57], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
#     11: [50, 51, 52, 53, 54, 55, 58, 59, 60, 61],
#     49: [], 50: [], 51: [], 52: [], 53: [], 54: [], 55: [],
#     56: [], 57: [], 58: [], 59: [], 60: [], 61: []
# }

# data = {0: [1, 2], 1: [2], 2: [], 3: [0, 1, 2], 6: [0, 1, 2, 3]}
# data = {0: [1, 2], 1: [2], 2: [], 3: [0, 1, 2, 4, 5], 4: [0, 1, 2, 5], 5: [0, 1, 2], 6: [0, 1, 2, 3, 4, 5]}
data = {0: [2], 1: [3, 4], 2: [], 3: [4], 4: [], 5: [0, 1, 2, 3, 4]}


def is_descendant(parent, target):
    if target in data.get(parent, []):
        return True
    for child in data.get(parent, []):
        if is_descendant(child, target):
            return True
    return False


def clean_children(node):
    children = data.get(node, [])
    cleaned = []
    for i, c in enumerate(children):
        if not any(is_descendant(other, c) for j, other in enumerate(children) if j != i):
            cleaned.append(c)
    return cleaned


def build_cleaned_tree_dict():
    cleaned_tree = {}
    for node in data.keys():
        cleaned_tree[node] = clean_children(node)
    return cleaned_tree


# 打印最终结果
import pprint
print(build_cleaned_tree_dict())
# pprint.pprint(build_cleaned_tree_dict())
