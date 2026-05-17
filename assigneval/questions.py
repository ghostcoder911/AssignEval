"""Parse assignment questions and define per-question metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Question:
    number: int
    title: str
    description: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    category: str = ""


_QUESTION_LINE = re.compile(
    r"^\s*(?:\d{1,2}\.\s*)?(?:Write a C program|Define a structure)\b",
    re.IGNORECASE,
)

_NUMBERED_SPLIT = re.compile(
    r"(?m)^\s*(\d{1,2})\.\s*(?=Write a C program|Define a structure)",
    re.IGNORECASE,
)

_CATEGORY_MARKERS = {
    "Functions": "functions",
    "STRINGS": "strings",
    "Bit Manipulation": "bit_manipulation",
    "Array": "array",
    "Structure": "structure",
}


def _keywords_for(title: str, description: str) -> tuple[str, ...]:
    text = f"{title} {description}".lower()
    pools: list[list[str]] = [
        ["even", "odd"],
        ["prime", "divis"],
        ["factorial", "fact"],
        ["fibonacci", "fib"],
        ["perfect", "divisor"],
        ["gcd", "euclidean", "recursive", "hcf"],
        ["frequency", "digit", "freq"],
        ["base", "decimal", "hexadecimal", "binary", "convert"],
        ["operator", "arithmetic", "divide", "multiply", "add", "subtract"],
        ["string", "integer", "atoi", "digit", "equivalent"],
        ["integer", "string", "character array"],
        ["palindrome", "palindrom"],
        ["reverse", "iterative", "swap"],
        ["pangram", "alphabet"],
        ["space", "consecutive", "multiple"],
        ["uppercase", "lowercase", "convert"],
        ["toggle", "bit", "position", "xor"],
        ["extract", "bit", "position"],
        ["replace", "bit", "second number"],
        ["swap", "bit", "two integers"],
        ["duplicate", "unique"],
        ["second largest", "second smallest"],
        ["rotate", "left", "right", "position"],
        ["merge", "sorted", "array"],
        ["pair", "target", "sum"],
        ["negative", "positive", "rearrange", "relative order"],
        ["complex", "imaginary", "real", "structure"],
    ]
    for pool in pools:
        hits = [w for w in pool if w in text]
        if len(hits) >= 2:
            return tuple(pool)
    words = re.findall(r"[a-z]{4,}", title.lower())
    return tuple(words[:6])


def _extract_description(block: str, title: str) -> str:
    desc_lines: list[str] = []
    for line in block.splitlines()[1:]:
        low = line.strip().lower()
        if low.startswith("description:"):
            desc_lines.append(line.split(":", 1)[-1].strip())
        elif desc_lines and not low.startswith("pre-requisites"):
            if line.strip():
                desc_lines.append(line.strip())
    return " ".join(desc_lines) if desc_lines else title


def _category_from_block(block: str) -> str:
    for marker, cat in _CATEGORY_MARKERS.items():
        if marker.lower() in block[:300].lower():
            return cat
    return ""


def _parse_numbered_pdf_style(text: str) -> list[Question]:
    parts = _NUMBERED_SPLIT.split(text)
    if len(parts) < 3:
        return []

    questions: list[Question] = []
    i = 1
    while i + 1 < len(parts):
        try:
            num = int(parts[i])
        except ValueError:
            i += 2
            continue
        body = parts[i + 1]
        lines = [ln.strip() for ln in body.strip().splitlines() if ln.strip()]
        if not lines:
            i += 2
            continue
        title = lines[0]
        if not _QUESTION_LINE.search(title):
            i += 2
            continue
        description = _extract_description(body, title)
        questions.append(
            Question(
                number=num,
                title=title[:200],
                description=description,
                keywords=_keywords_for(title, description),
                category=_category_from_block(body),
            )
        )
        i += 2

    by_num: dict[int, Question] = {}
    for q in questions:
        if q.number not in by_num:
            by_num[q.number] = q
    return [by_num[n] for n in sorted(by_num)]


def _parse_markdown_style(text: str) -> list[Question]:
    lines = text.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        if _QUESTION_LINE.search(line):
            body_start = i
            break
    lines = lines[body_start:]

    blocks: list[str] = []
    current: list[str] = []
    category = ""

    for line in lines:
        stripped = line.strip()
        for marker, cat in _CATEGORY_MARKERS.items():
            if marker.lower() in stripped.lower() and len(stripped) < 40:
                category = cat
                break
        if _QUESTION_LINE.match(line):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))

    questions: list[Question] = []
    for idx, block in enumerate(blocks, start=1):
        block_lines = block.strip().splitlines()
        title = block_lines[0].strip()
        description = _extract_description(block, title)
        questions.append(
            Question(
                number=idx,
                title=title,
                description=description,
                keywords=_keywords_for(title, description),
                category=category,
            )
        )
    return questions


def parse_questions(source: Path | str) -> list[Question]:
    from assigneval.pdf_text import load_document_text

    text = source if isinstance(source, str) else load_document_text(Path(source))
    numbered = _parse_numbered_pdf_style(text)
    if len(numbered) >= 20:
        return numbered
    return _parse_markdown_style(text)
