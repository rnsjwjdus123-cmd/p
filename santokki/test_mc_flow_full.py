import sys
import json
import urllib.request
import urllib.error
import time

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473
FLOW_NS = "content20260301052356_064344"

# 1. Update Custom Fields
url_update = "https://api.manychat.com/fb/subscriber/setCustomFields"
req_update = urllib.request.Request(url_update, method="POST")
req_update.add_header("Authorization", f"Bearer {API_KEY}")
req_update.add_header("Content-Type", "application/json")
req_update.add_header("Accept", "application/json")

body_update = {
    "subscriber_id": USER_ID,
    "fields": [
        {"field_name": "Quiz_Product_Name", "field_value": "Python Test Product"},
        {"field_name": "Quiz_Product_Url", "field_value": "https://example.com/test"},
        {"field_name": "Quiz_Promo_Code", "field_value": "TEST-CODE-15OFF"}
    ]
}

print("\n--- 1. Testing Field Update ---")
try:
    data = json.dumps(body_update).encode('utf-8')
    with urllib.request.urlopen(req_update, data=data) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    try:
        print("Error:", json.dumps(json.loads(e.read().decode('utf-8')), indent=2))
    except:
        print("Error:", e.read().decode('utf-8'))

# Wait a tiny bit just in case
time.sleep(1)

# 2. Trigger Flow via /ig/ endpoint
url_flow = "https://api.manychat.com/ig/sending/sendFlow"
req_flow = urllib.request.Request(url_flow, method="POST")
req_flow.add_header("Authorization", f"Bearer {API_KEY}")
req_flow.add_header("Content-Type", "application/json")
req_flow.add_header("Accept", "application/json")

body_flow = {
    "subscriber_id": USER_ID,
    "flow_ns": FLOW_NS
}

print(f"\n--- 2. Testing IG Flow Trigger ({FLOW_NS}) ---")
try:
    data = json.dumps(body_flow).encode('utf-8')
    with urllib.request.urlopen(req_flow, data=data) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    try:
        print("Error:", json.dumps(json.loads(e.read().decode('utf-8')), indent=2))
    except:
        print("Error:", e.read().decode('utf-8'))
