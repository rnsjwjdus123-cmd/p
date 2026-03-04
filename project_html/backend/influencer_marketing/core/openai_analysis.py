"""
influencer_marketing/core/openai_analysis.py
OpenAI GPT 분석 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[수정 내역 및 논리 구조]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ 문제 진단
  기존 max_tokens=4000 으로 6개 탭 전체 JSON을 한 번에 생성해야 하므로,
  앞쪽 탭(제품분석·인플루언서 전략)에서 토큰이 소진되어
  뒤쪽 탭(접촉전략, 예산, 리스크, 컴플라이언스)이 빈 값·빈 배열로 잘렸음.

▶ 해결 전략: max_tokens 4,000 유지 (gpt-4o-mini 응답 한도 4,096)
  GPT-4o-mini 기준 12,000 tokens ≈ 약 $0.03~0.06/회 (비용 증가 허용)

▶ 데이터 주입 방식
  ┌─────────────────────────────────────────────────────┐
  │ 1) evidence.py [A~H] 전체 DB                        │
  │    → get_evidence()로 시스템 프롬프트에 직접 삽입   │
  │    → GPT가 근거 코드 [A-1], [B-3] 등을 인용        │
  │                                                     │
  │ 2) Perplexity 실시간 검색 결과                      │
  │    → 영국 현지 인플루언서 계정 정보                 │
  │    → verified_accounts / unverified_accounts 분류   │
  │                                                     │
  │ 3) 제품 마스터 데이터 (products.py)                 │
  │    → category, concept, notes, marketing, uk_fit    │
  └─────────────────────────────────────────────────────┘

▶ 스키마 완전 명시 (기존 누락된 부분)
  - risks[]:        risk, description, mitigation, probability, impact, evidence[]
  - action_plan[]:  step, action, detail, timeline, owner, reason, evidence
  - compliance[]:   item, detail, evidence, required
  - contact:        timing_advice 필수화, email_template 구조화
  - budget:         £ 단위 숫자 명시 의무화

▶ 시각화 데이터 신규 추가 (tabs.py 차트 렌더링용)
  - budget_chart_data:     인플루언서 등급별 비용 비교 (바 차트용)
  - roi_projection:        월별 ROI 예상 (라인 차트용)
  - risk_matrix:           확률·영향도 매트릭스 (산점도용)
  - engagement_comparison: 나노/마이크로/매크로 참여율 비교
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import json
import concurrent.futures
from openai import OpenAI
from influencer_marketing.data.evidence import get_evidence


def generate_selling_points_with_openai(
    product_name: str,
    product_data: dict,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> list:
    """
    OpenAI API를 사용하여 evidence DB 기반 셀링 포인트를 생성합니다.
    가짜 데이터 없이 실제 근거(evidence DB [A~H])를 바탕으로 생성.
    """
    evidence_db = get_evidence()
    client = OpenAI(api_key=api_key, timeout=60.0)

    prompt = f"""당신은 영국 홈 프래그런스 인플루언서 마케팅 전문가입니다.

아래 제품과 근거 데이터베이스를 바탕으로 핵심 셀링 포인트 5가지를 생성하세요.

[제품 정보]
제품명: {product_name}
카테고리: {product_data['category']}
컨셉: {product_data['concept']}
향기 노트: {product_data['notes']}
마케팅 포인트: {product_data['marketing']}
영국 시장 적합성: {product_data['uk_fit']}

[근거 데이터베이스]
{evidence_db}

규칙:
1. 반드시 위 근거 DB의 실제 수치([D], [F], [B], [H] 등)를 인용할 것
2. 가짜 수치나 추측 금지 — DB에 없는 수치는 절대 사용하지 말 것
3. 각 포인트는 간결하고 설득력 있게 (1~2문장)
4. 반드시 JSON 배열로만 응답: ["포인트1", "포인트2", "포인트3", "포인트4", "포인트5"]
5. JSON 외 다른 텍스트 없이 배열만 출력"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,

        max_tokens=1000,
    )
    import re
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    # JSON 배열 직접 추출
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    # {"selling_points": [...]} 등 감싸진 경우
    for v in parsed.values():
        if isinstance(v, list):
            return v
    return []

OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]

MAX_LIST_ITEMS = 15


