"""FastText training / loading and product-level embeddings (Phase 3 of the notebook)."""
import logging
from typing import List

import numpy as np
from gensim.models import FastText

from app.config import ARTIFACT_DIR, FASTTEXT_PARAMS

log = logging.getLogger("acme.embedding")
MODEL_PATH = ARTIFACT_DIR / "fasttext.model"
MATRIX_PATH = ARTIFACT_DIR / "product_embeddings.npy"
SIZE_PATH = ARTIFACT_DIR / "catalog_size.txt"


def train_fasttext(sentences: List[List[str]]) -> FastText:
    log.info("Training FastText on %d products (first run only, ~1-3 min) ...", len(sentences))
    model = FastText(sentences=sentences, **FASTTEXT_PARAMS)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_PATH))
    return model


def embed_tokens(tokens: List[str], model: FastText) -> np.ndarray:
    """Mean of word vectors. FastText composes vectors for unseen words from character
    n-grams, so out-of-vocabulary tokens still contribute (key to generalisation)."""
    if not tokens:
        return np.zeros(model.vector_size, dtype=np.float32)
    return np.mean([model.wv[t] for t in tokens], axis=0).astype(np.float32)


def build_matrix(token_lists: List[List[str]], model: FastText) -> np.ndarray:
    """L2-normalised product matrix, so cosine similarity == a plain dot product."""
    matrix = np.vstack([embed_tokens(t, model) for t in token_lists])
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0, 1, norms)


def load_or_build(token_lists: List[List[str]]):
    """Reuse cached artifacts when they match the catalogue size, otherwise (re)train."""
    n = len(token_lists)
    if MODEL_PATH.exists() and MATRIX_PATH.exists() and SIZE_PATH.exists() \
            and SIZE_PATH.read_text().strip() == str(n):
        log.info("Loading cached FastText model + embeddings")
        return FastText.load(str(MODEL_PATH)), np.load(MATRIX_PATH)
    model = train_fasttext(token_lists)
    matrix = build_matrix(token_lists, model)
    np.save(MATRIX_PATH, matrix)
    SIZE_PATH.write_text(str(n))
    return model, matrix
