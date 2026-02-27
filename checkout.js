const checkoutRoot = document.getElementById('checkout-page');

function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  let pending = null;
  try {
    pending = JSON.parse(sessionStorage.getItem('pendingCheckout') || 'null');
  } catch (_) {
    pending = null;
  }

  const rawQty = Number(params.get('qty') || pending?.qty || 1);
  return {
    id: params.get('id') || pending?.id || sessionStorage.getItem('lastProductId'),
    qty: Math.max(1, Number.isFinite(rawQty) ? rawQty : 1)
  };
}

function parsePriceToNumber(priceStr) {
  return parseFloat(String(priceStr).replace(/[^\d.,]/g, '').replace(',', '.')) || 0;
}

function formatEuro(value) {
  return new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR' }).format(value);
}

function renderCheckoutShell(initialQty) {
  return `
    <section class="checkout-summary">
      <h1>Checkout</h1>
      <article class="checkout-product-card">
        <img src="https://placehold.co/600x600/2d3e2d/ffffff?text=Santokki+Item" alt="Selected product">
        <div>
          <p class="detail-category" id="summary-category">Selected Product</p>
          <h2 id="summary-name">Preparing your product</h2>
          <p class="checkout-line"><span>Unit price</span><strong id="summary-unit">-</strong></p>
          <p class="checkout-line"><span>Quantity</span><strong id="summary-qty">${initialQty}</strong></p>
          <p class="checkout-line total"><span>Total</span><strong id="summary-total">-</strong></p>
        </div>
      </article>
    </section>

    <section class="checkout-form-wrap">
      <h2>Shipping & Contact</h2>
      <form id="checkout-form-page" class="checkout-form-page">
        <label>
          Full Name
          <input type="text" name="name" required>
        </label>
        <label>
          Email
          <input type="email" name="email" required>
        </label>
        <label>
          Phone
          <input type="tel" name="phone" required>
        </label>
        <label>
          Address
          <textarea name="address" rows="3" required></textarea>
        </label>
        <label>
          Quantity
          <input id="qty-input" type="number" min="1" value="${initialQty}" required>
        </label>
        <button type="submit" class="btn btn-primary">Place Order Request</button>
        <a href="index.html#products" class="btn btn-secondary">Back to Product</a>
      </form>
      <p class="checkout-note">Demo checkout page. Payment gateway can be connected later (Shopify/Stripe).</p>
    </section>
  `;
}

function renderCheckout(product, initialQty) {
  checkoutRoot.innerHTML = renderCheckoutShell(initialQty);

  const qtyInput = document.getElementById('qty-input');
  const summaryQty = document.getElementById('summary-qty');
  const summaryTotal = document.getElementById('summary-total');
  const summaryUnit = document.getElementById('summary-unit');
  const summaryName = document.getElementById('summary-name');
  const summaryCategory = document.getElementById('summary-category');
  const summaryImg = document.querySelector('.checkout-product-card img');
  const backLink = document.querySelector('.checkout-form-page .btn.btn-secondary');
  const form = document.getElementById('checkout-form-page');
  const unitPrice = product ? parsePriceToNumber(product.price) : 0;

  if (product) {
    if (summaryName) summaryName.textContent = product.name;
    if (summaryCategory) summaryCategory.textContent = product.categoryLabel;
    if (summaryImg) {
      summaryImg.src = product.image;
      summaryImg.alt = product.name;
      summaryImg.onerror = () => {
        summaryImg.src = 'https://placehold.co/600x600/2d3e2d/ffffff?text=Santokki+Item';
      };
    }
    if (summaryUnit) summaryUnit.textContent = formatEuro(unitPrice);
    if (backLink) backLink.href = `product.html?id=${encodeURIComponent(product.id)}`;
  } else {
    if (summaryUnit) summaryUnit.textContent = '-';
    if (backLink) backLink.href = 'index.html#products';
  }

  const updateSummary = () => {
    const qty = Math.max(1, Number(qtyInput.value || 1));
    qtyInput.value = String(qty);
    summaryQty.textContent = String(qty);
    summaryTotal.textContent = unitPrice > 0 ? formatEuro(unitPrice * qty) : '-';
  };

  qtyInput.addEventListener('input', () => {
    updateSummary();
  });
  updateSummary();

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Order request received. We will contact you shortly for payment confirmation.');
    window.location.href = 'index.html#products';
  });
}

async function initCheckout() {
  const { id, qty } = getQueryParams();

  try {
    const res = await fetch('products.json');
    const data = await res.json();
    const product = id ? (data.products || []).find((item) => item.id === id) : null;
    renderCheckout(product, qty);
  } catch (error) {
    renderCheckout(null, qty);
  }
}

initCheckout();
