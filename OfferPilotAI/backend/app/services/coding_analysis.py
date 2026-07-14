"""Live coding static analysis and optimization providers."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re

from app.domain.enums import CodingLanguage
from app.schemas.coding import CodeAnalysisResult, CodeIssue


@dataclass(frozen=True)
class CodeAnalysisInput:
    """Analyzer input."""

    language: CodingLanguage
    source_code: str
    prompt: str | None = None


class CodeAnalysisProvider:
    """Code analysis provider interface."""

    analyzer_version = "provider-interface"

    async def analyze(self, payload: CodeAnalysisInput) -> CodeAnalysisResult:
        raise NotImplementedError


class HeuristicCodeAnalysisProvider(CodeAnalysisProvider):
    """Deterministic code analyzer until external AI review is configured."""

    analyzer_version = "heuristic-code-analyzer-v1"

    async def analyze(self, payload: CodeAnalysisInput) -> CodeAnalysisResult:
        bugs = self._bugs(payload)
        time_complexity = self._time_complexity(payload)
        space_complexity = self._space_complexity(payload)
        suggestions = self._suggestions(payload=payload, bugs=bugs, time_complexity=time_complexity)
        quality_score = self._quality_score(bugs=bugs, time_complexity=time_complexity, source_code=payload.source_code)

        return CodeAnalysisResult(
            language=payload.language,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            bugs=bugs,
            optimized_code=self._optimized_code(payload, suggestions),
            improvement_explanation=self._improvement_explanation(payload, suggestions),
            improvement_suggestions=suggestions,
            quality_score=quality_score,
            observations=self._observations(payload),
            analyzer_version=self.analyzer_version,
        )

    def _time_complexity(self, payload: CodeAnalysisInput) -> str:
        if payload.language == CodingLanguage.SQL:
            return self._sql_time_complexity(payload.source_code)

        source = payload.source_code
        loop_count = len(re.findall(r"\b(for|while)\b", source))
        sort_hits = len(re.findall(r"\b(sort|sorted|Collections\.sort|Arrays\.sort|ORDER BY)\b", source, re.IGNORECASE))
        recursion = self._has_recursion(payload)
        max_loop_nesting = self._python_loop_nesting(source) if payload.language == CodingLanguage.PYTHON else self._brace_loop_nesting(source)

        if recursion and sort_hits:
            return "O(n log n)"
        if recursion and max_loop_nesting >= 1:
            return "O(n log n)"
        if recursion:
            return "O(n)"
        if max_loop_nesting >= 3:
            return "O(n^3)"
        if max_loop_nesting == 2:
            return "O(n^2)"
        if sort_hits:
            return "O(n log n)"
        if loop_count:
            return "O(n)"
        return "O(1)"

    def _space_complexity(self, payload: CodeAnalysisInput) -> str:
        source = payload.source_code
        has_dynamic_container = bool(
            re.search(
                r"\b(list|dict|set|HashMap|HashSet|ArrayList|new\s+int\s*\[|new\s+String\s*\[|CREATE\s+TEMP)\b",
                source,
                re.IGNORECASE,
            )
            or re.search(r"=\s*(\[\]|\{\}|set\()", source)
            or re.search(r"\.(append|extend|add|put)\s*\(", source)
            or re.search(r"\[[^\]]+\s+for\s+", source)
        )
        if payload.language == CodingLanguage.SQL:
            if re.search(r"\b(GROUP BY|ORDER BY|DISTINCT)\b", source, re.IGNORECASE):
                return "O(n)"
            return "O(1)"
        if self._has_recursion(payload) or has_dynamic_container:
            return "O(n)"
        return "O(1)"

    def _bugs(self, payload: CodeAnalysisInput) -> list[CodeIssue]:
        if payload.language == CodingLanguage.PYTHON:
            return self._python_bugs(payload.source_code)
        if payload.language == CodingLanguage.JAVA:
            return self._java_bugs(payload.source_code)
        if payload.language == CodingLanguage.SQL:
            return self._sql_bugs(payload.source_code)
        return []

    def _python_bugs(self, source_code: str) -> list[CodeIssue]:
        issues: list[CodeIssue] = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            return [
                CodeIssue(
                    severity="error",
                    message=exc.msg,
                    line=exc.lineno,
                    rule="python.syntax",
                )
            ]

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(
                    CodeIssue(
                        severity="warning",
                        message="Bare except can hide real runtime failures.",
                        line=node.lineno,
                        rule="python.bare_except",
                    )
                )
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            CodeIssue(
                                severity="warning",
                                message="Mutable default arguments are shared across calls.",
                                line=node.lineno,
                                rule="python.mutable_default",
                            )
                        )
            if isinstance(node, ast.Compare):
                for operator in node.ops:
                    if isinstance(operator, (ast.Is, ast.IsNot)):
                        continue
                    if any(isinstance(comparator, ast.Constant) and comparator.value is None for comparator in node.comparators):
                        issues.append(
                            CodeIssue(
                                severity="info",
                                message="Use `is None` or `is not None` for None comparisons.",
                                line=getattr(node, "lineno", None),
                                rule="python.none_comparison",
                            )
                        )
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    issues.append(
                        CodeIssue(
                            severity="error",
                            message="Division by zero will fail at runtime.",
                            line=getattr(node, "lineno", None),
                            rule="python.division_by_zero",
                        )
                    )

        if re.search(r"range\s*\(\s*len\s*\(", source_code):
            issues.append(
                CodeIssue(
                    severity="info",
                    message="Iterating directly over values or enumerate is usually clearer than range(len(...)).",
                    line=None,
                    rule="python.range_len",
                )
            )
        if re.search(r"while\s+True\s*:", source_code) and "break" not in source_code:
            issues.append(
                CodeIssue(
                    severity="warning",
                    message="Unbounded loop does not contain an obvious break statement.",
                    line=None,
                    rule="python.unbounded_loop",
                )
            )
        return issues

    def _java_bugs(self, source_code: str) -> list[CodeIssue]:
        issues: list[CodeIssue] = []
        if "class Main" not in source_code:
            issues.append(
                CodeIssue(
                    severity="error",
                    message="Runnable Java submissions need a Main class.",
                    line=None,
                    rule="java.main_class",
                )
            )
        if re.search(r"\bString\s+\w+.*==", source_code) or re.search(r"==\s*\"[^\"]*\"", source_code):
            issues.append(
                CodeIssue(
                    severity="warning",
                    message="Use `.equals(...)` for Java String value comparison.",
                    line=None,
                    rule="java.string_equals",
                )
            )
        if source_code.count("{") != source_code.count("}"):
            issues.append(
                CodeIssue(
                    severity="error",
                    message="Brace count is unbalanced.",
                    line=None,
                    rule="java.unbalanced_braces",
                )
            )
        if "Scanner" in source_code and ".close()" not in source_code:
            issues.append(
                CodeIssue(
                    severity="info",
                    message="Close Scanner or use try-with-resources in production code.",
                    line=None,
                    rule="java.resource_cleanup",
                )
            )
        return issues

    def _sql_bugs(self, source_code: str) -> list[CodeIssue]:
        lowered = source_code.lower()
        issues: list[CodeIssue] = []
        if "select *" in lowered:
            issues.append(
                CodeIssue(
                    severity="info",
                    message="Select explicit columns to reduce coupling and transferred data.",
                    line=None,
                    rule="sql.select_star",
                )
            )
        if re.search(r"\b(update|delete)\b(?![\s\S]*\bwhere\b)", lowered):
            issues.append(
                CodeIssue(
                    severity="warning",
                    message="UPDATE or DELETE without WHERE can affect every row.",
                    line=None,
                    rule="sql.missing_where",
                )
            )
        if re.search(r"\bfrom\s+\w+\s*,\s*\w+", lowered):
            issues.append(
                CodeIssue(
                    severity="warning",
                    message="Comma joins can create accidental Cartesian products; prefer explicit JOIN syntax.",
                    line=None,
                    rule="sql.implicit_join",
                )
            )
        if "join" in lowered and " on " not in lowered:
            issues.append(
                CodeIssue(
                    severity="warning",
                    message="JOIN without an ON clause may create unintended row multiplication.",
                    line=None,
                    rule="sql.join_without_on",
                )
            )
        return issues

    def _suggestions(
        self,
        *,
        payload: CodeAnalysisInput,
        bugs: list[CodeIssue],
        time_complexity: str,
    ) -> list[str]:
        suggestions: list[str] = []
        if time_complexity in {"O(n^2)", "O(n^3)"}:
            suggestions.append("Look for a hash map, set, sorting, or two-pointer strategy to reduce nested scans.")
        if any(issue.severity == "error" for issue in bugs):
            suggestions.append("Fix blocking correctness issues before optimizing style or runtime.")
        if any(issue.severity == "warning" for issue in bugs):
            suggestions.append("Address warning-level issues to avoid hidden edge-case failures.")
        if payload.language == CodingLanguage.SQL:
            suggestions.append("Check indexes on JOIN, WHERE, GROUP BY, and ORDER BY columns.")
        if payload.language == CodingLanguage.PYTHON and "range(len(" in payload.source_code:
            suggestions.append("Use enumerate or direct iteration for clearer Python loops.")
        if not suggestions:
            suggestions.append("Add edge-case tests and document key assumptions.")
        return suggestions

    def _optimized_code(self, payload: CodeAnalysisInput, suggestions: list[str]) -> str:
        source = payload.source_code.rstrip()
        if payload.language == CodingLanguage.PYTHON and self._looks_like_two_sum(source):
            return (
                "def two_sum(nums, target):\n"
                "    seen = {}\n"
                "    for index, value in enumerate(nums):\n"
                "        complement = target - value\n"
                "        if complement in seen:\n"
                "            return [seen[complement], index]\n"
                "        seen[value] = index\n"
                "    return []\n"
            )
        if payload.language == CodingLanguage.JAVA and self._looks_like_two_sum(source):
            return (
                "import java.util.*;\n\n"
                "class Main {\n"
                "    static int[] twoSum(int[] nums, int target) {\n"
                "        Map<Integer, Integer> seen = new HashMap<>();\n"
                "        for (int i = 0; i < nums.length; i++) {\n"
                "            int complement = target - nums[i];\n"
                "            if (seen.containsKey(complement)) {\n"
                "                return new int[] { seen.get(complement), i };\n"
                "            }\n"
                "            seen.put(nums[i], i);\n"
                "        }\n"
                "        return new int[0];\n"
                "    }\n"
                "}\n"
            )
        comment = self._comment_prefix(payload.language)
        notes = "\n".join(f"{comment} {suggestion}" for suggestion in suggestions)
        return f"{notes}\n{source}\n"

    def _improvement_explanation(self, payload: CodeAnalysisInput, suggestions: list[str]) -> str:
        language_label = payload.language.value.upper()
        return (
            f"The {language_label} review prioritizes correctness first, then asymptotic efficiency and readability. "
            f"{' '.join(suggestions)}"
        )

    def _observations(self, payload: CodeAnalysisInput) -> list[str]:
        observations = [
            f"Source length: {len(payload.source_code)} characters.",
            f"Detected language: {payload.language.value}.",
        ]
        if payload.prompt:
            observations.append("Prompt context was included in the analysis.")
        return observations

    def _quality_score(self, *, bugs: list[CodeIssue], time_complexity: str, source_code: str) -> Decimal:
        score = Decimal("92.00")
        penalties = {"error": Decimal("22.00"), "warning": Decimal("10.00"), "info": Decimal("3.00")}
        for bug in bugs:
            score -= penalties[bug.severity]
        if time_complexity == "O(n^3)":
            score -= Decimal("18.00")
        elif time_complexity == "O(n^2)":
            score -= Decimal("10.00")
        if len(source_code.strip()) < 40:
            score -= Decimal("8.00")
        bounded = max(Decimal("0"), min(Decimal("100"), score))
        return bounded.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _sql_time_complexity(self, source_code: str) -> str:
        lowered = source_code.lower()
        join_count = len(re.findall(r"\bjoin\b", lowered))
        if "order by" in lowered or "group by" in lowered or "distinct" in lowered:
            return "O(n log n)"
        if join_count >= 2:
            return "O(n*m*k)"
        if join_count == 1:
            return "O(n*m)"
        if "where" in lowered:
            return "O(log n) with an index, O(n) without one"
        return "O(n)"

    def _has_recursion(self, payload: CodeAnalysisInput) -> bool:
        if payload.language == CodingLanguage.PYTHON:
            try:
                tree = ast.parse(payload.source_code)
            except SyntaxError:
                return False
            function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in function_names:
                    return True
            return False
        method_names = set(re.findall(r"\b(?:static\s+)?(?:int|long|double|boolean|String|void)\s+(\w+)\s*\(", payload.source_code))
        for name in method_names:
            if len(re.findall(rf"\b{name}\s*\(", payload.source_code)) > 1:
                return True
        return False

    def _python_loop_nesting(self, source_code: str) -> int:
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return 0

        class LoopVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.current = 0
                self.maximum = 0

            def visit_For(self, node: ast.For) -> None:
                self._visit_loop(node)

            def visit_While(self, node: ast.While) -> None:
                self._visit_loop(node)

            def _visit_loop(self, node: ast.stmt) -> None:
                self.current += 1
                self.maximum = max(self.maximum, self.current)
                self.generic_visit(node)
                self.current -= 1

        visitor = LoopVisitor()
        visitor.visit(tree)
        return visitor.maximum

    def _brace_loop_nesting(self, source_code: str) -> int:
        current = 0
        maximum = 0
        pending_loop = False
        for line in source_code.splitlines():
            stripped = line.strip()
            if re.search(r"\b(for|while)\s*\(", stripped):
                pending_loop = True
            if pending_loop and "{" in stripped:
                current += 1
                maximum = max(maximum, current)
                pending_loop = False
            if "}" in stripped and current:
                current = max(0, current - stripped.count("}"))
        return maximum

    def _looks_like_two_sum(self, source_code: str) -> bool:
        lowered = source_code.lower()
        return "target" in lowered and ("nums" in lowered or "array" in lowered) and len(re.findall(r"\bfor\b", lowered)) >= 1

    def _comment_prefix(self, language: CodingLanguage) -> str:
        if language == CodingLanguage.SQL:
            return "--"
        return "//" if language == CodingLanguage.JAVA else "#"
