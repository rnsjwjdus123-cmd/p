"""
influencer_marketing/data/evidence.py
────────────────────────────────────────────────────────────────────────
검증된 근거 데이터베이스 (v4 — 2026.03 대폭 강화)

[v4 수정 사항]
1. 개별 항목(A-1, B-3 등)에 인라인 출처 URL 직접 매핑
2. 신규 출처 12건 추가 (Sprout Social, Shopify UK, Afluencer, GoViral 등)
3. 신뢰도 등급 기준 명시
4. CAGR 불일치 해소를 위한 설명 강화
5. K-뷰티 ≠ K-프래그런스 면책조항 추가
6. 데이터 수집 기준일 명시

[신뢰도 등급 기준]
★★★ = 정부기관 / 피어리뷰 학술저널 / 공식 규제기관 / 공인 업계 단체(IPA 등)
★★☆ = 업계 공인 리서치 기관(Statista, Grand View 등) / 주요 마케팅 플랫폼(Sprout Social, HubSpot 등)
★☆☆ = 에이전시 블로그 / 뉴스 기사 / 비피어리뷰 리포트
⚠️   = 직접 데이터 없이 유추한 항목 (면책조항 포함)

[데이터 수집 기준일: 2026년 3월]
"""

EVIDENCE_DB = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[A] 영국 인플루언서 의뢰비 벤치마크  |  신뢰도: ★★☆  [7개 출처 교차검증]
    출처 1: Charle Agency UK (2026.02)  https://www.charle.co.uk/articles/influencer-marketing-statistics/
    출처 2: Awin UK (2026)  https://www.awin.com/gb/sector-insights/uk-influencer-marketing-cost
    출처 3: Influencer Marketing Hub (2025)  https://influencermarketinghub.com/influencer-rates/
    출처 4: Socially Powerful (2026)  https://sociallypowerful.com/influencer/marketing/cost
    출처 5: Journal of Marketing, Sage/AMA, DOI:10.1177/00222429231217471 (2024.07)  ★★★
    출처 6: Shopify UK "Influencer Pricing 2026" (2026)  https://www.shopify.com/uk/blog/influencer-pricing  ★★☆
    출처 7: Afluencer "Influencer Rates 2026" (2026)  https://afluencer.com/influencer-rates/  ★★☆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A-1. 나노(1K~10K): 게시물 £50~£350 / 스토리 £25~£175
     [출처: Charle UK 2026 + Awin 2026 + Socially Powerful 2026 교차검증]
     [Shopify UK 2026: 나노 Instagram $10~$100/post, TikTok $5~$25/post — 환율 감안 유사 범위]
A-2. 마이크로(10K~100K): 게시물 £150~£700 / 스토리 £75~£350
     [출처: Charle UK 2026 + Awin 2026 + IMH 2025 교차검증]
     [GoViral UK 2025: 47% 인플루언서가 $250~$1,000/post (글로벌 UK/US 혼합)]
A-3. 매크로(100K~500K): 게시물 £1,000~£5,500 / 스토리 £500~£2,750
     [출처: Charle UK 2026 + Socially Powerful 2026 교차검증]
A-4. 미드티어(500K~1M): 게시물 £5,000~£12,000 / 스토리 £2,500~£6,000
     [출처: Charle UK 2026 + Socially Powerful 2026]
A-5. 학술 근거: 나노 ROIS가 매크로 대비 3배+. 비용 18배 저렴, 매출 차이 6배
     [출처: Journal of Marketing (Sage/AMA) 2024, DOI:10.1177/00222429231217471]  ★★★
A-6. 권장 초기 캠페인 예산: £1,000~£3,000 (나노/마이크로 중심)
     [출처: Charle UK 2026 + Awin 2026 + IMH 2025 + Socially Powerful 2026 — 4개 출처 범위 교차검증]
     ⚠️ 이 수치는 일반적 권장 범위이며, 홈 프래그런스 특화 데이터는 아님
