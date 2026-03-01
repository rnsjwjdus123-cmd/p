import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473

url_flow = "https://api.manychat.com/fb/sending/sendFlow"

def test_flow(url, sub_id):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    
    # Just a dummy flow namespace to see what the error is
    body = {
        "subscriber_id": sub_id,
        "flow_ns": "content-2024"
    }
    
    print(f"\n--- Testing {url} Flow ---")
    try:
        data = json.dumps(body).encode('utf-8')
        with urllib.request.urlopen(req, data=data) as response:
            print("Status:", response.status)
            print("Response:", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        res = e.read().decode('utf-8')
        try:
            print("Error:", json.dumps(json.loads(res), indent=2))
        except:
            print("Error:", res)
    except Exception as e:
        print("Error:", str(e))

test_flow(url_flow, USER_ID)
