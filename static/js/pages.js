import * as api from "./api.js";
import * as ui from "./components.js";
import * as store from "./store.js";

const PAGE = 24;
let categories = [];
export const setCategories = (c) => { categories = c; };

export async function home() {
  const [best, all] = await Promise.all([api.listProducts({ size: 12 }), Promise.all(categories.slice(0, 8).map(c => api.listProducts({ category: c, size: 4 })))]);
  const tiles = all.map((r, i) => `<div class="tile"><h2>${ui.esc(categories[i])}</h2><div class="imgs">${r.items.map(p =>
    `<a href="#/product/${p.product_id}">${ui.img(p)}</a>`).join("")}</div><a href="#/category/${encodeURIComponent(categories[i])}">See more</a></div>`).join("");
  const hist = store.getHistory();
  let history = "";
  if (hist.length) {
    try { history = ui.shelf("Inspired by your browsing history", (await api.recommendBasket(hist, 12)).results, "Found by averaging the meaning of items you viewed"); } catch { /* ignore */ }
  }
  return `<section class="hero"><div><h1>Everything you need, matched to what you love</h1>
    <p>Search by describing a product in your own words. Our FastText engine finds items by meaning, not just keywords.</p>
    <a class="btn" href="#/search?q=${encodeURIComponent("wireless bluetooth earphones")}">Try: wireless earphones</a></div></section>
    <div class="tiles">${tiles}</div>${history}${ui.shelf("Best sellers", best.items)}`;
}

export async function search({ q, cat }) {
  const data = await api.recommend({ text: q, top_n: 40, category: cat || null });
  const side = `<aside class="side"><h3>Department</h3><a href="#/search?q=${encodeURIComponent(q)}" class="${cat ? "" : "on"}">Any department</a>${categories.map(c =>
    `<a class="${c === cat ? "on" : ""}" href="#/search?q=${encodeURIComponent(q)}&cat=${encodeURIComponent(c)}">${ui.esc(c)}</a>`).join("")}</aside>`;
  const ex = await api.explain({ text: q, category: cat || null, top_n: 5 });
  return `<div class="crumb">${data.results.length} results for <b>"${ui.esc(q)}"</b>${cat ? ` in ${ui.esc(cat)}` : ""}. Sorted by similarity.</div>
    <div class="layout">${side}<div><div class="list">${data.results.map(ui.listItem).join("") || ui.message("No results. Try other words.")}</div>${ui.whyPanel(ex, data.tokens)}</div></div>`;
}

export async function category(name, page) {
  const r = await api.listProducts({ category: name, page, size: PAGE });
  const pages = Math.ceil(r.total / PAGE);
  const link = (p, t) => `<a class="btn sm" href="#/category/${encodeURIComponent(name)}?page=${p}">${t}</a>`;
  return `<div class="crumb">${r.total.toLocaleString("en-IN")} products in <b style="text-transform:capitalize">${ui.esc(name)}</b>, most reviewed first</div>
    <div class="layout"><aside class="side"><h3>Department</h3>${categories.map(c => `<a class="${c === name ? "on" : ""}" href="#/category/${encodeURIComponent(c)}">${ui.esc(c)}</a>`).join("")}</aside>
    <div><div class="list">${r.items.map(ui.listItem).join("")}</div>
    <div class="pager">${page > 1 ? link(page - 1, "‹ Previous") : ""}<span>Page ${page} of ${pages}</span>${page < pages ? link(page + 1, "Next ›") : ""}</div></div></div>`;
}

export async function product(id) {
  const p = await api.getProduct(id);
  store.pushHistory(p.product_id);
  const [rec, ex] = await Promise.all([api.recommend({ product_id: id, top_n: 16 }), api.explain({ product_id: id, top_n: 5 })]);
  const same = rec.results.filter(r => r.main_category === p.main_category && r.sub_category === p.sub_category);
  return `<div class="crumb"><a href="#/category/${encodeURIComponent(p.main_category)}" style="text-transform:capitalize">${ui.esc(p.main_category)}</a> › ${ui.esc(p.sub_category)}</div>
    <section class="pdp"><div class="big">${ui.img(p)}</div>
    <div><h1>${ui.esc(p.name)}</h1><div>${ui.stars(p.ratings)} ${p.no_of_ratings ? `<span class="rv">${Number(p.no_of_ratings).toLocaleString("en-IN")} ratings</span>` : '<span class="rv">No ratings yet</span>'}</div><hr>
      <div>${ui.price(p, true)}</div><p style="color:var(--mut);margin:2px 0">Inclusive of all taxes</p><hr>
      <table class="facts"><tr><td>Category</td><td style="text-transform:capitalize">${ui.esc(p.main_category)}</td></tr><tr><td>Sub-category</td><td>${ui.esc(p.sub_category)}</td></tr><tr><td>Product ID</td><td>${ui.esc(p.product_id)}</td></tr></table>
      ${ui.whyPanel(ex, rec.tokens)}</div>
    <div class="buybox"><div>${ui.price(p, true)}</div><p class="instock">In stock</p>
      <button class="btn block" data-add="${ui.esc(p.product_id)}">Add to Cart</button>
      <button class="btn buy block" data-buy="${ui.esc(p.product_id)}">Buy Now</button>
      ${p.link ? `<p><a href="${ui.esc(p.link)}" target="_blank" rel="noopener">View original listing</a></p>` : ""}</div></section>
    ${ui.shelf("Customers who viewed this item also viewed", rec.results.slice(0, 12), "Ranked by FastText cosine similarity")}
    ${ui.shelf("More in " + p.sub_category, same.slice(0, 12))}`;
}

export async function cart() {
  const lines = store.getCart();
  if (!lines.length) return `<section class="box">${ui.message("Your Acme cart is empty.")}<p style="text-align:center"><a href="#/">Continue shopping</a></p></section>`;
  const sub = lines.reduce((s, l) => s + (l.product.discount_price ?? l.product.actual_price ?? 0) * l.qty, 0);
  let recs = "";
  try { recs = ui.shelf("Recommended based on your cart", (await api.recommendBasket(lines.map(l => l.product.product_id), 12)).results, "Average of the items' embeddings, ranked by similarity"); } catch { /* ignore */ }
  return `<section class="box"><h2>Shopping Cart</h2>${lines.map(l => `<div class="cartline"><a href="#/product/${l.product.product_id}">${ui.img(l.product)}</a>
    <div><a href="#/product/${l.product.product_id}">${ui.esc(l.product.name)}</a><div class="instock" style="font-size:12px">In stock</div>
    <div style="margin-top:8px">Qty: <button class="btn sm" data-qty="${l.product.product_id}:-1">−</button> <b>${l.qty}</b> <button class="btn sm" data-qty="${l.product.product_id}:1">+</button></div></div>
    <b>${l.product.discount_price ?? l.product.actual_price ? ui.inr((l.product.discount_price ?? l.product.actual_price) * l.qty) : ""}</b></div>`).join("")}
    <div class="sub">Subtotal (${store.cartCount()} items): <b>${ui.inr(sub)}</b></div>
    <div style="text-align:right"><button class="btn" data-checkout>Proceed to Buy</button></div></section>${recs}`;
}
