import re
from collections.abc import Iterable

from knowledge_engine.utils import clamp_score, dedupe_preserve_order


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", ":", value.lower()).strip(":")


def score_from_signals(*signals: float, base: float = 0.0) -> float:
    return clamp_score(base + sum(signals))


def top_unique(values: Iterable[str], limit: int) -> list[str]:
    return dedupe_preserve_order(values)[:limit]


def similarity(left: Iterable[str], right: Iterable[str]) -> tuple[float, list[str]]:
    left_set = {value.lower() for value in left if value}
    right_set = {value.lower() for value in right if value}
    if not left_set or not right_set:
        return 0.0, []
    shared = sorted(left_set & right_set)
    union = left_set | right_set
    return clamp_score(len(shared) / max(1, len(union))), shared
