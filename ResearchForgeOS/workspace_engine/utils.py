from __future__ import annotations

import hashlib
import re
from collections import Counter
from difflib import SequenceMatcher

STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "because",
    "before",
    "being",
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

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_+#.-]{1,}")
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
ACTION_PATTERN = re.compile(
    r"\b(?:todo|task|action|next|follow up|implement|read|review|fix|write|create|compare|verify)\b",
    re.I,
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_key(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9+#._-]+", "-", value.casefold().strip())
    return re.sub(r"-+", "-", cleaned).strip("-") or "untitled"


def stable_hash(*parts: object) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(str(part).encode("utf-8", errors="ignore"))
        hasher.update(b"\x1f")
    return hasher.hexdigest()


def tokenize(value: str, *, remove_stopwords: bool = True) -> list[str]:
    tokens = [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(value)]
    if not remove_stopwords:
        return tokens
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def sentences(value: str) -> list[str]:
    fragments = [normalize_space(fragment) for fragment in SENTENCE_PATTERN.split(value)]
    return [fragment for fragment in fragments if len(fragment) > 2]


def title_case_phrase(value: str) -> str:
    words = value.replace("_", " ").replace("-", " ").split()
    small = {"a", "an", "and", "as", "for", "in", "of", "on", "or", "the", "to", "with"}
    titled = [word.upper() if word.isupper() else word.capitalize() for word in words]
    return " ".join(
        word.casefold() if index > 0 and word.casefold() in small else word
        for index, word in enumerate(titled)
    )


def top_keywords(value: str, *, limit: int = 12) -> list[str]:
    tokens = tokenize(value)
    counter = Counter(tokens)
    bigrams = Counter(zip(tokens, tokens[1:], strict=False))
    scored: dict[str, float] = {token: float(count) for token, count in counter.items()}
    for (left, right), count in bigrams.items():
        if left != right and count > 1:
            scored[f"{left} {right}"] = count * 1.8
    return [
        keyword
        for keyword, _score in sorted(scored.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def extract_concepts(value: str, *, limit: int = 10) -> list[str]:
    concepts: list[str] = []
    for match in re.finditer(r"\b[A-Z][A-Za-z0-9+#.-]+(?:\s+[A-Z][A-Za-z0-9+#.-]+){0,4}\b", value):
        candidate = match.group(0).strip()
        if candidate.lower() not in STOPWORDS and len(candidate) > 2:
            concepts.append(title_case_phrase(candidate))
    concepts.extend(title_case_phrase(keyword) for keyword in top_keywords(value, limit=limit))
    return dedupe(concepts)[:limit]


def summarize(value: str, *, title: str, keywords: list[str], max_sentences: int = 3) -> str:
    candidates = sentences(value)
    if not candidates:
        return f"{title} captures a knowledge fragment that can be linked into the workspace."
    keyword_set = set(tokenize(" ".join(keywords)))
    ranked = sorted(
        enumerate(candidates),
        key=lambda item: (
            -sum(1 for token in tokenize(item[1]) if token in keyword_set),
            item[0],
        ),
    )
    selected_indexes = sorted(index for index, _sentence in ranked[:max_sentences])
    return " ".join(candidates[index] for index in selected_indexes).strip()


def generate_title(value: str, *, fallback: str = "Untitled Note") -> str:
    for sentence in sentences(value):
        tokens = tokenize(sentence, remove_stopwords=False)
        if 3 <= len(tokens) <= 16:
            return sentence.strip("# -:")[:140]
    keywords = top_keywords(value, limit=5)
    if keywords:
        return title_case_phrase(" ".join(keywords[:4]))[:140]
    return fallback


def action_items(value: str, *, limit: int = 8) -> list[str]:
    items: list[str] = []
    for sentence in sentences(value):
        if ACTION_PATTERN.search(sentence):
            items.append(sentence.strip("-* "))
    return dedupe(items)[:limit]


def infer_category(value: str, explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()[:120]
    lower = value.casefold()
    if any(marker in lower for marker in ("experiment", "paper", "hypothesis", "methodology", "citation")):
        return "Research"
    if any(marker in lower for marker in ("bug", "api", "implementation", "code", "deploy", "database")):
        return "Engineering"
    if any(marker in lower for marker in ("learn", "revision", "exam", "interview", "roadmap")):
        return "Learning"
    if any(marker in lower for marker in ("meeting", "decision", "stakeholder", "milestone")):
        return "Project"
    return "Knowledge"


def infer_tags(value: str, keywords: list[str], concepts: list[str], *, explicit: list[str] | None = None) -> list[str]:
    tags = [normalize_key(tag).replace("-", "_") for tag in explicit or [] if tag.strip()]
    tags.extend(normalize_key(keyword).replace("-", "_") for keyword in keywords[:8])
    tags.extend(normalize_key(concept).replace("-", "_") for concept in concepts[:4])
    return [tag[:48] for tag in dedupe(tags) if tag][:12]


def fuzzy_similarity(left: str, right: str) -> float:
    return round(SequenceMatcher(None, left.casefold(), right.casefold()).ratio(), 4)


def token_overlap(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return round(len(left_tokens & right_tokens) / max(len(left_tokens), len(right_tokens)), 4)


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = normalize_key(value)
        if normalized and normalized not in seen:
            output.append(value.strip())
            seen.add(normalized)
    return output


def markdown_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item.strip()}" for item in items if item.strip())
