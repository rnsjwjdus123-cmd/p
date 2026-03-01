import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473

url_fb = "https://api.manychat.com/fb/sending/sendContent"

def test_api_with_tag(url, sub_id):
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
                        "text": "Hello with tag!"
                    }
                ]
            }
        },
        "message_tag": "ACCOUNT_UPDATE"
    }
    
    body_no_tag = {
        "subscriber_id": sub_id,
        "data": {
            "version": "v2",
            "content": {
                "messages": [
                    {
                        "type": "text",
                        "text": "Hello without tag!"
                    }
                ]
            }
        }
    }
    
    for name, b in [("NO TAG", body_no_tag), ("WITH TAG", body)]:
        print(f"\n--- Testing {url} {name} ---")
        try:
            data = json.dumps(b).encode('utf-8')
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
                print(res[:500])
        except Exception as e:
            print("Error:", str(e))

test_api_with_tag(url_fb, USER_ID)
