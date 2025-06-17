# # 测试数据 2
# # {3:{4:{5:{6:{0:{1:{2:2}}}}}}}

data2 = {3: [0, 1, 2, 4, 5, 6], 4: [0, 1, 2, 5, 6], 5: [0, 1, 2, 6], 6: [0, 1, 2], 0: [1, 2], 1: [2], 2: []}
data2 = {0: [5, 6, 8, 9, 10, 11, 12, 13, 14, 15], 5: [], 6: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: []}
data2 = {0: [1, 2, 3, 4, 5], 1: [4, 5], 2: [3], 3: [], 4: [5], 5: []}

# {0:{1:{4:5},2:{3}}}
# data2 = dict(sorted(data2.items(), key=lambda item: len(item[1]), reverse=True))
# all = {}
# max_list = list(data2.keys())[0]
# end_dist = {}
# end_dist[max_list] = {}
# for i in data2[max_list]:
#     all[i] = data2[i]
# # print(all)
# for i in all.keys():
#     aa = {}
#     # end_dist[max_list] = all[i]
#     print(i)
#     if len(all[i]) != 0:
#         for j in all[i]:
#             # print(end_dist[max_list])
#             # print(j)
#             end_dist[max_list][j] = data2[j]
#     else:
#         end_dist[max_list][i] = 0
#     # print(all[i])
# print(end_dist)


def build_nested_dict(data):
    def find_root_keys(data):
        """找到所有没有被包含的父级轮廓，即根节点"""
        all_children = {c for children in data.values() for c in children}
        return [key for key in data if key not in all_children]

    def build_tree(parent):
        """递归构建树"""
        children = data[parent]
        if not children:
            return parent  # 叶子节点直接返回数字
        tree = {}
        for child in children:
            tree[child] = build_tree(child)
        return tree

    roots = find_root_keys(data)  # 找到所有根节点
    nested_dict = {root: build_tree(root) for root in roots}

    return nested_dict


# 测试数据
data_list = [
    {3: [0, 1, 2, 4, 5, 6], 4: [0, 1, 2, 5, 6], 5: [0, 1, 2, 6], 6: [0, 1, 2], 0: [1, 2], 1: [2], 2: []},
    {0: [1, 2, 3, 4, 5], 1: [4, 5], 2: [3], 3: [], 4: [5], 5: []}
]

for data in data_list:
    print(build_nested_dict(data))
