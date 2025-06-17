import json

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

# # 三轴粗加工
# data = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1}
#
# files = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/commonPath", files=files, data=data)
# aa = json.dumps(b.json()['modelPath'])
#
# data1 = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1, 'modelPath': aa}
#
# files1 = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/commonPath", files=files1, data=data1)
# print(b.json())

# # 三轴精加工
# data = {'diameter': 6, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1}
#
# files = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/finePath", files=files, data=data)
# aa = json.dumps(b.json()['modelPath'])
#
# data1 = {'diameter': 6, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1, 'modelPath': aa}
#
# files1 = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/finePath", files=files1, data=data1)
# print(b.json())

# # 三轴曲面加工
# data = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1}
#
# files = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/camberPath", files=files, data=data)
# aa = json.dumps(b.json()['modelPath'])
#
# data1 = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
#         'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1, 'modelPath': aa}
#
# files1 = {'file': open("../file/测试件312.stl", 'rb')}
#
# b = requests.post("http://127.0.0.1:5000/api/camberPath", files=files1, data=data1)
# print(b.json())

# 全面雕刻
data = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
        'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1}

files = {'file': open("../file/测试件312.stl", 'rb')}

b = requests.post("http://127.0.0.1:5000/api/parallelPath", files=files, data=data)
aa = json.dumps(b.json()['modelPath'])

data1 = {'diameter': 6, 'zPer': 1, 'stepOver': 3, 'toolNum': 1, 'spindleSpeed': 18000,
        'feed': 3000, "plungeFeed": 3000, 'zDepth': -10, 'toolType': 'endmill', 'materialDepth': -10, 'tabLength': 0, 'tabHigh': 0, 'tabNum': 0, 'tiltAngle': 90, 'margin': 0, 'spray': 1, 'modelPath': aa}

files1 = {'file': open("../file/测试件312.stl", 'rb')}

b = requests.post("http://127.0.0.1:5000/api/parallelPath", files=files1, data=data1)
print(b.json())