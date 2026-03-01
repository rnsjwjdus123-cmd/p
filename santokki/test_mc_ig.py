import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473

url_ig = "https://api.manychat.com/ig/sending/sendContent"

def test_api_ig(url, sub_id):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    
    body = {
        "subscriber_id": sub_id,
        "data": {
            "version": "v2",
            "content": {
                "messages": [
                    {
                        "type": "text",
                        "text": "Hello IG!"
                    }
                ]
            }
        }
    }
    
    print(f"\n--- Testing {url} IG ---")
    try:
        data = json.dumps(body).encode('utf-8')
        with urllib.request.urlopen(req, data=data) as response:
            print("Status:", response.status)
            print("Response:", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        res = e.read().decode('utf-8')
        print("Error Response:")
        try:
            print(json.dumps(json.loads(res), indent=2))
        except:
            print(res)
    except Exception as e:
        print("Error:", str(e))

test_api_ig(url_ig, USER_ID)

# Test with Flow
url_flow = "https://api.manychat.com/ig/sending/sendFlow"
def test_flow_ig(url, sub_id):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    
    body = {
        "subscriber_id": sub_id,
        "flow_ns": "content-2024" # just dummy to see error
    }
    
    print(f"\n--- Testing {url} Flow IG ---")
    try:
        data = json.dumps(body).encode('utf-8')
        with urllib.request.urlopen(req, data=data) as response:
            print("Status:", response.status)
            print("Response:", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        res = e.read().decode('utf-8')
        try:
            print(json.dumps(json.loads(res), indent=2))
        except:
            print(res)

test_flow_ig(url_flow, USER_ID)
