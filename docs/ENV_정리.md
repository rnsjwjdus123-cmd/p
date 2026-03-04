# .env 파일 정리

프로젝트에서 환경 변수(.env)가 쓰이는 위치와 역할을 정리한 문서입니다. **기능 변경 없이** 참고용입니다.

---

## 요약

| 위치 | 용도 | 필수 여부 |
|------|------|-----------|
| **p/.env** | Node API(7000), 구글 시트, OpenAI, Firebase 등. Python 백엔드(8000)도 루트 .env 우선 로드 | 메인 설정 |
| **p/project_html/backend/.env** | Python 분석 API 전용 오버라이드 (루트에 키 없을 때만 사용) | 선택 |
| **p/santokki/.env** | 인스타·퀴즈·ManyChat·Meta API 등 santokki 파이프라인 전용 | santokki 기능 쓸 때 |
| **p/santokki/n8n-docker/.env** | n8n Docker 로그인·웹훅 URL 등 | n8n Docker 쓸 때 |

---

## 1. 루트 p/.env

- **참조:** `server.js` (Node, 포트 7000), `project_html/backend/server.py`(루트 .env 있으면 우선 로드)
- **주요 변수:** `OPENAI_API_KEY`, `LINKTREE_URL`, `GOOGLE_SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON` 또는 `GOOGLE_APPLICATION_CREDENTIALS`, `DAILY_CRON_*`, Firebase는 `santokki/firebase-key.json` 사용
- **복사:** `p/.env.example` → `p/.env` 후 값 채우기

---

## 2. project_html/backend/.env

- **참조:** `project_html/backend/server.py` (루트 p/.env 로드 후, 없으면 여기 .env)
- **용도:** OpenAI·Perplexity 등 분석 API 키. 루트에 키를 두면 별도 설정 없이 동작
- **복사:** `project_html/backend/.env.example` → `project_html/backend/.env`

---

## 3. santokki/.env

- **참조:** santokki 폴더 내 스크립트·n8n 워크플로우 등
- **용도:** Meta/Instagram API, ManyChat, 웹훅, 설문 링크 등
- **복사:** `santokki/.env.example` → `santokki/.env`

---

## 4. santokki/n8n-docker/.env

- **참조:** n8n Docker 실행 시 (`docker-compose`)
- **용도:** N8N_USER, N8N_PASSWORD, WEBHOOK_URL 등
- **복사:** n8n-docker 폴더 내 README 참고

---

## 정리

- **한 곳에서 대부분 쓰는 경우:** 루트 `p/.env`만 채워도 server.js + project_html 백엔드 동작
- **인스타/퀴즈/n8n 사용 시:** 해당 폴더의 `.env` / `.env.example` 추가 설정
