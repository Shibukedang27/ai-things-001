from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from typing import Any

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_+#.-]{1,}")
CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_query(query: str, *, max_length: int = 4000) -> str:
    cleaned = CONTROL_PATTERN.sub(" ", query)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:max_length]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def tokenize(value: str, *, remove_stopwords: bool = True) -> list[str]:
    tokens = [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(value)]
    if not remove_stopwords:
        return tokens
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def term_frequencies(value: str) -> Counter[str]:
    return Counter(tokenize(value))


def stable_hash(*parts: object) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(str(part).encode("utf-8", errors="ignore"))
        hasher.update(b"\x1f")
    return hasher.hexdigest()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return max(0.0, min(1.0, dot_product / (left_norm * right_norm)))


def clamp(value: float, *, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def sentence_split(value: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", value.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def compress_text(value: str, query_terms: list[str], *, max_characters: int) -> str:
    if len(value) <= max_characters:
        return value.strip()
    sentences = sentence_split(value)
    if not sentences:
        return value[:max_characters].strip()
    normalized_terms = set(query_terms)
    ranked = sorted(
        sentences,
        key=lambda sentence: sum(1 for token in tokenize(sentence) if token in normalized_terms),
        reverse=True,
    )
    selected: list[str] = []
    current_length = 0
    for sentence in ranked:
        projected = current_length + len(sentence) + 1
        if projected > max_characters and selected:
            continue
        selected.append(sentence)
        current_length = projected
        if current_length >= max_characters:
            break
    return " ".join(selected)[:max_characters].strip()


def content_signature(value: str) -> str:
    tokens = tokenize(value)
    return stable_hash(" ".join(tokens[:80]))


def flatten_metadata(value: dict[str, Any]) -> dict[str, str | int | float | bool]:
    flattened: dict[str, str | int | float | bool] = {}
    for key, item in value.items():
        if isinstance(item, str | int | float | bool):
            flattened[key] = item
        elif item is None:
            continue
        else:
            flattened[key] = ", ".join(str(part) for part in item) if isinstance(item, list) else str(item)
    return flattened