A-7. [신규] 39% 브랜드가 나노 인플루언서를 최우선 파트너로 선택 (2025)
     [출처: Afluencer 2026 — 원본: IMH 2025 서베이]
A-8. [신규] 62% 브랜드가 2026년 인플루언서 예산 증액 예정, 30%+가 $5M 이상 투자
     [출처: Afluencer 2026 — 원본: Linqia "2026 State of Influencer Marketing" 리포트]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[B] 인플루언서 마케팅 ROI 및 효과  |  신뢰도: ★★★
    출처 1: IPA "Influencer Marketing ROI" (2025.11)  https://ipa.co.uk/news/influencer-marketing  ★★★
    출처 2: PMC/NLM 체계적 문헌 검토 (2024.03)  https://pmc.ncbi.nlm.nih.gov/articles/PMC10968221/  ★★★
    출처 3: Journal of Marketing (Sage/AMA) (2024.07)  ★★★
    출처 4: JMSR 니치 마켓 연구 (2025)  https://jmsr-online.com/  ★★☆
    출처 5: Charle UK (2026.02)  https://www.charle.co.uk/articles/influencer-marketing-statistics/  ★★☆
    출처 6: [신규] Sprout Social "2026 UK Guide" (2026.01)  https://sproutsocial.com/insights/uk-influencers/  ★★☆
    출처 7: [신규] GoViral Global UK (2025.11)  https://www.goviralglobal.com/post/united-kingdom-influencer-marketing-kol-statistics-updated-2025  ★★☆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B-1. 단기 ROI 지수: 99 (전채널 평균 100과 동등)
     [출처: IPA 2025 — 영국 59개 캠페인 £133M 실측]  ★★★
B-2. 장기 ROI 지수: 151 (전채널 1위) / 장기 승수 3.35 (TV 3.27 상회)
     [출처: IPA 2025 — 영국 220개 캠페인 실측]  ★★★
B-3. £1 투자 대비 평균 £5.78 수익
     [출처: Charle UK 2026]  ★★☆
     ⚠️ 단일 에이전시 출처. IPA 실측 데이터(B-1, B-2)와 교차 확인 시 방향성 일치하나 정확한 수치 검증은 제한적
B-4. Instagram 마이크로 참여율: 3~5% (매크로 대비 2~3배)
     [출처: PMC/NLM 2024 체계적 문헌 검토]  ★★★
B-5. TikTok 나노 참여율: 15.2% / TikTok 마이크로: 12.4%
     [출처: Statista (Charle UK 2026 인용)]  ★★☆
     ⚠️ Statista 원본 유료 리포트에서 재인용. Charle UK가 명시적으로 Statista를 출처로 표기함
B-6. 61% 마케터가 마이크로 인플루언서 우선 투자
     [출처: Charle UK 2026]  ★★☆
B-7. 83% 브랜드가 인플루언서 마케팅을 "효과적"으로 평가
     [출처: Charle UK 2026]  ★★☆
B-8. 니치 마켓에서 마이크로 참여율 매크로 대비 3~4배
     [출처: JMSR 2025]  ★★☆
B-9. Instagram Reels 참여율: 정적 게시물 대비 22% 높음
     [출처: Charle UK 2026]  ★★☆
B-10. [신규] UK 성인 25%가 인플루언서 추천으로 구매 결정. Gen Z는 50%+
      [출처: Sprout Social 2026 UK Guide]  ★★☆
B-11. [신규] 81% UK 브랜드가 마이크로 인플루언서(10K~100K) 활용
      [출처: GoViral Global UK 2025]  ★★☆
B-12. [신규] 69% UK 소비자가 인플루언서 추천 후 구매 경험 있음
      [출처: GoViral Global UK 2025]  ★★☆
