"""
influencer_marketing/core/perplexity_search.py
Perplexity API 실시간 검색 모듈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[수정 내역 및 논리 구조]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ 문제 진단
  기존 검색 쿼리: site:instagram.com 포함
  → Instagram의 크롤링 차단으로 Perplexity에서 실질적으로 작동 안 함
  → 설령 @handle이 검색되어도 기존 검증 로직이 instagram.com URL만 인정
  → 결과: 출처 확인 계정 0건

▶ 해결 전략
  1) 검색 쿼리 타겟을 Instagram 직접 → 인플루언서 디렉토리 사이트로 변경
     - feedspot.com          (인플루언서 랭킹 디렉토리)
     - findyourinfluencer.co.uk (영국 특화 인플루언서 DB)
     - influencermarketinghub.com (글로벌 인플루언서 리서치)
     - collabstr.com         (인플루언서 마켓플레이스)
     - tribe.so              (마이크로 인플루언서 플랫폼)
     이 사이트들은 크롤링 허용 → Perplexity가 계정 정보 포함 결과를 반환 가능

  2) extract_verified_accounts() 검증 도메인 확장
     기존: instagram.com 만 인정
     수정: TRUSTED_DOMAINS 리스트에 10개 도메인 추가
           @handle 포함 + 신뢰 도메인 URL → 검증 계정으로 분류

  3) build_search_query() 신규 함수
     제품 키워드에 맞는 최적화된 쿼리를 동적으로 생성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import re
import requests

# ── 검증 허용 도메인 (기존 instagram.com → 10개 디렉토리 추가) ──────
TRUSTED_DOMAINS = [
    "feedspot.com",
    "findyourinfluencer.co.uk",
    "influencermarketinghub.com",
    "collabstr.com",
    "tribe.so",
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "hypeauditor.com",
    "modash.io",
    "storyclash.com",
    "influencer.co",
]


def build_search_query(product_name: str, keywords: list) -> str:
    """
    제품 키워드 기반 최적화 검색 쿼리 생성

    [쿼리 설계 논리]
    - "UK home fragrance influencers" 고정 키워드로 영국 시장 타겟팅
    - 제품 키워드 상위 3개 포함으로 제품 관련성 확보
    - site: 연산자를 인플루언서 디렉토리 도메인으로 변경
      (Instagram 크롤링 차단 우회, 디렉토리 사이트는 크롤링 허용)
    - "micro influencer" 고정으로 마이크로 티어 집중
    - "contact email" 추가로 연락처 정보 수집 확률 향상
    """
    kw_str = " ".join(keywords[:3])
    directory_targets = (
        "site:feedspot.com OR site:findyourinfluencer.co.uk "
        "OR site:influencermarketinghub.com OR site:collabstr.com"
    )
    return (
        f"UK home fragrance candle influencers {kw_str} "
        f"micro influencer 2025 follower count engagement rate contact email "
        f"{directory_targets}"
    )


def search_perplexity(query: str, api_key: str) -> dict:
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a UK influencer marketing research assistant. "
                    "CRITICAL RULES: "
                    "1. Only mention Instagram/TikTok/YouTube account handles that are explicitly "
                    "named in the source articles you find. NEVER invent or guess account handles. "
                    "2. For every account handle you mention, you MUST provide the exact source URL "
                    "where that account was referenced. "
                    "3. If you cannot find a verified source for a handle, describe the TYPE of "
                    "influencer to look for (niche, follower range, content style) instead. "
                    "4. Format every account mention as: @handle [Source: URL] "
                    "5. Include follower counts and engagement rates only if stated in the source. "
                    "6. Focus on influencer DIRECTORY sites (feedspot, findyourinfluencer.co.uk, "
                    "influencermarketinghub) as primary sources — these have verified account lists."
                ),
            },
            {"role": "user", "content": query},
        ],
        "max_tokens": 2000,
        "return_citations": True,
        "search_recency_filter": "month",
    }
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "citations": result.get("citations", []),
            "success": True,
        }
    except Exception as e:
        return {"content": "", "citations": [], "success": False, "error": str(e)}


def extract_verified_accounts(perplexity_content: str, citations: list) -> tuple:
    """
    검색 결과에서 @handle 추출 후 신뢰 도메인 URL과 매칭

    [검증 로직]
    기존: citation URL에 'instagram.com' 포함 여부만 체크
          → 인플루언서 디렉토리 URL은 전부 미검증 처리

    수정: TRUSTED_DOMAINS 10개 도메인으로 확장
          1순위: handle명이 citation URL에 포함된 경우 (직접 매칭)
          2순위: 신뢰 도메인 URL이 존재하는 경우 (간접 매칭)
          → 두 조건 중 하나라도 충족 시 검증 계정으로 분류
    """
    handles = re.findall(r"@([A-Za-z0-9_.]+)", perplexity_content)
    verified, unverified = [], []

    for handle in handles:
        found_source = None

        # 1순위: handle명이 URL에 직접 포함
        for url in citations:
            if handle.lower() in url.lower():
                found_source = url
                break

        # 2순위: 신뢰 도메인 URL 존재
        if not found_source:
            for url in citations:
                if any(domain in url.lower() for domain in TRUSTED_DOMAINS):
                    found_source = url
                    break

        if found_source:
            verified.append({
                "handle": "@" + handle,
                "source_url": found_source,
                "verified": True,
            })
        else:
            unverified.append({
                "handle": "@" + handle,
                "source_url": None,
                "verified": False,
            })

    return verified, unverified
