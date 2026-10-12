// Reusable HTML builders (no network code).
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export const inr = (n) => "₹" + Number(n).toLocaleString("en-IN");
const FALLBACK = "data:image/svg+xml;utf8," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#f0f2f2"/><text x="50" y="54" font-size="10" text-anchor="middle" fill="#888">No image</text></svg>');

export const img = (p) => `<img src="${esc(p.image || FALLBACK)}" alt="${esc(p.name)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='${FALLBACK}'">`;
export const offPct = (p) => (p.discount_price && p.actual_price && p.actual_price > p.discount_price) ? Math.round(100 * (1 - p.discount_price / p.actual_price)) : 0;

export const stars = (r) => r == null ? "" :
  `<span class="stars" aria-label="${r} out of 5">★★★★★<i style="width:${(r / 5) * 100}%">★★★★★</i></span> <span class="rv">${r}</span>`;

export function price(p, big = false) {
  const cur = p.discount_price ?? p.actual_price;
  if (cur == null) return `<span class="price" style="color:var(--mut)">Price not listed</span>`;
  const off = offPct(p);
  return `<span class="price ${big ? "bigp" : ""}">${off && big ? `<span class="off">-${off}%</span>` : ""}${inr(cur)}${off ? `<span class="mrp">M.R.P.: ${inr(p.actual_price)}</span>${big ? "" : `<span class="off">(${off}% off)</span>`}` : ""}</span>`;
}
export const match = (p) => p.similarity_score != null ? `<span class="match" title="Cosine similarity">${Math.round(Math.max(0, p.similarity_score) * 100)}% match</span>` : "";

export const card = (p) => `<a class="pc" href="#/product/${esc(p.product_id)}">
  <div class="im">${img(p)}</div><div class="t">${esc(p.name)}</div>
  <div>${stars(p.ratings)}${p.no_of_ratings ? ` <span class="rv">(${Number(p.no_of_ratings).toLocaleString("en-IN")})</span>` : ""}</div>
  ${price(p)}${match(p)}</a>`;

export const shelf = (title, items, sub = "") =>
  items.length ? `<section class="box"><h2>${esc(title)}</h2>${sub ? `<p style="margin:-6px 0 10px;color:var(--mut)">${sub}</p>` : ""}<div class="row">${items.map(card).join("")}</div></section>` : "";

export const listItem = (p) => `<div class="li"><a class="im" href="#/product/${esc(p.product_id)}">${img(p)}</a><div>
  <h3><a href="#/product/${esc(p.product_id)}">${esc(p.name)}</a></h3>
  <div>${stars(p.ratings)} <span class="rv">${p.no_of_ratings ? Number(p.no_of_ratings).toLocaleString("en-IN") : ""}</span></div>
  <div style="margin:6px 0">${price(p)}</div>${match(p)}
  <div style="color:var(--mut);margin:6px 0;text-transform:capitalize">${esc(p.main_category)} › ${esc(p.sub_category)}</div>
  <button class="btn sm" data-add="${esc(p.product_id)}">Add to cart</button></div></div>`;

export const skeleton = (n = 4) => `<div class="tiles" style="margin-top:16px">${Array.from({ length: n }, () => '<div class="sk"></div>').join("")}</div>`;
export const message = (m, err = false) => `<div class="msg ${err ? "err" : ""}">${esc(m)}</div>`;

export function whyPanel(e, tokens) {
  const tk = (tokens || []).map(t => `<span class="tk ${t.in_vocab ? "" : "un"}">${esc(t.token)}</span>`).join("");
  return `<details class="why"><summary>How were these recommendations chosen?</summary>
   <p>Words in yellow were not seen in the catalogue. FastText rebuilds their meaning from character n-grams.</p>
   <div>${tk}</div>
   <ol><li>Raw text: <code>${esc(e.raw_text)}</code></li>
   <li>Tokens: ${e.tokens.map(t => `<code>${esc(t)}</code>`).join(" ")}</li>
   <li>Related words: ${e.word_vectors.map(w => `<code>${esc(w.token)}</code> ≈ ${w.neighbours.map(esc).join(", ")}`).join("; ")}</li>
   <li>Product vector: ${e.product_vector.dimensions}-D, first values <code>[${e.product_vector.preview.slice(0, 5).join(", ")}…]</code></li>
   <li>Cosine similarity ranking: ${e.ranking.map(r => `${esc(r.product_id)} (${(r.score * 100).toFixed(1)}%)`).join(", ")}</li></ol></details>`;
}
