"""Resolve question document paths (PDF preferred, then Markdown)."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

C_QUESTION_CANDIDATES = (
    "Document from Abhirami.b.pdf",
    "C Assignment Questions BASIC REFRESHER.pdf",
    "C Assignment Questions.pdf",
    "C Assignment Questions BASIC REFRESHER.md",
)

AVR_QUESTION_CANDIDATES = (
    "AVR Programming (ATmega328P) Assignments Questions.pdf",
    "AVR Assignment questions.pdf",
    "AVR Assignment Questions.pdf",
    "AVR Assignment questions.md",
)


def resolve_questions_path(track: str, override: Path | None = None) -> Path:
    if override is not None:
        path = Path(override)
        if not path.is_file():
            raise FileNotFoundError(f"Questions file not found: {path}")
        return path

    candidates = AVR_QUESTION_CANDIDATES if track == "avr" else C_QUESTION_CANDIDATES
    for name in candidates:
        path = PROJECT_ROOT / name
        if path.is_file():
            return path
    raise FileNotFoundError(
        f"No questions file found for track '{track}'. "
        f"Expected one of: {', '.join(candidates)}"
    )
