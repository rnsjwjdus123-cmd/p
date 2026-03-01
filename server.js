/**
 * Santokki — 대시보드 결과 → 최적 상품 → 15초 광고·게시글 프롬프트 생성 API
 * .env: OPENAI_API_KEY, LINKTREE_URL(선택)
 * Firebase: santokki/firebase-key.json (시향 테스트 10명 이상일 때 자동 통계)
 */
require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const OpenAI = require('openai');

let firebaseAdmin = null;
const firebaseKeyPath = path.join(__dirname, 'santokki', 'firebase-key.json');
if (fs.existsSync(firebaseKeyPath)) {
  try {
    firebaseAdmin = require('firebase-admin');
    firebaseAdmin.initializeApp({ credential: firebaseAdmin.credential.cert(require(firebaseKeyPath)) });
  } catch (e) {
    console.warn('Firebase Admin init skip:', e.message);
  }
}

const app = express();
const PORT = process.env.PORT || 7000;

app.use(express.json());

// /santokki/dashboard → dashboard.html 로 연결 (주소에 .html 안 쳐도 됨)
app.get('/santokki/dashboard', (req, res) => {
  res.redirect(302, '/santokki/dashboard.html');
});

app.use(express.static(__dirname));

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const linktreeUrl = process.env.LINKTREE_URL || 'https://linktr.ee/santokki';

/** GET /api/stats-from-firebase — 시향 테스트 10명 이상일 때만 Firestore 통계 반환 */
app.get('/api/stats-from-firebase', async (req, res) => {
  if (!firebaseAdmin) {
    return res.status(503).json({ ok: false, message: 'Firebase 연동 없음. santokki/firebase-key.json 확인.', count: 0 });
  }
  try {
    const db = firebaseAdmin.firestore();
    const snap = await db.collection('quiz_results').orderBy('created_at', 'desc').get();
    const count = snap.size;
    if (count < 10) {
      return res.json({ ok: false, count, message: '시향 테스트 응답이 10명 이상일 때만 자동 생성할 수 있습니다.', stats: null });
    }
    const scentCount = {};
    const productCount = {};
    const genderCount = {};
    const spaceCount = {};
    snap.docs.forEach(doc => {
      const d = doc.data();
      const scent = d.result?.top_scent;
      const product = d.result?.matched_product_name_en || d.result?.matched_product_name;
      const gender = d.basic_info?.gender;
      const space = d.selected_space;
      if (scent) scentCount[scent] = (scentCount[scent] || 0) + 1;
      if (product) productCount[product] = (productCount[product] || 0) + 1;
      if (gender) genderCount[gender] = (genderCount[gender] || 0) + 1;
      if (space) spaceCount[space] = (spaceCount[space] || 0) + 1;
    });
    const topScents = Object.entries(scentCount).sort((a, b) => b[1] - a[1]).map(([k]) => k);
    const topProducts = Object.entries(productCount).sort((a, b) => b[1] - a[1]).map(([k]) => k);
    const stats = {
      topScents,
      topProducts,
      totalResponses: count,
      period: '30d',
      genderRatio: genderCount,
      spaceRatio: spaceCount
    };
    return res.json({ ok: true, count, stats });
  } catch (err) {
    console.error('Firebase stats error:', err.message);
    return res.status(500).json({ ok: false, message: err.message, count: 0 });
  }
});

// products.json 로드
function getProducts() {
  try {
    const raw = fs.readFileSync(path.join(__dirname, 'products.json'), 'utf8');
    const data = JSON.parse(raw);
    return data.products || [];
  } catch (e) {
    return [];
  }
}

// 대시보드 통계 요약 예시 (스키마)
const statsSchema = {
  topScents: ['FLORAL', 'GREEN', 'FRESH', 'WOODY_INK', 'WARMING'],
  topProducts: ['제품명(한/영)'],
  totalResponses: 0,
  genderRatio: { female: 0, male: 0 },
  spaceRatio: { living_bedroom: 0, kitchen: 0, car: 0 },
  period: '7d'
};

/**
 * POST /api/generate-prompts
 * Body: { stats: { topScents, topProducts, totalResponses, ... } }
 * Returns: { optimalProduct, adScript15s, feedPostCopy, rawPrompt }
 */