B-13. [신규] 59% 마케터가 2025년 인플루언서 파트너십 확대 계획
      [출처: Sprout Social Q1 2025 서베이 — 650명 US/UK/AU 마케터]  ★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[C] 인플루언서 접촉 채널  |  신뢰도: ★★☆
    출처 1: HubSpot "2026 Marketing Statistics" (2025.09)  https://www.hubspot.com/marketing-statistics  ★★☆
    출처 2: InfluenceFlow "Outreach Best Practices 2026" (2026.02)  https://influenceflow.io/  ★☆☆
    출처 3: Instagram Help Center (2025)  https://help.instagram.com/  ★★★
    출처 4: CreatorFlow (2026)  ★☆☆
    출처 5: StarNgage Pro (2025)  ★☆☆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C-1. B2C 이메일 평균 오픈율: 19.7%
     [출처: HubSpot 2026]  ★★☆
     ⚠️ 전업종 B2C 평균. 인플루언서 아웃리치 전용 오픈율은 별도 공개 데이터 없음
C-2. 개인화 아웃리치 응답률: 비개인화 대비 3~5배 상승
     [출처: InfluenceFlow 2026]  ★☆☆
     ⚠️ 마케팅 업체 블로그 출처. 원본 데이터셋 비공개. 방향성은 HubSpot 개인화 연구와 일치
C-3. Instagram DM: 신규 계정 일일 한도 초과 시 계정 제한/정지 위험
     [출처: Instagram Help Center 2025 공식 정책]  ★★★
     [출처: StarNgage Pro 2025 — DM 한도 96% 축소 보고]  ★☆☆
     [출처: CreatorFlow 2026 — 신규 계정 일일 10~20건 한도]  ★☆☆
C-4. 플랫 피(고정 지급)가 가장 일반적. 퍼포먼스 기반 25%로 성장
     [출처: Charle UK 2026]  ★★☆
C-5. [신규] Creator Marketplace 사용 시 응답률 37% (DM 대비 4배+)
     [출처: CreatorFlow 2026]  ★☆☆
     ⚠️ 단일 출처, 자사 플랫폼 홍보 가능성 고려 필요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[D] 영국 홈 프래그런스 시장  |  신뢰도: ★★☆ (5개 기관 교차 확인)
    출처 1: Deep Market Insights (2026.01)  https://deepmarketinsights.com/vista/insights/home-fragrance-market/united-kingdom  ★★☆
    출처 2: Research and Markets (2025)  https://www.researchandmarkets.com/report/united-kingdom-home-fragrance-market  ★★☆
    출처 3: Grand View Research (2026.01)  https://www.grandviewresearch.com/horizon/outlook/home-fragrance-market/uk  ★★☆
    출처 4: 6W Research (2025.11)  https://www.6wresearch.com/industry-report/united-kingdom-uk-home-fragrance-market-outlook  ★★☆
    출처 5: [신규] Knowledge Sourcing (2025)  https://www.knowledge-sourcing.com/report/uk-home-fragrance-market  ★★☆
    출처 6: [신규] Expert Market Research (2025)  https://www.expertmarketresearch.com/reports/united-kingdom-home-fragrance-market  ★★☆
    ※ CAGR 기관별 차이(4.80%~9.49%) 설명:
       - 4.80% (Knowledge Sourcing): 2025~2030 기준, USD $622M→$787M
       - 6.10% (Research and Markets / Expert MR): 2025~2034 기준, 10년 장기 전망
       - 8.4~8.5% (Grand View Research): 2024~2030 기준, 스프레이 포함 넓은 범위
       - 9.49% (Deep Market Insights): 2025~2033 기준, £833M→£1,864M
       기관별 차이 원인: 집계 기간, 포함 제품 범위(캔들만 vs 디퓨저 포함), 환율 기준 상이
       투자자 커뮤니케이션 시: "복수 기관 5~9.5% 범위 교차 확인, 중앙값 약 7%" 표현 권장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D-1. UK 홈 프래그런스 시장: £833.11M (2024)
     [출처: Deep Market Insights 2026]  ★★☆
