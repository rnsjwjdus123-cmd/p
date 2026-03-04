"""
influencer_marketing/core/competitor_analysis.py
경쟁사 실시간 분석 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[기능]
  Perplexity로 영국 홈 프래그런스 경쟁사 인플루언서 캠페인을 실시간 검색하고,
  GPT로 경쟁 분석 + 포지셔닝 맵 데이터를 생성한다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
import requests
from openai import OpenAI
from influencer_marketing.data.evidence import get_evidence


UK_COMPETITORS = [
    {"name": "Jo Malone London", "tier": "럭셔리", "price_range": "£50~£120",
     "positioning": "영국 정통 럭셔리 향수 하우스"},
    {"name": "Diptyque", "tier": "럭셔리", "price_range": "£55~£90",
     "positioning": "프랑스 니치 향수, 영국 프리미엄 시장 강자"},
    {"name": "The White Company", "tier": "프리미엄 매스", "price_range": "£20~£45",
     "positioning": "영국 중산층 라이프스타일 브랜드"},
    {"name": "Yankee Candle", "tier": "매스", "price_range": "£10~£30",
     "positioning": "대중적 홈 프래그런스 시장 점유율 1위"},
    {"name": "NEOM Organics", "tier": "웰니스 프리미엄", "price_range": "£25~£65",
     "positioning": "자연주의 웰니스 포지셔닝"},
]


def search_competitor_campaigns(api_key: str) -> dict:
    """Perplexity로 경쟁사 인플루언서 캠페인 실시간 검색"""
    competitor_names = ", ".join(c["name"] for c in UK_COMPETITORS)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a UK home fragrance market research analyst. "
                    "Provide factual, source-backed information about competitor "
                    "influencer marketing campaigns. Include specific details: "
                    "which influencers they used, platforms, campaign themes, "
                    "engagement results if available. Always cite sources."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Research the latest influencer marketing campaigns and social media "
                    f"strategies of these UK home fragrance brands: {competitor_names}. "
                    f"For each brand: "
                    f"1) Recent influencer collaborations (2025-2026) "
                    f"2) Which social platforms they focus on "
                    f"3) What type/tier of influencers they use "
                    f"4) Campaign themes and content style "
                    f"5) Any notable engagement metrics or results "
                    f"Focus on the UK market."
                ),
            },
        ],
        "max_tokens": 3000,
        "return_citations": True,
        "search_recency_filter": "month",
    }
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers, json=payload, timeout=45,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "citations": data.get("citations", []),
            "success": True,
        }
    except Exception as e:
        return {"content": "", "citations": [], "success": False, "error": str(e)}


def analyze_competitors_with_gpt(
    product_name: str,
    product_data: dict,
    perplexity_competitor_data: dict,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """GPT로 경쟁사 분석 + 포지셔닝 맵 좌표 + 차별화 전략 생성"""
    client = OpenAI(api_key=api_key, timeout=90.0)

    competitor_context = ""
    if perplexity_competitor_data.get("success"):
        competitor_context = (
            "[Perplexity 실시간 경쟁사 검색 결과]\n"
            + perplexity_competitor_data["content"]
        )

    competitors_json = json.dumps(UK_COMPETITORS, ensure_ascii=False, indent=2)

    system_prompt = (
        "당신은 영국 홈 프래그런스 시장 전략 분석가입니다.\n"
        "근거 DB와 실시간 검색 결과를 기반으로 경쟁 분석 JSON을 출력하십시오.\n\n"
        "━━ 근거 데이터베이스 ━━\n" + get_evidence()
    )

    user_prompt = f"""[분석 대상 제품]
제품명: {product_name}
카테고리: {product_data['category']}
컨셉: {product_data['concept']}
마케팅: {product_data['marketing']}
영국 적합성: {product_data['uk_fit']}

[경쟁사 기본 정보]
{competitors_json}

{competitor_context}

━━ 분석 원칙 (필수) ━━
- 팩트·실제 시장 포지션 기반으로 작성. 가격이 비싸다고 시장에서 실패한 것으로 단순화하지 말 것.
  예: Jo Malone은 고가이지만 영국 프리미엄/퍼스널·홈 프래그런스에서 1위급 시장 지위. 가격 경쟁력 점수만으로 순위를 매기지 말고, 실제 브랜드 파워·시장 점유·타겟 세그먼트 성과를 반영할 것.
- why_competitor: 같은 채널·같은 타겟(홈/퍼스널 프래그런스, UK)에서 왜 경쟁 관계인지 구체적 사실로 서술 (채널, 타겟, 가격대 겹침, 인플루언서 전략 등).
- win_points: Santokki가 해당 브랜드 대비 어디서 이길 수 있는지 예상 가능한 차별화 포인트를 팩트 기반으로 (가격대, 스토리, 지속가능성, 한국 헤리티지 등). 단순 나열이 아니라 전략적 의미 포함.

━━ 출력 JSON 스키마 (모든 필드 필수) ━━
{{
  "competitor_analysis": [
    {{
      "brand": "브랜드명",
      "tier": "럭셔리/프리미엄/매스",
      "why_competitor": "같은 채널·타겟에서 왜 경쟁자인지 팩트 기반 2~3문장 (채널/타겟/실제 시장 포지션 포함)",
      "win_points": "Santokki가 이 브랜드 대비 공략할 수 있는 포인트, 팩트·예상 기반 (가격·스토리·차별화 등)",
      "influencer_strategy_summary": "인플루언서 전략 요약 2~3문장",
      "influencer_type": "주 사용 인플루언서 유형",
      "platforms": ["Instagram", "TikTok"],
      "strengths": ["강점1", "강점2"],
      "weaknesses": ["약점1", "약점2"],
      "estimated_monthly_spend": "추정 월간 인플루언서 예산 £"
    }}
  ],
  "positioning_map": [
    {{
      "brand": "브랜드명",
      "x_price": 0~100 숫자 (높을수록 고가),
      "y_uniqueness": 0~100 숫자,
      "bubble_size": 10~60 숫자
    }}
  ],
  "our_differentiation": {{
    "unique_value_proposition": "핵심 차별점 3~4문장",
    "gap_opportunities": ["시장 공백1", "공백2", "공백3"],
    "recommended_counter_strategy": "추천 인플루언서 전략 3~4문장",
    "price_positioning_advice": "가격 포지셔닝 제안"
  }},
  "competitive_threat_level": {{
    "direct_competitors": ["직접 경쟁"],
    "indirect_competitors": ["간접 경쟁"],
    "threat_assessment": "경쟁 위협 평가 2~3문장 (실제 시장 포지션 반영)",
    "moat_strategy": "K-라이프스타일 기반 해자 구축 방안"
  }},
  "evidence_used": ["[코드] 내용 (출처)"]
}}

규칙:
1. positioning_map에 'Santokki ({product_name})'도 반드시 포함
2. Perplexity 결과 최우선 활용
3. why_competitor, win_points는 팩트·실제 시장 포지션 기반. 고가=실패가 아님(조말론 등 1위급 사례 반영)
4. 빈 값 금지
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
        max_tokens=4000,
    )
    return json.loads(response.choices[0].message.content)
