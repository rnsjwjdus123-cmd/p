"""
influencer_marketing/core/timeline_generator.py
캠페인 타임라인 자동 생성 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[기능]
  제품 출시 시점(월)을 입력하면, 영국 시즌/이벤트에 맞춰
  12주 또는 24주 캠페인 타임라인을 GPT가 자동 생성한다.
  간트 차트 렌더링용 데이터 포함.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
from openai import OpenAI
from influencer_marketing.data.evidence import get_evidence


# ── 영국 주요 시즌/이벤트 캘린더 ────────────────────────────────
UK_EVENTS = {
    1: ["New Year, Dry January, Winter home cocooning season"],
    2: ["Valentine's Day (14th), London Fashion Week"],
    3: ["Mother's Day (UK, varies), Spring equinox, Home refresh season begins"],
    4: ["Easter, Spring cleaning, Chelsea Flower Show prep"],
    5: ["Bank Holiday weekends, Chelsea Flower Show, Mental Health Awareness Week"],
    6: ["Father's Day, Summer Solstice, Wimbledon prep, Wedding season peaks"],
    7: ["Wimbledon, Summer sales, Outdoor living season"],
    8: ["Edinburgh Fringe, Back-to-school prep, Late summer"],
    9: ["London Design Festival, Autumn equinox, Cosy season begins"],
    10: ["Halloween (31st), Bonfire Night prep, Hygge season, Black History Month"],
    11: ["Bonfire Night (5th), Black Friday, Christmas shopping begins, Diwali"],
    12: ["Christmas, Boxing Day, New Year prep, Gift-giving peak"],
}


def generate_campaign_timeline(
    product_name: str,
    product_data: dict,
    launch_month: int,
    campaign_weeks: int,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    GPT로 영국 시즌 맞춤 캠페인 타임라인 생성

    [프롬프트 설계]
    - 출시 월 기준으로 해당 기간의 영국 이벤트 자동 매핑
    - evidence DB [E] ASA 규정, [A] 비용, [G] 실무 리스크 반영
    - 간트 차트용 구조화 데이터 출력
    """
    client = OpenAI(api_key=api_key, timeout=90.0)

    # 캠페인 기간에 해당하는 영국 이벤트 수집
    months_covered = []
    for i in range(max(campaign_weeks // 4, 3)):
        m = ((launch_month - 1 + i) % 12) + 1
        events = UK_EVENTS.get(m, [])
        months_covered.append({"month": m, "events": events})

    events_context = json.dumps(months_covered, ensure_ascii=False, indent=2)

    system_prompt = (
        "당신은 영국 시장 전문 인플루언서 마케팅 캠페인 플래너입니다.\n"
        "영국 소비자 시즌과 이벤트를 정확히 이해하고,\n"
        "실행 가능한 주차별 캠페인 타임라인을 설계합니다.\n\n"
        "━━ 근거 데이터베이스 ━━\n" + get_evidence()
    )

    user_prompt = f"""[제품 정보]
제품명: {product_name}
카테고리: {product_data['category']}
컨셉: {product_data['concept']}
마케팅: {product_data['marketing']}
영국 적합성: {product_data['uk_fit']}

[캠페인 설정]
출시 월: {launch_month}월
캠페인 기간: {campaign_weeks}주

[해당 기간 영국 이벤트]
{events_context}

━━ 출력 JSON 스키마 ━━
{{
  "timeline_overview": {{
    "total_weeks": {campaign_weeks},
    "launch_month": {launch_month},
    "campaign_theme": "전체 캠페인 테마/슬로건 (영문)",
    "strategy_summary": "전체 전략 요약 3~4문장"
  }},
  "phases": [
    {{
      "phase_name": "Phase 1: 사전 준비 (Pre-Launch)",
      "weeks": "Week 1~3",
      "week_start": 1,
      "week_end": 3,
      "color": "#3498db",
      "objectives": ["목표1", "목표2"],
      "tasks": [
        {{
          "week": 1,
          "task": "구체적 태스크",
          "detail": "상세 실행 방법",
          "kpi": "측정 지표",
          "owner": "담당자 역할",
          "uk_event_tie_in": "관련 영국 이벤트 (없으면 null)"
        }}
      ],
      "milestone": "이 단계의 핵심 마일스톤",
      "budget_allocation_pct": 15
    }}
  ],
  "key_milestones": [
    {{
      "week": 1,
      "milestone": "마일스톤 제목",
      "description": "설명"
    }}
  ],
  "uk_event_activations": [
    {{
      "event": "영국 이벤트명",
      "week": 5,
      "activation_idea": "이 이벤트를 활용한 구체적 마케팅 아이디어",
      "expected_impact": "예상 효과"
    }}
  ],
  "risk_checkpoints": [
    {{
      "week": 4,
      "check": "확인 사항",
      "action_if_underperforming": "성과 미달 시 대응 방안"
    }}
  ],
  "evidence_used": ["[코드] 내용"]
}}

규칙:
1. phases는 최소 4단계 (사전 준비 / 소프트 런칭 / 본격 캠페인 / 최적화·확장)
2. 각 phase의 tasks는 주차별 구체적 태스크 포함
3. 영국 이벤트와 연계 가능한 주차에는 반드시 uk_event_tie_in 명시
4. budget_allocation_pct 합계 = 100
5. evidence DB [E] ASA 컴플라이언스 체크 타이밍 필수 포함
6. 빈 값 금지
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
