import json

with open(r'C:\Users\user\Desktop\santokki\n8n-docker\santokki_workflow_v4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Firestore 조회 노드(v4-node-002) jsCode에서 crypto require 복원
for node in data['nodes']:
    if node['id'] == 'v4-node-002':
        code = node['parameters']['jsCode']
        # Google OAuth2 토큰 생성 주석 뒤에 require('crypto') 추가
        code = code.replace(
            "// Google OAuth2 토큰 생성 (crypto는 n8n 글로벌)\nfunction base64url",
            "// Google OAuth2 토큰 생성\nconst crypto = require('crypto');\nfunction base64url"
        )
        node['parameters']['jsCode'] = code
        print("Fixed node:", node['name'])
        print("First 300 chars of jsCode:", code[:300])
        break

with open(r'C:\Users\user\Desktop\santokki\n8n-docker\santokki_workflow_v4.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Done!")
