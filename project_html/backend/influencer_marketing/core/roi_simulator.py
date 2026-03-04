"""
influencer_marketing/core/roi_simulator.py
시나리오별 ROI 시뮬레이션 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[기능]
  투자 금액과 인플루언서 티어를 입력하면,
  evidence DB 수치 기반으로 낙관/보통/비관 3개 시나리오의
  월별 도달·전환·매출을 계산하고 차트 데이터를 반환한다.

[핵심 수치 출처]
  - ROI: [B-3] £1 → £5.78 (Charle UK 2026)
  - 참여율: [B-4] Instagram 마이크로 3~5%, [B-5] TikTok 나노 15.2%
  - 전환율: [B-8] 니치 마켓 마이크로 참여율 매크로 3~4배
  - 의뢰비: [A-1~A-4] 티어별 게시물/스토리 비용
  - 장기 승수: [B-2] 3.35 (IPA 2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
from influencer_marketing.data.evidence import get_evidence


# ── evidence 기반 고정 파라미터 ─────────────────────────────────
TIER_PARAMS = {
    "나노": {
        "post_cost_avg": 200,       # [A-1] £50~£350 중간값
        "story_cost_avg": 100,      # [A-1] £25~£175 중간값
        "avg_followers": 5_000,     # 1K~10K 중간값
        "engagement_rate": 0.152,   # [B-5] TikTok 나노 15.2%
        "ig_engagement": 0.06,      # 나노 Instagram 추정 6%
    },
    "마이크로": {
        "post_cost_avg": 425,       # [A-2] £150~£700 중간값
        "story_cost_avg": 212,      # [A-2] £75~£350 중간값
        "avg_followers": 50_000,    # 10K~100K 중간값
        "engagement_rate": 0.04,    # [B-4] Instagram 마이크로 3~5% 중간
        "ig_engagement": 0.04,
    },
    "매크로": {
        "post_cost_avg": 3_250,     # [A-3] £1,000~£5,500 중간값
        "story_cost_avg": 1_625,    # [A-3] £500~£2,750 중간값
        "avg_followers": 300_000,
        "engagement_rate": 0.015,   # [B-4] 매크로 1.5% 추정
        "ig_engagement": 0.015,
    },
}

# [B-3] 평균 ROI £5.78, [B-2] 장기 승수 3.35
BASE_ROI_MULTIPLIER = 5.78
LONG_TERM_MULTIPLIER = 3.35

# 시나리오별 보정 계수
SCENARIO_FACTORS = {
    "낙관": {
        "label": "🟢 낙관 (Best Case)",
        "engagement_mult": 1.3,     # 참여율 30% 상회
        "conversion_rate": 0.025,   # 참여자 중 2.5% 전환
        "roi_mult": 1.4,            # ROI 40% 상회
        "growth_rate": 0.15,        # 월 15% 성장
        "color": "#2ecc71",
    },
    "보통": {
        "label": "🟡 보통 (Base Case)",
        "engagement_mult": 1.0,
        "conversion_rate": 0.015,   # 1.5% 전환
        "roi_mult": 1.0,
        "growth_rate": 0.08,        # 월 8% 성장
        "color": "#f39c12",
    },
    "비관": {
        "label": "🔴 비관 (Worst Case)",
        "engagement_mult": 0.6,     # 참여율 40% 하회
        "conversion_rate": 0.008,   # 0.8% 전환
        "roi_mult": 0.5,            # ROI 50% 하회
        "growth_rate": 0.02,        # 월 2% 성장
        "color": "#e74c3c",
    },
}


def calculate_roi_scenarios(
    monthly_budget: float,
    tier: str = "마이크로",
    campaign_months: int = 6,
    avg_product_price: float = 35.0,
) -> dict:
    """
    evidence DB 기반 시나리오별 ROI 계산 (순수 로직, API 호출 없음)

    [계산 흐름]
    1. 월 예산 ÷ 게시물 단가 = 월간 인플루언서 수
    2. 인플루언서 수 × 평균 팔로워 = 총 노출
    3. 총 노출 × 참여율 × 시나리오 보정 = 참여 수
    4. 참여 수 × 전환율 = 예상 구매 수
    5. 구매 수 × 제품 가격 = 예상 매출
    6. 월별 성장률 적용 → 누적 매출
    7. 누적 매출 ÷ 총 투자 = ROI

    Returns:
        dict with 'scenarios', 'summary', 'params' keys
    """
    params = TIER_PARAMS.get(tier, TIER_PARAMS["마이크로"])
    cost_per_campaign = params["post_cost_avg"] + params["story_cost_avg"]
    influencers_per_month = max(1, int(monthly_budget / cost_per_campaign))

    results = {}
    for scenario_key, factors in SCENARIO_FACTORS.items():
        monthly_data = []
        cumulative_spend = 0
        cumulative_revenue = 0

        for month in range(1, campaign_months + 1):
            # 성장률 적용 (2개월차부터)
            growth = (1 + factors["growth_rate"]) ** (month - 1)
            effective_influencers = influencers_per_month * growth

            # 노출 → 참여 → 전환 → 매출
            total_reach = effective_influencers * params["avg_followers"]
            engagements = total_reach * params["ig_engagement"] * factors["engagement_mult"]
            conversions = engagements * factors["conversion_rate"]
            revenue = conversions * avg_product_price

            cumulative_spend += monthly_budget
            cumulative_revenue += revenue
            roi = (cumulative_revenue / cumulative_spend) if cumulative_spend > 0 else 0

            monthly_data.append({
                "month": month,
                "spend": round(monthly_budget, 0),
                "cumulative_spend": round(cumulative_spend, 0),
                "influencer_count": round(effective_influencers, 1),
                "reach": round(total_reach, 0),
                "engagements": round(engagements, 0),
                "conversions": round(conversions, 0),
                "revenue": round(revenue, 0),
                "cumulative_revenue": round(cumulative_revenue, 0),
                "roi_ratio": round(roi, 2),
            })

        # 최종 요약
        final = monthly_data[-1]
        results[scenario_key] = {
            "label": factors["label"],
            "color": factors["color"],
            "monthly_data": monthly_data,
            "final_summary": {
                "total_spend": final["cumulative_spend"],
                "total_revenue": final["cumulative_revenue"],
                "final_roi": final["roi_ratio"],
                "total_conversions": sum(m["conversions"] for m in monthly_data),
                "total_reach": sum(m["reach"] for m in monthly_data),
                "break_even_month": next(
                    (m["month"] for m in monthly_data if m["cumulative_revenue"] >= m["cumulative_spend"]),
                    None,
                ),
            },
        }

    return {
        "scenarios": results,
        "params": {
            "monthly_budget": monthly_budget,
            "tier": tier,
            "campaign_months": campaign_months,
            "avg_product_price": avg_product_price,
            "influencers_per_month": influencers_per_month,
            "cost_per_campaign": cost_per_campaign,
        },
        "evidence_sources": [
            "[B-3] £1 투자 → £5.78 수익 평균 ROI (Charle UK 2026)",
            "[B-4] Instagram 마이크로 참여율 3~5% (PMC/NLM 2024)",
            "[B-5] TikTok 나노 참여율 15.2% (Statista/Charle 2026)",
            "[A-1~A-4] 티어별 의뢰비 벤치마크 (Charle UK 2026)",
            "[B-2] 장기 ROI 승수 3.35 (IPA 2025 영국 실측)",
            "[B-8] 니치 마켓 마이크로 참여율 매크로 3~4배 (JMSR 2025)",
        ],
    }


def generate_roi_insights_with_gpt(
    roi_data: dict,
    product_name: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    GPT로 ROI 시뮬레이션 결과에 대한 투자자용 인사이트 생성

    [생성 내용]
    - 시나리오별 핵심 시사점
    - 투자자에게 강조할 포인트
    - 리스크 요인과 대응 방안
    - 추천 투자 전략
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key, timeout=60.0)

    scenarios_summary = {}
    for key, val in roi_data["scenarios"].items():
        scenarios_summary[key] = val["final_summary"]

    prompt = f"""당신은 스타트업 투자 분석가입니다.

아래는 '{product_name}'의 영국 인플루언서 마케팅 ROI 시뮬레이션 결과입니다.

[시뮬레이션 파라미터]
{json.dumps(roi_data['params'], ensure_ascii=False, indent=2)}

[시나리오별 최종 결과]
{json.dumps(scenarios_summary, ensure_ascii=False, indent=2)}

[사용된 근거]
{chr(10).join(roi_data['evidence_sources'])}

다음 JSON을 출력하십시오:
{{
  "executive_summary": "투자자용 핵심 요약 3~4문장",
  "scenario_insights": {{
    "낙관": "낙관 시나리오 시사점 2문장",
    "보통": "보통 시나리오 시사점 2문장",
    "비관": "비관 시나리오에서도 주목할 점 2문장"
  }},
  "investor_highlights": ["투자자 어필 포인트1", "포인트2", "포인트3"],
  "risk_factors": ["리스크1", "리스크2"],
  "recommended_strategy": "추천 투자/실행 전략 3~4문장",
  "break_even_analysis": "손익분기점 분석 2~3문장"
}}

규칙: evidence DB 수치를 반드시 인용. 빈 값 금지."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
        max_tokens=2000,
    )
    return json.loads(response.choices[0].message.content)
