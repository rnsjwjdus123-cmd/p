/**
 * Santokki — 대시보드 결과 → 최적 상품 → 15초 광고·게시글 프롬프트 생성 API
 * .env: OPENAI_API_KEY, LINKTREE_URL(선택)
 * Firebase: santokki/firebase-key.json (시향 테스트 10명 이상일 때 자동 통계)
 * Google Sheets: GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_SHEET_ID (일일 프롬프트 자동 저장)
 */
require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const OpenAI = require('openai');
const cron = require('node-cron');

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
// Netlify 등 다른 도메인에서 API 호출 시 CORS 허용
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// /santokki/dashboard → dashboard.html 로 연결 (주소에 .html 안 쳐도 됨)
app.get('/santokki/dashboard', (req, res) => {
  res.redirect(302, '/santokki/dashboard.html');
});

app.use(express.static(__dirname));

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const linktreeUrl = process.env.LINKTREE_URL || 'https://linktr.ee/santokki';

/** Firebase에서 기간별 통계 수집 (period: 1d = 최근 24h, 7d, 30d, all) */
async function getFirebaseStats(period = '30d') {
  if (!firebaseAdmin) return { ok: false, count: 0, stats: null };
  const db = firebaseAdmin.firestore();
  const snap = await db.collection('quiz_results').orderBy('created_at', 'desc').get();
  let docs = snap.docs;
  if (period === '1d') {
    const since = new Date(Date.now() - 24 * 60 * 60 * 1000);
    docs = docs.filter(d => {
      const t = d.data().created_at;
      if (!t) return false;
      const date = t.toDate ? t.toDate() : new Date(t);
      return date >= since;
    });
  } else if (period === '7d') {
    const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    docs = docs.filter(d => {
      const t = d.data().created_at;
      if (!t) return false;
      const date = t.toDate ? t.toDate() : new Date(t);
      return date >= since;
    });
  }
  const count = docs.length;
  if (count < 10) return { ok: false, count, stats: null };
  const scentCount = {};
  const productCount = {};
  const genderCount = {};
  const spaceCount = {};
  docs.forEach(doc => {
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
    period,
    genderRatio: genderCount,
    spaceRatio: spaceCount
  };
  return { ok: true, count, stats };
}

/** GET /api/stats-from-firebase — 시향 테스트 10명 이상일 때만 Firestore 통계 반환. ?period=1d|7d|30d|all */
app.get('/api/stats-from-firebase', async (req, res) => {
  if (!firebaseAdmin) {
    return res.status(503).json({ ok: false, message: 'Firebase 연동 없음. santokki/firebase-key.json 확인.', count: 0 });
  }
  const period = req.query.period || '30d';
  try {
    const out = await getFirebaseStats(period);
    if (!out.ok) {
      return res.json({ ok: false, count: out.count, message: '시향 테스트 응답이 10명 이상일 때만 자동 생성할 수 있습니다.', stats: null });
    }
    return res.json({ ok: true, count: out.count, stats: out.stats });
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

/** GET /api/sheet-url — 일일 프롬프트 저장 구글 시트 주소 + 게시글관리 탭 바로가기 */
app.get('/api/sheet-url', async (req, res) => {
  let raw = process.env.GOOGLE_SHEET_ID;
  if (!raw || !(raw = raw.trim())) {
    return res.json({ configured: false });
  }
  let id = raw;
  const m = raw.match(/\/spreadsheets\/d\/([a-zA-Z0-9_-]+)/);
  if (m) id = m[1];
  const baseUrl = raw.startsWith('http') ? raw.replace(/#.*$/, '') : `https://docs.google.com/spreadsheets/d/${id}/edit`;
  const url = baseUrl.includes('/edit') ? baseUrl : (baseUrl + '/edit');
  let gamePostManagementUrl = url;
  try {
    const sheets = getGoogleSheetsClient();
    if (sheets && id) {
      const info = await getFirstSheetInfo(sheets, id);
      if (info) gamePostManagementUrl = url.replace(/#.*$/, '') + '#gid=' + info.sheetId;
    }
  } catch (_) {}
  return res.json({ configured: true, url, gamePostManagementUrl });
});

/** GET /api/funnel-stats — ManyChat 퍼널 상단 2단계 숫자 (댓글 키워드, 퀴즈 링크 DM) */
app.get('/api/funnel-stats', async (req, res) => {
  try {
    if (!firebaseAdmin) {
      return res.json({ commentKeywordCount: 0, quizLinkDmCount: 0 });
    }
    const db = firebaseAdmin.firestore();
    const ref = db.collection('stats').doc('manychat_funnel');
    const snap = await ref.get();
    const d = snap.exists ? snap.data() : {};
    return res.json({
      commentKeywordCount: d.comment_keyword_count ?? 0,
      quizLinkDmCount: d.quiz_link_sent_count ?? 0
    });
  } catch (err) {
    console.warn('funnel-stats error:', err.message);
    return res.json({ commentKeywordCount: 0, quizLinkDmCount: 0 });
  }
});

/** POST /api/manychat/webhook — ManyChat 웹훅 수신 시 퍼널 카운트 증가 */
app.post('/api/manychat/webhook', async (req, res) => {
  try {
    const body = req.body || {};
    const event = body.event || body.type;
    if (!firebaseAdmin) {
      return res.status(200).send('OK');
    }
    const db = firebaseAdmin.firestore();
    const ref = db.collection('stats').doc('manychat_funnel');
    const snap = await ref.get();
    const current = snap.exists ? snap.data() : { comment_keyword_count: 0, quiz_link_sent_count: 0 };
    let updated = false;
    if (event === 'subscriber_added') {
      current.comment_keyword_count = (current.comment_keyword_count || 0) + 1;
      updated = true;
    } else if (event === 'message_sent' || event === 'flow_trigger') {
      current.quiz_link_sent_count = (current.quiz_link_sent_count || 0) + 1;
      updated = true;
    }
    if (updated) {
      current.updated_at = firebaseAdmin.firestore.FieldValue.serverTimestamp();
      await ref.set(current, { merge: true });
    }
    return res.status(200).send('OK');
  } catch (err) {
    console.error('ManyChat webhook error:', err.message);
    return res.status(500).json({ error: err.message });
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

// ─── Google Sheets (일일 프롬프트 자동 저장) ─────────────────────────────
let googleSheetsClient = null;
let lastSheetsAuthError = null; // 클라이언트 생성 실패 시 사유 (화면 안내용)
function getGoogleSheetsClient() {
  lastSheetsAuthError = null;
  if (googleSheetsClient) return googleSheetsClient;
  const json = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;
  const keyPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  let key = null;
  if (json && typeof json === 'string' && json.trim()) {
    try {
      key = JSON.parse(json);
    } catch (e) {
      console.warn('GOOGLE_SERVICE_ACCOUNT_JSON parse error:', e.message);
      lastSheetsAuthError = 'GOOGLE_SERVICE_ACCOUNT_JSON 파싱 오류. Render에 JSON을 줄바꿈 없이 한 줄로 넣었는지 확인하고, 저장 후 재배포(Manual Deploy) 하세요.';
      return null;
    }
  } else if (keyPath && fs.existsSync(path.resolve(keyPath))) {
    key = require(path.resolve(keyPath));
  }
  if (!key) {
    lastSheetsAuthError = 'GOOGLE_SERVICE_ACCOUNT_JSON이 비어 있습니다. Render → Environment → Edit에서 변수 추가 후, 서비스 계정 JSON 전체를 한 줄로 붙여넣고 재배포하세요.';
    return null;
  }
  const { google } = require('googleapis');
  const auth = new google.auth.GoogleAuth({
    credentials: key,
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });
  googleSheetsClient = google.sheets({ version: 'v4', auth });
  return googleSheetsClient;
}
function getGoogleSheetsAuthErrorMessage() {
  return lastSheetsAuthError || 'Google 시트 인증이 없습니다. .env에 GOOGLE_APPLICATION_CREDENTIALS(파일 경로) 또는 GOOGLE_SERVICE_ACCOUNT_JSON을 설정하고, 해당 스프레드시트를 서비스 계정 이메일에 공유해 주세요.';
}

/** .env의 GOOGLE_SHEET_ID(전체 링크, ID만, 또는 ID/edit?gid=0 등)에서 스프레드시트 ID 추출 */
function getSheetId() {
  const raw = process.env.GOOGLE_SHEET_ID;
  if (!raw || !raw.trim()) return null;
  const m = raw.trim().match(/\/spreadsheets\/d\/([a-zA-Z0-9_-]+)/);
  if (m) return m[1];
  const idOnly = raw.trim().match(/^([a-zA-Z0-9_-]{40,})/);
  return idOnly ? idOnly[1] : raw.trim();
}

/** 생성 결과 한 행을 시트에 추가 */
async function appendPromptRowToSheet(payload) {
  const sheetId = getSheetId();
  const tabName = process.env.GOOGLE_SHEET_TAB_NAME || '일일프롬프트';
  if (!sheetId) {
    console.warn('GOOGLE_SHEET_ID not set, skip append');
    return { ok: false, message: 'GOOGLE_SHEET_ID not set' };
  }
  const sheets = getGoogleSheetsClient();
  if (!sheets) {
    console.warn('Google Sheets auth not configured');
    return { ok: false, message: getGoogleSheetsAuthErrorMessage() };
  }
  const {
    date,
    topScents,
    topProducts,
    totalResponses,
    optimalProduct,
    adScript15s,
    feedPostCopy,
    seoTitle,
    seoBody,
    seoHashtags
  } = payload;
  const optName = optimalProduct && (Array.isArray(optimalProduct) ? optimalProduct[0] : optimalProduct);
  const nameStr = optName && typeof optName === 'object' ? (optName.nameKo || optName.name || JSON.stringify(optName)) : (optimalProduct ? JSON.stringify(optimalProduct) : '');
  const row = [
    date || new Date().toISOString().slice(0, 10),
    (topScents || []).join(', '),
    (topProducts || []).join(', '),
    totalResponses ?? '',
    nameStr,
    (adScript15s || '').slice(0, 50000),
    (feedPostCopy || '').slice(0, 50000),
    seoTitle || '',
    (seoBody || '').slice(0, 50000),
    seoHashtags || ''
  ];
  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId: sheetId,
      range: `'${tabName}'!A:J`,
      valueInputOption: 'USER_ENTERED',
      insertDataOption: 'INSERT_ROWS',
      requestBody: { values: [row] }
    });
    await organizeSheetAfterAppend(sheets, sheetId, tabName);
    return { ok: true };
  } catch (err) {
    console.error('Google Sheets append error:', err.message);
    return { ok: false, message: err.message };
  }
}

/** 시트 탭 이름으로 시트 gid(숫자) 조회 */
async function getSheetIdByTitle(sheets, spreadsheetId, tabName) {
  const res = await sheets.spreadsheets.get({ spreadsheetId });
  const sheet = (res.data.sheets || []).find(s => (s.properties.title || '') === tabName);
  return sheet ? sheet.properties.sheetId : (res.data.sheets && res.data.sheets[0] ? res.data.sheets[0].properties.sheetId : 0);
}

/** append 후 시트 정리: 1행 고정, 날짜(최신순) 정렬, 열 너비 */
async function organizeSheetAfterAppend(sheets, spreadsheetId, tabName) {
  if (!sheets || !spreadsheetId) return;
  try {
    const gid = await getSheetIdByTitle(sheets, spreadsheetId, tabName);
    const dataRes = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: `'${tabName}'!A:J`
    });
    const rowCount = (dataRes.data.values || []).length;
    if (rowCount <= 1) {
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: {
          requests: [
            { updateSheetProperties: { properties: { sheetId: gid, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } },
            { updateDimensionProperties: { range: { sheetId: gid, dimension: 'COLUMNS', startIndex: 0, endIndex: 10 }, properties: { pixelSize: 120 }, fields: 'pixelSize' } }
          ]
        }
      });
      return;
    }
    const requests = [
      { updateSheetProperties: { properties: { sheetId: gid, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } },
      { sortRange: { range: { sheetId: gid, startRowIndex: 1, startColumnIndex: 0, endRowIndex: rowCount, endColumnIndex: 10 }, sortSpecs: [{ dimensionIndex: 0, sortOrder: 'DESCENDING' }] } }
    ];
    for (let c = 0; c < 10; c++) {
      const w = c === 0 ? 100 : c <= 4 ? 120 : 220;
      requests.push({ updateDimensionProperties: { range: { sheetId: gid, dimension: 'COLUMNS', startIndex: c, endIndex: c + 1 }, properties: { pixelSize: w }, fields: 'pixelSize' } });
    }
    await sheets.spreadsheets.batchUpdate({ spreadsheetId, requestBody: { requests } });
  } catch (err) {
    console.warn('Sheet organize skip:', err.message);
  }
}

/** 시트에 헤더 행이 없으면 한 번 추가 */
async function ensureSheetHeaders() {
  const sheetId = getSheetId();
  const tabName = process.env.GOOGLE_SHEET_TAB_NAME || '일일프롬프트';
  const sheets = getGoogleSheetsClient();
  if (!sheets || !sheetId) return;
  try {
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: sheetId,
      range: `'${tabName}'!A1:J1`
    });
    const rows = res.data.values || [];
    if (rows.length === 0) {
      await sheets.spreadsheets.values.update({
        spreadsheetId: sheetId,
        range: `'${tabName}'!A1:J1`,
        valueInputOption: 'USER_ENTERED',
        requestBody: {
          values: [[
            '날짜', '인기 향', '인기 매칭 제품', '총 응답 수', '최적 상품', '15초 광고 스크립트', '게시글 카피', 'SEO 제목', 'SEO 본문', '해시태그'
          ]]
        }
      });
    }
  } catch (_) {}
}

/** 스프레드시트의 첫 번째 시트 정보 (제목·gid) — 게시글/프롬프트 저장용 */
function getFirstSheetInfo(sheets, spreadsheetId) {
  return sheets.spreadsheets.get({ spreadsheetId }).then(res => {
    const list = res.data.sheets || [];
    const first = list[0];
    if (!first || !first.properties) return null;
    return { title: first.properties.title || '시트1', sheetId: first.properties.sheetId };
  });
}

/** 첫 번째 시트에 헤더만 확인 후 없으면 넣기 (별도 탭 생성 없음) */
async function ensurePromptHistorySheet(sheets, spreadsheetId) {
  const info = await getFirstSheetInfo(sheets, spreadsheetId);
  if (!info) return;
  const titleEsc = String(info.title).replace(/'/g, "''");
  const range = `'${titleEsc}'!A1:I1`;
  const headerRes = await sheets.spreadsheets.values.get({ spreadsheetId, range });
  const rows = headerRes.data.values || [];
  if (rows.length === 0) {
    await sheets.spreadsheets.values.update({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values: [[
          '날짜', '상품명', '인스타용', '트위터(X)용', '게시글용', '15초 광고', 'SEO 제목', 'SEO 본문', '해시태그'
        ]]
      }
    });
  }
}

/** 프롬프트 생성 결과를 Santokki 스프레드시트 첫 번째 시트에 한 행 추가 */
async function appendPromptHistoryRow(payload) {
  const spreadsheetId = getSheetId();
  const sheets = getGoogleSheetsClient();
  if (!spreadsheetId) return { ok: false, message: '.env에 GOOGLE_SHEET_ID를 넣어 주세요 (스프레드시트 URL 또는 ID)' };
  if (!sheets) return { ok: false, message: getGoogleSheetsAuthErrorMessage() };
  const {
    date,
    productName,
    instagram,
    twitter,
    feedCopy,
    adScript15s,
    seoTitle,
    seoBody,
    hashtags
  } = payload;
  try {
    await ensurePromptHistorySheet(sheets, spreadsheetId);
    const info = await getFirstSheetInfo(sheets, spreadsheetId);
    if (!info) return { ok: false, message: 'First sheet not found' };
    const titleEsc = String(info.title).replace(/'/g, "''");
    const row = [
      date || new Date().toISOString().slice(0, 10),
      (productName || '').slice(0, 500),
      (instagram || '').slice(0, 50000),
      (twitter || '').slice(0, 50000),
      (feedCopy || '').slice(0, 50000),
      (adScript15s || '').slice(0, 50000),
      (seoTitle || '').slice(0, 5000),
      (seoBody || '').slice(0, 50000),
      (hashtags || '').slice(0, 2000)
    ];
    const range = `'${titleEsc}'!A:I`;
    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      insertDataOption: 'INSERT_ROWS',
      requestBody: { values: [row] }
    });
    await organizePromptHistorySheet(sheets, spreadsheetId);
    return { ok: true };
  } catch (err) {
    console.error('Prompt history append error:', err.message);
    return { ok: false, message: err.message };
  }
}

async function organizePromptHistorySheet(sheets, spreadsheetId) {
  try {
    const info = await getFirstSheetInfo(sheets, spreadsheetId);
    if (!info) return;
    const gid = info.sheetId;
    const titleEsc = String(info.title).replace(/'/g, "''");
    const dataRes = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: `'${titleEsc}'!A:I`
    });
    const rowCount = (dataRes.data.values || []).length;
    if (rowCount <= 1) {
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId,
        requestBody: {
          requests: [
            { updateSheetProperties: { properties: { sheetId: gid, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } }
          ]
        }
      });
      return;
    }
    const requests = [
      { updateSheetProperties: { properties: { sheetId: gid, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } },
      { sortRange: { range: { sheetId: gid, startRowIndex: 1, startColumnIndex: 0, endRowIndex: rowCount, endColumnIndex: 9 }, sortSpecs: [{ dimensionIndex: 0, sortOrder: 'DESCENDING' }] } }
    ];
    const widths = [100, 140, 220, 220, 220, 220, 180, 220, 120];
    for (let c = 0; c < 9; c++) {
      requests.push({ updateDimensionProperties: { range: { sheetId: gid, dimension: 'COLUMNS', startIndex: c, endIndex: c + 1 }, properties: { pixelSize: widths[c] }, fields: 'pixelSize' } });
    }
    await sheets.spreadsheets.batchUpdate({ spreadsheetId, requestBody: { requests } });
  } catch (err) {
    console.warn('Prompt history organize skip:', err.message);
  }
}

/** 일일 자동 실행: Firebase(최근 24h) → 프롬프트 생성 → 구글 시트 추가 */
async function runDailyPromptsToSheets() {
  console.log('[Daily] runDailyPromptsToSheets started');
  if (!firebaseAdmin) {
    console.warn('[Daily] Firebase not configured');
    return;
  }
  if (!process.env.OPENAI_API_KEY) {
    console.warn('[Daily] OPENAI_API_KEY not set');
    return;
  }
  const out = await getFirebaseStats('1d');
  if (!out.ok || !out.stats) {
    console.log('[Daily] Not enough data (need 10+ in last 24h), count=', out.count);
    return;
  }
  const stats = out.stats;
  const products = getProducts();
  const productList = products.map(p =>
    `- ${p.nameKo} (${p.name}), id: ${p.id}, image: ${p.image || ''}: ${p.categoryLabel}, ${p.description}`
  ).join('\n');
  const systemPrompt = `You are a Santokki (Korean fragrance for Europe/UK) marketing copywriter. Target audience: Europeans. Output only valid JSON.`;
  const userPrompt = `Given these scent quiz dashboard results (last 24h):

**Stats:** Top scents: ${(stats.topScents || []).join(', ')}, Top products: ${(stats.topProducts || []).join(', ')}, Total: ${stats.totalResponses}.

**Our products:**\n${productList}

Return a single JSON: optimalProduct (object or array of 1-2 items with id, name, nameKo, reason), adScript15s (string, 35-45 words), feedPostCopy (string, 2-3 sentences + hashtags), seoPost (object with title, metaDescription, body, suggestedImage, hashtags). No markdown.`;

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
    const parsed = JSON.parse(completion.choices[0].message.content || '{}');
    const seoPost = parsed.seoPost || {};
    await ensureSheetHeaders();
    const appendResult = await appendPromptRowToSheet({
      date: new Date().toISOString().slice(0, 10),
      topScents: stats.topScents,
      topProducts: stats.topProducts,
      totalResponses: stats.totalResponses,
      optimalProduct: parsed.optimalProduct ?? null,
      adScript15s: parsed.adScript15s ?? '',
      feedPostCopy: (parsed.feedPostCopy || '').replace(/\[LINK\]/g, linktreeUrl),
      seoTitle: seoPost.title ?? '',
      seoBody: seoPost.body ?? '',
      seoHashtags: seoPost.hashtags ?? ''
    });
    if (appendResult.ok) {
      console.log('[Daily] Prompts generated and saved to Google Sheet');
    } else {
      console.warn('[Daily] Sheet append failed:', appendResult.message);
    }
  } catch (err) {
    console.error('[Daily] Error:', err.message);
  }
}

/** POST /api/save-prompt-to-sheet — 프롬프트 생성 결과를 게시글관리 시트에 저장 (날짜·상품명·인스타·트위터·게시글용 등) */
app.post('/api/save-prompt-to-sheet', async (req, res) => {
  const body = req.body || {};
  const opt = body.optimalProduct;
  const productName = opt && (Array.isArray(opt) ? opt[0] : opt);
  const nameStr = productName && typeof productName === 'object'
    ? (productName.nameKo || productName.name || '')
    : (body.productName || '');
  const seo = body.seoPost || {};
  try {
    const result = await appendPromptHistoryRow({
      date: body.date || new Date().toISOString().slice(0, 10),
      productName: nameStr,
      instagram: body.instagram || body.feedPostCopy || '',
      twitter: body.twitter || body.feedPostCopy || '',
      feedCopy: body.feedPostCopy || '',
      adScript15s: body.adScript15s || '',
      seoTitle: seo.title || body.seoTitle || '',
      seoBody: seo.body || body.seoBody || '',
      hashtags: seo.hashtags || body.hashtags || ''
    });
    if (result.ok) {
      return res.json({ ok: true, message: '게시글관리 시트에 저장됨' });
    }
    return res.status(400).json({ ok: false, message: result.message });
  } catch (err) {
    return res.status(500).json({ ok: false, message: err.message });
  }
});

