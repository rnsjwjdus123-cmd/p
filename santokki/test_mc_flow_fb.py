import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473
FLOW_NS = "content20260301052356_064344"

# 1. Test /fb/sending/sendFlow (Might give 24h error, but let's see if 404)
url_fb = "https://api.manychat.com/fb/sending/sendFlow"
req_fb = urllib.request.Request(url_fb, method="POST")
req_fb.add_header("Authorization", f"Bearer {API_KEY}")
req_fb.add_header("Content-Type", "application/json")
req_fb.add_header("Accept", "application/json")

body = {
    "subscriber_id": USER_ID,
    "flow_ns": FLOW_NS
}

print(f"\n--- Testing FB Flow Trigger ({FLOW_NS}) ---")
try:
    data = json.dumps(body).encode('utf-8')
    with urllib.request.urlopen(req_fb, data=data) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    try:
        print("Error:", json.dumps(json.loads(e.read().decode('utf-8')), indent=2))
    except:
        print("Error:", e.read().decode('utf-8'))
