# 🐰 Santokki — Instagram DM 자동화 파이프라인

유럽(영국) 시장을 타겟으로 한 한국 홈 프래그런스 브랜드 **Santokki**의 마케팅 자동화 시스템입니다.

---

## ✨ 전체 흐름

```
유저가 인스타 댓글에 "test" 작성
    ↓
ManyChat 감지 → 퀴즈 링크 DM 자동 발송
(링크: https://santokki-f7c72.web.app?subscriber_id={{subscriber_id}})
    ↓
유저가 퀴즈 페이지에서 15문항 설문 완료
    ↓
Firebase Firestore에 결과 저장 (dm_sent: false)
    ↓
n8n 워크플로우 (30초 폴링) → 미처리 문서 감지
    ↓
매칭 알고리즘 → 제품 선택 → 프로모코드 발급
    ↓
ManyChat API → 추천 제품 + 할인코드 DM 자동 발송
    ↓
Firestore 업데이트 (dm_sent: true)
```

---

## 🛠️ 기술 스택

| 항목 | 기술 |
|------|------|
| 퀴즈 페이지 | HTML/CSS/JS (Firebase Hosting) |
| 데이터베이스 | Firebase Firestore (프로젝트: santokki-f7c72) |
| 자동화 엔진 | n8n v2.9.4 (Docker, 로컬 셀프호스팅) |
| DM 발송 | ManyChat API |
| 댓글 감지 | ManyChat Automation (Comment Growth Tool) |

---

## 📁 프로젝트 구조

```
santokki/
├── dashboard.html                 ← 📊 통계 대시보드 (Firestore quiz_results 실시간)
│   → 배포 주소: https://santokki-f7c72.web.app/dashboard.html
├── dashboard_demo.html            ← 대시보드 데모 (목업 데이터, Firebase 불필요)
├── quiz/                          ← 퀴즈 페이지 (Firebase Hosting)
│   ├── index.html                 # 15문항 퀴즈 + 결과 페이지
│   ├── dashboard.html             # 대시보드 (quiz 폴더 내 복사본)
│   ├── firebase.json              # Hosting 설정
│   └── .firebaserc                # 프로젝트 연결
│
├── n8n-docker/                    ← n8n 자동화 엔진
│   ├── docker-compose.yml         # n8n Docker 설정
│   ├── .env                       # n8n 자격 증명
│   ├── firebase-key.json          # Firestore 인증키
│   └── santokki_workflow_v4.json  # 워크플로우 (Firestore 폴링)
│
├── firebase-key.json              ← Firestore 서비스 계정 키
├── privacy.html                   ← 개인정보 처리방침
├── .env / .env.example            ← 환경변수
└── README.md
```

---

## 🚀 시작하기

### 1. n8n 실행 (Docker)

```bash
cd n8n-docker
docker compose up -d
```
→ `http://localhost:5678` 에서 n8n 접속

### 2. n8n 워크플로우 Import

1. n8n에서 **Import from file** → `santokki_workflow_v4.json`
2. 워크플로우 **Active** 토글 켜기
3. 30초마다 Firestore 자동 폴링 시작

### 3. 퀴즈 페이지 배포

```bash
cd quiz
firebase deploy --only hosting
```
→ `https://santokki-f7c72.web.app` 배포됨

### 4. 대시보드 (통계) 보기

- **배포 주소 (공용):** **https://santokki-f7c72.web.app/dashboard.html**

Firestore `quiz_results` 실시간 통계를 보려면:

1. **p 폴더 루트**에서 로컬 서버 실행 (파일 직접 열기 `file://` 는 Firestore 보안상 불가):
   ```bash
   cd C:\Users\user\Desktop\p
   npm run start
   ```
2. 브라우저에서 **http://localhost:7000/santokki/dashboard.html** 접속.

- **dashboard.html** → 실제 Firestore 데이터 (KPI, 향별·성별·공간별 차트, 퍼널, 최근 응답 테이블). 60초마다 자동 새로고침.
- **dashboard_demo.html** → Firebase 없이 목업 데이터로 UI만 확인할 때 사용.
- 대시보드 Firebase 설정은 이미 **santokki-f7c72** / `quiz_results` 로 되어 있음. Firestore 규칙에서 해당 도메인(또는 테스트 모드) 읽기 허용 필요.

### 5. ManyChat 설정

DM 자동 발송 메시지:
```
🐰 Welcome to the Santokki Scent Quiz!

Answer 15 simple questions and we'll find your perfect Korean fragrance match ✨

👉 Start the quiz: https://santokki-f7c72.web.app?subscriber_id={{subscriber_id}}
```

