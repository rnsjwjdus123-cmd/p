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
// 배포 시: FIREBASE_SERVICE_ACCOUNT_JSON 환경 변수에 서비스 계정 JSON 문자열 넣기 (키 파일 대신)
const firebaseJsonEnv = process.env.FIREBASE_SERVICE_ACCOUNT_JSON;
if (firebaseJsonEnv) {
  try {
    const key = JSON.parse(firebaseJsonEnv);
    firebaseAdmin = require('firebase-admin');
    firebaseAdmin.initializeApp({ credential: firebaseAdmin.credential.cert(key) });
  } catch (e) {
    console.warn('Firebase Admin init from env skip:', e.message);
  }
} else {
  const firebaseKeyPath = path.join(__dirname, 'santokki', 'firebase-key.json');
  if (fs.existsSync(firebaseKeyPath)) {
    try {
      firebaseAdmin = require('firebase-admin');
      firebaseAdmin.initializeApp({ credential: firebaseAdmin.credential.cert(require(firebaseKeyPath)) });
    } catch (e) {
      console.warn('Firebase Admin init skip:', e.message);
    }
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
    `- ${p.nameKo} (${p.name}), id: ${p.id}, image: ${p.image || ''}: ${p.categoryLabel}, ${p.description}`
  ).join('\n');

  const systemPrompt = `You are a Santokki (Korean fragrance for Europe/UK) marketing copywriter. Target audience: Europeans who use Instagram, Twitter/X, and TikTok. Optimise tone and hashtags for these platforms. Also create SEO-focused post copy (keyword-rich) for blog/social. Output only valid JSON.`;

  const userPrompt = `Given these scent quiz dashboard results from our Instagram campaign (European audience):

**Stats:**
- Top scent preferences: ${(stats.topScents || []).join(', ') || 'not provided'}
- Top matched products (from quiz): ${(stats.topProducts || []).join(', ') || 'not provided'}
- Total responses (period): ${stats.totalResponses ?? 'N/A'} (${stats.period || '7d'})
- Gender ratio: ${JSON.stringify(stats.genderRatio || {})}
- Space usage: ${JSON.stringify(stats.spaceRatio || {})}

**Our product lineup (id, nameKo, name, image path in assets):**
${productList}

**Audience & platforms:** European users who actively use Instagram, Twitter/X, and TikTok. Use hashtags and tone that perform well on these SNS (e.g. #fragrance #koreanbeauty #santokki #findyourscent and platform-appropriate style).

**Important:** All copy must match the top scent preferences above. If stats say woody, smoky, ink, green, or fresh, do NOT emphasize floral or flowers; use woody/ink/calm vocabulary. If stats say floral, use flower imagery. The output must be optimal for the actual dashboard input.

Tasks:
1. **optimalProduct**: Pick 1 or 2 products that are the best to promote this week based on the stats. Return: { "id": "product-id", "name": "English name", "nameKo": "한글명", "reason": "one sentence why" }.
2. **adScript15s**: Write a 15-second video ad script in English for the chosen product(s). About 35-45 words when read aloud at normal pace. Tone: elegant, Korean heritage meets modern UK/Europe. End with a soft CTA (e.g. "Find your scent at the link in bio"). Suited for Reels / TikTok / X video.
3. **feedPostCopy**: Write a feed post caption in English: 2-3 sentences + 5-7 hashtags that work on Instagram and X. Include the placeholder [LINK] where we will insert the Linktree URL (${linktreeUrl}). Tone: Santokki brand—refined, storytelling, not pushy; suitable for European SNS.
4. **seoPost**: SEO-style 게시글용. 추천한 상품(optimalProduct)과 위 product lineup의 **image 경로**를 사용해서, 단어/키워드 중심의 게시글 초안을 만들어 주세요. 반드시 포함할 키워드 예: Korean fragrance, Santokki, 제품 영문명, scent, candle/room spray 등. Return: { "title": "SEO-friendly title (e.g. for blog or social)", "metaDescription": "한 문장 메타 설명", "body": "2-3문장 본문 (키워드 자연스럽게 포함)", "suggestedImage": "위 목록에서 고른 상품 이미지 경로 하나 (예: assets/Product Name.png)", "hashtags": "5-7개 해시태그" }.

Return a single JSON object with keys: optimalProduct (object or array of 1-2 items), adScript15s (string), feedPostCopy (string), seoPost (object with title, metaDescription, body, suggestedImage, hashtags). No markdown, no code block wrapper.`;

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

    const seoPost = parsed.seoPost || null;
    if (seoPost && seoPost.body && linktreeUrl) {
      seoPost.body = (seoPost.body || '').replace(/\[LINK\]/g, linktreeUrl);
    }

    return res.json({
      optimalProduct: parsed.optimalProduct ?? null,
      adScript15s: parsed.adScript15s ?? '',
      feedPostCopy: (parsed.feedPostCopy || '').replace(/\[LINK\]/g, linktreeUrl),
      seoPost,
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
 * POST /api/format-for-social
 * Body: { feedPostCopy, seoPost, productName? } (앞선 프롬프트 생성 결과)
 * Returns: { instagramCaption, naverBlogPost } — 인스타·네이버 블로그에 바로 붙여넣기용
 */
app.post('/api/format-for-social', async (req, res) => {
  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not set in .env' });
  }
  const { feedPostCopy = '', seoPost = {}, productName = '', topScents = [], topProducts = [] } = req.body;
  const product = productName || (seoPost && seoPost.title ? '' : '') || 'Santokki product';
  const scentList = Array.isArray(topScents) ? topScents : (typeof topScents === 'string' ? topScents.split(/[,،]/).map(s => s.trim()).filter(Boolean) : []);
  const productList = Array.isArray(topProducts) ? topProducts : (typeof topProducts === 'string' ? topProducts.split(/[,،]/).map(s => s.trim()).filter(Boolean) : []);
  const scentHint = scentList.length ? `Dashboard input: preferred scent profile is [${scentList.join(', ')}]. Use ONLY emojis and wording that match this (e.g. woody→🌲🖤, smoky/ink→✨, fresh→🌿). Do NOT use floral emojis (🌸) or flower-related words when the profile is woody/smoky/ink/fresh/green.` : '';

  const systemPrompt = `You are a social media and blog copy formatter for Santokki (Korean fragrance brand for Europe). Match emojis and vocabulary to the scent profile given. Output only valid JSON.`;

  const userPrompt = `We have existing marketing copy below. Reformat it for direct copy-paste use.

**Source copy:**
- Feed post: ${feedPostCopy}
- SEO post title: ${(seoPost && seoPost.title) || ''}
- SEO post body: ${(seoPost && seoPost.body) || ''}
- Product: ${product}
${scentList.length ? `- Dashboard: popular scents = [${scentList.join(', ')}], popular products = [${productList.join(', ')}]` : ''}

**Important:** ${scentHint || 'Use 1–2 tasteful emojis that fit the product (elegant, not noisy).'}

**Tasks (return a single JSON object):**

1. **instagramCaption**: Format for Instagram. Rules: Use clear line breaks (one blank line between sections). Keep under ~150 words. Add 1–2 emojis that match the scent profile above (e.g. woody/smoky→🌲✨🖤, floral→🌸✨, green→🌿). Put hashtags at the end. No invisible characters; output must paste cleanly into Instagram caption. English.

2. **naverBlogPost**: Format for Naver blog. Rules: Title 35–40 characters (Korean or English, keyword-rich). Meta description 1–2 sentences. Body: 2–3 short paragraphs with line breaks; first 200 chars include main keywords. Match vocabulary to the scent profile (woody/smoky = no flower emphasis). Language: Korean preferred. Return object: { "title": "...", "metaDescription": "...", "body": "..." }.

Return JSON: { "instagramCaption": "string", "naverBlogPost": { "title": "...", "metaDescription": "...", "body": "..." } }. No markdown.`;

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.5
    });
    const content = completion.choices[0].message.content;
    let parsed = {};
    try {
      parsed = JSON.parse(content);
    } catch (e) {
      parsed = { instagramCaption: content, naverBlogPost: { title: '', metaDescription: '', body: '' } };
    }
    const nb = parsed.naverBlogPost || {};
    return res.json({
      instagramCaption: parsed.instagramCaption || '',
      naverBlogPost: {
        title: nb.title || '',
        metaDescription: nb.metaDescription || '',
        body: (nb.body || '').replace(/\[LINK\]/g, linktreeUrl)
      }
    });
  } catch (err) {
    console.error('OpenAI format error:', err.message);
    return res.status(500).json({ error: 'Format failed', detail: err.message });
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