D-2. 2033년 전망: £1,864.34M / CAGR 9.49%
     [출처: Deep Market Insights 2026]  ★★☆
D-3. CAGR 6.10% (2025~2034)
     [출처: Research and Markets 2025 + Expert Market Research 2025 — 2개 기관 일치]  ★★☆
D-4. CAGR 8.4% (2024~2030), UK 시장 $1,203M by 2030
     [출처: Grand View Research 2026.01]  ★★☆
D-5. 영국 E-commerce 비중 1위: £420.14M (2024)
     [출처: Deep Market Insights 2026]  ★★☆
D-6. 비럭셔리(매스) 제품 비중: 62% (2024)
     [출처: Research and Markets 2025]  ★★☆
     [교차확인: Expert Market Research 2025 — "62% non-luxury" 동일 수치]
D-7. 영국 수입 성장률: 10.28% (2024) / CAGR 3.77% (2020~2024)
     [출처: 6W Research 2025]  ★★☆
D-8. [신규] UK 홈 프래그런스 USD $622.5M (2025) → $787M (2030), CAGR 4.80%
     [출처: Knowledge Sourcing 2025]  ★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[E] 영국 ASA 광고 규제  |  신뢰도: ★★★
    출처 1: ASA 공식 (2025.05)  https://www.asa.org.uk/news/influencer-ad-disclosure-on-social-media-instagram-and-tiktok-report-2024.html  ★★★
    출처 2: RPC Legal (Winter 2025)  https://www.rpclegal.com/snapshots/advertising-and-marketing/winter-2025/  ★★★
    출처 3: IMTB (2025.05)  https://imtb.org.uk/imtb-responds-to-asa-influencer-ad-sweep/  ★★★
    출처 4: Lewis Silkin LLP (2025.05)  https://www.lewissilkin.com/insights/2025/05/09/asa-publishes-new-report-on-influencer-transparency-102kaqy  ★★★
    출처 5: Jamieson Law (2025.11)  https://jamiesonlaw.legal/resources/blog/influencer-marketing-rules-uk/  ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E-1. 유료 협찬 + 기프팅 모두 #ad 또는 "Paid Partnership" 표기 의무
     [출처: ASA 2025 + RPC Legal 2025 — 2개 법률/규제 출처 일치]  ★★★
E-2. #gifted 단독 사용: 2025년부터 규정 미준수
     [출처: ASA 2025 업데이트]  ★★★
E-3. 2024년 ASA 불만 신고: 3,566건 (인플루언서 광고 관련)
     [출처: ASA 공식 2024 연간 보고서]  ★★★
E-4. 인플루언서 광고 공시 적절 비율: 49% (2021년 35% → 개선 중)
     [출처: Lewis Silkin 2025 + IMTB 2025 — 2개 법률 출처 일치]  ★★★
E-5. 브랜드 공동 책임 적용 (DMCC Act 2025~)
     [출처: RPC Legal Winter 2025]  ★★★
