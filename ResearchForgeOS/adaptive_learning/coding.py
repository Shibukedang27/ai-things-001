from __future__ import annotations

from adaptive_learning.types import CardDifficulty, CodingChallengeDraft, LearningSource
from adaptive_learning.utils import dedupe


class CodingChallengeEngine:
    def generate(self, source: LearningSource) -> list[CodingChallengeDraft]:
        concepts = source.concepts[:4]
        if not concepts and not source.algorithms:
            return [self._generic_challenge(source, CardDifficulty.EASY)]
        challenges: list[CodingChallengeDraft] = []
        for index, concept in enumerate(concepts):
            difficulty = [CardDifficulty.EASY, CardDifficulty.MEDIUM, CardDifficulty.HARD, CardDifficulty.EXPERT][
                min(index, 3)
            ]
            challenges.append(
                CodingChallengeDraft(
                    difficulty=difficulty,
                    title=f"Implement a {concept.name} Practice Tool",
                    prompt=(
                        f"Build a small function or service component that demonstrates {concept.name}. "
                        "The implementation should expose clear inputs, outputs, validation, and edge-case behavior."
                    ),
                    starter_code=self._starter_code(concept.name),
                    hints=[
                        f"Start by defining the inputs and outputs for {concept.name}.",
                        "Add validation before optimizing.",
                        "Write tests for empty, normal, and adversarial inputs.",
                    ],
                    optimal_solution=self._solution_code(concept.name),
                    complexity_analysis=(
                        "Time complexity is O(n) over the input items; "
                        "space complexity is O(k) for tracked signals."
                    ),
                    alternative_solutions=[
                        "Use a class-based implementation when state needs to be retained.",
                        "Use a pure function when the challenge is a single deterministic transform.",
                    ],
                    edge_cases=["empty input", "duplicate concepts", "very long text", "unknown terms"],
                    unit_tests=[
                        {"name": "empty_input", "input": [], "expected": []},
                        {"name": "deduplicates_items", "input": ["A", "A", "B"], "expected": ["A", "B"]},
                    ],
                    tags=dedupe([source.category, concept.name, *source.technologies[:4]]),
                    metadata={"document_id": source.document_id, "concept": concept.name},
                )
            )
        for algorithm in source.algorithms[:2]:
            name = str(algorithm.get("name") or algorithm.get("algorithm") or "Algorithm")
            challenges.append(
                CodingChallengeDraft(
                    difficulty=CardDifficulty.HARD,
                    title=f"Implement {name}",
                    prompt=f"Implement {name}, explain its invariants, and test edge cases.",
                    starter_code=self._starter_code(name),
                    hints=[
                        "Identify the invariant.",
                        "Write brute-force tests first.",
                        "Optimize only after correctness.",
                    ],
                    optimal_solution=self._solution_code(name),
                    complexity_analysis="State the dominant operation and justify time and memory usage.",
                    alternative_solutions=[
                        "Iterative implementation",
                        "Recursive implementation",
                        "Streaming implementation",
                    ],
                    edge_cases=["minimum input", "maximum input", "repeated values", "invalid input"],
                    unit_tests=[{"name": "basic_case", "input": [1, 2, 3], "expected": [1, 2, 3]}],
                    tags=dedupe([source.category, "algorithm", name]),
                    metadata={"document_id": source.document_id, "algorithm": name},
                )
            )
        return challenges[:8]

    def _generic_challenge(self, source: LearningSource, difficulty: CardDifficulty) -> CodingChallengeDraft:
        return CodingChallengeDraft(
            difficulty=difficulty,
            title=f"Build a Study Index for {source.title}",
            prompt="Create a function that receives knowledge items and returns deduplicated study topics.",
            starter_code="def build_study_index(items: list[str]) -> list[str]:\n    return []\n",
            hints=["Normalize whitespace.", "Preserve order.", "Remove duplicates."],
            optimal_solution=(
                "def build_study_index(items: list[str]) -> list[str]:\n"
                "    seen = set()\n"
                "    output = []\n"
                "    for item in items:\n"
                "        key = ' '.join(item.lower().split())\n"
                "        if key and key not in seen:\n"
                "            output.append(item.strip())\n"
                "            seen.add(key)\n"
                "    return output\n"
            ),
            complexity_analysis="O(n) time and O(n) memory.",
            alternative_solutions=["Use dict.fromkeys after normalization."],
            edge_cases=["empty list", "case differences", "extra spaces"],
            unit_tests=[{"name": "dedupe", "input": ["AI", " ai "], "expected": ["AI"]}],
            tags=dedupe([source.category, *source.topics[:4]]),
            metadata={"document_id": source.document_id},
        )

    def _starter_code(self, concept: str) -> str:
        function_name = "_".join(part.lower() for part in concept.split())
        safe_name = "".join(character if character.isalnum() else "_" for character in function_name).strip("_")
        safe_name = safe_name or "solve_challenge"
        return f"def {safe_name}(items: list[str]) -> list[str]:\n    \"\"\"Implement {concept}.\"\"\"\n    return []\n"

    def _solution_code(self, concept: str) -> str:
        return (
            "# One optimal baseline is a deterministic normalize-and-deduplicate pass.\n"
            "def solve(items: list[str]) -> list[str]:\n"
            "    seen = set()\n"
            "    output = []\n"
            "    for item in items:\n"
            "        key = ' '.join(str(item).casefold().split())\n"
            "        if key and key not in seen:\n"
            "            output.append(str(item).strip())\n"
            "            seen.add(key)\n"
            "    return output\n"
        )