def _trim_lists_to_max(obj, max_items: int = MAX_LIST_ITEMS) -> None:
    """분석 결과 내 모든 리스트를 상위 max_items개로 자릅니다 (in-place)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list):
                if len(v) > max_items:
                    obj[k] = v[:max_items]
                for item in obj[k]:
                    _trim_lists_to_max(item, max_items)
            else:
                _trim_lists_to_max(v, max_items)
    elif isinstance(obj, list):
        for item in obj:
            _trim_lists_to_max(item, max_items)


def calc_confidence(result: dict) -> str:
    conf = result.get("confidence_score", {})
    return conf.get("overall", "중간")


def analyze_with_openai(
    product_name: str,
    product_data: dict,
    perplexity_result: dict,
    verified_accounts: list,
    unverified_accounts: list,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict:
    client = OpenAI(api_key=api_key, timeout=120.0)

    # ── Perplexity 결과 컨텍스트 구성 ─────────────────────────────
    verified_str = ""
    if verified_accounts:
        verified_str = "[Perplexity 출처 확인 계정 목록 - 사용 가능]\n"
        for acc in verified_accounts:
            verified_str += f"  - {acc['handle']} (출처: {acc['source_url']})\n"

    unverified_str = ""
    if unverified_accounts:
        unverified_str = "[출처 미확인 계정 - 절대 사용 금지]\n"
        for acc in unverified_accounts:
            unverified_str += f"  - {acc['handle']} (출처 없음)\n"

    perplexity_context = ""
    if perplexity_result.get("success"):
        perplexity_context = (
            "[Perplexity 실시간 검색 원문]\n"
            + perplexity_result["content"]
            + "\n\n" + verified_str
            + "\n" + unverified_str
        )

    # ── 시스템 프롬프트 ────────────────────────────────────────────
    system_prompt = (
        "당신은 영국 홈 프래그런스 인플루언서 마케팅 전문가입니다.\n\n"
        "━━ 절대 규칙: 계정 추천 ━━\n"
        "1. 인스타그램/틱톡/유튜브 계정 아이디(@handle)를 절대로 직접 생성하지 마십시오.\n"
        "2. 계정 아이디는 오직 두 경우에만 출력 가능합니다:\n"
        "   (a) Perplexity 검색 결과에서 출처 URL과 함께 확인된 계정\n"
        "   (b) 사용자가 직접 제공한 계정\n"
        "3. 검증된 계정이 없을 경우 탐색 키워드/해시태그/계정 유형 설명을 제공하십시오.\n\n"
        "━━ 근거 규칙 ━━\n"
        "모든 판단에는 [근거코드] 형식으로 최소 5가지 근거를 명시하십시오.\n"
        "근거코드는 아래 evidence DB의 [A-1], [B-3], [D-2] 등 코드를 사용하십시오.\n\n"
        "━━ 출력 규칙 ━━\n"
        "반드시 유효한 JSON 형식으로만 응답하십시오.\n"
        "모든 수치는 파운드(£) 단위로 구체적 숫자를 포함하십시오.\n"
        "빈 문자열이나 빈 배열을 절대 남기지 마십시오.\n\n"
        "━━ 아래는 분석에 사용할 근거 데이터베이스입니다 ━━\n"
        + get_evidence()
    )

    keywords_str = ", ".join(product_data["keywords"])

    user_prompt = f"""다음 제품에 대한 영국 인플루언서 마케팅 전략을 분석하십시오.

[제품 정보]
제품명: {product_name}
카테고리: {product_data['category']}
컨셉: {product_data['concept']}
향기 노트: {product_data['notes']}
마케팅 포인트: {product_data['marketing']}
영국 시장 적합성: {product_data['uk_fit']}
핵심 키워드: {keywords_str}

{perplexity_context}

━━ 출력 JSON 스키마 (모든 필드 필수, 빈 값 금지) ━━

