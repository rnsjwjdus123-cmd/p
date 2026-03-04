"""
influencer_marketing/core/hashtag_trends.py
실시간 해시태그/키워드 트렌드 분석 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[기능]
  Perplexity로 홈 프래그런스 관련 해시태그/키워드 트렌드를 실시간 검색하고,
  GPT로 제품별 최적 해시태그 세트 + 콘텐츠 전략을 생성한다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
import requests
from openai import OpenAI
from influencer_marketing.data.evidence import get_evidence


def search_hashtag_trends(product_keywords: list, api_key: str) -> dict:
    """
    Perplexity로 현재 트렌드 해시태그/키워드 실시간 검색

    [검색 전략]
    - 제품 키워드를 포함한 인스타그램/틱톡 해시태그 트렌드
    - UK 시장 특화 검색
    - 경쟁사 해시태그 + K-beauty/K-lifestyle 해시태그 포함
    """
    kw_str = ", ".join(product_keywords[:4])
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
                    "You are a social media trend analyst specializing in "
                    "UK home fragrance and lifestyle markets. "
                    "Provide specific, data-backed hashtag and keyword trends "
                    "with actual post counts, growth rates, and engagement metrics "
                    "where available. Always cite sources."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Research current trending hashtags and keywords on Instagram and TikTok "
                    f"related to: {kw_str}, home fragrance, candles, room spray, K-beauty, "
                    f"K-lifestyle in the UK market (2025-2026). Include:\n"
                    f"1) Top performing hashtags with approximate post counts\n"
                    f"2) Rising/emerging hashtags gaining traction\n"
                    f"3) Hashtag engagement rates where available\n"
                    f"4) Seasonal trending keywords right now\n"
                    f"5) K-beauty and K-lifestyle related trending tags in UK\n"
                    f"6) Niche hashtags that home fragrance influencers are using\n"
                    f"7) Any platform-specific trends (Reels vs TikTok differences)"
                ),
            },
        ],
        "max_tokens": 2500,
        "return_citations": True,
        "search_recency_filter": "week",
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


def analyze_trends_with_gpt(
    product_name: str,
    product_data: dict,
    perplexity_trends: dict,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    GPT로 트렌드 데이터 기반 제품 맞춤 해시태그 전략 생성

    [생성 내용]
    - 추천 해시태그 세트 (카테고리별)
    - 트렌드 활용 콘텐츠 아이디어
    - 경쟁사 vs 우리의 해시태그 차별화
    - 급상승 키워드 기반 타이밍 제안
    """
    client = OpenAI(api_key=api_key, timeout=90.0)

    trends_context = ""
    if perplexity_trends.get("success"):
        trends_context = (
            "[Perplexity 실시간 트렌드 검색 결과]\n"
            + perplexity_trends["content"]
        )

    system_prompt = (
        "당신은 영국 소셜 미디어 마케팅 전략가입니다.\n"
        "해시태그와 키워드 트렌드를 분석하여 제품 맞춤 전략을 수립합니다.\n\n"
        "━━ 근거 데이터베이스 ━━\n" + get_evidence()
    )

    user_prompt = f"""[제품 정보]
제품명: {product_name}
카테고리: {product_data['category']}
컨셉: {product_data['concept']}
키워드: {', '.join(product_data['keywords'])}
영국 적합성: {product_data['uk_fit']}

{trends_context}

━━ 출력 JSON 스키마 ━━
{{
  "trend_summary": {{
    "market_pulse": "현재 영국 홈 프래그런스 소셜 미디어 트렌드 요약 3~4문장",
    "platform_comparison": {{
      "instagram": "Instagram 현재 트렌드 특징 2문장",
      "tiktok": "TikTok 현재 트렌드 특징 2문장"
    }},
    "k_lifestyle_momentum": "K-라이프스타일 관련 현재 트렌드 동향 2~3문장"
  }},
  "recommended_hashtags": {{
    "primary_tags": [
      {{"tag": "#해시태그", "category": "브랜드/제품/니치/트렌드", "estimated_reach": "추정 노출", "reason": "선택 이유"}}
    ],
    "trending_tags": [
      {{"tag": "#급상승태그", "growth_signal": "성장 신호 설명", "timing": "지금/이번주/이번달", "reason": "왜 지금인가"}}
    ],
    "niche_tags": [
      {{"tag": "#니치태그", "audience": "타겟 오디언스", "competition": "낮음/중간/높음", "reason": "이유"}}
    ],
    "k_culture_tags": [
      {{"tag": "#K관련태그", "relevance": "제품과의 연결고리", "uk_audience_size": "추정 UK 오디언스"}}
    ]
  }},
  "content_ideas_from_trends": [
    {{
      "trend": "현재 트렌드명",
      "content_idea": "이 트렌드를 활용한 구체적 콘텐츠 아이디어",
      "platform": "Instagram/TikTok/Both",
      "format": "Reel/Story/Feed/TikTok",
      "hashtag_set": ["#태그1", "#태그2", "#태그3"],
      "best_posting_time": "최적 게시 시간 (UK 기준)"
    }}
  ],
  "hashtag_strategy": {{
    "do": ["해야 할 것1", "할 것2", "할 것3"],
    "dont": ["하지 말아야 할 것1", "말 것2"],
    "optimal_count": "게시물당 최적 해시태그 수 + 이유",
    "rotation_strategy": "해시태그 로테이션 전략"
  }},
  "weekly_keyword_calendar": [
    {{
      "week": "이번 주 / 다음 주 / 2주 후 / 3주 후",
      "focus_keyword": "집중 키워드",
      "reason": "왜 이 시기인가",
      "suggested_tags": ["#태그1", "#태그2"]
    }}
  ],
  "evidence_used": ["[코드] 내용"]
}}

규칙:
1. Perplexity 검색 결과의 실제 데이터 최우선 활용
2. primary_tags: 8~12개, trending_tags: 5~8개, niche_tags: 5~8개, k_culture_tags: 5~8개
3. content_ideas_from_trends: 최소 5개 아이디어
4. weekly_keyword_calendar: 4주분
5. evidence DB [B-9] Reels 참여율 22% 높음 등 활용
6. 빈 값 금지
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
        max_tokens=4000,
    )
    return json.loads(response.choices[0].message.content)
