import json

all_str = """[PRB:-153.339,-77.775,-28.480:1]
ok
ok
[PRB:-153.339,-77.775,-28.481:1]
ok
ok"""
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
print(txt)
data_list = json.loads(txt)
print(data_list)
