import json

with open("11.json") as f:
    data = json.load(f)

for i in data:
    print(i['content'])
