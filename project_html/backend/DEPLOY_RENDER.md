# Strategy API — Render 배포

Hub의 Strategy / Dashboard에서 **Run analysis** 를 배포 환경에서 쓰려면 이 백엔드를 Render에 Python Web Service로 배포하면 됩니다.

## 1. Render에서 할 일

1. **Dashboard** → **New** → **Web Service**
2. **저장소:** 같은 GitHub `p` 선택
3. **Root Directory:** `project_html/backend` 입력 (필수)
4. **Runtime:** **Python**
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
7. **Environment Variables:**
   - `OPENAI_API_KEY` — (필수)
   - `PERPLEXITY_API_KEY` — (필수, 경쟁사·인플루언서 검색용)
8. **Create Web Service** → 배포 완료 후 URL 복사 (예: `https://santokki-strategy.onrender.com`)

## 2. config.json 연결

저장소 **루트** `config.json` 에 다음처럼 넣고 푸시:

```json
{
  "apiBase": "https://api-santokki-2835.onrender.com",
  "strategyApiBase": "https://여기에_복사한_Strategy_API_URL"
}
```

Netlify 재배포 후 strategy.html / unified-dashboard.html 이 위 주소를 자동 사용합니다.
