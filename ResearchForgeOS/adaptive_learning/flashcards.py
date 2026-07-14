from __future__ import annotations

from adaptive_learning.types import CardDifficulty, CardType, FlashcardDraft, LearningSource
from adaptive_learning.utils import dedupe, excerpt_for, first_sentence_for


class FlashcardEngine:
    def generate(self, source: LearningSource, *, limit: int = 48) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        cards.extend(self._definition_cards(source))
        cards.extend(self._concept_cards(source))
        cards.extend(self._formula_cards(source))
        cards.extend(self._algorithm_cards(source))
        cards.extend(self._code_cards(source))
        cards.extend(self._interview_cards(source))
        cards.extend(self._true_false_cards(source))
        cards.extend(self._fill_blank_cards(source))
        cards.extend(self._reverse_cards(source))
        cards.extend(self._image_placeholder_cards(source))
        unique: dict[tuple[str, str], FlashcardDraft] = {}
        for card in cards:
            unique.setdefault((card.card_type.value, card.front.casefold()), card)
        return list(unique.values())[:limit]

    def _definition_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        for definition in source.definitions[:10]:
            term = definition.get("term") or definition.get("name") or definition.get("title")
            meaning = definition.get("definition") or definition.get("description") or definition.get("value")
            if not term or not meaning:
                continue
            cards.append(
                FlashcardDraft(
                    card_type=CardType.DEFINITION,
                    difficulty=CardDifficulty.EASY,
                    front=f"What is {term}?",
                    back=meaning,
                    explanation=f"{term} is a definition extracted from {source.title}.",
                    tags=dedupe([source.category, *source.topics[:3], str(term)]),
                    source_excerpt=excerpt_for(str(term), source.cleaned_text, fallback=str(meaning)),
                    metadata={"document_id": source.document_id, "term": term},
                )
            )
        return cards

    def _concept_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        return [
            FlashcardDraft(
                card_type=CardType.CONCEPT,
                difficulty=concept.difficulty,
                front=f"Explain the concept of {concept.name}.",
                back=concept.description,
                explanation=f"{concept.name} is one of the core learning concepts in {source.title}.",
                tags=dedupe([source.category, *concept.keywords, concept.name]),
                source_excerpt=concept.source_excerpt or first_sentence_for(concept.name, source.cleaned_text),
                metadata={"document_id": source.document_id, "concept": concept.name},
            )
            for concept in source.concepts[:16]
        ]

    def _formula_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        for equation in source.equations[:8]:
            expression = equation.get("equation") or equation.get("expression") or equation.get("value")
            label = equation.get("name") or equation.get("label") or "formula"
            if not expression:
                continue
            cards.append(
                FlashcardDraft(
                    card_type=CardType.FORMULA,
                    difficulty=CardDifficulty.HARD,
                    front=f"Write and explain the {label} formula.",
                    back=str(expression),
                    explanation=f"The formula appears in {source.title} and should be remembered with its context.",
                    tags=dedupe([source.category, "formula", str(label)]),
                    source_excerpt=excerpt_for(str(expression), source.cleaned_text, fallback=str(expression)),
                    metadata={"document_id": source.document_id, "label": label},
                )
            )
        return cards

    def _algorithm_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        for algorithm in source.algorithms[:10]:
            name = algorithm.get("name") or algorithm.get("algorithm") or "Algorithm"
            description = (
                algorithm.get("description")
                or algorithm.get("steps")
                or first_sentence_for(str(name), source.cleaned_text)
            )
            cards.append(
                FlashcardDraft(
                    card_type=CardType.ALGORITHM,
                    difficulty=CardDifficulty.HARD,
                    front=f"What are the key steps of {name}?",
                    back=str(description),
                    explanation=f"{name} is an algorithmic element extracted from {source.title}.",
                    tags=dedupe([source.category, "algorithm", str(name)]),
                    source_excerpt=excerpt_for(str(name), source.cleaned_text, fallback=str(description)),
                    metadata={"document_id": source.document_id, "algorithm": name},
                )
            )
        return cards

    def _code_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        for snippet in source.code_snippets[:8]:
            language = snippet.get("language") or "code"
            code = snippet.get("code") or snippet.get("content") or ""
            if not code:
                continue
            cards.append(
                FlashcardDraft(
                    card_type=CardType.CODE,
                    difficulty=CardDifficulty.MEDIUM,
                    front=f"What does this {language} snippet do?",
                    back=str(code)[:1200],
                    explanation="Review the snippet by identifying inputs, outputs, and edge cases.",
                    tags=dedupe([source.category, "code", str(language), *source.technologies[:4]]),
                    source_excerpt=str(code)[:500],
                    metadata={"document_id": source.document_id, "language": language},
                )
            )
        return cards

    def _interview_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        return [
            FlashcardDraft(
                card_type=CardType.INTERVIEW,
                difficulty=CardDifficulty.MEDIUM,
                front=f"How would you explain {concept.name} in an interview?",
                back=f"Start with the intuition, define the mechanism, then connect it to {source.title}.",
                explanation=concept.description,
                tags=dedupe([source.category, "interview", concept.name]),
                source_excerpt=concept.source_excerpt,
                metadata={"document_id": source.document_id, "concept": concept.name},
            )
            for concept in source.concepts[:8]
        ]

    def _true_false_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        return [
            FlashcardDraft(
                card_type=CardType.TRUE_FALSE,
                difficulty=CardDifficulty.EASY,
                front=f"True or false: {concept.name} is important for understanding {source.title}.",
                back="True",
                explanation=concept.description,
                tags=dedupe([source.category, "true_false", concept.name]),
                source_excerpt=concept.source_excerpt,
                metadata={"document_id": source.document_id, "concept": concept.name},
            )
            for concept in source.concepts[:6]
        ]

    def _fill_blank_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        cards: list[FlashcardDraft] = []
        for concept in source.concepts[:8]:
            sentence = first_sentence_for(concept.name, source.cleaned_text)
            if not sentence:
                continue
            front = sentence.replace(concept.name, "____", 1)
            if front == sentence:
                front = f"____ is a key concept in {source.title}."
            cards.append(
                FlashcardDraft(
                    card_type=CardType.FILL_BLANK,
                    difficulty=concept.difficulty,
                    front=front,
                    back=concept.name,
                    explanation=concept.description,
                    tags=dedupe([source.category, "fill_blank", concept.name]),
                    source_excerpt=sentence,
                    metadata={"document_id": source.document_id, "concept": concept.name},
                )
            )
        return cards

    def _reverse_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        return [
            FlashcardDraft(
                card_type=CardType.REVERSE,
                difficulty=concept.difficulty,
                front=concept.description[:260],
                back=concept.name,
                explanation=f"Reverse recall strengthens recognition of {concept.name}.",
                tags=dedupe([source.category, "reverse", concept.name]),
                source_excerpt=concept.source_excerpt,
                metadata={"document_id": source.document_id, "concept": concept.name},
            )
            for concept in source.concepts[:8]
            if concept.description
        ]

    def _image_placeholder_cards(self, source: LearningSource) -> list[FlashcardDraft]:
        if not source.concepts:
            return []
        concept = source.concepts[0]
        return [
            FlashcardDraft(
                card_type=CardType.IMAGE_PLACEHOLDER,
                difficulty=CardDifficulty.MEDIUM,
                front=f"Draw a diagram that explains {concept.name}.",
                back=f"The diagram should show {concept.name}, prerequisites, inputs, outputs, and related concepts.",
                explanation="This card reserves space for future visual learning assets.",
                tags=dedupe([source.category, "diagram", concept.name]),
                source_excerpt=concept.source_excerpt,
                metadata={"document_id": source.document_id, "concept": concept.name},
            )
        ]
