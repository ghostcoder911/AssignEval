"""Match AVR source files to assignment questions."""

from __future__ import annotations

import re
from pathlib import Path

from assigneval.discovery import (
    CodeSource,
    extract_readme_sections,
    guess_question_from_filename,
    read_file_sources,
)
from assigneval.questions import Question


def _score_avr_code(code: str, question: Question) -> float:
    text = code.lower()
    score = 0.0
    for kw in question.keywords:
        if kw in text:
            score += 2.0
    signals: dict[int, list[str]] = {
        1: [r"portd", r"pd5", r"ddr"],
        2: [r"red", r"green", r"button", r"toggle"],
        3: [r"portb", r"train", r"<<|shift"],
        4: [r"counter", r"portb", r"binary"],
        5: [r"traffic", r"tccr", r"timer"],
        6: [r"int0", r"isr", r"flag"],
        7: [r"timer1", r"timer2", r"ocr"],
        8: [r"ocr0a", r"tccr0", r"pwm"],
        9: [r"debounc", r"ocr0a"],
        10: [r"adc", r"lm35", r"motor"],
        11: [r"servo", r"ocr1a", r"phase"],
        12: [r"lcd", r"long", r"press"],
        13: [r"uart", r"ubrr", r"9600"],
        14: [r"adc", r"potentiometer", r"ocr0a"],
        15: [r"bmp280", r"i2c", r"twi", r"oled"],
    }
    for pat in signals.get(question.number, []):
        if re.search(pat, text, re.I):
            score += 3.0
    if _has_avr_registers(text):
        score += 2.0
    return score


def _has_avr_registers(text: str) -> bool:
    return bool(
        re.search(
            r"\b(DDR|PORT|PIN|TCCR|OCR|ADMUX|ADCSRA|UBRR|TWCR)[A-Z0-9]*\b",
            text,
            re.I,
        )
    )


def match_avr_sources(
    questions: list[Question],
    file_entries: list[tuple[Path, str]],
    readme_sections: dict[int, str],
) -> dict[int, CodeSource]:
    assigned: dict[int, CodeSource] = {}
    used: set[Path] = set()

    for num, code in readme_sections.items():
        if 1 <= num <= 15 and _has_avr_registers(code.lower()):
            assigned[num] = CodeSource(
                num, None, code, f"readme:avr-q{num}", 0.95
            )

    for path, code in file_entries:
        guess = guess_question_from_filename(path)
        if guess and guess not in assigned:
            assigned[guess] = CodeSource(
                guess, path, code, f"file:{path.name}", 0.85
            )
            used.add(path)

    remaining_q = [q for q in questions if q.number not in assigned]
    remaining_files = [(p, c) for p, c in file_entries if p not in used]

    for question in remaining_q:
        best: tuple[float, Path, str] | None = None
        for path, code in remaining_files:
            s = _score_avr_code(code, question)
            if s < 5.0:
                continue
            if best is None or s > best[0]:
                best = (s, path, code)
        if best:
            _, path, code = best
            assigned[question.number] = CodeSource(
                question.number, path, code, f"file:{path.name}", min(0.9, best[0] / 20)
            )
            used.add(path)
            remaining_files = [(p, c) for p, c in remaining_files if p != path]

    return assigned


def build_avr_sources_for_repo(
    repo_root: Path,
    questions: list[Question],
    roots: list[Path],
    scoped: bool = False,
) -> dict[int, CodeSource]:
    from assigneval.discovery import collect_c_files

    files = collect_c_files(roots, track="avr")
    file_entries = [
        (p, c)
        for p, c in read_file_sources(files)
        if _has_avr_registers(c.lower())
    ]
    readme_sections: dict[int, str] = {}
    for root in roots:
        readme_sections.update(extract_readme_sections(root, scoped=scoped))
    if not scoped:
        readme_sections.update(extract_readme_sections(repo_root))
    return match_avr_sources(questions, file_entries, readme_sections)
