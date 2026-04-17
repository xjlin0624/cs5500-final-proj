class SephoraExtractor extends BaseExtractor {
  constructor() {
    super("sephora");
  }

  extractOrders() {
    const orders = [];

    // Order detail page: extract total, status, and items
    const detailTotalEl = document.querySelector("[data-at='orderdetail_order_total']");
    if (detailTotalEl) {
      const orderId = window.location.pathname.match(/\/orderdetail\/(\w+)/)?.[1];
      if (orderId) {
        const totalText = detailTotalEl.textContent.trim();
        const total = parseFloat(totalText.replace(/[^0-9.]/g, "")) || 0;
        const orderDate = document.querySelector("[data-at='order_date']")?.textContent?.trim() || "";
        const orderStatus = document.querySelector("[data-at='order_status']")?.textContent?.trim() || "";

        const brands = [...document.querySelectorAll("[data-at='sku_item_brand']")];
        const names = [...document.querySelectorAll("[data-at='sku_item_name']")];
        const prices = [...document.querySelectorAll("[data-at='sku_item_price_list']")];
        const skus = [...document.querySelectorAll("[data-at='sku_size']")];

        const items = brands.map((brandEl, i) => {
          const brand = brandEl?.textContent?.trim() || "";
          const name = names[i]?.textContent?.trim() || "";
          const priceText = prices[i]?.textContent?.trim() || "";
          const paidPrice = parseFloat(priceText.replace(/[^0-9.]/g, "")) || null;
          const skuText = skus[i]?.textContent?.trim() || "";
          const skuId = skuText.match(/ITEM\s+(\d+)/)?.[1] || null;
          return {
            name: brand ? `${brand} ${name}` : name,
            productId: skuId,
            productUrl: null,
            imageUrl: null,
            paidPrice,
          };
        }).filter(item => item.name);

        orders.push({
          externalOrderId: orderId,
          orderDate,
          orderUrl: window.location.href,
          orderStatus,
          total,
          currency: "USD",
          items,
        });
      }
      return orders;
    }

    // Order history list page
    const orderCards = document.querySelectorAll("[data-at='item_row']");
    for (const card of orderCards) {
      try {
        const orderId = card.querySelector(
          "[data-at='order_number']"
        )?.textContent?.trim();

        const dateEl = card.querySelector("[data-at='order_date']");
        const orderDate = dateEl?.textContent?.trim() || "";

        const orderUrl = orderId
          ? `https://www.sephora.com/profile/orderdetail/${orderId}`
          : null;

        const orderStatus = card.querySelector("[data-at='order_status']")?.textContent?.trim() || "";

        if (orderId) {
          orders.push({
            externalOrderId: orderId,
            orderDate,
            orderUrl,
            orderStatus,
            total: 0,
            currency: "USD",
            items: [],
          });
        }
      } catch (e) {
        console.warn("[AfterCart] Failed to parse Sephora order card:", e);
      }
    }
    return orders;
  }

  extractCurrentPrice() {
    // Product detail pages: /product/{slug}-P{skuId}
    const skuMatch = window.location.pathname.match(/-P(\d+)/);
    if (!skuMatch) return null;

    // Sephora shows original price + sale price
    const currentPriceEl = document.querySelector(
      "[data-at='price_sale'], [data-at='price'], " +
      "[data-comp='Price'] b, .css-0"
    );
    const priceText = currentPriceEl?.textContent?.trim() || "";
    const price = parseFloat(priceText.replace(/[^0-9.]/g, "")) || null;

    const titleEl = document.querySelector(
      "[data-at='product_name'], [data-comp='DisplayName'], " +
      "h1 span[data-at='product_name']"
    );
    const brandEl = document.querySelector(
      "[data-at='brand_name'], [data-comp='BrandName']"
    );
    const brand = brandEl?.textContent?.trim() || "";
    const name = titleEl?.textContent?.trim() || "";
    const productName = brand ? `${brand} — ${name}` : name;

    if (price) {
      return {
        productId: skuMatch[1],
        productName,
        price,
        currency: "USD",
      };
    }
    return null;
  }
}

// Wait for Sephora's SPA to render order rows before extracting
const sephoraExtractor = new SephoraExtractor();

function runWhenReady() {
  const isReady = () =>
    document.querySelector("[data-at='item_row']") ||
    document.querySelector("[data-at='orderdetail_order_total']");

  if (isReady()) {
    sephoraExtractor.run();
    return;
  }
  const observer = new MutationObserver(() => {
    if (isReady()) {
      observer.disconnect();
      sephoraExtractor.run();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

runWhenReady();
