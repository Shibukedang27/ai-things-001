import re


class CodeBlockExtractor:
    FENCED_BLOCK_PATTERN = re.compile(r"```(?P<language>[A-Za-z0-9_+-]*)\n(?P<code>[\s\S]*?)```")
    INDENTED_BLOCK_PATTERN = re.compile(r"(?:^|\n)((?: {4}|\t).+(?:\n(?: {4}|\t).+)*)")

    def extract(self, text: str) -> list[dict[str, str]]:
        snippets: list[dict[str, str]] = []
        for match in self.FENCED_BLOCK_PATTERN.finditer(text):
            code = match.group("code").strip()
            if code:
                snippets.append(
                    {
                        "language": match.group("language") or "text",
                        "code": code[:4000],
                        "source": "fenced_code_block",
                    }
                )

        if snippets:
            return snippets[:20]

        for match in self.INDENTED_BLOCK_PATTERN.finditer(text):
            code = "\n".join(
                line[4:] if line.startswith("    ") else line.strip()
                for line in match.group(1).splitlines()
            )
            if self._looks_like_code(code):
                snippets.append({"language": "text", "code": code[:4000], "source": "indented_block"})
        return snippets[:20]

    def _looks_like_code(self, value: str) -> bool:
        markers = ("def ", "class ", "import ", "=>", "function ", "const ", "let ", "SELECT ", "{", "}")
        return any(marker in value for marker in markers)
