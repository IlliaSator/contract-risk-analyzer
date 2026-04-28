from __future__ import annotations

import re

from contract_risk_analyzer.data.schemas import Clause
from contract_risk_analyzer.preprocessing.cleaning import clean_legal_text

SECTION_RE = re.compile(r"(?:^|\n)\s*(?:\d+(?:\.\d+)*\.|[A-Z][A-Za-z ]{2,40}\.)\s+")
SENTENCE_END_RE = re.compile(r"(?<=[.;:!?])\s+")


def split_into_clauses(text: str, document_id: str = "document") -> list[Clause]:
    cleaned = clean_legal_text(text)
    if not cleaned:
        return []

    # Preserve simple numbered sections when possible; otherwise fall back to sentence groups.
    raw_parts = re.split(r"\s+(?=\d+(?:\.\d+)*\.\s+[A-Z])", cleaned)
    if len(raw_parts) == 1:
        raw_parts = [part.strip() for part in SENTENCE_END_RE.split(cleaned) if part.strip()]

    clauses: list[Clause] = []
    cursor = 0
    for index, part in enumerate(raw_parts):
        clause_text = part.strip()
        if not clause_text:
            continue
        start = cleaned.find(clause_text, cursor)
        if start < 0:
            start = cursor
        end = start + len(clause_text)
        cursor = end
        clauses.append(
            Clause(
                clause_id=f"{document_id}-clause-{index + 1}",
                text=clause_text,
                source_document_id=document_id,
                start_char=start,
                end_char=end,
                metadata={"chunking": "split_into_clauses"},
            )
        )
    return clauses


def _find_boundary(text: str, max_chars: int) -> int:
    boundary = max(text.rfind(". ", 0, max_chars), text.rfind("; ", 0, max_chars), text.rfind("\n", 0, max_chars))
    if boundary < max_chars * 0.5:
        return max_chars
    return boundary + 1


def chunk_long_document(
    text: str,
    document_id: str = "document",
    max_chars: int = 1500,
    overlap: int = 150,
    preserve_sentence_boundaries: bool = True,
) -> list[Clause]:
    cleaned = clean_legal_text(text)
    if not cleaned:
        return []
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    chunks: list[Clause] = []
    start = 0
    while start < len(cleaned):
        remaining = len(cleaned) - start
        if remaining <= max_chars:
            end = len(cleaned)
        elif preserve_sentence_boundaries:
            end = start + _find_boundary(cleaned[start : start + max_chars], max_chars)
        else:
            end = start + max_chars
        chunk_text = cleaned[start:end].strip()
        if chunk_text:
            chunks.append(
                Clause(
                    clause_id=f"{document_id}-chunk-{len(chunks) + 1}",
                    text=chunk_text,
                    source_document_id=document_id,
                    start_char=start,
                    end_char=end,
                    metadata={"chunking": "chunk_long_document", "overlap": overlap},
                )
            )
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks
