/**
 * Santokki - Scent Test & Product Recommendation
 */

// State
let productsData = null;
let currentQuestion = 0;
let userAnswers = {};
let scentTestQuestions = [];
let currentCategory = 'all';
let currentFacette = 'all';
let currentSort = 'default';

// DOM Elements
const productsGrid = document.getElementById('products-grid');
const scentTestPopup = document.getElementById('scent-test-popup');
const popupClose = document.getElementById('popup-close');
const scentTestTriggers = document.querySelectorAll('.scent-test-trigger');
const quizContainer = document.getElementById('quiz-container');
const quizResult = document.getElementById('quiz-result');
const recommendedProductEl = document.getElementById('recommended-product');
const getCouponBtn = document.getElementById('get-coupon-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const filterBtns = document.querySelectorAll('.filter-btn');
const facetteBtns = document.querySelectorAll('.facette-btn');
const sortSelect = document.getElementById('sort-select');
const resultsCount = document.getElementById('results-count');
const featuredGrid = document.getElementById('featured-grid');
const categoryBanners = document.getElementById('category-banners');
const homeSlides = document.querySelectorAll('.home-slide');
const sliderDots = document.querySelectorAll('.slider-dot');
const conciergeToggle = document.getElementById('concierge-toggle');
const conciergePanel = document.getElementById('concierge-panel');
const conciergeChips = document.querySelectorAll('.concierge-chip');

// Mood to scent profile mapping (Q1)
const moodToProfile = {
  fresh: { fresh: 10, green: 8 },
  calm: { floral: 10, fresh: 6 },
  warm: { warm: 10, woody: 7, sweet: 5 },
  energizing: { citrus: 10, fresh: 8 }
};

const categoryOrder = ['roomspray', 'diffuser', 'car', 'candle'];
const categoryBannerMeta = {
  roomspray: {
    title: 'Room Spray',
    subtitle: 'Immediate atmosphere refresh for living spaces.'
  },
  diffuser: {
    title: 'Diffuser · Jagae Edition',
    subtitle: 'Premium Joseon royal-inspired diffusers for the home.'
  },
  car: {
    title: 'Car Air Freshener',
    subtitle: 'Focused freshness for daily driving moments.'
  },
  candle: {
    title: 'Candle',
    subtitle: 'Split by mood: bedroom candles and kitchen candles.'
  }
};

// Init
async function init() {
  try {
    const res = await fetch('products.json');
    const data = await res.json();
    productsData = data.products;
    scentTestQuestions = data.scentTestQuestions || [];
    renderProducts();
    setupEventListeners();
    setupScrollHeader();
    setupHomeSlider();
    setupConcierge();
  } catch (err) {
    console.error('Failed to load products:', err);
    productsGrid.innerHTML = '<p class="error">Unable to load products. Please try again later.</p>';
  }
}

function setupHomeSlider() {
  if (!homeSlides.length) return;
  let current = 0;

  const goToSlide = (index) => {
    current = ((index % homeSlides.length) + homeSlides.length) % homeSlides.length;
    homeSlides.forEach((slide, idx) => {
      slide.classList.toggle('active', idx === current);
    });
  };

  const prevBtn = document.getElementById('home-slider-prev');
  const nextBtn = document.getElementById('home-slider-next');
  if (prevBtn) prevBtn.addEventListener('click', () => goToSlide(current - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => goToSlide(current + 1));

  setInterval(() => {
    goToSlide(current + 1);
  }, 7000);
}

function setupConcierge() {
  if (!conciergeToggle || !conciergePanel) return;

  conciergeToggle.addEventListener('click', () => {
    conciergePanel.classList.toggle('hidden');
  });

  conciergeChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const mode = chip.dataset.concierge;
      currentFacette = mode === 'calm' ? 'floral' : mode;
      facetteBtns.forEach((b) => b.classList.remove('active'));
      const target = document.querySelector(`.facette-btn[data-facette="${currentFacette}"]`);
      if (target) target.classList.add('active');
      renderProducts();
      document.getElementById('products')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      conciergePanel.classList.add('hidden');
    });
  });
}

// Check if product matches facette (scent tag)
function productMatchesFacette(product, facette) {
  if (facette === 'all') return true;
  const p = product.scentProfile;
  if (!p || !p[facette]) return false;
  return p[facette] >= 5;
}