E-6. 표기 위치: 게시물 첫 줄 / 영상 시작부
     [출처: ASA 2025 + Jamieson Law 2025 — 규제+법률 출처 일치]  ★★★

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[F] K-라이프스타일 영국 트렌드  |  신뢰도: ★★☆ ~ ★☆☆ (혼합)
    출처 1: Korea Times (2026.02)  ★☆☆
    출처 2: Omdia / Ampere Analysis  ★★☆
    출처 3: Global Hallyu Trends  ★☆☆
    출처 4: [신규] MEIYUME / Future Market Insights (2025)  https://meiyume.com/k-beauty-export-trends/  ★★☆
    출처 5: [신규] International Trade Council (2025.07)  https://tradecouncil.org/south-korea-becomes-global-trade-leader-in-cosmetics/  ★★☆
    출처 6: [신규] REACH24H / KITA (2024.10)  https://en.reach24h.com/news/industry-news/cosmetic/k-beauty-exports-reach-new-records-in-q3-2024  ★★☆
    출처 7: [신규] PersonalCareInsights (2025.05)  https://www.personalcareinsights.com/news/k-beauty-global-export-growth-2025.html  ★★☆

    ⚠️ 중요 면책조항: 아래 데이터는 K-뷰티(화장품) 전체 수치입니다.
       "K-홈 프래그런스" 별도 수출/수입 통계는 현재 공개된 것이 없습니다.
       K-뷰티 성장 → K-프래그런스 기회는 유추이며, 직접 근거가 아닙니다.
       KITA(한국무역협회) 수출 통계가 "화장품" 카테고리로 묶여 있어 홈 프래그런스만 분리 불가.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F-1. 영국 K-뷰티 수입 증가율: 2024년 20% / 2025년 17%
     [출처: Korea Times 2026.02]  ★☆☆
     [교차확인: 한국 화장품 수출 전체 20.3% YoY 성장 — International Trade Council 2025]  ★★☆
F-2. BORNTOSTANDOUT — Selfridges 입점 K-향수 브랜드 실제 사례
     [출처: Korea Times 2026.02 + Selfridges 웹사이트 확인 가능]  ★☆☆
F-3. BTS 영국 유튜브 구독자: 24.6M (2025)
     [출처: Global Hallyu Trends]  ★☆☆
     ⚠️ K-팝 인지도 지표. K-프래그런스 구매 연결성은 간접적
F-4. K-콘텐츠 Netflix 영국 1위, 89개국 80% 점유
     [출처: Omdia/Ampere Analysis]  ★★☆
     ⚠️ K-콘텐츠 소비 지표. K-프래그런스 직접 연결 아님
F-5. P1Harmony 2024 Troxy 3,000명 → 2026 OVO Arena Wembley 8,000명
     [출처: Korea Times]  ★☆☆
F-6. [신규] 한국 화장품 수출 $10.2B (2024), YoY 20.3% 성장 — 세계 3위
     [출처: International Trade Council 2025 + PersonalCareInsights 2025]  ★★☆
F-7. [신규] K-뷰티 수출 Q3 2024 누적 $7.4B, YoY 19.3% 증가
     [출처: REACH24H / KITA 2024.10 — 한국 식약처 공식 발표 기반]  ★★☆
F-8. [신규] 유럽 K-뷰티 시장 $5.6B by 2032 전망, UK가 유럽 내 성장 선도
     [출처: MEIYUME / Future Market Insights 2025]  ★★☆
F-9. [신규] L'Oreal이 K-뷰티 브랜드 인수 (Dr.G, 2025.01) — 글로벌 대기업의 K-뷰티 생태계 투자 확대
     [출처: Future Market Insights 2026]  ★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[G] 캠페인 리스크 및 실무  |  신뢰도: ★★★~★★☆ (혼합)
    출처 1: IPA (2025.11)  https://ipa.co.uk/news/influencer-marketing  ★★★
    출처 2: RPC Legal / ASA 2025  ★★★
    출처 3: Charle UK (2026.02)  ★★☆
    출처 4: [신규] Sprout Social UK 2026  https://sproutsocial.com/insights/uk-influencers/  ★★☆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
G-1. ROI는 미디어 최적화보다 브랜드-인플루언서 적합도에 좌우
     [출처: IPA 2025 — 220개 캠페인 실측]  ★★★
G-2. 가짜 팔로워 탐지 AI 정확도: 95%+ (HypeAuditor, Modash)
     [출처: Charle UK 2026]  ★★☆
G-3. 사전 크리에이티브 브리핑 없이 진행 시 브랜드-콘텐츠 불일치 위험
     ⚠️ 업계 통상적 베스트 프랙티스. 특정 연구 수치 없음.
     [출처: Sprout Social UK 2026 — 성과 측정 및 브랜드 세이프티 강조]  ★★☆
