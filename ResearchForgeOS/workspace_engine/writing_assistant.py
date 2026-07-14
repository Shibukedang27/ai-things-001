from __future__ import annotations

import re

from workspace_engine.types import WritingMode, WritingResult
from workspace_engine.utils import markdown_bullets, normalize_space, sentences, top_keywords


class WritingAssistant:
    def assist(
        self,
        text: str,
        *,
        mode: WritingMode,
        citation_sources: list[dict[str, str]] | None = None,
    ) -> WritingResult:
        cleaned = normalize_space(text)
        handlers = {
            WritingMode.REWRITE: self._rewrite,
            WritingMode.EXPAND: self._expand,
            WritingMode.SIMPLIFY: self._simplify,
            WritingMode.PROFESSIONAL: self._professional,
            WritingMode.ACADEMIC: self._academic,
            WritingMode.ELI5: self._eli5,
            WritingMode.TECHNICAL: self._technical,
            WritingMode.GRAMMAR: self._grammar,
            WritingMode.CITATION: lambda value: self._citation(value, citation_sources or []),
            WritingMode.MARKDOWN: self._markdown,
        }
        output, changes, citations = handlers[mode](cleaned)
        return WritingResult(
            mode=mode,
            original_text=text,
            output_text=output,
            changes=changes,
            citations=citations,
            metadata={"engine": "workspace_writing_assistant_v1", "mode": mode.value},
        )

    def _rewrite(self, text: str) -> tuple[str, list[str], list[str]]:
        rewritten = " ".join(self._polish_sentence(sentence) for sentence in sentences(text))
        return rewritten or text, ["Rewrote sentences for clarity and flow."], []

    def _expand(self, text: str) -> tuple[str, list[str], list[str]]:
        keywords = top_keywords(text, limit=5)
        expansion = [
            text,
            "",
            "Additional Context",
            markdown_bullets(
                [
                    f"{keyword.title()} matters because it shapes the note's core reasoning."
                    for keyword in keywords
                ]
            ),
            "",
            "Implications",
            "This can be connected to prior notes, source documents, and follow-up research tasks.",
        ]
        return "\n".join(part for part in expansion if part), ["Expanded the note with context and implications."], []

    def _simplify(self, text: str) -> tuple[str, list[str], list[str]]:
        simplified = []
        replacements = {
            "utilize": "use",
            "approximately": "about",
            "demonstrates": "shows",
            "facilitates": "helps",
            "subsequently": "then",
            "therefore": "so",
        }
        for sentence in sentences(text):
            updated = sentence
            for source, target in replacements.items():
                updated = re.sub(rf"\b{source}\b", target, updated, flags=re.I)
            simplified.append(updated)
        return " ".join(simplified), ["Simplified wording and shortened complex phrasing."], []

    def _professional(self, text: str) -> tuple[str, list[str], list[str]]:
        opening = "The key takeaway is that"
        body = text[0].lower() + text[1:] if text else text
        output = f"{opening} {body}".strip()
        output = output.replace("I think", "The analysis suggests").replace("maybe", "potentially")
        return output, ["Adjusted tone for concise professional communication."], []

    def _academic(self, text: str) -> tuple[str, list[str], list[str]]:
        output = (
            "This note argues that "
            + (text[0].lower() + text[1:] if text else text)
            + " The claim should be evaluated against source evidence, methodology, and competing interpretations."
        )
        return output.strip(), ["Adjusted tone toward academic framing and evidence-aware language."], []

    def _eli5(self, text: str) -> tuple[str, list[str], list[str]]:
        keywords = top_keywords(text, limit=3)
        topic = ", ".join(keyword.title() for keyword in keywords) if keywords else "this idea"
        output = (
            f"Imagine {topic} as a set of building blocks. "
            "Each block helps explain the next one. "
            f"In simple terms: {self._first_sentence(text)}"
        )
        return output, ["Converted the explanation into simple, concrete language."], []

    def _technical(self, text: str) -> tuple[str, list[str], list[str]]:
        keywords = top_keywords(text, limit=6)
        output = "\n".join(
            [
                "Technical Explanation",
                "",
                text,
                "",
                "Core Mechanisms",
                markdown_bullets(
                    [
                        f"{keyword.title()}: operational signal extracted from the note."
                        for keyword in keywords
                    ]
                ),
                "",
                "Implementation Considerations",
                "- Identify inputs, outputs, invariants, and failure modes.",
                "- Connect the concept to existing source documents and graph nodes.",
            ]
        )
        return output, ["Added technical structure, mechanisms, and implementation considerations."], []

    def _grammar(self, text: str) -> tuple[str, list[str], list[str]]:
        output = text.strip()
        output = re.sub(r"\s+([,.;:!?])", r"\1", output)
        output = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", output)
        output = re.sub(r"\bi\b", "I", output)
        if output and output[-1] not in ".!?":
            output += "."
        return output, ["Fixed spacing, capitalization, and terminal punctuation."], []

    def _citation(self, text: str, sources: list[dict[str, str]]) -> tuple[str, list[str], list[str]]:
        citations: list[str] = []
        for index, source in enumerate(sources, start=1):
            title = source.get("title") or "Untitled Source"
            author = source.get("author") or source.get("authors") or "Unknown"
            year = source.get("year") or "n.d."
            url = source.get("url")
            citation = f"[{index}] {author} ({year}). {title}."
            if url:
                citation += f" {url}"
            citations.append(citation)
        if not citations:
            title = self._first_sentence(text)[:80] or "Workspace note"
            citations.append(f"[1] ResearchForge Workspace. (n.d.). {title}.")
        return f"{text}\n\nReferences\n{markdown_bullets(citations)}", ["Generated citation entries."], citations

    def _markdown(self, text: str) -> tuple[str, list[str], list[str]]:
        note_sentences = sentences(text)
        title = self._first_sentence(text)[:80] or "Formatted Note"
        bullets = note_sentences[1:8] if len(note_sentences) > 1 else note_sentences[:8]
        output = f"# {title}\n\n## Key Points\n{markdown_bullets(bullets)}"
        return output, ["Formatted the text as Markdown with a heading and key points."], []

    def _polish_sentence(self, sentence: str) -> str:
        sentence = sentence.strip()
        if not sentence:
            return sentence
        sentence = sentence[0].upper() + sentence[1:]
        if sentence[-1] not in ".!?":
            sentence += "."
        return sentence

    def _first_sentence(self, text: str) -> str:
        return sentences(text)[0] if sentences(text) else text[:160]
