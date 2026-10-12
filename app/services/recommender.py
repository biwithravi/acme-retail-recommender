"""Similarity search + ranking, and a step-by-step explanation of the pipeline."""
from typing import Optional

import numpy as np
import pandas as pd

from app.services.catalog import load_catalog
from app.services.embedding import embed_tokens, load_or_build
from app.services.preprocessing import clean_text

CARD_COLS = ["product_id", "name", "main_category", "sub_category", "image", "link",
             "ratings", "no_of_ratings", "discount_price", "actual_price"]


def _clean(v):
    """Make a pandas/numpy value JSON-safe (NaN -> None)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return v.item() if hasattr(v, "item") else v


class Recommender:
    def __init__(self):
        self.df: pd.DataFrame = load_catalog()
        self.model, self.matrix = load_or_build(self.df["tokens"].tolist())
        self.id_to_idx = {pid: i for i, pid in enumerate(self.df["product_id"])}
        self.categories = sorted(self.df["main_category"].unique())
        # popularity order (most-rated first) used for category pages and best-sellers
        pop = self.df["no_of_ratings"].fillna(0) if "no_of_ratings" in self.df else pd.Series(0, index=self.df.index)
        self.popular_idx = np.argsort(-pop.values, kind="stable")

    # ---------- helpers ----------
    def product(self, idx: int, score: Optional[float] = None) -> dict:
        row = self.df.iloc[idx]
        out = {c: _clean(row[c]) for c in CARD_COLS if c in self.df.columns}
        if score is not None:
            out["similarity_score"] = round(float(score), 4)
        return out

    def get(self, product_id: str) -> dict:
        idx = self.id_to_idx.get(product_id.upper())
        if idx is None:
            raise KeyError(product_id)
        return self.product(idx)

    def random(self, n: int) -> list:
        return [self.product(int(i)) for i in np.random.choice(len(self.df), n, replace=False)]

    def list_products(self, category=None, page=1, size=24):
        idx = self.popular_idx
        if category:
            idx = idx[self.df["main_category"].values[idx] == category]
        start = (page - 1) * size
        return {"total": int(len(idx)), "items": [self.product(int(i)) for i in idx[start:start + size]]}

    def recommend_basket(self, product_ids, top_n=12):
        """Recommendations for several products at once (cart / browsing history):
        average their unit vectors, then rank by cosine similarity."""
        idxs = [self.id_to_idx[p.upper()] for p in product_ids if p.upper() in self.id_to_idx]
        if not idxs:
            raise ValueError("None of the product IDs exist.")
        vec = self.matrix[idxs].mean(axis=0)
        scores = self.matrix @ (vec / (np.linalg.norm(vec) or 1))
        scores[idxs] = -np.inf
        top = np.argpartition(-scores, top_n - 1)[:top_n]
        top = sorted((int(i) for i in top), key=lambda i: -scores[i])
        return {"results": [self.product(i, scores[i]) for i in top]}

    def _query_vector(self, product_id: Optional[str], text: Optional[str]):
        """Returns (unit vector, query row index or None, tokens)."""
        if product_id:
            idx = self.id_to_idx.get(product_id.upper())
            if idx is None:
                raise KeyError(product_id)
            return self.matrix[idx], idx, list(self.df.at[idx, "tokens"])
        tokens = clean_text(text or "")
        if not tokens:
            raise ValueError("The text has no usable words after cleaning.")
        vec = embed_tokens(tokens, self.model)
        norm = np.linalg.norm(vec)
        return (vec / norm if norm else vec), None, tokens

    # ---------- main API ----------
    def recommend(self, product_id=None, text=None, top_n=10, category: Optional[str] = None):
        vec, q_idx, tokens = self._query_vector(product_id, text)
        scores = self.matrix @ vec                       # cosine similarity (unit vectors)
        if q_idx is not None:
            scores[q_idx] = -np.inf                      # never recommend the query itself
        if category:
            scores = np.where(self.df["main_category"].values == category, scores, -np.inf)
        k = min(top_n, int(np.isfinite(scores).sum()))
        top = np.argpartition(-scores, k - 1)[:k] if k else []
        top = sorted((int(i) for i in top), key=lambda i: -scores[i])   # highest -> lowest
        return {
            "query": self.product(q_idx) if q_idx is not None else {"text": text},
            "tokens": self.describe_tokens(tokens),
            "results": [self.product(i, scores[i]) for i in top],
        }

    def describe_tokens(self, tokens):
        vocab = self.model.wv.key_to_index
        return [{"token": t, "in_vocab": t in vocab} for t in tokens]

    def explain(self, product_id=None, text=None, top_n=5, category=None):
        """Dry-run: what the data looks like at each stage of the pipeline."""
        vec, q_idx, tokens = self._query_vector(product_id, text)
        raw = self.df.at[q_idx, "raw_text"] if q_idx is not None else text
        word_vecs = []
        for t in tokens:
            v = self.model.wv[t]
            nb = self.model.wv.similar_by_vector(v, topn=4)
            word_vecs.append({
                "token": t,
                "in_vocab": t in self.model.wv.key_to_index,
                "norm": round(float(np.linalg.norm(v)), 3),
                "neighbours": [w for w, _ in nb if w != t][:3],
            })
        rec = self.recommend(product_id, text, top_n, category)
        return {
            "raw_text": raw,
            "tokens": tokens,
            "word_vectors": word_vecs,
            "product_vector": {
                "dimensions": int(vec.shape[0]),
                "preview": [round(float(x), 4) for x in vec[:8]],
                "unit_norm": round(float(np.linalg.norm(vec)), 4),
            },
            "ranking": [{"product_id": r["product_id"], "name": r["name"],
                         "score": r["similarity_score"]} for r in rec["results"]],
        }

    def stats(self):
        return {
            "products": len(self.df),
            "vocabulary": len(self.model.wv),
            "vector_size": self.model.vector_size,
            "categories": self.categories,
            "model": "FastText skip-gram, char n-grams 3-6",
        }
