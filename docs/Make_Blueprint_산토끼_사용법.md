# Make.com Blueprint — 산토끼 Firestore → SNS 문구·텔레그램

`Santokki_Make_Blueprint.json`은 **Firebase Firestore `quiz_results`에 새 문서가 생길 때** → **OpenAI로 인스타/스레드/X용 문구 생성** → **상품 이미지 URL 조합** → **텔레그램 봇으로 전송**하는 워크플로우입니다.

---

## 1. Import 방법

1. [Make.com](https://www.make.com) 시나리오 편집 화면에서 **우측 상단 ⋮** 클릭  
2. **Import blueprint** 선택  
3. `docs/Santokki_Make_Blueprint.json` 파일 선택 후 업로드  

Import 후 아래 연결만 설정하면 됩니다.

- **Google Cloud Firestore** — 프로젝트·서비스 계정 연결 (Firestore 읽기 권한)
- **OpenAI** — API 키 연결
- **Telegram** — 봇 토큰·채팅 ID

---

## 2. Import가 안 될 때 (수동으로 시나리오 만들기)

Blueprint의 `module` 식별자가 Make 버전에 맞지 않으면 수동으로 같은 흐름을 만들 수 있습니다.

### 흐름 순서

| 순서 | 모듈 | 설명 |
|------|------|------|
| 1 | **Google Cloud Firestore** → **Watch documents** (또는 **Watch records**) | 컬렉션: `quiz_results`, 새 문서 생성 시 트리거 |
| 2 | **OpenAI** → **Create a completion** (또는 **Chat completion**) | 아래 프롬프트 사용 |
| 3 | **Tools** → **Parse JSON** | 2번 모듈의 응답 텍스트(JSON)를 파싱 → `instagram`, `threads`, `twitter`, `productImagePath` |
| 4 | **Tools** → **Set variable** | `imageUrl` = `https://famous-pie-9e1a00.netlify.app/` + `3.productImagePath` |
| 5 | **Telegram** → **Send a message** | 채팅 ID·메시지 본문에 3번·4번 출력 매핑 |

### OpenAI에 넣을 프롬프트 (복사용)

```
You are a copywriter for Santokki, a Korean fragrance brand targeting the European market. Tone: elegant, minimal, culturally refined (Korean heritage + British sensibility). No hype; subtle luxury.

**Input — scent quiz result:**
- Top scent profile: {{1.result.top_scent}}
- Matched product (EN): {{1.result.matched_product_name_en}}
- Matched product (KO): {{1.result.matched_product_name}}
- Category: {{1.result.category}}
- Gender: {{1.basic_info.gender}}
- Space: {{1.selected_space}}
- Scores: {{1.scores}}

**Tasks:** Generate three short promotional texts (English) for the matched product, keeping Santokki brand voice:
1. **instagram** — 1–2 sentences, 1–2 tasteful emojis, hashtags at end (~120 words).
2. **threads** — Slightly conversational, same tone (~80 words).
3. **twitter** — Concise, under 280 characters, no hashtag overload.

Also return the **product image path** for this product (use only this exact mapping):
room-001→assets/Mornig Mist of Namsan.png, room-002→assets/Jeju Sea Salt & Mint.png, room-003→assets/Memory of Tiles.png, diffuser-001→assets/The king's Room.png, diffuser-002→assets/The Queen's Room.png, candle-001→assets/The Princess's Flower Garden.png, candle-002→assets/Naju Pear Blossom.png, candle-003→assets/Ginger & Citron Warmth.png, candle-004→assets/The Rainsound under the Dancheong.png, candle-005→assets/The korean Jangdokdae.png, candle-006→assets/The Crown Prince's Study.png, car-001→assets/Ink on Hangi.png, car-002→assets/Black Pine & Amber Edition.png, car-003→assets/Trace of Inkstone.png.

Output valid JSON only, no markdown:
{"instagram": "...", "threads": "...", "twitter": "...", "productImagePath": "assets/..."}
```

(실제 설정 시 `{{1.result.top_scent}}` 등은 Make.com에서 1번 모듈의 해당 필드로 매핑.)

---

## 3. Firebase 구조 참고

- **컬렉션 ID:** `quiz_results`
- **문서 필드:**  
  `subscriber_id`, `created_at`, `basic_info` (gender, age_group), `selected_space`, `answers`, `scores`,  
  `result` (top_scent, matched_product_id, matched_product_name, matched_product_name_en, category),  
  `dm_sent`, `dm_sent_at`, `promo_code`

트리거는 **새 문서 생성** 시 한 번씩 실행되도록 설정합니다.

---

## 4. 상품 이미지 URL

상품 이미지는 **p 프로젝트**의 `products.json`과 동일한 경로를 사용합니다.  
Base URL: `https://famous-pie-9e1a00.netlify.app/`

| productId   | 이미지 경로 |
|------------|-------------|
| room-001   | assets/Mornig Mist of Namsan.png |
| room-002   | assets/Jeju Sea Salt & Mint.png |
| room-003   | assets/Memory of Tiles.png |
| diffuser-001 | assets/The king's Room.png |
| diffuser-002 | assets/The Queen's Room.png |
| candle-001 ~ candle-006, car-001 ~ car-003 | Blueprint 내 `metadata.santokki.productIdToImage` 참고 |

Blueprint JSON 안의 `metadata.santokki.productIdToImage`에 전체 매핑이 들어 있습니다.

---

## 5. 텔레그램 설정

- **Send a message** 모듈에서 **Chat ID**에 본인 채팅 ID 입력 (Import 시 `YOUR_TELEGRAM_CHAT_ID` 교체).
- 봇 토큰은 Telegram 연결에서 설정합니다.

---

## 6. Bannerbear 대안 (선택)

요구사항에 “Bannerbear 또는 이미지 처리”가 있었으나, 현재 Blueprint는 **우리 상품 이미지 URL만 조합해 텔레그램으로 전달**하는 방식입니다.  
이미지 위에 텍스트를 겹치거나 캔버스 조합이 필요하면 Make 시나리오에 **Bannerbear** 모듈을 추가해, `imageUrl`을 배경으로 하고 문구를 오버레이하는 식으로 확장할 수 있습니다.
