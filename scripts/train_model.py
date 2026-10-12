"""Force a re-train:  python -m scripts.train_model"""
import logging

from app.services.catalog import load_catalog
from app.services.embedding import (MATRIX_PATH, SIZE_PATH, build_matrix, train_fasttext)
import numpy as np

logging.basicConfig(level=logging.INFO)
df = load_catalog()
model = train_fasttext(df["tokens"].tolist())
np.save(MATRIX_PATH, build_matrix(df["tokens"].tolist(), model))
SIZE_PATH.write_text(str(len(df)))
print("Done. Vocabulary:", len(model.wv), "| Products:", len(df))
