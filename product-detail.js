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
  return new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR' }).format(value);
}

function buildCheckoutPageUrl(productId, qty) {
  const params = new URLSearchParams({
    id: productId,
    qty: String(qty)
  });
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

function renderProduct(product) {
  const basePrice = parsePriceToNumber(product.price);
  detailRoot.innerHTML = `
    <div class="detail-media">
      <img src="${product.image}" alt="${product.name}" onerror="this.src='https://placehold.co/900x900/2d3e2d/ffffff?text=Santokki+Product'">
    </div>
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
          <a class="btn btn-secondary" href="index.html#products">Continue Shopping</a>
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

  buyNowBtn.addEventListener('click', () => {
    const qty = Math.max(1, Number(qtyInput.value || 1));
    sessionStorage.setItem('pendingCheckout', JSON.stringify({ id: product.id, qty }));
    const checkoutUrl = buildCheckoutPageUrl(product.id, qty);
    window.location.href = checkoutUrl;
  });
}

async function initProductDetail() {
  const productId = getProductId();
  if (!productId) {
    renderNotFound();
    return;
  }

  try {
    const res = await fetch('products.json');
    const data = await res.json();
    const product = (data.products || []).find((item) => item.id === productId);
    if (!product) {
      renderNotFound();
      return;
    }
    renderProduct(product);
  } catch (error) {
    renderNotFound();
  }
}

initProductDetail();
