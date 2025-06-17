import requests


# # 四轴
# data = {'diameter': 2, 'zPer': 10, 'stepOver': 0.1, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -20, 'toolType': 'ball', 'materialDepth': 20}
#
# # data = {'diameter': 3, 'zPer': 2, 'stepOver': 1.5, 'toolNum': 1, 'spindleSpeed': 18000,
# #         'feed': 3000, "plungeFeed": 3000, 'zDepth': -20, 'toolType': 'endmill', 'materialDepth': 20}
#
# files = {'file': open("xq2.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/rotationPath", files=files, data=data)
# print(b.text)

# 三轴粗加工
data = {'diameter': 2, 'zPer': 10, 'stepOver': 0.1, 'toolNum': 1, 'spindleSpeed': 18000,
        'feed': 3000, "plungeFeed": 3000, 'zDepth': -20, 'toolType': 'ball', 'materialDepth': 20}

# data = {'diameter': 3, 'zPer': 2, 'stepOver': 1.5, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -20, 'toolType': 'endmill', 'materialDepth': 20}

files = {'file': open("xq2.stl", 'rb')}

b = requests.post("http://127.0.0.1:5000/api/rotationPath", files=files, data=data)
print(b.text)