// Apply all filters and sort
function getFilteredProducts() {
  let list = [...productsData];
  if (currentCategory === 'candle-bedroom') {
    list = list.filter((p) => p.category === 'candle' && p.useArea === 'bedroom');
  } else if (currentCategory === 'candle-kitchen') {
    list = list.filter((p) => p.category === 'candle' && p.useArea === 'kitchen');
  } else if (currentCategory !== 'all') {
    list = list.filter(p => p.category === currentCategory);
  }
  if (currentFacette !== 'all') {
    list = list.filter(p => productMatchesFacette(p, currentFacette));
  }
  if (currentSort === 'name') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  } else if (currentSort === 'price-low') {
    list.sort((a, b) => parsePrice(a.price) - parsePrice(b.price));
  } else if (currentSort === 'price-high') {
    list.sort((a, b) => parsePrice(b.price) - parsePrice(a.price));
  } else {
    list.sort((a, b) => {
      const catA = categoryOrder.indexOf(a.category);
      const catB = categoryOrder.indexOf(b.category);
      if (catA !== catB) return catA - catB;
      return a.name.localeCompare(b.name);
    });
  }
  return list;
}

function parsePrice(str) {
  return parseFloat(str.replace(/[^\d.,]/g, '').replace(',', '.')) || 0;
}

// Render products — clean 3-column grid, no featured/banners
function renderProducts() {
  const filtered = getFilteredProducts();
  if (resultsCount) resultsCount.textContent = `Showing ${filtered.length} product${filtered.length !== 1 ? 's' : ''}`;

  productsGrid.innerHTML = filtered.length === 0
    ? '<p class="products-empty">No products found for this filter.</p>'
    : filtered.map(product => `
    <article class="product-card" data-category="${product.category}">
      <a href="product.html?id=${encodeURIComponent(product.id)}" class="product-link" data-product-id="${product.id}">
        <div class="product-image-wrap">
          <img class="product-image" src="${product.image}" alt="${product.name}" onerror="this.src='https://placehold.co/400x400/2d3e2d/ffffff?text=Santokki'">
        </div>
        <div class="product-info">
          <span class="product-category">${product.categoryLabel}</span>
          ${product.category === 'candle' && product.useArea ? `<span class="product-subcategory">${product.useArea === 'bedroom' ? 'Bedroom Candle' : 'Kitchen Candle'}</span>` : ''}
          <h3 class="product-name">${product.name}</h3>
          <p class="product-desc">${product.description}</p>
          <div class="product-footer">
            <span class="product-price">From ${product.price}</span>
            <span class="product-cta">Discover</span>
          </div>
        </div>
      </a>
    </article>
  `).join('');
}

function renderCategoryBanners(filtered) {
  if (!categoryBanners) return;
  const normalizedCategory = currentCategory.startsWith('candle-') ? 'candle' : currentCategory;
  const visibleCategories = normalizedCategory === 'all'
    ? categoryOrder.filter((cat) => filtered.some((item) => item.category === cat))
    : [normalizedCategory];

  categoryBanners.innerHTML = visibleCategories.map((cat) => {
    const meta = categoryBannerMeta[cat];
    if (!meta) return '';
    return `
      <article class="category-banner">
        <p class="category-banner-kicker">Category</p>
        <h4>${meta.title}</h4>
        <p>${meta.subtitle}</p>
      </article>
    `;
  }).join('');
}

function renderFeaturedProducts(filtered) {
  if (!featuredGrid) return;
  if (!filtered.length) {
    featuredGrid.innerHTML = '<p class="featured-empty">No featured products available for this filter.</p>';
    return;
  }

  const featuredOrder = ['diffuser-001', 'candle-001', 'room-001'];
  const byId = new Map(filtered.map((item) => [item.id, item]));
  const picked = [];

  featuredOrder.forEach((id) => {
    const match = byId.get(id);
    if (match) picked.push(match);
  });

  filtered.forEach((item) => {
    if (picked.length >= 3) return;
    if (!picked.some((p) => p.id === item.id)) picked.push(item);
  });

  featuredGrid.innerHTML = picked.slice(0, 3).map((product) => `
    <a href="product.html?id=${encodeURIComponent(product.id)}" class="featured-card" data-product-id="${product.id}">
      <img src="${product.image}" alt="${product.name}" class="featured-image" onerror="this.src='https://placehold.co/800x800/2d3e2d/ffffff?text=Santokki+Featured'">
      <div class="featured-overlay">
        <span class="featured-category">${product.categoryLabel}${product.category === 'candle' && product.useArea ? ` · ${product.useArea === 'bedroom' ? 'Bedroom' : 'Kitchen'}` : ''}</span>
        <h4 class="featured-name">${product.name}</h4>
        <p class="featured-price">From ${product.price}</p>
      </div>
    </a>
  `).join('');
}

// Filter products
function setupEventListeners() {
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategory = btn.dataset.category;
      renderProducts();
    });
  });

  facetteBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      facetteBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFacette = btn.dataset.facette;
      renderProducts();
    });
  });

  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      renderProducts();
    });
  }

  scentTestTriggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      openScentTest();
    });
  });

  popupClose.addEventListener('click', closeScentTest);
  scentTestPopup.addEventListener('click', (e) => {
    if (e.target === scentTestPopup) closeScentTest();
  });

  prevBtn.addEventListener('click', () => {
    if (currentQuestion > 0) {
      currentQuestion--;
      renderQuiz();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentQuestion < scentTestQuestions.length - 1) {
      const q = scentTestQuestions[currentQuestion];
      const selected = document.querySelector(`input[name="${q.id}"]:checked`);
      if (selected) {
        userAnswers[q.id] = selected.value;
        currentQuestion++;
        renderQuiz();
      }
    } else {
      finishQuiz();
    }
  });

  getCouponBtn.addEventListener('click', () => {
    alert('Thank you! Your 15% discount code: SANTOKKI15\nValid for 30 days.');
    closeScentTest();
  });

  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-product-id]');
    if (!link) return;
    const pid = link.getAttribute('data-product-id');
    if (pid) {
      sessionStorage.setItem('lastProductId', pid);
    }
  });
}

