"""Text cleaning + tokenisation (mirrors Phase 1 of the notebook)."""
import re
from typing import List

try:
    import nltk
    from nltk.corpus import stopwords

    try:
        STOP_WORDS = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        STOP_WORDS = set(stopwords.words("english"))
except Exception:  # offline fallback so the app never fails to start
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "of", "for", "with", "in", "on", "to", "from", "by",
        "is", "are", "was", "be", "it", "this", "that", "as", "at", "its", "your", "you",
        "me", "my", "we", "our", "they", "their", "not", "no", "so", "than", "too", "very",
    }

_URL = re.compile(r"https?://\S+|www\.\S+")
_HTML = re.compile(r"<.*?>")
_NON_ALPHA = re.compile(r"[^a-z\s]")
_SPACES = re.compile(r"\s+")


def clean_text(text: str) -> List[str]:
    """lower-case -> strip URLs/HTML/non-letters -> tokenise -> drop stop-words & 1-letter tokens."""
    text = str(text or "").lower()
    text = _URL.sub(" ", text)
    text = _HTML.sub(" ", text)
    text = _NON_ALPHA.sub(" ", text)
    text = _SPACES.sub(" ", text).strip()
    # Only [a-z ] remain here, so whitespace split is equivalent to NLTK word_tokenize.
    return [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]
