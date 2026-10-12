"""Central configuration. Every path can be overridden with an environment variable."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = Path(os.getenv("ACME_DATA_PATH", BASE_DIR / "data" / "AcmeRetail_Products_70000.csv"))
ARTIFACT_DIR = Path(os.getenv("ACME_ARTIFACT_DIR", BASE_DIR / "artifacts"))
STATIC_DIR = BASE_DIR / "static"

# Text columns combined into one string per product (missing ones are skipped).
TEXT_COLUMNS = ["name", "main_category", "sub_category"]

# FastText hyper-parameters: same as the notebook, except `bucket`, which is reduced from
# gensim's 2,000,000 default so the saved model is ~80 MB instead of ~1.6 GB.
FASTTEXT_PARAMS = dict(
    vector_size=200,
    window=5,
    min_count=2,
    sg=1,
    epochs=10,
    min_n=3,
    max_n=6,
    bucket=100_000,
    workers=int(os.getenv("ACME_WORKERS", os.cpu_count() or 4)),
    seed=42,
)

DEFAULT_TOP_N = 10
MAX_TOP_N = 50
