"""Catalogue loading. Works with any CSV that has at least one of the configured text columns."""
import logging
from typing import List

import pandas as pd

from app.config import DATA_PATH, TEXT_COLUMNS
from app.services.preprocessing import clean_text

log = logging.getLogger("acme.catalog")


def _price(value):
    if pd.isna(value):
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
    return float(digits) if digits else None


def load_catalog(path=DATA_PATH, text_columns: List[str] = TEXT_COLUMNS) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], errors="ignore")

    cols = [c for c in text_columns if c in df.columns]
    if not cols:
        raise ValueError(f"None of the text columns {text_columns} found in {path}")
    for c in cols:
        df[c] = df[c].fillna("").astype(str)

    df["raw_text"] = df[cols].agg(" ".join, axis=1)
    df["tokens"] = df["raw_text"].apply(clean_text)
    df = df[df["tokens"].map(len) > 0].reset_index(drop=True)  # drop products with no usable text

    df.insert(0, "product_id", ["ACME_" + str(i).zfill(6) for i in range(1, len(df) + 1)])
    df["clean_text"] = df["tokens"].str.join(" ")

    for c in ("discount_price", "actual_price"):
        if c in df.columns:
            df[c] = df[c].apply(_price)
    for c in ("ratings", "no_of_ratings"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ""), errors="coerce")

    log.info("Catalogue loaded: %d products", len(df))
    return df
