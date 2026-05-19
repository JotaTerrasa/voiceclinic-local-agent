from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", value)


def contains_any(value: str, words: tuple[str, ...]) -> bool:
    normalized = normalize_text(value)
    return any(word in normalized for word in words)
