const detailRoot = document.getElementById('product-detail');

function getProductId() {
  const params = new URLSearchParams(window.location.search);
  const fromQuery = params.get('id');
  if (fromQuery) return fromQuery;
  const fromSession = sessionStorage.getItem('lastProductId');
  if (fromSession) return fromSession;
  return null;
}

function parsePriceToNumber(priceStr) {
  return parseFloat(String(priceStr).replace(/[^\d.,]/g, '').replace(',', '.')) || 0;
}

function formatEuro(value) {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(value);
}

function buildCheckoutPageUrl(productId, qty) {
  const params = new URLSearchParams({ id: productId, qty: String(qty) });
  return `checkout.html?${params.toString()}`;
}

function renderNotFound() {
  detailRoot.innerHTML = `
    <div class="product-not-found">
      <h1>Product not found</h1>
      <p>The item you selected is not available right now.</p>
      <a class="btn btn-primary" href="index.html#products">Back to products</a>
    </div>
  `;
}

function buildSliderHTML(product) {
  const rawImages = Array.isArray(product.images) && product.images.length > 0
    ? product.images
    : [product.image];
  const images = rawImages.slice(0, 2);
  const hasMultiple = images.length > 1;

  const slides = images.map((src, i) => `
    <div class="slider-slide" data-index="${i}">
      <img src="${src}" alt="${product.name} - view ${i + 1}"
        onerror="this.src='https://placehold.co/900x900/2d3e2d/ffffff?text=Santokki'">
    </div>
  `).join('');

  const nav = hasMultiple ? `
    <button class="slider-btn slider-prev" aria-label="Previous image" type="button">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
    </button>
    <button class="slider-btn slider-next" aria-label="Next image" type="button">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    </button>
  ` : '';

  return `
    <div class="detail-media">
      <div class="slider-wrap">
        <div class="slider-track">${slides}</div>
        ${nav}
      </div>
    </div>
  `;
}

function initSlider(container) {
  const wrap = container.querySelector('.slider-wrap');
  if (!wrap) return;

  const track = wrap.querySelector('.slider-track');
  const slides = wrap.querySelectorAll('.slider-slide');
  const total = slides.length;
  if (total <= 1) return;

  const dotsWrap = container.querySelector('.detail-media');
  const dots = dotsWrap ? dotsWrap.querySelectorAll('.slider-dot') : [];

  let current = 0;
  let animating = false;

  // Lay slides side-by-side
  track.style.display = 'flex';
  track.style.width = `${total * 100}%`;
  track.style.willChange = 'transform';
  track.style.transition = 'transform 0.48s cubic-bezier(0.4, 0, 0.2, 1)';
  slides.forEach(slide => {
    slide.style.flex = `0 0 ${100 / total}%`;
    slide.style.minWidth = `${100 / total}%`;
  });

  function goTo(index) {
    if (animating) return;
    const next = ((index % total) + total) % total;
    if (next === current) return;
    animating = true;

    current = next;

    track.style.transform = `translateX(-${(current / total) * 100}%)`;

    setTimeout(() => { animating = false; }, 500);
  }

  wrap.querySelector('.slider-prev')?.addEventListener('click', () => goTo(current - 1));
  wrap.querySelector('.slider-next')?.addEventListener('click', () => goTo(current + 1));

  // Touch swipe
  let touchStartX = 0;
  wrap.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
  wrap.addEventListener('touchend', e => {
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 40) goTo(diff > 0 ? current + 1 : current - 1);
  });
}

function renderProduct(product) {
  const basePrice = parsePriceToNumber(product.price);
  detailRoot.innerHTML = `
    ${buildSliderHTML(product)}
    <div class="detail-info">
      <p class="detail-category">${product.categoryLabel}${product.edition ? ` <span class="detail-edition-badge">${product.edition}</span>` : ''}</p>
      <h1 class="detail-name">${product.name}${product.nameKo ? `<span class="detail-name-ko">${product.nameKo}</span>` : ''}</h1>
      <p class="detail-description">${product.description}</p>
      ${product.concept ? `<div class="detail-block"><h3 class="detail-block-title">Concept</h3><p class="detail-block-text">${product.concept}</p></div>` : ''}
      ${product.scentNotes ? `<div class="detail-block"><h3 class="detail-block-title">Scent notes</h3><p class="detail-block-text">${product.scentNotes}</p></div>` : ''}
      ${product.marketingPoint ? `<div class="detail-block"><h3 class="detail-block-title">Design & story</h3><p class="detail-block-text">${product.marketingPoint}</p></div>` : ''}
      <p class="detail-price" id="detail-price">${formatEuro(basePrice)}</p>

      <div class="purchase-box">
        <h3>Purchase</h3>
        <div class="purchase-row">
          <label for="quantity">Quantity</label>
          <input id="quantity" type="number" min="1" value="1">
        </div>
        <div class="purchase-total">
          <span>Total</span>
          <strong id="purchase-total">${formatEuro(basePrice)}</strong>
        </div>
        <p class="checkout-hint">Proceed to secure checkout page</p>
        <div class="purchase-actions">
          <button id="buy-now-btn" class="btn btn-primary" type="button">Buy Now</button>
          <button id="add-cart-btn" class="btn btn-secondary" type="button">Add Cart</button>
        </div>
      </div>
    </div>
  `;

  const qtyInput = document.getElementById('quantity');
  const totalEl = document.getElementById('purchase-total');
  const buyNowBtn = document.getElementById('buy-now-btn');

  qtyInput.addEventListener('input', () => {
    const qty = Math.max(1, Number(qtyInput.value || 1));
    qtyInput.value = String(qty);
    totalEl.textContent = formatEuro(basePrice * qty);
  });

  initSlider(detailRoot);

  buyNowBtn.addEventListener('click', () => {
    const qty = Math.max(1, Number(qtyInput.value || 1));
    window.location.href = 'checkout.html?id=' + encodeURIComponent(product.id) + '&qty=' + qty;
  });

  const addCartBtn = document.getElementById('add-cart-btn');
  addCartBtn.addEventListener('click', () => {
    const qty = Math.max(1, Number(qtyInput.value || 1));
    const cart = JSON.parse(localStorage.getItem('santokki_cart') || '[]');
    const existing = cart.find(function(i){ return i.id === product.id; });
    if (existing) { existing.qty += qty; } else { cart.push({ id: product.id, qty: qty }); }
    localStorage.setItem('santokki_cart', JSON.stringify(cart));
    addCartBtn.textContent = '✓ Added!';
    addCartBtn.style.color = 'var(--accent)';
    addCartBtn.style.borderColor = 'var(--accent)';
    setTimeout(function(){
      addCartBtn.textContent = 'Add Cart';
      addCartBtn.style.color = '';
      addCartBtn.style.borderColor = '';
    }, 1800);
  });
}

async function initProductDetail() {
  const productId = getProductId();
  if (!productId) { renderNotFound(); return; }

  try {
    const res = await fetch('products.json');
    const data = await res.json();
    const product = (data.products || []).find(item => item.id === productId);
    if (!product) { renderNotFound(); return; }
    renderProduct(product);
  } catch (error) {
    renderNotFound();
  }
}

initProductDetail();
