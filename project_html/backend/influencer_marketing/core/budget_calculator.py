"""
influencer_marketing/core/budget_calculator.py
예산 계산 보조 모듈
"""

TIER_RANGES = {
    "나노 (1K~10K)":         {"post": (8, 80),    "story": (4, 20)},
    "마이크로 (10K~100K)":   {"post": (100, 500),  "story": (20, 100)},
    "미드티어 (50K~100K)":   {"post": (400, 4000), "story": (100, 500)},
    "매크로 (100K~500K)":    {"post": (1000, 10000), "story": (500, 2000)},
    "메가 (500K+)":          {"post": (8000, 50000), "story": (2000, 10000)},
}


def estimate_campaign_cost(tier: str, num_influencers: int, posts: int = 1, stories: int = 1) -> dict:
    r = TIER_RANGES.get(tier, TIER_RANGES["마이크로 (10K~100K)"])
    mid_post  = sum(r["post"])  / 2
    mid_story = sum(r["story"]) / 2
    total = (mid_post * posts + mid_story * stories) * num_influencers
    return {
        "tier": tier,
        "num_influencers": num_influencers,
        "estimated_total_gbp": round(total, 2),
        "per_influencer_gbp": round(total / num_influencers, 2),
    }
