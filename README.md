# 프로젝트 p — Santokki 쇼핑몰 + 인스타 자동화

이 저장소는 **두 가지**를 한 폴더에서 관리합니다.

---

## 📁 구조 요약

| 경로 | 설명 |
|------|------|
| **루트** (`index.html`, `product.html`, `checkout.html`, `script.js`, `styles.css`, `products.json` 등) | **Santokki 자사 쇼핑몰** — Netlify 배포, 상품 14종, 카트/결제 페이지 |
| **santokki/** | **인스타 DM 자동화 파이프라인** — 퀴즈 페이지, n8n, ManyChat, Firestore 연동 |

---

## 🛒 쇼핑몰 (루트)

- **메인:** `index.html` — 상품 목록, 카테고리(룸스프레이·디퓨저·차량용·침실/주방 향초)
- **상세:** `product.html` + `product-detail.js` — 제품 상세
- **결제:** `checkout.html` + `checkout.js`
- **데이터:** `products.json` — 14종 제품 정보
- **스타일:** `styles.css` — 공통 스타일

배포: Netlify 등 정적 호스팅에 그대로 올리면 됩니다.

---

## 🐰 인스타 자동화 (santokki/)

**santokki**는 유럽(영국) 타겟 Santokki 브랜드의 **인스타 댓글 → 퀴즈 링크 DM → 설문 완료 → Firestore 저장 → n8n 폴링 → ManyChat DM 발송** 파이프라인입니다.

| 폴더/파일 | 용도 |
|-----------|------|
| **santokki/dashboard.html** | 📊 통계 대시보드 — Firestore `quiz_results` 실시간 (로컬 서버 실행 후 `/santokki/dashboard.html` 접속) |
| **santokki/quiz/** | 15문항 시향 퀴즈 페이지 (Firebase Hosting 배포) |
| **santokki/n8n-docker/** | n8n Docker 설정, 워크플로우 JSON (v4, v5), Firestore·ManyChat 연동 |
| **santokki/docs/** | 설문/매칭 계획서, 제품 라인업, 회의록, 퀴즈 질문 목록, 진단 리포트 등 문서 |
| **santokki/README.md** | santokki 전용 상세 설명·흐름·기술 스택 |
| **santokki/privacy.html** | 개인정보 처리방침 |
| **santokki/** `fix_*.py`, `test_mc*.py` | 퀴즈 UI 수정·ManyChat API 테스트용 스크립트 (일부는 절대 경로 사용 — 경로 변경 시 수정 필요) |

자세한 흐름, 매칭 알고리즘, Firestore 구조, n8n 사용법은 **santokki/README.md**를 보세요.

---

## 🔗 연결 관계

- 쇼핑몰 상품 상세 URL은 ManyChat DM·퀴즈 결과에서 “구매 링크”로 사용됩니다.
- 제품 ID·이름은 `p/products.json`과 santokki 쪽 매칭 로직이 맞아야 합니다.
- 퀴즈 배포 URL: `https://santokki-f7c72.web.app` (Firebase Hosting)

---

## ⚠️ 참고

- **santokki** 내 `fix_quiz_ui.py`, `fix_line975.py`, `fix_n8n_crypto.py` 등은 예전에 `C:\Users\user\Desktop\santokki\` 같은 **절대 경로**를 참조할 수 있습니다. `p` 폴더 구조에 맞게 쓰려면 스크립트 안의 경로를 `p\santokki\quiz\index.html` 등으로 바꿔야 합니다.
- `.env`, `firebase-key.json` 등 비밀 키는 Git에 올리지 마세요. `santokki/.env.example`을 참고해 로컬에 `.env`를 만듭니다.
