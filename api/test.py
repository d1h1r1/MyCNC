import requests

data = {
    "q": "hi",
}

files = {
    'file': ('Throwing.stl', open('Throwing.stl', 'rb')),
}
url = "http://127.0.0.1:5000/stl_api"
resp = requests.post(url, data=data, files=files)
print(resp.json())
