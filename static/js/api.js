// Thin wrapper around the FastAPI endpoints.
async function request(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    throw new Error(typeof d === "string" ? d : Array.isArray(d) ? d.map(e => e.msg).join("; ") : "Request failed");
  }
  return data;
}
const post = (path, body) => request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const qs = (o) => new URLSearchParams(Object.entries(o).filter(([, v]) => v != null && v !== "")).toString();

export const getStats = () => request("/api/stats");
export const getProduct = (id) => request(`/api/products/${encodeURIComponent(id)}`);
export const listProducts = (o) => request(`/api/products?${qs(o)}`);
export const recommend = (payload) => post("/api/recommend", payload);
export const recommendBasket = (ids, top_n = 12) => post("/api/recommend/basket", { product_ids: ids, top_n });
export const explain = (payload) => post("/api/explain", payload);
