import re


class DefinitionExtractor:
    PATTERNS = (
        re.compile(r"\b([A-Z][A-Za-z0-9 -]{2,80})\s+is\s+([^.\n]{20,280})", re.I),
        re.compile(r"\b([A-Z][A-Za-z0-9 -]{2,80})\s+refers to\s+([^.\n]{20,280})", re.I),
        re.compile(r"\b([A-Z][A-Za-z0-9 -]{2,80})\s+means\s+([^.\n]{20,280})", re.I),
    )

    def extract(self, text: str) -> list[dict[str, str]]:
        definitions: list[dict[str, str]] = []
        for pattern in self.PATTERNS:
            for match in pattern.finditer(text):
                term = match.group(1).strip(" :;,.")
                definition = match.group(2).strip(" :;,.")
                if 2 <= len(term.split()) <= 8:
                    definitions.append({"term": term[:120], "definition": definition[:360]})
        return self._dedupe(definitions)[:30]

    def _dedupe(self, definitions: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for definition in definitions:
            key = definition["term"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(definition)
        return unique


class AlgorithmExtractor:
    PATTERN = re.compile(
        r"\b([A-Z][A-Za-z0-9 -]*(?:Algorithm|Search|Sort|Descent|Propagation|Regression|Transformer|Network))\b"
    )

    def extract(self, text: str) -> list[dict[str, str]]:
        algorithms: list[dict[str, str]] = []
        for match in self.PATTERN.finditer(text):
            name = match.group(1).strip()
            context = text[max(0, match.start() - 160) : min(len(text), match.end() + 240)].replace("\n", " ").strip()
            algorithms.append({"name": name[:120], "description": context[:420]})
        return self._dedupe(algorithms)[:25]

    def _dedupe(self, algorithms: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for algorithm in algorithms:
            key = algorithm["name"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(algorithm)
        return unique


class EquationExtractor:
    BLOCK_PATTERN = re.compile(r"\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]")
    INLINE_PATTERN = re.compile(r"(?<!\w)([A-Za-z][A-Za-z0-9_]*\s*=\s*[^.\n]{3,160})")

    def extract(self, text: str) -> list[dict[str, str]]:
        equations: list[dict[str, str]] = []
        for match in self.BLOCK_PATTERN.finditer(text):
            expression = (match.group(1) or match.group(2) or "").strip()
            if expression:
                equations.append({"expression": expression[:500], "format": "latex_block"})
        for match in self.INLINE_PATTERN.finditer(text):
            expression = match.group(1).strip(" ;,")
            if any(symbol in expression for symbol in ("+", "-", "*", "/", "^", "Σ", "∑", "sqrt", "log")):
                equations.append({"expression": expression[:300], "format": "inline"})
        return self._dedupe(equations)[:25]

    def _dedupe(self, equations: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for equation in equations:
            key = equation["expression"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(equation)
        return unique
