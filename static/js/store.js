// Cart + browsing history, persisted in the browser (localStorage, guarded for private mode).
const read = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* ignore */ } };

export const getCart = () => read("acme_cart", []);          // [{product, qty}]
export const cartCount = () => getCart().reduce((n, l) => n + l.qty, 0);

export function addToCart(product) {
  const cart = getCart();
  const line = cart.find(l => l.product.product_id === product.product_id);
  line ? line.qty++ : cart.push({ product, qty: 1 });
  write("acme_cart", cart);
}
export function updateCart(id, delta) {
  const cart = getCart().map(l => l.product.product_id === id ? { ...l, qty: l.qty + delta } : l).filter(l => l.qty > 0);
  write("acme_cart", cart);
}
export const getHistory = () => read("acme_history", []);
export function pushHistory(id) {
  write("acme_history", [id, ...getHistory().filter(x => x !== id)].slice(0, 8));
}