/** POST /api/organize-prompts-sheet — 시트만 정리 (정렬·헤더 고정·열 너비). 갱신 후 호출용 */
app.post('/api/organize-prompts-sheet', async (req, res) => {
  const sheetId = getSheetId();
  const tabName = process.env.GOOGLE_SHEET_TAB_NAME || '일일프롬프트';
  const sheets = getGoogleSheetsClient();
  if (!sheets || !sheetId) {
    return res.status(400).json({ ok: false, message: 'Google Sheet not configured' });
  }
  try {
    await organizeSheetAfterAppend(sheets, sheetId, tabName);
    return res.json({ ok: true, message: 'Sheet organized' });
  } catch (err) {
    return res.status(500).json({ ok: false, message: err.message });
  }
});

/** POST /api/run-daily-prompts — 일일 job 수동 실행 (외부 cron용). ?token=xxx 필요 시 DAILY_CRON_SECRET 설정 */
app.post('/api/run-daily-prompts', async (req, res) => {
  const secret = process.env.DAILY_CRON_SECRET;
  if (secret && req.query.token !== secret) {
    return res.status(403).json({ ok: false, message: 'Invalid token' });
  }
  try {
    await runDailyPromptsToSheets();
    return res.json({ ok: true, message: 'Daily job completed' });
  } catch (err) {
    console.error('run-daily-prompts error:', err.message);
    return res.status(500).json({ ok: false, message: err.message });
  }
});

// 유럽 시간 기준 새벽/아침에 실행 (예: 7:00 UTC = 8:00 Berlin). cron: 분 시 일 월 요일
if (process.env.DAILY_CRON_SCHEDULE) {
  cron.schedule(process.env.DAILY_CRON_SCHEDULE, runDailyPromptsToSheets);
  console.log('Daily prompts cron:', process.env.DAILY_CRON_SCHEDULE);
} else {
  cron.schedule('0 7 * * *', runDailyPromptsToSheets); // 매일 07:00 UTC
}

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`  Dashboard:     http://localhost:${PORT}/santokki/dashboard.html`);
  console.log(`  Prompt generator: http://localhost:${PORT}/prompt-generator.html`);
  console.log(`  API:           POST http://localhost:${PORT}/api/generate-prompts`);
  console.log(`  Firebase stats: GET http://localhost:${PORT}/api/stats-from-firebase (10명 이상 시 자동 생성)`);
});