---

## 🎯 제품 라인업 (12종 + 자개 Edition 2종)

### 룸 스프레이 (Room Spray) — 3종

| # | 제품명 | 영문명 | 핵심 향조 | 향 성격 |
|---|--------|--------|----------|--------|
| 1 | 남산의 새벽 안개 | Morning Mist of Namsan | Oakmoss, Pine Needle, Cedarwood | 🌲 그린/어시 |
| 2 | 제주 소금과 민트 | Jeju Sea Salt & Mint | Sea Salt, Peppermint, Eucalyptus | 🌊 프레시 |
| 3 | 기와의 기억 | Memory of Tiles | Mineral, Rainwater, Oakmoss | 🌲 어시/오크모스 |

### 침실 캔들 (Bedroom Candle) — 3종

| # | 제품명 | 영문명 | 핵심 향조 | 향 성격 |
|---|--------|--------|----------|--------|
| 4 | 공주의 화원 | The Princess's Flower Garden | Peony, Pink Pepper, White Rose, Soft Amber | 🌸 플로럴 |
| 5 | 나주 배꽃의 향연 | Naju Pear Blossom | Pear, Freesia, White Floral, Honey | 🌸 플로럴/프루티 |
| 6 | 단청 아래 빗소리 | Rain Under Dancheong | Wet Cedar, Wild Flowers, Sandalwood | 🌲 우디/그린 |

### 주방 캔들 (Kitchen Candle) — 3종

| # | 제품명 | 영문명 | 핵심 향조 | 향 성격 |
|---|--------|--------|----------|--------|
| 7 | 세자의 서재 | The Crown Prince's Study | Sandalwood, Ink, Bergamot, Thyme | 🖤 우디/잉크 |
| 8 | 생강과 유자 | Ginger & Citron Warmth | Yuzu, Ginger, Lemongrass | 🍊 시트러스/스파이시 |
| 9 | 조용한 찻자리 | A Quiet Tea Ceremony | Roasted Rice, Barley Tea, Vetiver | 🍵 곡물/어시 |

### 차량용 방향제 (Car Diffuser) — 3종

| # | 제품명 | 영문명 | 핵심 향조 | 향 성격 |
|---|--------|--------|----------|--------|
| 10 | 한지 위 먹향 | Ink on Hanji | Black Ink, Cedarwood, Incense | 🖤 잉크/우디 |
| 11 | 흑송과 호박 | Black Pine & Amber | Black Pine, Sandalwood, Amber | 🌲 우디/앰버 |
| 12 | 묵향의 자취 | Trace of Inkstone | Green Tea, Bergamot, Plum Blossom, Bamboo, Moss | 🌲 그린/플로럴 |

### ✨ 자개 Edition (스페셜 에디션, 매칭 알고리즘 제외)

| 제품명 | 영문명 | 카테고리 |
|--------|--------|---------|
| 왕비의 방 | The Queen's Chamber | 캔들 |
| 왕의 방 | The King's Chamber | 캔들 |

---

## 🧪 시향 설문 & 매칭 알고리즘 (v2)

### 향 성격 5가지

| 향 성격 | 코드명 | 키워드 |
|---------|--------|--------|
| 🌸 플로럴 | FLORAL | 꽃, 정원, 부드러운, 로맨틱 |
| 🌲 그린/어시 | GREEN | 숲, 이끼, 비, 흙, 자연 |
| 🌊 프레시 | FRESH | 상쾌, 시원, 민트, 시트러스, 바다 |
| 🖤 우디/잉크 | WOODY_INK | 나무, 먹, 지적, 무게감, 고요 |
| 🔥 워밍/스파이시 | WARMING | 따뜻, 훈연, 스파이스, 앰버 |

### 설문 구성 (15문항, 영어 UI)

- **Q1-Q2**: 기본 정보 (성별, 나이) — 데이터 수집 전용
- **Q3**: 공간 선택 (거실/침실, 주방, 차량) → 제품 카테고리 결정
- **Q4-Q14**: 향 성향 질문 (간접적 라이프스타일 질문 → 5가지 향 성격에 점수 부여)
- **Q15**: 핵심 키워드 (1.5배 가중치)

### 점수 계산

```
Q4~Q14: 주 향 +3, 부 향 +1 (11문항)
Q15: 주 향 +4.5, 부 향 +1.5 (1.5배 가중치)
최대 점수: 37.5점 (한 향에 올인 시)
```

### 매칭 테이블 (공간 × 향 성격 → 제품)

