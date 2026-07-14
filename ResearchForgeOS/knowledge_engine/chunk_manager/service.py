from knowledge_engine.types import TextChunk
from knowledge_engine.utils import content_hash, words


class ChunkManager:
    def __init__(self, target_words: int = 450, overlap_words: int = 80) -> None:
        self.target_words = target_words
        self.overlap_words = overlap_words

    def split(self, text: str) -> list[TextChunk]:
        tokens = text.split()
        if not tokens:
            return []

        chunks: list[TextChunk] = []
        cursor = 0
        chunk_index = 0
        char_cursor = 0

        while cursor < len(tokens):
            end = min(cursor + self.target_words, len(tokens))
            chunk_text = " ".join(tokens[cursor:end])
            start_char = text.find(tokens[cursor], char_cursor)
            if start_char < 0:
                start_char = char_cursor
            end_char = start_char + len(chunk_text)
            chunks.append(
                TextChunk(
                    index=chunk_index,
                    content=chunk_text,
                    start_char=start_char,
                    end_char=end_char,
                    token_count=len(words(chunk_text)),
                    content_hash=content_hash(chunk_text),
                )
            )
            if end == len(tokens):
                break
            cursor = max(end - self.overlap_words, cursor + 1)
            char_cursor = end_char
            chunk_index += 1

        return chunks
