from typing import Any

from ai.agents.core.types import AgentDNA, AgentDocument


def first_items(values: list[str], limit: int = 5) -> list[str]:
    return [value for value in values if value][:limit]


def concept_names(document: AgentDocument, limit: int = 10) -> list[str]:
    return [str(concept.get("name")) for concept in document.concepts if concept.get("name")][:limit]


def technology_names(document: AgentDocument, limit: int = 10) -> list[str]:
    return [str(technology.get("name")) for technology in document.technologies if technology.get("name")][:limit]


def source_refs(document: AgentDocument) -> list[str]:
    refs: list[str] = []
    for reference in document.references[:8]:
        value = reference.get("title") or reference.get("citation_text") or reference.get("url")
        if value:
            refs.append(str(value))
    return refs or [document.title]


def dna_or_empty(dna: AgentDNA | None) -> AgentDNA:
    if dna is not None:
        return dna
    return AgentDNA(
        id=None,
        research_category=None,
        knowledge_score=None,
        interview_importance=None,
        industry_relevance=None,
        implementation_complexity=None,
        primary_concepts=[],
        secondary_concepts=[],
        prerequisites=[],
        future_learning_topics=[],
        learning_order=[],
        estimated_mastery_time_hours=None,
        parent_topics=[],
        child_topics=[],
        sibling_topics=[],
        knowledge_chains=[],
        research_evolution=[],
    )


def summary_by_type(document: AgentDocument, summary_type: str, fallback: str = "") -> str:
    return document.summaries.get(summary_type) or fallback or document.cleaned_text[:500]


def compact_dict(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value not in (None, [], {}, "")}
