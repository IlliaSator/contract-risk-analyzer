from __future__ import annotations


def estimate_token_count(text: str | None) -> int:
    if not text:
        return 0
    return len(str(text).split())


def truncate_text(text: str, max_tokens: int | None = None, max_chars: int | None = None) -> str:
    output = text or ""
    if max_chars is not None and len(output) > max_chars:
        output = output[:max_chars].rstrip()
    if max_tokens is not None:
        tokens = output.split()
        if len(tokens) > max_tokens:
            output = " ".join(tokens[:max_tokens])
    return output
