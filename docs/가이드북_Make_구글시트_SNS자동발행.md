# 가이드북 — Make.com + 구글 시트로 SNS 자동 발행

프롬프트 생성기·대시보드 결과를 구글 시트에 넣고, Make.com 시나리오로 **링크드인·네이버 블로그·X(트위터)** 에 자동 발행하기 위한 단계별 가이드입니다.

---

## 1. 준비물

| 항목 | 설명 |
|------|------|
| **Make.com** | make.com 가입, 시나리오 생성 권한 |
| **구글 계정** | 스프레드시트 생성·연동용 |
| **프롬프트 생성기** | 우리 p 프로젝트의 `prompt-generator.html` (로컬 `npm run start:api` 또는 배포된 API) |
| **API 키** | LinkedIn, X(Twitter), 네이버 블로그 (각 플랫폼 개발자 페이지에서 발급) |

---

## 2. 구글 시트 구조

**시트 이름:** `SNS 발행 대기` (또는 원하는 이름)

| 열 | 컬럼명(예) | 용도 |
|----|------------|------|
| A | 제목 | 게시글 제목 또는 상품명 |
| B | 원문/요약 | 프롬프트 생성기에서 나온 본문 요약 또는 SEO 본문 |
| C | URL | 링크트리/상품 URL |
| D | 작성일 | 자동 입력 또는 수동 |
| E | SNS 문구 생성 | ☐ 체크 시 → F·G·H열 내용 생성(필요 시 GPT 호출) |
| F | 링크드인 | 링크드인용 포스트 원문 |
| G | 트위터/인스타 | X 또는 인스타 캡션 |
| H | 네이버 블로그 | 네이버용 제목+본문 (또는 별도 시트) |
| I | 발행 | ☐ 체크 시 → 실제 API로 발행 실행 |

**참고:** 프롬프트 생성기에서 이미 인스타·네이버용 문구를 만들므로, **A~D는 우리가 넣고, F·G·H는 생성기 결과를 복사해 넣거나** Make.com이 우리 API를 호출해 받은 값을 시트에 채우도록 할 수 있습니다.

---

## 3. 전체 흐름 요약

```
[1] 데이터 넣기
    프롬프트 생성기 결과를 시트 한 행에 수동 입력 또는
    Make.com이 우리 API(POST /api/generate-prompts) 호출 → 결과를 시트에 Add a Row

[2] (선택) SNS 문구 생성
    E열 체크 시 → B·C열 기반으로 GPT가 F(링크드인), G(트위터), H(네이버) 생성 후 시트 업데이트

[3] 발행
    I열(발행) 체크 시 → F열 → LinkedIn API, G열 → X API, H열 → 네이버 블로그 API 호출
```

---

## 4. Make.com 시나리오 1 — 데이터를 시트에 넣기

**목표:** 프롬프트 생성기 결과를 구글 시트 새 행으로 추가.

### 방법 A: 수동 입력 후 자동 발행만 쓰는 경우

- 시트에 직접 A~H열 입력. 시나리오 2만 사용.

### 방법 B: Make.com이 우리 API를 호출해 시트에 채우기

1. **트리거:** Schedule (매일/매주) 또는 Webhook (버튼 클릭 시).
2. **모듈 1 — HTTP:**  
   - **Make a request**  
   - URL: `https://당신API주소/api/generate-prompts` (또는 Firebase 통계 쓰려면 먼저 GET `/api/stats-from-firebase` 호출 후 그 결과로 POST)  
   - Method: POST  
   - Body: `{ "stats": { "topScents": ["GREEN"], "topProducts": ["상품명"], "totalResponses": 50, "period": "7d" } }`  
   - (Firebase 사용 시: 이전 모듈에서 GET으로 stats 받아서 그대로 body에 넣기)
3. **모듈 2 — Google Sheets: Add a Row**  
   - Spreadsheet: 연동한 구글 시트 선택  
   - Sheet: `SNS 발행 대기`  
   - A열: `{{1.optimalProduct.name}}` 또는 제목에 해당하는 값  
   - B열: `{{1.seoPost.body}}` 또는 원문  
   - C열: 링크트리 URL 등  
   - D열: `{{now}}` 또는 빈칸  
   - E·I열: 체크 안 함(False)

**주의:** 우리 API가 배포되어 있어야 함. 로컬만 쓰면 Make.com에서 접근 불가하므로, Render 등에 API 배포 후 URL 사용.

---

## 5. Make.com 시나리오 2 — 체크박스로 SNS 문구 생성 및 발행

**트리거:** Google Sheets — **Watch Rows** (특정 시트의 변경 감지).

### 5-1. 라우터로 분기

- **Router** 모듈 추가.
- **분기 1:** E열(5번째 열)이 `true`로 바뀐 경우 → SNS 문구 생성 플로우.
- **분기 2:** I열(9번째 열)이 `true`로 바뀐 경우 → 발행 플로우.

