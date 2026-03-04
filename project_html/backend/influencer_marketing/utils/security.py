"""
influencer_marketing/utils/security.py
API 키 보안 처리
"""
import os


def get_env_key(env_name: str, fallback: str = "") -> str:
    return os.environ.get(env_name, fallback)