G-4. 계약서에 ASA 공시 의무 조항 포함 필수 — 브랜드 법적 공동 책임
     [출처: RPC Legal 2025]  ★★★
G-5. Instagram Reels 참여율: 정적 게시물 대비 22% 높음
     [출처: Charle UK 2026]  ★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[H] 영국 인플루언서 마케팅 시장 규모  |  신뢰도: ★★☆ (4개 기관 교차)
    출처 1: Statista (2024.10)  https://www.statista.com/outlook/amo/advertising/influencer-advertising/united-kingdom  ★★☆
    출처 2: Our Own Brand (2026.02)  https://ourownbrand.co/influencer-marketing-statistics-uk-trends-spend-compliance/  ★★☆
    출처 3: Charle UK (2026.02)  ★★☆
    출처 4: [신규] IMARC Group (2025)  ★★☆
    출처 5: [신규] Kolsquare (2025)  ★★☆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H-1. UK 인플루언서 마케팅 시장: £2.36B (2024) → £2.9B (2026E), CAGR 29.5%
     [출처: IMARC Group (Charle UK 2026 인용) + Our Own Brand 2026]  ★★☆
     [교차확인: IMARC Group — UK $3.1B (2025), CAGR 28.03% (2026-2034)]  ★★☆
H-2. UK 인플루언서 광고 지출: £930M (2024) → £1.3B (2029E)
     [출처: Statista 2024 + Kolsquare 2025]  ★★☆
     [교차확인: Statista — UK $1.51B (2025), CAGR 13.17% (2025-2030)]  ★★☆
H-3. UK 내 5,000+ 팔로워 Instagram 계정: 98,000개+
     [출처: Charle UK 2026]  ★★☆
H-4. 글로벌 인플루언서 마케팅 시장: $34.1B (2026E)
     [출처: Statista + Charle UK 2026]  ★★☆
H-5. [신규] UK 기업 평균 인플루언서 마케팅 연간 지출: £849K
     [출처: GoViral Global UK 2025]  ★★☆
H-6. [신규] UK 브랜드 33%가 2025년에 인플루언서 2배 이상 확대 예정
     [출처: GoViral Global UK 2025]  ★★☆

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[I] 리스크 매트릭스 검증 데이터 (1~10 척도)  |  신뢰도: ★★☆ + ⚠️
    ※ 발생확률·영향도 각 1(낮음)~10(높음) 척도
    ⚠️ 아래 1~10 척도는 복수 출처의 정성적 데이터를 종합하여 산출한 주관적 평가입니다.
       특정 연구가 "ASA 위반 확률 = 4/10"이라고 발표한 것이 아닙니다.
       산출 방법: 각 리스크의 발생 빈도(출처 기반) × 영향 심각도(출처 기반)를
       업계 표준 리스크 프레임워크(확률×영향 매트릭스)에 매핑하여 1~10 척도로 변환.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I-1. ASA 위반: 발생 4/10, 영향 4/10
     산출 근거: ASA 민원 3,566건(E-3) + 공시 적절 비율 49%(E-4) → 약 절반이 미준수하나
     실제 제재는 경고 수준이 대부분 → 영향도 중간
     [출처: ASA 2024 + Lewis Silkin 2025 + NetInfluencer 2024]
I-2. 인플루언서 성과 미달: 발생 6/10, 영향 8/10
     산출 근거: 약 73% 캠페인이 유의미한 결과 미달(Launchpoint 2025) +
     소비자 61%가 불일치 시 신뢰 상실(Socially Powerful 2026) → 빈도 높고 영향 큼
     [출처: Launchpoint 2025 + Socially Powerful 2026]
I-3. 브랜드 평판 리스크: 발생 4/10, 영향 8/10
     산출 근거: ASA 공동 제재 사례 다수 + 신생 브랜드에는 단 1건도 치명적
     [출처: NetInfluencer 2024 + Socially Powerful 2026]
