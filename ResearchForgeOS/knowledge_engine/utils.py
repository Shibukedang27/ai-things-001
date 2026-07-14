from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_+-]{1,}")


def content_hash(content: str | bytes) -> str:
    payload = content.encode("utf-8", errors="ignore") if isinstance(content, str) else content
    return hashlib.sha256(payload).hexdigest()


def normalize_space(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def sentences(text: str) -> list[str]:
    normalized = normalize_space(text.replace("\n", " "))
    if not normalized:
        return []
    parts = SENTENCE_PATTERN.split(normalized)
    return [part.strip() for part in parts if len(part.strip()) > 20]


def words(text: str) -> list[str]:
    return WORD_PATTERN.findall(text)


def clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def title_case_phrase(value: str) -> str:
    words_to_keep_upper = {"AI", "API", "GPU", "CPU", "SQL", "HTTP", "RAG", "PDF", "JWT", "NLP", "ML"}
    parts = []
    for word in value.split():
        upper = word.upper()
        if upper in words_to_keep_upper:
            parts.append(upper)
        else:
            parts.append(word[:1].upper() + word[1:].lower())
    return " ".join(parts)
