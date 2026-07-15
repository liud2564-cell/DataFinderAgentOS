import requests

# 测试用户列表API
url = "http://localhost:10010/api/users/list"
params = {
    "page": 1,
    "page_size": 20,
    "search": "",
    "role_id": "",
    "status": ""
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
