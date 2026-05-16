"""Match discovered code sources to assignment questions."""

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


def _score_code_against_question(code: str, question: Question) -> float:
    text = code.lower()
    title = question.title.lower()
    score = 0.0

    for kw in question.keywords:
        if kw in text:
            score += 2.0
        if kw in title and kw in text:
            score += 1.0

    # title-specific signals
    signals: dict[int, list[str]] = {
        1: [r"%\s*2", r"even", r"odd"],
        2: [r"prime", r"divis"],
        3: [r"factorial", r"fact\s*="],
        4: [r"fibonacci", r"fib", r"\ba\s*=\s*0"],
        5: [r"perfect", r"proper\s*div"],
        6: [r"\bgcd\b", r"euclid", r"hcf"],
        7: [r"freq", r"frequency", r"digit"],
        8: [r"base", r"convert", r"0x", r"'a'\s*-\s*'0'"],
        9: [r"switch", r"operator", r"multiply", r"divide"],
        10: [r"str\[.*\]\s*-\s*'0'", r"string.*int", r"atoi"],
        11: [r"digit\s*\+\s*'0'", r"numbertostring", r"int.*string"],
        12: [r"palindrom"],
        13: [r"reverse", r"swap.*str"],
        14: [r"pangram"],
        15: [r"space", r"consecutive"],
        16: [r"tolower", r"lowercase", r"'a'\s*-\s*'A'"],
        17: [r"toggle", r"\^=", r"xor"],
        18: [r"extract", r">>\s*pos"],
        19: [r"replace", r"~\s*mask"],
        20: [r"swap.*bit"],
        21: [r"duplicate", r"unique"],
        22: [r"second\s*largest", r"sec_lar", r"second\s*smallest"],
        23: [r"rotate", r"left", r"right"],
        24: [r"merge", r"sorted"],
        25: [r"pair", r"target"],
        26: [r"negative", r"rearrange", r"positive"],
        27: [r"complex", r"imaginary", r"imag", r"\.img"],
    }
    for pat in signals.get(question.number, []):
        if re.search(pat, text, re.IGNORECASE):
            score += 3.0

    if "main" in text:
        score += 0.5
    if "#include" in text:
        score += 0.5
    return score


def match_sources(
    questions: list[Question],
    file_entries: list[tuple[Path, str]],
    readme_sections: dict[int, str],
) -> dict[int, CodeSource]:
    """Return best CodeSource per question number (1-27)."""
    assigned: dict[int, CodeSource] = {}
    used_files: set[Path] = set()

    # 1) README sections — highest confidence when numbered correctly
    for num, code in readme_sections.items():
        if 1 <= num <= len(questions):
            assigned[num] = CodeSource(
                question_number=num,
                path=None,
                code=code,
                origin=f"readme:question-{num}",
                confidence=0.95,
            )

    # 2) Filename hints (lower confidence — may be wrong numbering)
    file_by_guess: dict[int, list[tuple[Path, str, float]]] = {}
    for path, code in file_entries:
        guess = guess_question_from_filename(path)
        if guess:
            stem = path.stem
            conf = 0.85 if re.match(r"^\d{1,2}[_\sA-Za-z]", stem) else 0.55
            file_by_guess.setdefault(guess, []).append((path, code, conf))

    for num, entries in file_by_guess.items():
        if num in assigned:
            continue
        path, code, conf = entries[0]
        assigned[num] = CodeSource(
            question_number=num,
            path=path,
            code=code,
            origin=f"file:{path.name}",
            confidence=conf,
        )
        used_files.add(path)

    # 3) Content-based matching for remaining
    remaining_q = [q for q in questions if q.number not in assigned]
    remaining_files = [(p, c) for p, c in file_entries if p not in used_files]

    for question in remaining_q:
        best: tuple[float, Path | None, str] | None = None
        for path, code in remaining_files:
            s = _score_code_against_question(code, question)
            if s < 4.0:
                continue
            if best is None or s > best[0]:
                best = (s, path, code)
        if best:
            score, path, code = best
            assigned[question.number] = CodeSource(
                question_number=question.number,
                path=path,
                code=code,
                origin=f"file:{path.name}" if path else "unknown",
                confidence=min(0.9, score / 20.0),
            )
            if path:
                used_files.add(path)
                remaining_files = [(p, c) for p, c in remaining_files if p != path]

    return assigned


def build_sources_for_repo(
    repo_root: Path,
    questions: list[Question],
    roots: list[Path],
    scoped: bool = False,
) -> dict[int, CodeSource]:
    from assigneval.discovery import collect_c_files

    files = collect_c_files(roots)
    file_entries = read_file_sources(files)
    readme_sections: dict[int, str] = {}
    for root in roots:
        readme_sections.update(extract_readme_sections(root, scoped=scoped))
    if not scoped:
        readme_sections.update(extract_readme_sections(repo_root))
    return match_sources(questions, file_entries, readme_sections)