**거실/침실:**
| 향 성격 | 추천 제품 |
|---------|----------|
| FLORAL | 왕실의 모란 / 나주 배꽃의 향연 |
| GREEN | 남산의 새벽 안개 / 기와의 기억 |
| FRESH | 제주 소금과 민트 |
| WOODY_INK | 단청 아래 빗소리 |
| WARMING | 고가구의 온기 |

**주방:**
| 향 성격 | 추천 제품 |
|---------|----------|
| FRESH / FLORAL | 생강과 유자 |
| WOODY_INK / GREEN | 조용한 찻자리 |
| WARMING | 고가구의 온기 |

**차량:**
| 향 성격 | 추천 제품 |
|---------|----------|
| GREEN / FRESH | 흑송과 호박 |
| WOODY_INK 1위 | 한지 위 먹향 |
| WOODY_INK 2위 / WARMING | 묵향의 자취 |

### 동점 해소
1. Q15 점수가 높은 향 우선
2. Q14 → Q12 순서 역추적
3. 최종 동점 → 카테고리 내 첫 번째 제품

### 자개 Edition 추천
- 일반 매칭에 포함하지 않음
- 결과 페이지에서 "Premium Option" 섹션으로 별도 노출
  - 룸스프레이 결과 → "제왕의 아침" 소개
  - 캔들(침실) 결과 → "황후의 방" 소개

---

## 🔧 n8n 워크플로우 v4 (Firestore 폴링)

```
[30초마다 실행] Schedule Trigger
    ↓
[Firestore 미처리 조회] dm_sent === false 문서 가져오기 (REST API + JWT)
    ↓
[제품 매칭] 14종 제품 DB에서 검증 + 프리미엄 추천 결정
    ↓
[프로모코드 생성] SANTOKKI-XXXX-15OFF 형식
    ↓
[ManyChat DM 발송] 영어 기반 결과 메시지 + 프로모코드
    ↓
[Firestore 업데이트] dm_sent: true, promo_code 저장
```

---

## 💾 Firestore 데이터 구조

### `quiz_results` 컬렉션

```json
{
  "subscriber_id": "ManyChat 구독자 ID",
  "created_at": "2026-02-26T18:00:00+09:00",
  "basic_info": { "gender": "female", "age_group": "20s" },
  "selected_space": "living_bedroom",
  "answers": { "q4": "B", "q5": "A", ... "q15": "B" },
  "scores": { "FLORAL": 2, "GREEN": 31.5, "FRESH": 3, "WOODY_INK": 12, "WARMING": 1 },
  "result": {
    "top_scent": "GREEN",
    "matched_product_id": "RS-001",
    "matched_product_name": "남산의 새벽 안개",
    "matched_product_name_en": "Morning Mist of Namsan",
    "category": "room_spray"
  },
  "dm_sent": false,
  "dm_sent_at": null,
  "promo_code": null
}
```

---

## 📋 프로젝트 히스토리

### 2025-02-25 — ManyChat 전략 채택
- 자체 코드(FastAPI)로 Instagram Webhook + DM 자동화 구현 완료
- Meta 앱 검수에 **법인 등록 필요** → 개인 사업자로 불가
- **ManyChat 하이브리드 전략** 채택 (Meta 공식 파트너, 앱 검수 불필요)

### 2026-02-26 — n8n 파이프라인 완성
- n8n 로컬 셀프호스팅 (Docker) 구축
- Firebase Hosting 퀴즈 페이지 배포
- Firestore 폴링 방식 v4 워크플로우 완성
- 14종 + 자개 Edition 2종 제품 라인업 확정
- 15문항 설문지 + 5가지 향 프로필 매칭 알고리즘 설계

---

## 🔗 주요 URL

| 항목 | URL |
|------|-----|
| 퀴즈 페이지 | https://santokki-f7c72.web.app |
| Firebase Console | https://console.firebase.google.com/project/santokki-f7c72 |
| n8n (로컬) | http://localhost:5678 |
| 자사몰 (Netlify) | https://comforting-snickerdoodle-5ce097.netlify.app |
| Instagram | https://www.instagram.com/santokki.official/ |

---

## ⚠️ TODO

- [ ] 자사몰 상세 페이지 URL 확정 → DM에 구매링크 연결
- [ ] 제품 가격 확정 → products.json 반영
- [ ] 실제 ManyChat 구독자 End-to-End 테스트
- [ ] DM 메시지 CTA "Discover more" → "Shop now" 변경 (상점 오픈 시)
- [ ] GDPR 개인정보 처리방침 ManyChat 사용 고지 추가
