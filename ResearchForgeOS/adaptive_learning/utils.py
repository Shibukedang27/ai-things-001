from __future__ import annotations

import hashlib
import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_+#.-]{1,}")
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "between",
    "could",
    "during",
    "from",
    "have",
    "into",
    "more",
    "most",
    "other",
    "should",
    "than",
    "that",
    "their",
    "there",
    "these",
    "this",
    "those",
    "through",
    "under",
    "using",
    "were",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def stable_hash(*parts: object) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(str(part).encode("utf-8", errors="ignore"))
        hasher.update(b"\x1f")
    return hasher.hexdigest()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def tokenize(value: str, *, remove_stopwords: bool = True) -> list[str]:
    tokens = [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(value)]
    if not remove_stopwords:
        return tokens
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def sentences(value: str) -> list[str]:
    return [normalize_space(fragment) for fragment in SENTENCE_PATTERN.split(value) if normalize_space(fragment)]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def title_case(value: str) -> str:
    small = {"a", "an", "and", "as", "for", "in", "of", "on", "or", "the", "to", "with"}
    words = value.replace("_", " ").replace("-", " ").split()
    output: list[str] = []
    for index, word in enumerate(words):
        candidate = word.upper() if word.isupper() else word.capitalize()
        output.append(candidate.casefold() if index > 0 and candidate.casefold() in small else candidate)
    return " ".join(output)


def top_terms(value: str, *, limit: int = 12) -> list[str]:
    counter = Counter(tokenize(value))
    return [term for term, _count in counter.most_common(limit)]


def excerpt_for(term: str, text: str, *, fallback: str = "", radius: int = 180) -> str:
    pattern = re.compile(re.escape(term), re.I)
    match = pattern.search(text)
    if match is None:
        return fallback[: radius * 2].strip()
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    return normalize_space(text[start:end])


def first_sentence_for(term: str, text: str) -> str:
    lower_term = term.casefold()
    for sentence in sentences(text):
        if lower_term in sentence.casefold():
            return sentence[:420]
    return sentences(text)[0][:420] if sentences(text) else ""


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        key = normalize_space(value).casefold()
        if key and key not in seen:
            output.append(value.strip())
            seen.add(key)
    return output
