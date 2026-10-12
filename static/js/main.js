import * as api from "./api.js";
import * as pages from "./pages.js";
import * as ui from "./components.js";
import * as store from "./store.js";

const $ = (id) => document.getElementById(id);
const app = $("app");
const refreshCount = () => { $("cart-count").textContent = store.cartCount(); };

function parseHash() {
  const [path, query = ""] = (location.hash.slice(1) || "/").split("?");
  return { parts: path.split("/").filter(Boolean).map(decodeURIComponent), params: new URLSearchParams(query) };
}

async function route() {
  const { parts, params } = parseHash();
  app.innerHTML = ui.skeleton();
  window.scrollTo(0, 0);
  try {
    const [a, b] = parts;
    if (a === "search") { $("q").value = params.get("q") || ""; app.innerHTML = await pages.search({ q: params.get("q") || "", cat: params.get("cat") }); }
    else if (a === "category" && b) app.innerHTML = await pages.category(b, +(params.get("page") || 1));
    else if (a === "product" && b) app.innerHTML = await pages.product(b);
    else if (a === "cart") app.innerHTML = await pages.cart();
    else app.innerHTML = await pages.home();
  } catch (err) { app.innerHTML = ui.message(err.message, true); }
}

$("search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("q").value.trim();
  if (!q) return;
  if (/^ACME_\d+$/i.test(q)) { location.hash = `#/product/${q.toUpperCase()}`; return; }   // product-ID lookup
  const cat = $("cat-select").value;
  location.hash = `#/search?q=${encodeURIComponent(q)}${cat ? `&cat=${encodeURIComponent(cat)}` : ""}`;
});

document.addEventListener("click", async (e) => {
  const add = e.target.closest("[data-add],[data-buy]");
  if (add) {
    const id = add.dataset.add || add.dataset.buy;
    store.addToCart(await api.getProduct(id)); refreshCount();
    if (add.dataset.buy) location.hash = "#/cart"; else { add.textContent = "✓ Added"; }
  }
  const qty = e.target.closest("[data-qty]");
  if (qty) { const [id, d] = qty.dataset.qty.split(":"); store.updateCart(id, +d); refreshCount(); route(); }
  if (e.target.closest("[data-checkout]")) alert("Demo store: checkout is not implemented.");
});
$("to-top").addEventListener("click", (e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); });
window.addEventListener("hashchange", route);

(async function init() {
  refreshCount();
  try {
    const s = await api.getStats();
    pages.setCategories(s.categories);
    $("cat-select").insertAdjacentHTML("beforeend", s.categories.map(c => `<option>${ui.esc(c)}</option>`).join(""));
    $("subnav").insertAdjacentHTML("beforeend", s.categories.slice(0, 12).map(c => `<a href="#/category/${encodeURIComponent(c)}">${ui.esc(c)}</a>`).join(""));
  } catch { app.innerHTML = ui.message("Backend offline. Start the server and refresh.", true); return; }
  route();
})();
