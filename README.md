# Santokki (프로젝트 p)

**한국 홈 프래그런스 브랜드 Santokki** — 유럽 타겟 쇼핑몰 + 인스타 시향 테스트·DM 자동화를 한 저장소에서 관리합니다.

---

## 📁 프로젝트 구조

```
p/
├── README.md                 ← 이 문서 (전체 개요)
├── package.json              # npm 스크립트, 의존성
├── server.js                 # API 서버 (프롬프트 생성, Firebase 통계)
├── .env.example              # 환경 변수 예시 (복사 → .env)
├── .gitignore
├── netlify.toml              # Netlify 배포 설정
├── _redirects                # Netlify: /santokki/dashboard → .html
│
├── index.html                # 쇼핑몰 메인
├── product.html, product-detail.js
├── checkout.html, checkout.js
├── cart.html, auth.html
├── styles.css, script.js
├── products.json             # 상품 14종 (쇼핑몰 + 퀴즈 매칭 공용)
│
├── prompt-generator.html     # 광고/게시글 프롬프트 생성 UI (API 서버 필요)
├── BACKBRIEF_프롬프트생성.md  # 프롬프트 생성 기능 백브리핑
│
└── santokki/                 # 인스타 자동화 파이프라인
    ├── README.md             # 상세 흐름, n8n, Firestore, 매칭 알고리즘
    ├── dashboard.html        # 시향 테스트 통계 대시보드
    ├── dashboard_demo.html    # 대시보드 데모 (목업)
    ├── quiz/
    │   ├── index.html        # 15문항 시향 퀴즈 (Firebase Hosting 배포)
    │   ├── dashboard.html    # 대시보드 복사본
    │   ├── firebase.json, .firebaserc
    ├── n8n-docker/           # n8n Docker, 워크플로우 JSON
    ├── docs/                 # 설문/매칭 계획서, 회의록, 제품 라인업 등
    ├── privacy.html
    ├── fix_*.py, test_mc*.py # 퀴즈·ManyChat 테스트 스크립트
    └── firebase-key.json     # Firestore 서비스 계정 (Git 제외)
```

---

## 🔗 배포·접속 주소

| 용도 | URL |
|------|-----|
| **대시보드** (시향 테스트 통계) | **https://santokki-f7c72.web.app/dashboard.html** |
| **시향 퀴즈** | https://santokki-f7c72.web.app |
| **프롬프트 생성기** (로컬 API 필요) | http://localhost:7000/prompt-generator.html |
| 쇼핑몰 (Netlify) | 배포한 Netlify 사이트 URL (예: lucky-lollipop-dea96a.netlify.app) |
| n8n (로컬 Docker) | http://localhost:5678 |

- 프롬프트 생성기의 **「Firebase 통계로 자동 생성」「생성하기」**는 **로컬에서 API 서버**를 켜야 동작합니다 (Netlify에는 API 미배포).

---

## 🚀 실행 방법

### 정적 사이트만 (쇼핑몰·대시보드·프롬프트 페이지 열기)

```bash
npm install   # 최초 1회
npm run start
```

→ http://localhost:7000  
→ 대시보드: http://localhost:7000/santokki/dashboard.html  
→ 프롬프트 생성 **페이지**는 열리지만, **생성 버튼**은 API가 없어 동작하지 않음.

### API 서버 포함 (프롬프트 생성 사용)

```bash
npm run start:api
```

→ 동일한 URL이지만 **POST /api/generate-prompts**, **GET /api/stats-from-firebase** 사용 가능.  
→ **Firebase 통계로 자동 생성** (시향 테스트 10명 이상 시), **생성하기** 버튼 동작.

### n8n (인스타 DM 자동화)

```bash
cd santokki/n8n-docker
docker compose up -d
```

→ http://localhost:5678  
자세한 워크플로우·Firestore·ManyChat 설정은 **santokki/README.md** 참고.

---

## ⚙️ 환경 설정

| 항목 | 설명 |
|------|------|
| **.env** (루트) | `OPENAI_API_KEY`, `LINKTREE_URL`, (선택) 트위터·네이버 키. `.env.example`을 복사해 사용. **Git에 올리지 않음.** |
| **santokki/firebase-key.json** | Firestore 서비스 계정 키. 프롬프트 생성 시 Firebase 통계 10명 이상 자동 연동에 사용. **Git에 올리지 않음.** |

---

## 📚 문서

| 문서 | 내용 |
|------|------|
| **santokki/README.md** | 인스타 DM 파이프라인 전체 흐름, n8n, Firestore 구조, 15문항 설문·매칭 알고리즘, 제품 라인업 |
| **BACKBRIEF_프롬프트생성.md** | 대시보드 → 최적 상품 → 15초 광고·게시글 프롬프트 생성 설계·사용법·n8n 연동 |
| **docs/배포_프롬프트생성기.md** | 프롬프트 생성기만 따로 배포하는 방법 (Render 기준) |
| **docs/가이드북_Make_구글시트_SNS자동발행.md** | Make.com + 구글 시트로 링크드인·네이버·X 자동 발행 가이드 |
| **docs/Santokki_Make_Blueprint.json** | Make.com용 Blueprint: Firestore 퀴즈 결과 → OpenAI SNS 문구 생성 → 텔레그램 전송 (Import 후 연결만 설정) |
| **docs/Make_Blueprint_산토끼_사용법.md** | 위 Blueprint Import 방법·수동 설정·Firebase·상품 이미지·프롬프트 복사용 설명 |
| **santokki/docs/** | 설문지 매칭 알고리즘 계획서, 제품 라인업·구매 링크, 회의록, 퀴즈 질문 목록 등 |

---

## ⚠️ 주의

- **.env**, **santokki/firebase-key.json** 은 Git에 커밋하지 마세요. (`.gitignore`에 포함됨)
- santokki 내 `fix_*.py`, `test_mc*.py` 일부는 절대 경로(`C:\...\santokki\`)를 참조할 수 있음. `p\santokki\` 구조에 맞게 경로 수정 후 사용.
