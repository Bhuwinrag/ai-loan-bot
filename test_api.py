import urllib.request
import json

url = "http://127.0.0.1:5001/api/chat"
payload = {
    "message": "__START__",
    "session_id": "test_python_urllib_1",
    "metadata": {
        "name": "UrllibUser",
        "amount": "500000"
    }
}
headers = {"Content-Type": "application/json"}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print(f"Response: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
