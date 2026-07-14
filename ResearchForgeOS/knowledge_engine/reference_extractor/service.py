import re

from knowledge_engine.types import ReferenceCandidate
from knowledge_engine.utils import clamp_score


class ReferenceExtractor:
    URL_PATTERN = re.compile(r"https?://[^\s)\]>\"']+")
    DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
    YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

    def extract(self, text: str) -> list[ReferenceCandidate]:
        references: list[ReferenceCandidate] = []
        references.extend(self._url_references(text))
        references.extend(self._bibliography_references(text))
        references.extend(self._doi_references(text))
        return self._dedupe(references)[:40]

    def _url_references(self, text: str) -> list[ReferenceCandidate]:
        results: list[ReferenceCandidate] = []
        for match in self.URL_PATTERN.finditer(text):
            url = match.group(0).rstrip(".,;")
            results.append(
                ReferenceCandidate(
                    title=None,
                    authors=[],
                    year=None,
                    source=None,
                    url=url,
                    citation_text=url,
                    reference_type="url",
                    confidence_score=0.88,
                )
            )
        return results

    def _bibliography_references(self, text: str) -> list[ReferenceCandidate]:
        section_match = re.search(r"\b(references|bibliography)\b[:\n]([\s\S]+)$", text, re.I)
        if not section_match:
            return []
        lines = [
            line.strip(" -[]0123456789.")
            for line in section_match.group(2).splitlines()
            if len(line.strip()) > 12
        ]
        results: list[ReferenceCandidate] = []
        for line in lines[:30]:
            year_match = self.YEAR_PATTERN.search(line)
            title = self._title_from_line(line)
            results.append(
                ReferenceCandidate(
                    title=title,
                    authors=self._authors_from_line(line),
                    year=int(year_match.group(0)) if year_match else None,
                    source=None,
                    url=self._first_url(line),
                    citation_text=line[:1000],
                    reference_type="bibliography_entry",
                    confidence_score=clamp_score(0.72 + (0.12 if year_match else 0)),
                )
            )
        return results

    def _doi_references(self, text: str) -> list[ReferenceCandidate]:
        results = []
        for match in self.DOI_PATTERN.finditer(text):
            doi = match.group(0)
            results.append(
                ReferenceCandidate(
                    title=None,
                    authors=[],
                    year=None,
                    source="DOI",
                    url=f"https://doi.org/{doi}",
                    citation_text=doi,
                    reference_type="doi",
                    confidence_score=0.95,
                )
            )
        return results

    def _title_from_line(self, line: str) -> str | None:
        quoted = re.search(r"[\"“](.+?)[\"”]", line)
        if quoted:
            return quoted.group(1)[:240]
        parts = [part.strip() for part in re.split(r"\.\s+", line) if part.strip()]
        if len(parts) >= 2:
            return parts[1][:240]
        return line[:120]

    def _authors_from_line(self, line: str) -> list[str]:
        first_part = re.split(r"\.\s+|\(\d{4}\)", line, maxsplit=1)[0]
        authors = [part.strip() for part in re.split(r",| and ", first_part) if part.strip()]
        return authors[:8]

    def _first_url(self, line: str) -> str | None:
        match = self.URL_PATTERN.search(line)
        return match.group(0).rstrip(".,;") if match else None

    def _dedupe(self, references: list[ReferenceCandidate]) -> list[ReferenceCandidate]:
        seen: set[str] = set()
        unique: list[ReferenceCandidate] = []
        for reference in references:
            key = (reference.url or reference.citation_text).lower()
            if key not in seen:
                seen.add(key)
                unique.append(reference)
        return unique
