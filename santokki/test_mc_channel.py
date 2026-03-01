import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473

url_fb = "https://api.manychat.com/fb/sending/sendContent"

def test_api_channel(url, sub_id):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    
    # Try different ways to specify instagram channel
    payloads = [
        {
            "name": "channel at root",
            "body": {
                "subscriber_id": sub_id,
                "channel": "instagram",
                "data": {
                    "version": "v2",
                    "content": {
                        "messages": [{"type": "text", "text": "Test root channel"}]
                    }
                }
            }
        },
        {
            "name": "channel in data",
            "body": {
                "subscriber_id": sub_id,
                "data": {
                    "channel": "instagram",
                    "version": "v2",
                    "content": {
                        "messages": [{"type": "text", "text": "Test data channel"}]
                    }
                }
            }
        }
    ]
    
    for p in payloads:
        print(f"\n--- Testing {p['name']} ---")
        try:
            data = json.dumps(p['body']).encode('utf-8')
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

test_api_channel(url_fb, USER_ID)