(실제 열 번호는 시트에 맞게 조정.)

### 5-2. 분기 1 — SNS 문구 생성

1. **Filter:** 변경된 행의 E열 = true (또는 “체크됨”).
2. **OpenAI — Create a Completion**  
   - Model: gpt-4o-mini  
   - Prompt 예시:
     ```
     당신은 Santokki(한국 향 브랜드) 마케터입니다.
     아래 원문과 URL을 바탕으로 다음을 작성해 주세요.
     - 링크드인용 포스트 1개 (전문적·스토리텔링, 1~2문단)
     - 트위터/X용 캡션 1개 (짧게, 해시태그 3~5개)
     - 네이버 블로그용: 제목(35자 내외) + 본문 2~3문단
     원문: {{원문(B열)}}
     URL: {{C열}}
     출력 형식: [LINKEDIN] ... [/LINKEDIN] [TWITTER] ... [/TWITTER] [NAVER] 제목: ... 본문: ... [/NAVER]
     ```
   - Temperature: 0.3, Max tokens: 1000
3. **Text Parser — Match Pattern**  
   - 정규식으로 `[LINKEDIN]...[/LINKEDIN]`, `[TWITTER]...[/TWITTER]`, `[NAVER]...[/NAVER]` 분리.
4. **Google Sheets — Update a Row**  
   - 해당 행의 F열 = 링크드인, G열 = 트위터, H열 = 네이버 내용으로 업데이트.

### 5-3. 분기 2 — 발행

1. **Filter:** 변경된 행의 I열 = true.
2. **Google Sheets — Search Rows**  
   - 같은 스프레드시트에서 방금 체크된 행 1건 조회 (또는 트리거에서 넘어온 행 ID 사용).
3. **LinkedIn — Create a Text Post**  
   - F열 내용을 포스트 본문으로 사용. 연동 시 OAuth 설정 필요.
4. **X (Twitter) — Create a Post**  
   - G열 내용을 트윗 텍스트로 사용. API 키·시크릿·액세스 토큰 설정.
5. **(선택) HTTP — Make a request**  
   - 네이버 블로그 API 호출.  
   - URL: `https://openapi.naver.com/blog/writePost.json` 등 (네이버 개발자 문서 참고).  
   - Method: POST, Body에 H열 제목·본문 포함.

6. **Google Sheets — Update a Row**  
   - 발행 완료 후 I열 체크 해제(False) 또는 “발행완료” 표시로 업데이트 (중복 발행 방지).

---

## 6. API 연동 요약

| 플랫폼 | 필요한 것 | Make.com |
|--------|-----------|----------|
| **LinkedIn** | LinkedIn Developer 앱, OAuth 2.0 | Make.com LinkedIn 모듈 연결 (OAuth 로그인) |
| **X (Twitter)** | developer.x.com 앱, API Key/Secret, Access Token/Secret | Make.com X (Twitter) 모듈 연결 |
| **네이버 블로그** | 네이버 개발자센터 앱, Client ID/Secret, 발행 API | 전용 모듈 없을 수 있음 → **HTTP** 모듈로 API 호출 |

---

## 7. 체크리스트

- [ ] 구글 시트 생성, 위와 같은 열 구조로 시트 만들기
- [ ] Make.com에서 구글 시트 연동 (연결 추가)
- [ ] 시나리오 1 (선택): 우리 API 또는 수동 입력으로 시트에 행 추가
- [ ] 시나리오 2: Watch Rows 트리거 설정, 라우터로 E열/I열 분기
- [ ] OpenAI 연결 (Make.com에서), SNS 문구 생성 프롬프트 입력
- [ ] LinkedIn·X 연동 (OAuth/API 키)
- [ ] 네이버 블로그: HTTP 모듈로 API 호출 설정 (문서 참고)
- [ ] 테스트: 시트에 한 행 넣고 E열 체크 → F·G·H 채워지는지 확인
- [ ] 테스트: I열 체크 → 실제 발행되는지 확인 (테스트 계정 권장)

---

## 8. 참고

- 프롬프트 생성기에서 **이미 인스타·네이버·SEO 문구**를 만들므로, 시트에 **직접 복사해 넣고** E열 생성 단계를 생략하고 **I열 발행만** 써도 됩니다.
- 발행 전에 **한 번 더 눈으로 확인**하려면, I열 체크 시 “발행 대기” 시트에서 “발행 완료” 시트로 행을 복사한 뒤, 그 시트를 감시하는 시나리오로 발행하는 방식도 가능합니다.

이 가이드대로 하시다가 특정 단계(예: 네이버 API 호출 형식, 정규식 예시)가 필요하면 그 부분만 따로 요청해 주세요.
