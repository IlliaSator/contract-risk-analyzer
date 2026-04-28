from __future__ import annotations

import re
import unicodedata


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WHITESPACE_RE = re.compile(r"\s+")


def remove_control_chars(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    return CONTROL_CHAR_RE.sub(" ", normalized)


def normalize_whitespace(text: str | None) -> str:
    if not text:
        return ""
    return WHITESPACE_RE.sub(" ", text).strip()


def clean_legal_text(text: str | None) -> str:
    return normalize_whitespace(remove_control_chars(text))
