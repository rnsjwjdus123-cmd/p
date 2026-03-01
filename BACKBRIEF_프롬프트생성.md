# 백브리핑 — 대시보드 → 최적 상품 → 15초 광고·게시글 프롬프트 자동 생성

---

## 1. 설계 요약

- **입력:** 대시보드 통계(인기 향, 인기 매칭 제품, 응답 수, 기간, 성별/공간 비율 등)
- **처리:** `.env`의 `OPENAI_API_KEY`로 OpenAI 호출. `products.json` 상품 목록 + 통계를 넣어 **최적 상품 1~2개** 선정 후, 해당 상품에 맞춰 **15초 광고 스크립트**와 **피드 게시글용 카피(캡션+해시태그)** 생성.
- **출력:** 최적 상품, 15초 스크립트, 게시글 카피(링크트리 URL은 `.env`의 `LINKTREE_URL` 반영).

---

## 2. 추가된 파일

| 파일 | 역할 |
|------|------|
| **server.js** | Express 서버. 정적 파일 서빙 + `POST /api/generate-prompts` API. `.env`에서 `OPENAI_API_KEY`, `LINKTREE_URL` 읽음. `products.json` 로드 후 OpenAI에 통계+상품 목록 전달. |
| **prompt-generator.html** | 대시보드 통계 입력 폼. 예시 채우기 → 생성 버튼 → API 호출 → 최적 상품 / 15초 스크립트 / 게시글 카피 표시 + 복사 버튼. |
| **package.json** | `start:api` 스크립트 추가, `dotenv`, `express`, `openai` 의존성 추가. |
| **BACKBRIEF_프롬프트생성.md** | 이 백브리핑 문서. |

---

## 3. .env 사용

- **OPENAI_API_KEY** — 필수. 프롬프트 생성에 사용.
- **LINKTREE_URL** — 선택. 없으면 `https://linktr.ee/santokki` 사용. 생성된 게시글 카피에 링크로 들어감.

(트위터/네이버 키는 이번 설계에서 사용하지 않음. 이후 자동 게시 연동 시 사용.)

---

## 4. 사용 방법

### 4.1 의존성 설치 (최초 1회)

```bash
cd C:\Users\user\Desktop\p
npm install
```

### 4.2 API 서버 실행 (프롬프트 생성 쓰려면 이걸로 실행)

```bash
npm run start:api
```

- 대시보드: **http://localhost:7000/santokki/dashboard.html**
- 프롬프트 생성 페이지: **http://localhost:7000/prompt-generator.html**

### 4.3 프롬프트 생성 페이지에서

1. **예시로 채우기** 클릭 → 인기 향, 인기 제품, 응답 수 등이 채워짐.
2. 실제 대시보드에서 본 값으로 수정 (인기 향, 인기 매칭 제품, 총 응답 수, 기간, 필요 시 추가 통계 JSON).
3. **생성하기** 클릭 → 최적 상품 / 15초 광고 스크립트 / 게시글 카피가 나옴.
4. 각 블록 옆 **복사** 버튼으로 클립보드 복사 후 광고·게시글 제작에 사용.

### 4.4 n8n/동료 연동

- **엔드포인트:** `POST http://localhost:7000/api/generate-prompts` (서버 실행 중일 때)
- **Body (JSON):** `{ "stats": { "topScents": ["GREEN","FLORAL"], "topProducts": ["Morning Mist of Namsan"], "totalResponses": 128, "period": "7d" } }`
- **스키마 확인:** `GET http://localhost:7000/api/schema`

동료가 n8n에서 대시보드 결과를 위 `stats` 형식으로 모아서 이 URL로 POST하면, 같은 구조의 결과(최적 상품 + 15초 스크립트 + 게시글 카피)를 받을 수 있음.

---

## 5. 결과물 형태

- **optimalProduct:** 통계와 상품 라인업을 기준으로 이번에 밀어줄 1~2개 상품 (id, name, nameKo, reason).
- **adScript15s:** 약 15초 분량 영문 비디오 광고 스크립트 (약 35~45단어, Santokki 톤, CTA 포함).
- **feedPostCopy:** 피드용 캡션 2~3문장 + 해시태그 5~7개, `LINKTREE_URL` 반영.

---

## 6. 정리

- **대시보드 결과**를 넣으면 → **최적 상품**이 정해지고 → 그 상품에 맞춘 **15초 광고 스크립트**와 **게시글 전용 카피**가 자동으로 나오도록 설계됨.
- `.env`에 OpenAI 키만 있으면 동작하며, 링크트리 주소는 선택으로 넣으면 생성 카피에 반영됨.
- 프롬프트 생성 페이지에서 수동 실행하거나, n8n에서 `POST /api/generate-prompts`로 연동하면 됨.