// Open / close scent test popup
function openScentTest() {
  currentQuestion = 0;
  userAnswers = {};
  quizResult.classList.add('hidden');
  quizContainer.classList.remove('hidden');
  prevBtn.classList.add('hidden');
  nextBtn.textContent = 'Next';
  renderQuiz();
  scentTestPopup.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeScentTest() {
  scentTestPopup.classList.remove('active');
  document.body.style.overflow = '';
}

// Render quiz questions
function renderQuiz() {
  const q = scentTestQuestions[currentQuestion];
  if (!q) return;

  prevBtn.classList.toggle('hidden', currentQuestion === 0);
  nextBtn.textContent = currentQuestion === scentTestQuestions.length - 1 ? 'See Result' : 'Next';

  quizContainer.innerHTML = `
    <div class="quiz-question">
      <h4>${q.question}</h4>
      <div class="quiz-options">
        ${q.options.map(opt => `
          <label class="quiz-option ${userAnswers[q.id] === opt.value ? 'selected' : ''}">
            <input type="radio" name="${q.id}" value="${opt.value}" ${userAnswers[q.id] === opt.value ? 'checked' : ''}>
            ${opt.label}
          </label>
        `).join('')}
      </div>
    </div>
  `;

  quizContainer.querySelectorAll('.quiz-option').forEach(opt => {
    opt.addEventListener('click', () => {
      quizContainer.querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      opt.querySelector('input').checked = true;
      userAnswers[q.id] = opt.querySelector('input').value;
    });
  });
}

// Build user scent profile from answers
function buildUserProfile() {
  const profile = { fresh: 0, woody: 0, green: 0, citrus: 0, floral: 0, warm: 0, sweet: 0 };

  const q1 = userAnswers['q1'];
  const q2 = userAnswers['q2'];
  const q3 = userAnswers['q3'];

  if (q1 && moodToProfile[q1]) {
    Object.entries(moodToProfile[q1]).forEach(([k, v]) => {
      if (profile.hasOwnProperty(k)) profile[k] += v;
    });
  }

  if (q2 && profile.hasOwnProperty(q2)) {
    profile[q2] += 10;
  }

  return { profile, preferredCategory: q3 };
}

// Compute similarity score between user profile and product
function similarityScore(userProfile, product) {
  const p = product.scentProfile;
  if (!p) return 0;

  let score = 0;
  const keys = Object.keys(userProfile);

  for (const k of keys) {
    const userVal = userProfile[k] || 0;
    const prodVal = p[k] || 0;
    score += Math.min(userVal, prodVal);
  }

  return score;
}

// Find best matching product
function recommendProduct() {
  const { profile, preferredCategory } = buildUserProfile();

  let best = null;
  let bestScore = -1;

  for (const product of productsData) {
    if (preferredCategory && preferredCategory !== 'all') {
      if (product.category !== preferredCategory) continue;
    }
    const score = similarityScore(profile, product);
    if (score > bestScore) {
      bestScore = score;
      best = product;
    }
  }

  return best || productsData[0];
}

// Finish quiz and show result
function finishQuiz() {
  const q = scentTestQuestions[currentQuestion];
  const selected = document.querySelector(`input[name="${q.id}"]:checked`);
  if (selected) userAnswers[q.id] = selected.value;

  const product = recommendProduct();

  quizContainer.classList.add('hidden');
  quizResult.classList.remove('hidden');
  prevBtn.classList.add('hidden');
  nextBtn.classList.add('hidden');

  recommendedProductEl.innerHTML = `
    <span class="product-category">${product.categoryLabel}</span>
    <h3 class="product-name">${product.name}</h3>
    <p class="product-desc">${product.description}</p>
    <span class="product-price">${product.price}</span>
  `;
}

// Header scroll effect
function setupScrollHeader() {
  const header = document.querySelector('.header');
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// ── Shoppable Hotspot ─────────────────────────────────────
function setupHotspots() {
  const pins = document.querySelectorAll('.hotspot-pin');
  const tooltip = document.getElementById('hotspot-tooltip');
  if (!pins.length || !tooltip) return;

  let activePin = null;

  function closeTooltip() {
    tooltip.classList.add('hidden');
    tooltip.innerHTML = '';
    if (activePin) { activePin.classList.remove('active'); activePin = null; }
  }

  pins.forEach((pin) => {
    pin.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = pin.dataset.hotspot;
      if (activePin === pin) { closeTooltip(); return; }

      const product = productsData ? productsData.find(p => p.id === id) : null;
      if (!product) return;

      if (activePin) { activePin.classList.remove('active'); }
      activePin = pin;
      pin.classList.add('active');

      // Position: parse left/top from inline style
      const leftPct = parseFloat(pin.style.left);
      const topPct  = parseFloat(pin.style.top);
      const scene   = pin.parentElement;
      const sw = scene.offsetWidth;
      const sh = scene.offsetHeight;
      const tw = 272; // tooltip width + margin

      let tooltipLeft = (leftPct / 100) * sw + 26;
      if (tooltipLeft + tw > sw) tooltipLeft = (leftPct / 100) * sw - tw - 10;

      tooltip.style.left = tooltipLeft + 'px';
      tooltip.style.top  = (topPct / 100) * sh + 'px';

      tooltip.classList.remove('hidden');
      tooltip.innerHTML = `
        <button class="hotspot-tooltip-close" id="hotspot-close" type="button" aria-label="Close">✕</button>
        <div class="hotspot-tooltip-inner">
          <img class="hotspot-tooltip-img" src="${product.image}" alt="${product.name}" onerror="this.src='https://placehold.co/54x54/2d3e2d/ffffff?text=S'">
          <div class="hotspot-tooltip-body">
            <p class="hotspot-tooltip-name">${product.name}</p>
            <p class="hotspot-tooltip-desc">${product.description}</p>
            <div class="hotspot-tooltip-footer">
              <a class="hotspot-tooltip-link" href="product.html?id=${encodeURIComponent(product.id)}">View product</a>
              <span class="hotspot-tooltip-price">· ${product.price}</span>
            </div>
          </div>
        </div>
      `;

      document.getElementById('hotspot-close').addEventListener('click', (ev) => {
        ev.stopPropagation();
        closeTooltip();
      });
    });
  });

  document.addEventListener('click', (e) => {
    if (!tooltip.contains(e.target)) closeTooltip();
  });
}

init();

// Hotspots require productsData — call after init resolves
(async () => {
  // Wait until productsData is populated by init()
  const waitForData = () => new Promise(res => {
    const check = setInterval(() => {
      if (productsData) { clearInterval(check); res(); }
    }, 50);
  });
  await waitForData();
  setupHotspots();
})();