app.post('/api/generate-prompts', async (req, res) => {
  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not set in .env' });
  }

  const stats = req.body.stats || {};
  const products = getProducts();

  const productList = products.map(p => 
    `- ${p.nameKo} (${p.name}): ${p.categoryLabel}, ${p.description}`
  ).join('\n');

  const systemPrompt = `You are a Santokki (Korean fragrance for Europe/UK) marketing copywriter. Target audience: Europeans who use Instagram, Twitter/X, and TikTok. Optimise tone and hashtags for these platforms. Output only valid JSON.`;

  const userPrompt = `Given these scent quiz dashboard results from our Instagram campaign (European audience):

**Stats:**
- Top scent preferences: ${(stats.topScents || []).join(', ') || 'not provided'}
- Top matched products (from quiz): ${(stats.topProducts || []).join(', ') || 'not provided'}
- Total responses (period): ${stats.totalResponses ?? 'N/A'} (${stats.period || '7d'})
- Gender ratio: ${JSON.stringify(stats.genderRatio || {})}
- Space usage: ${JSON.stringify(stats.spaceRatio || {})}

**Our product lineup (id, nameKo, name, categoryLabel, description):**
${productList}

**Audience & platforms:** European users who actively use Instagram, Twitter/X, and TikTok. Use hashtags and tone that perform well on these SNS (e.g. #fragrance #koreanbeauty #santokki #findyourscent and platform-appropriate style).

Tasks:
1. **optimalProduct**: Pick 1 or 2 products that are the best to promote this week based on the stats. Return: { "id": "product-id", "name": "English name", "nameKo": "한글명", "reason": "one sentence why" }.
2. **adScript15s**: Write a 15-second video ad script in English for the chosen product(s). About 35-45 words when read aloud at normal pace. Tone: elegant, Korean heritage meets modern UK/Europe. End with a soft CTA (e.g. "Find your scent at the link in bio"). Suited for Reels / TikTok / X video.
3. **feedPostCopy**: Write a feed post caption in English: 2-3 sentences + 5-7 hashtags that work on Instagram and X. Include the placeholder [LINK] where we will insert the Linktree URL (${linktreeUrl}). Tone: Santokki brand—refined, storytelling, not pushy; suitable for European SNS.

Return a single JSON object with keys: optimalProduct (object or array of 1-2 items), adScript15s (string), feedPostCopy (string). No markdown, no code block wrapper.`;

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.7
    });

    const content = completion.choices[0].message.content;
    let parsed = {};
    try {
      parsed = JSON.parse(content);
    } catch (e) {
      parsed = { raw: content, optimalProduct: null, adScript15s: content, feedPostCopy: '' };
    }

    return res.json({
      optimalProduct: parsed.optimalProduct ?? null,
      adScript15s: parsed.adScript15s ?? '',
      feedPostCopy: (parsed.feedPostCopy || '').replace(/\[LINK\]/g, linktreeUrl),
      linktreeUrl
    });
  } catch (err) {
    console.error('OpenAI error:', err.message);
    return res.status(500).json({
      error: 'Generation failed',
      detail: err.message
    });
  }
});

/**
 * GET /api/schema — 대시보드 통계 스키마 (n8n/동료 연동용)
 */
app.get('/api/schema', (req, res) => {
  res.json({
    statsSchema: {
      topScents: 'string[] (e.g. FLORAL, GREEN)',
      topProducts: 'string[] (matched product names)',
      totalResponses: 'number',
      genderRatio: 'object',
      spaceRatio: 'object',
      period: 'string (e.g. 7d, 30d)'
    },
    endpoint: 'POST /api/generate-prompts',
    bodyExample: { stats: { topScents: ['GREEN'], topProducts: ['Morning Mist of Namsan'], totalResponses: 42, period: '7d' } }
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`  Dashboard:     http://localhost:${PORT}/santokki/dashboard.html`);
  console.log(`  Prompt generator: http://localhost:${PORT}/prompt-generator.html`);
  console.log(`  API:           POST http://localhost:${PORT}/api/generate-prompts`);
  console.log(`  Firebase stats: GET http://localhost:${PORT}/api/stats-from-firebase (10명 이상 시 자동 생성)`);
});