{{
  "product_analysis": {{
    "target_persona": "구체적인 인물 묘사 (나이, 직업, 라이프스타일, 구매 동기 포함)",
    "uk_cultural_fit": "영국 문화·트렌드와의 구체적 접점 3가지 이상",
    "key_selling_points": ["셀링포인트1", "셀링포인트2", "셀링포인트3", "셀링포인트4", "셀링포인트5"],
    "market_size_context": "evidence DB [D] 시장 규모 데이터를 인용한 시장 기회 분석",
    "k_lifestyle_relevance": "evidence DB [F] K-라이프스타일 트렌드와의 연결성",
    "evidence": ["[코드] 내용 (출처명)", "[코드] 내용", "[코드] 내용", "[코드] 내용", "[코드] 내용"]
  }},

  "influencer_strategy": {{
    "primary_type": "1순위 인플루언서 유형명",
    "primary_reason": "선정 근거 2~3문장",
    "secondary_type": "2순위 인플루언서 유형명",
    "secondary_reason": "선정 근거 2~3문장",
    "recommended_tier": "나노/마이크로/미드티어/매크로 중 선택",
    "tier_reason": "해당 티어 추천 이유 (evidence [A], [B] 근거 포함)",
    "follower_range": "예: 10K~50K",
    "follower_reason": "팔로워 범위 선정 이유",
    "verified_accounts": [],
    "search_guide": {{
      "instagram_keywords": ["키워드1", "키워드2", "키워드3"],
      "hashtags": ["#태그1", "#태그2", "#태그3", "#태그4", "#태그5"],
      "account_type_description": "찾아야 할 계정 유형의 구체적 묘사",
      "manual_search_tip": "직접 탐색 시 실용적 팁",
      "directory_sites": ["feedspot.com", "findyourinfluencer.co.uk", "influencermarketinghub.com"]
    }},
    "engagement_comparison": {{
      "nano": {{"rate": "숫자%", "label": "나노 1K~10K", "source": "[B-x]"}},
      "micro": {{"rate": "숫자%", "label": "마이크로 10K~100K", "source": "[B-x]"}},
      "macro": {{"rate": "숫자%", "label": "매크로 100K~500K", "source": "[B-x]"}},
      "mega": {{"rate": "숫자%", "label": "메가 500K+", "source": "[B-x]"}}
    }},
    "evidence": ["[코드] 내용 (출처명)", "[코드] 내용", "[코드] 내용", "[코드] 내용", "[코드] 내용"]
  }},

  "contact_strategy": {{
    "primary_channel": "채널명 (예: 비즈니스 이메일)",
    "primary_reason": "1순위 이유 2~3문장 (evidence [C] 수치 포함)",
    "secondary_channel": "채널명",
    "secondary_reason": "2순위 이유",
    "instagram_dm_risk": "DM 사용 시 구체적 위험 및 대응 방법 (evidence [C-3] 인용)",
    "email_template": {{
      "subject_line": "제안 이메일 제목 예시 (영어)",
      "opening": "첫 2문장 핵심 메시지 방향",
      "key_points": ["포인트1", "포인트2", "포인트3"],
      "cta": "명확한 행동 유도 문구"
    }},
    "timing_advice": "최적 접촉 시기 및 이유 (영국 계절·이벤트 기반)",
    "follow_up_strategy": "초기 미응답 시 후속 대응 전략",
    "evidence": ["[코드] 내용 (출처명)", "[코드] 내용", "[코드] 내용", "[코드] 내용", "[코드] 내용"]
  }},

  "budget": {{
    "recommended_tier": "나노/마이크로/미드티어 중 선택",
    "cost_per_post": "£숫자~£숫자 (evidence [A-x] 인용)",
    "cost_per_story": "£숫자~£숫자 (evidence [A-x] 인용)",
    "initial_campaign_budget": "£숫자 (총액, 이유 포함)",
    "initial_influencer_count": "숫자",
    "expected_roi": "£1 투자 대비 £숫자 수익 예상 (evidence [B-x] 인용)",
    "gifting_option": "제품 기프팅 전략 및 비용 효율성 분석",
    "payment_model": "지급 방식 권장 (플랫 피/퍼포먼스 기반/혼합) + 이유",
    "budget_chart_data": [
      {{"tier": "나노 (1K~10K)", "post_min": 50, "post_max": 350, "story_min": 25, "story_max": 175}},
      {{"tier": "마이크로 (10K~100K)", "post_min": 150, "post_max": 700, "story_min": 75, "story_max": 350}},
      {{"tier": "매크로 (100K~500K)", "post_min": 1000, "post_max": 5500, "story_min": 500, "story_max": 2750}},
      {{"tier": "미드티어 (500K~1M)", "post_min": 5000, "post_max": 12000, "story_min": 2500, "story_max": 6000}}
    ],
    "roi_projection": [
      {{"month": 1, "spend": 0, "estimated_reach": 0, "estimated_revenue": 0}},
      {{"month": 2, "spend": 0, "estimated_reach": 0, "estimated_revenue": 0}},
      {{"month": 3, "spend": 0, "estimated_reach": 0, "estimated_revenue": 0}},
      {{"month": 6, "spend": 0, "estimated_reach": 0, "estimated_revenue": 0}}
    ],
    "evidence": ["[코드] 내용 (출처명)", "[코드] 내용", "[코드] 내용", "[코드] 내용", "[코드] 내용"]
  }},

  "risks": [
    {{
      "risk": "리스크 제목",
      "description": "구체적 위험 상황 묘사",
      "mitigation": "대응 방안 (실행 가능한 조치)",
      "probability": "높음 또는 중간 또는 낮음",
      "impact": "높음 또는 중간 또는 낮음",
      "evidence": ["[코드] 내용"]
    }}
  ],

  "risk_matrix": [
    {{
      "risk_name": "리스크명 (짧게)",
      "probability_score": 6,
      "impact_score": 8,
      "category": "법적 또는 운영 또는 평판 또는 재무 중 하나"
    }}
  ],

  "compliance_checklist": [
    {{
      "item": "체크리스트 항목 제목",
      "detail": "구체적 적용 방법 및 예시",
      "evidence": "근거코드와 출처 (예: [E-1] ASA 2025)",
      "required": true
    }}
  ],

  "action_plan": [
    {{
      "step": 1,
      "action": "실행 항목 제목",
      "detail": "구체적 실행 방법 및 체크포인트",
      "timeline": "예: 1~2주차",
      "owner": "담당자 역할 (예: 마케팅 담당자)",
      "reason": "이 단계가 필요한 이유",
      "evidence": "[코드] 근거"
    }}
  ],

  "confidence_score": {{
    "overall": "높음 또는 중간 또는 낮음",
    "reason": "신뢰도 판단 근거",
    "data_sources_used": ["출처1", "출처2", "출처3"],
    "limitations": "데이터 한계 및 주의사항"
  }}
}}