I-4. 외국 브랜드 UK 시장 진입: 발생 6/10, 영향 6/10
     산출 근거: K-뷰티 Boots 입점 등 긍정 사례 있으나 현지화 마케팅 없이는 실패
     [출처: The Guardian 2025 + Accuvion 2025 + SiliconII/MK News 2025]
I-5. 예산/ROI 미달: 발생 6/10, 영향 6/10
     산출 근거: 평균 ROI £5.78(B-3)이나 73% 성과 미달(I-2) + 단가 연 25%+ 상승
     [출처: Charle UK 2026 + Launchpoint 2025 + Socially Powerful 2026]
I-6. Instagram DM 계정 제한: 발생 8/10, 영향 9/10
     산출 근거: Instagram 공식 정책으로 콜드 DM 아웃리치 사실상 금지(2025~) +
     한도 96% 축소 + 수천 계정 영구 정지 보고 → 신규 한국 브랜드 계정에 최고 위험
     [출처: Instagram Help Center 2025 + StarNgage Pro 2025 + CreatorFlow 2026]
"""


# ── 신뢰도 등급 기준 (프로그램 내 표시용) ────────────────────────
RELIABILITY_CRITERIA = """
📊 데이터 신뢰도 등급 기준
━━━━━━━━━━━━━━━━━━━━━━━━━━
★★★ 높음: 정부기관(ASA, IPA), 피어리뷰 학술저널(PMC, Journal of Marketing), 공식 규제기관
★★☆ 중간: 업계 공인 리서치(Statista, Grand View), 주요 마케팅 플랫폼(Sprout Social, HubSpot)
★☆☆ 낮음: 에이전시 블로그, 뉴스 기사, 비피어리뷰 리포트
⚠️  주의: 직접 데이터 없이 유추한 항목, 이중 인용, 단일 출처

📅 데이터 수집 기준일: 2026년 3월
⚠️ 시장 데이터는 시간이 지나면 노후화됩니다. 최신 수치는 Perplexity 실시간 검색으로 교차 확인하세요.
"""


# ── 근거 부족 항목 면책조항 (프로그램 내 표시용) ──────────────────
DATA_LIMITATIONS = """
⚠️ 데이터 한계 및 면책조항
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. K-프래그런스 영국 수입 통계: K-뷰티(화장품) 전체 데이터만 존재.
   KITA(한국무역협회) 수출 통계가 "화장품"으로 묶여 홈 프래그런스 분리 불가.
   → K-뷰티 성장 데이터는 유추 근거이며, K-프래그런스 직접 근거가 아닙니다.

2. 리스크 매트릭스 1~10 척도: 복수 출처의 정성적 데이터를 종합한 주관적 평가.
   특정 연구가 이 척도를 발표한 것이 아닙니다.

3. 인플루언서 아웃리치 전용 오픈율/응답률: 공개된 전용 데이터가 없어
   B2C 전업종 평균(HubSpot)을 대리지표로 사용합니다.

4. 홈 프래그런스 특화 전환율: 공개된 니치 마켓 전환율 데이터 없음.
   ROI 시뮬레이션의 전환율은 일반 소셜 미디어 전환율 범위(0.5~3%) 내 추정치입니다.

5. CAGR 불일치: 영국 홈 프래그런스 시장 CAGR이 기관별 4.8%~9.5%로 차이남.
   집계 기간, 포함 제품 범위, 예측 방법론이 다르기 때문. 중앙값 약 7% 기준 권장.
"""


def get_evidence() -> str:
    """evidence.py 전체 DB 문자열 반환 — GPT 프롬프트 주입용"""
    return EVIDENCE_DB


def get_reliability_criteria() -> str:
    """신뢰도 등급 기준 반환 — UI 표시용"""
    return RELIABILITY_CRITERIA


def get_data_limitations() -> str:
    """데이터 한계 면책조항 반환 — UI 표시용"""
    return DATA_LIMITATIONS
