"""
influencer_marketing/core/validators.py
입력값 검증 유틸리티
"""


def validate_api_keys(openai_key: str, perplexity_key: str = "") -> tuple[bool, str]:
    if not openai_key or not openai_key.startswith("sk-"):
        return False, "유효한 OpenAI API 키를 입력하세요 (sk-로 시작)."
    if perplexity_key and not perplexity_key.startswith("pplx-"):
        return False, "유효한 Perplexity API 키를 입력하세요 (pplx-로 시작)."
    return True, ""
