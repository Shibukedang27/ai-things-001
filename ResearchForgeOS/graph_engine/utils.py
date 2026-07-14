from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from typing import Any

from graph_engine.types import GraphNodeType

NODE_COLORS = {
    GraphNodeType.DOCUMENT.value: "#2563eb",
    GraphNodeType.RESEARCH_PAPER.value: "#7c3aed",
    GraphNodeType.BOOK.value: "#a16207",
    GraphNodeType.CONCEPT.value: "#059669",
    GraphNodeType.ALGORITHM.value: "#dc2626",
    GraphNodeType.TECHNOLOGY.value: "#0891b2",
    GraphNodeType.PROGRAMMING_LANGUAGE.value: "#4f46e5",
    GraphNodeType.FRAMEWORK.value: "#9333ea",
    GraphNodeType.LIBRARY.value: "#0d9488",
    GraphNodeType.DATASET.value: "#65a30d",
    GraphNodeType.AUTHOR.value: "#db2777",
    GraphNodeType.COMPANY.value: "#475569",
    GraphNodeType.UNIVERSITY.value: "#b45309",
    GraphNodeType.COURSE.value: "#0284c7",
    GraphNodeType.PROJECT.value: "#16a34a",
    GraphNodeType.INTERVIEW_TOPIC.value: "#ea580c",
    GraphNodeType.TOOL.value: "#64748b",
    GraphNodeType.MODEL.value: "#c026d3",
    GraphNodeType.API.value: "#0369a1",
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_+#.-]{1,}")


def normalize_key(value: str) -> str:
    lowered = value.casefold().strip()
    cleaned = re.sub(r"[^a-z0-9+#._-]+", "-", lowered)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "unknown"


def stable_node_key(node_type: str, name: str, *, document_id: str | None = None) -> str:
    if node_type == GraphNodeType.DOCUMENT.value and document_id:
        return f"document:{document_id}"
    return f"{node_type}:{normalize_key(name)}"


def stable_edge_key(source_key: str, target_key: str, relationship_type: str) -> str:
    return hashlib.sha256(f"{source_key}|{relationship_type}|{target_key}".encode()).hexdigest()


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def node_color(node_type: str) -> str:
    return NODE_COLORS.get(node_type, "#334155")


def node_size(importance_score: float, node_type: str) -> float:
    base = 38.0 if node_type == GraphNodeType.DOCUMENT.value else 24.0
    return round(base + clamp(importance_score) * 24.0, 2)


def tokenize(value: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(value)]


def top_terms(value: str, *, limit: int = 12) -> list[str]:
    stopwords = {"and", "the", "for", "with", "from", "that", "this", "into", "are", "was", "were"}
    counter = Counter(token for token in tokenize(value) if token not in stopwords and len(token) > 2)
    return [term for term, _count in counter.most_common(limit)]


def normalized_similarity(left: str, right: str) -> float:
    left_terms = set(tokenize(left))
    right_terms = set(tokenize(right))
    if not left_terms or not right_terms:
        return 0.0
    return len(left_terms & right_terms) / math.sqrt(len(left_terms) * len(right_terms))


def merge_metadata(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in incoming.items():
        if key not in merged:
            merged[key] = value
            continue
        current = merged[key]
        if isinstance(current, list):
            additions = value if isinstance(value, list) else [value]
            merged[key] = list(dict.fromkeys([*current, *additions]))
        elif current != value:
            merged[key] = list(dict.fromkeys([current, value]))
    return merged
