import sys
import urllib.request
import json
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "4433599:c69bab2399cb2e3b7ff0990b6028298b"
USER_ID = 1930322473

url = f"https://api.manychat.com/fb/subscriber/getInfo?subscriber_id={USER_ID}"

req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {API_KEY}")
req.add_header("Accept", "application/json")

try:
    with urllib.request.urlopen(req) as response:
        print(json.dumps(json.loads(response.read().decode('utf-8')), indent=2))
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode('utf-8'))
