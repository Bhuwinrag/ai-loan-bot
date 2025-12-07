import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:5002/api/chat"
SESSION_ID = str(uuid.uuid4())

def send_message(message, metadata=None):
    payload = {"message": message, "session_id": SESSION_ID}
    if metadata:
        payload["metadata"] = metadata
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE_URL, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["response_message"]
    except Exception as e:
        return f"Error: {e}"

print(f"--- Starting Verification Session: {SESSION_ID} ---")

# 1. Start / Name
print("\n1. Sending Name: ParsingTestUser")
resp = send_message("ParsingTestUser")
print(f"Bot: {resp}")

# 2. Send Amount Only
print("\n2. Sending Amount: 30000")
resp = send_message("30000")
print(f"Bot: {resp}")

if "how many months" in resp.lower() or "duration" in resp.lower():
    print("SUCCESS: Bot asked for tenure.")
else:
    print("FAILURE: Bot did not ask for tenure.")

# 3. Send Tenure
print("\n3. Sending Tenure: 12")
resp = send_message("12")
print(f"Bot: {resp}")

if "30,000" in resp and "12 months" in resp:
    print("SUCCESS: Bot confirmed correct details.")
else:
    print("FAILURE: Bot confirmation incorrect.")
