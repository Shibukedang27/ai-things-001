import re

from knowledge_engine.utils import normalize_space


class ContentCleaner:
    URL_NOISE_PATTERN = re.compile(r"\b(?:cookie policy|privacy policy|terms of service|all rights reserved)\b", re.I)

    def clean(self, text: str) -> str:
        text = text.replace("\u00a0", " ")
        text = re.sub(r"-\n(?=[a-z])", "", text)
        text = re.sub(r"(?<![.!?:;])\n(?!\n|[-*#])", " ", text)
        lines = [line.strip() for line in text.splitlines()]
        useful_lines = [line for line in lines if line and not self.URL_NOISE_PATTERN.fullmatch(line.lower())]
        return normalize_space("\n".join(useful_lines))
