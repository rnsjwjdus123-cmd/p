# n8n 셀프호스팅 설정 (Santokki 프로젝트)

## 📁 폴더 구조

```
n8n-docker/
├── docker-compose.yml   # n8n 컨테이너 설정
├── .env                 # 환경 변수 (비밀키 - Git 올리지 말 것!)
├── .gitignore
└── README.md
```

---

## 🚀 시작하는 법 (딱 3단계)

### 1단계 — firebase-key.json 복사

```bash
# 프로젝트 루트의 firebase-key.json을 이 폴더에 복사
cp ../firebase-key.json ./firebase-key.json
```

### 2단계 — .env 파일 수정

`.env` 파일을 열어서 아래 두 가지를 채우세요:

```
N8N_PASSWORD=원하는비밀번호   ← 반드시 변경
MANYCHAT_API_KEY=실제키값     ← ManyChat 대시보드에서 복사
FIREBASE_PROJECT_ID=프로젝트ID ← Firebase 콘솔에서 확인
```

### 3단계 — 실행

```bash
cd n8n-docker
docker compose up -d
```

브라우저에서 → **http://localhost:5678**

로그인: `.env`에 설정한 `N8N_USER` / `N8N_PASSWORD`

---

## 🛑 멈추는 법

```bash
docker compose down        # 중지 (데이터 유지)
docker compose down -v     # 중지 + 데이터 전체 삭제 (주의!)
```

## 📋 로그 확인

```bash
docker compose logs -f n8n
```

---

## 🔗 Webhook 외부 노출 (ngrok)

Firestore Trigger가 외부 webhook을 필요로 할 경우, ngrok으로 임시 공개 URL을 만들 수 있습니다.

```bash
# ngrok 설치 후
ngrok http 5678
```

ngrok이 발급한 URL (예: `https://xxxx.ngrok.io`)을 `.env`의 `WEBHOOK_URL`에 넣고 재시작:

```bash
docker compose down && docker compose up -d
```

---

## ⚙️ Santokki 워크플로우 체크리스트

n8n 접속 후 순서대로 진행:

- [ ] **Credentials** 메뉴에서 Google Service Account 등록 (`firebase-key.json` 사용)
- [ ] **Credentials** 메뉴에서 HTTP Header Auth 등록 (ManyChat API Key)
- [ ] 새 워크플로우 생성 → `n8n_handoff.md` 3단계 파이프라인 구성
- [ ] Code 노드에 `n8n_code_matcher.js` 내용 붙여넣기
- [ ] 테스트 실행으로 Firestore → ManyChat DM 흐름 확인

---

## ❓ 자주 하는 실수

| 문제 | 해결 |
|------|------|
| `port 5678 already in use` | `docker compose down` 후 재시작 |
| firebase-key.json 없다는 오류 | 이 폴더에 파일 복사했는지 확인 |
| Webhook이 안 들어옴 | ngrok 설정 후 `WEBHOOK_URL` 업데이트 |
