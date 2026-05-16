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


_QUESTION_START = re.compile(
    r"^\s*(?:Write a C program|Define a structure)\b",
    re.IGNORECASE | re.MULTILINE,
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
        if len(hits) >= 2 or (len(hits) == 1 and pool == pools[0]):
            return tuple(pool)
    # fallback: significant words from title
    words = re.findall(r"[a-z]{4,}", title.lower())
    return tuple(words[:6])


def parse_questions(md_path: Path) -> list[Question]:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # strip leading doc title
    body_start = 0
    for i, line in enumerate(lines):
        if _QUESTION_START.search(line):
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
        if _QUESTION_START.match(line):
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
        desc_lines: list[str] = []
        for line in block_lines[1:]:
            if line.strip().lower().startswith("description:"):
                desc_lines.append(line.split(":", 1)[-1].strip())
            elif desc_lines and not line.strip().startswith("Pre-requisites"):
                if line.strip():
                    desc_lines.append(line.strip())
        description = " ".join(desc_lines) if desc_lines else title
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
