"""
server.py — FastAPI 백엔드
기존 influencer_marketing core 모듈을 HTTP API로 노출

API 키는 서버 환경변수에서 관리 → 프론트엔드에 노출 안 됨
"""
import os
import time
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# p/.env 우선 로드 (루트에 키 두면 여기서도 사용), 없으면 backend/.env
_root_env = Path(__file__).resolve().parent.parent.parent / ".env"
if _root_env.exists():
    load_dotenv(_root_env)
load_dotenv()

# ── API 키 환경변수에서 로드 ──────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")

# ── Core 모듈 임포트 ─────────────────────────────────────────
# 주의: openai_analysis.py는 상단에서 `from openai import OpenAI`를 하므로
# openai 패키지가 설치되어 있어야 합니다.
# 서버 배포 시 requirements.txt로 자동 설치됩니다.
from influencer_marketing.core.openai_analysis import (
    analyze_with_openai,
    calc_confidence,
    OPENAI_MODELS,
)
from influencer_marketing.core.perplexity_search import (
    search_perplexity,
    extract_verified_accounts,
    build_search_query,
)
from influencer_marketing.core.competitor_analysis import (
    search_competitor_campaigns,
    analyze_competitors_with_gpt,
)
from influencer_marketing.core.roi_simulator import (
    calculate_roi_scenarios,
    generate_roi_insights_with_gpt,
)
from influencer_marketing.core.timeline_generator import generate_campaign_timeline
from influencer_marketing.core.hashtag_trends import (
    search_hashtag_trends,
    analyze_trends_with_gpt,
)
from influencer_marketing.data.products import PRODUCTS
from influencer_marketing.data.evidence import (
    get_evidence,
    get_reliability_criteria,
    get_data_limitations,
)

# ── FastAPI 앱 생성 ──────────────────────────────────────────
app = FastAPI(title="Influencer Marketing API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 사내 전용이므로 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response 모델 ────────────────────────────────────
class AnalyzeRequest(BaseModel):
    product_name: str
    model: str = ""
    use_perplexity: bool = True
    # 신규 기능 on/off
    use_competitor: bool = True
    use_roi: bool = True
    use_timeline: bool = True
    use_hashtag: bool = True
    # ROI 설정
    roi_monthly_budget: float = 1000
    roi_tier: str = "마이크로"
    roi_months: int = 6
    roi_product_price: float = 35.0
    # 타임라인 설정
    timeline_launch_month: int = 3
    timeline_weeks: int = 12


class StatusMessage(BaseModel):
    step: str
    status: str  # "running", "success", "error"
    message: str


# ── 유틸 ─────────────────────────────────────────────────────
def _get_model(requested: str) -> str:
    if requested and requested in OPENAI_MODELS:
        return requested
    return DEFAULT_MODEL


def _check_keys(use_perplexity: bool):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="서버에 OPENAI_API_KEY가 설정되지 않았습니다.")
    if use_perplexity and not PERPLEXITY_API_KEY:
        raise HTTPException(status_code=500, detail="서버에 PERPLEXITY_API_KEY가 설정되지 않았습니다.")


# ══════════════════════════════════════════════════════════════
# API 엔드포인트
# ══════════════════════════════════════════════════════════════

@app.get("/api/products")
def get_products():
    """제품 목록 + 상세 정보 반환"""
    return {
        "products": {
            name: {
                "category": data["category"],
                "concept": data["concept"],
                "notes": data["notes"],
                "marketing": data["marketing"],
                "keywords": data["keywords"],
                "uk_fit": data["uk_fit"],
            }
            for name, data in PRODUCTS.items()
        },
        "models": OPENAI_MODELS,
    }


@app.get("/api/evidence")
def get_evidence_data():
    """데이터 출처 & 신뢰도 정보 반환"""
    return {
        "reliability_criteria": get_reliability_criteria(),
        "data_limitations": get_data_limitations(),
    }


@app.post("/api/analyze")
def run_full_analysis(req: AnalyzeRequest):
    """
    전체 분석 실행 (메인 6탭 + 신규 4탭)
    기존 app.py의 분석 흐름을 그대로 재현
    """
    model = _get_model(req.model)
    _check_keys(req.use_perplexity)

    if req.product_name not in PRODUCTS:
        raise HTTPException(status_code=400, detail=f"존재하지 않는 제품: {req.product_name}")

    product_data = PRODUCTS[req.product_name]
    steps = []  # 진행 상황 로그

    # ── 1. Perplexity 인플루언서 검색 ─────────────────────────
    perplexity_result = {"success": False}
    verified_accounts = []
    unverified_accounts = []

    if req.use_perplexity and PERPLEXITY_API_KEY:
        try:
            query = build_search_query(req.product_name, product_data["keywords"])
            perplexity_result = search_perplexity(query, PERPLEXITY_API_KEY)
            if perplexity_result["success"]:
                verified_accounts, unverified_accounts = extract_verified_accounts(
                    perplexity_result["content"],
                    perplexity_result.get("citations", []),
                )
                steps.append({
                    "step": "Perplexity 인플루언서 검색",
                    "status": "success",
                    "message": f"출처 확인 계정: {len(verified_accounts)}개 / 미검증: {len(unverified_accounts)}개",
                })
            else:
                steps.append({
                    "step": "Perplexity 인플루언서 검색",
                    "status": "error",
                    "message": perplexity_result.get("error", "알 수 없는 오류"),
                })
        except Exception as e:
            steps.append({
                "step": "Perplexity 인플루언서 검색",
                "status": "error",
                "message": str(e),
            })

    # ── 2. OpenAI 메인 분석 (6탭) ─────────────────────────────
    try:
        result = analyze_with_openai(
            req.product_name, product_data,
            perplexity_result, verified_accounts, unverified_accounts,
            OPENAI_API_KEY, model,
        )
        steps.append({"step": "OpenAI 메인 분석", "status": "success", "message": "6개 탭 분석 완료"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI 메인 분석 실패: {e}")

    # ── 3. 신규 분석 병렬 실행 ────────────────────────────────
    competitor_result = {}
    perplexity_comp = {"success": False}
    roi_data = {}
    roi_insights = {}
    timeline_data = {}
    trends_data = {}
    perplexity_trends = {"success": False}

    # Phase 1: Perplexity 검색 병렬
    if req.use_perplexity and PERPLEXITY_API_KEY:
        def _search_comp():
            time.sleep(1)
            return search_competitor_campaigns(PERPLEXITY_API_KEY)

        def _search_hash():
            time.sleep(2)
            return search_hashtag_trends(product_data["keywords"], PERPLEXITY_API_KEY)

        with ThreadPoolExecutor(max_workers=2) as ex:
            futures = {}
            if req.use_competitor:
                futures["competitor"] = ex.submit(_search_comp)
            if req.use_hashtag:
                futures["hashtag"] = ex.submit(_search_hash)

            for key, future in futures.items():
                try:
                    res = future.result(timeout=60)
                    if key == "competitor":
                        perplexity_comp = res
                        steps.append({
                            "step": "Perplexity 경쟁사 검색",
                            "status": "success" if res["success"] else "error",
                            "message": f"출처 {len(res.get('citations', []))}건" if res["success"] else "검색 실패",
                        })
                    elif key == "hashtag":
                        perplexity_trends = res
                        steps.append({
                            "step": "Perplexity 해시태그 검색",
                            "status": "success" if res["success"] else "error",
                            "message": f"출처 {len(res.get('citations', []))}건" if res["success"] else "검색 실패",
                        })
                except Exception as e:
                    steps.append({"step": f"Perplexity {key}", "status": "error", "message": str(e)})

    # Phase 2: ROI 계산 (로컬)
    if req.use_roi:
        roi_data = calculate_roi_scenarios(
            monthly_budget=req.roi_monthly_budget,
            tier=req.roi_tier,
            campaign_months=req.roi_months,
            avg_product_price=req.roi_product_price,
        )
        steps.append({"step": "ROI 시뮬레이션 계산", "status": "success", "message": "3개 시나리오 계산 완료"})

    # Phase 3: GPT 분석 병렬
    with ThreadPoolExecutor(max_workers=4) as ex:
        gpt_futures = {}

        if req.use_competitor:
            gpt_futures["competitor"] = ex.submit(
                analyze_competitors_with_gpt,
                req.product_name, product_data,
                perplexity_comp, OPENAI_API_KEY, model,
            )
        if req.use_roi and roi_data:
            gpt_futures["roi_insights"] = ex.submit(
                generate_roi_insights_with_gpt,
                roi_data, req.product_name, OPENAI_API_KEY, model,
            )
        if req.use_timeline:
            gpt_futures["timeline"] = ex.submit(
                generate_campaign_timeline,
                req.product_name, product_data,
                req.timeline_launch_month, req.timeline_weeks,
                OPENAI_API_KEY, model,
            )
        if req.use_hashtag:
            gpt_futures["trends"] = ex.submit(
                analyze_trends_with_gpt,
                req.product_name, product_data,
                perplexity_trends, OPENAI_API_KEY, model,
            )

        labels = {
            "competitor": "경쟁사 GPT 분석",
            "roi_insights": "ROI 인사이트 생성",
            "timeline": "타임라인 생성",
            "trends": "해시태그 트렌드 분석",
        }

        for key, future in gpt_futures.items():
            try:
                res = future.result(timeout=120)
                if key == "competitor":
                    competitor_result = res
                elif key == "roi_insights":
                    roi_insights = res
                elif key == "timeline":
                    timeline_data = res
                elif key == "trends":
                    trends_data = res
                steps.append({"step": labels[key], "status": "success", "message": "완료"})
            except Exception as e:
                steps.append({"step": labels[key], "status": "error", "message": str(e)})

    # ── 응답 조립 ─────────────────────────────────────────────
    response = {
        "product": req.product_name,
        "product_data": {
            "category": product_data["category"],
            "concept": product_data["concept"],
            "notes": product_data["notes"],
            "marketing": product_data["marketing"],
            "keywords": product_data["keywords"],
            "uk_fit": product_data["uk_fit"],
        },
        "analysis": result,
        "perplexity": {
            "success": perplexity_result.get("success", False),
            "citations": perplexity_result.get("citations", []),
            "content": perplexity_result.get("content", ""),
        },
        "verified_accounts": verified_accounts,
        "unverified_accounts": unverified_accounts,
        "competitor": competitor_result,
        "perplexity_competitor": {
            "success": perplexity_comp.get("success", False),
            "content": perplexity_comp.get("content", ""),
            "citations": perplexity_comp.get("citations", []),
        },
        "roi_data": roi_data,
        "roi_insights": roi_insights,
        "timeline": timeline_data,
        "trends": trends_data,
        "perplexity_trends": {
            "success": perplexity_trends.get("success", False),
            "content": perplexity_trends.get("content", ""),
            "citations": perplexity_trends.get("citations", []),
        },
        "steps": steps,
        "settings": {
            "model": model,
            "use_perplexity": req.use_perplexity,
            "use_competitor": req.use_competitor,
            "use_roi": req.use_roi,
            "use_timeline": req.use_timeline,
            "use_hashtag": req.use_hashtag,
        },
    }

    return response


# ── 프론트엔드 정적 파일 서빙 (Railway 배포 시) ────────────────
# Netlify를 사용하면 이 부분은 불필요하지만,
# 로컬 개발 또는 단일 서버 배포 시 편의를 위해 포함
import pathlib
FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── 서버 실행 ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