━━ 필수 조건 ━━
0. [속도 최적화] 모든 배열형 필드는 최대 15개만 출력 (예: risks, risk_matrix, evidence 배열, verified_accounts 등). action_plan은 5단계, compliance_checklist는 6개 유지.
1. risks: 최대 15개 (최소 5개, ASA 위반·가짜팔로워·브랜드 불일치·플랫폼 제한·문화적 오해 포함)
2. risk_matrix: risks와 1:1 매핑, 최대 15개 (확률·영향도 1~10, evidence [I-1~I-6] 우선)
3. compliance_checklist: 6개 (#ad, #gifted, 표기 위치, DMCC Act, 계약서, 모니터링)
4. action_plan: 정확히 5단계
5. budget_chart_data: evidence [A] 그대로 (4개 티어)
6. roi_projection: evidence [B-3] 기준 월별 수치 (4개 월만)
7. engagement_comparison: evidence [B-4]/[B-5] 수치 반영
"""

    def _run_main_analysis():
        return client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=12000,
        )

    def _run_selling_points():
        return generate_selling_points_with_openai(product_name, product_data, api_key, model)

    # ── 메인 분석 + 셀링포인트 병렬 실행 ──────────────────────────
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_main = executor.submit(_run_main_analysis)
        future_sp   = executor.submit(_run_selling_points)

        response = future_main.result()
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            # GPT 응답 잘림 시: 미종료 문자열 닫고 괄호 맞춤 시도
            result = None
            repaired = raw
            if "Unterminated string" in str(e) or "Expecting value" in str(e):
                if repaired and repaired[-1] not in ('"', '}', ']'):
                    repaired += '"'
                repaired += "]" * max(0, repaired.count("[") - repaired.count("]"))
                repaired += "}" * max(0, repaired.count("{") - repaired.count("}"))
                try:
                    result = json.loads(repaired)
                except json.JSONDecodeError:
                    pass
            if result is None:
                raise ValueError(
                    f"OpenAI 응답 JSON 파싱 실패(응답이 잘렸을 수 있음): {e!s}. "
                    "다시 Run analysis 해보거나, 제품을 바꿔서 시도해 보세요."
                ) from e

        # 상위 15개로 제한해 응답 크기·표시 부담 감소
        _trim_lists_to_max(result, max_items=15)

        try:
            selling_points = future_sp.result()
            if selling_points:
                result.setdefault("product_analysis", {})["key_selling_points"] = selling_points
        except Exception:
            pass  # 실패 시 메인 분석의 셀링포인트 유지

    return result
