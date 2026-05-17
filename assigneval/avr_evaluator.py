"""Evaluate AVR bare-metal submissions."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from assigneval.avr_checks import AVR_QUESTION_CHECKS
from assigneval.avr_compiler import compile_avr_source
from assigneval.discovery import CodeSource
from assigneval.evaluator import QuestionResult, TestResult
from assigneval.questions import Question


@dataclass
class AvrTestResult:
    name: str
    passed: bool
    detail: str


def evaluate_avr_question(
    question: Question,
    source: CodeSource | None,
    work_root: Path | None = None,
) -> QuestionResult:
    result = QuestionResult(
        question=question,
        source=source,
        compile_ok=False,
        compile_message="No submission found for this AVR question.",
    )

    if source is None or not source.code.strip():
        result.review_comments.append(
            f"No AVR answer detected for Q{question.number}. "
            "Add a .c file or README section with ATmega328P register code."
        )
        result.score = 0.0
        return result

    checks = AVR_QUESTION_CHECKS.get(question.number, [])
    if not checks:
        result.review_comments.append("No checks configured for this question.")
        return result

    cleanup = work_root is None
    if work_root is None:
        work_root = Path(tempfile.mkdtemp(prefix="assigneval_avr_q_"))
    qdir = work_root / f"avr_q{question.number:02d}"
    qdir.mkdir(parents=True, exist_ok=True)

    comp = compile_avr_source(source.code, qdir)
    result.compile_ok = comp.success
    result.compile_message = comp.message

    compile_weight = 1.0
    total_weight = compile_weight + sum(c[0].weight for c in checks)
    earned = 0.0

    if comp.success:
        earned += compile_weight
        result.tests.append(TestResult("avr_compile", True, "Compiles for ATmega328P"))
    else:
        result.tests.append(
            TestResult("avr_compile", False, comp.message[:300])
        )

    for check_def, check_fn in checks:
        ok, detail = check_fn(source.code)
        result.tests.append(
            TestResult(check_def.name, ok, detail if ok else detail)
        )
        if ok:
            earned += check_def.weight

    result.score = round((earned / total_weight) * 10.0, 1)

    result.review_comments.extend(_avr_review(result, source, comp.warnings))
    if cleanup:
        import shutil

        shutil.rmtree(work_root, ignore_errors=True)
    return result


def _avr_review(
    result: QuestionResult, source: CodeSource, warnings: list[str]
) -> list[str]:
    comments: list[str] = []
    comments.append(
        f"Matched via {source.origin} (confidence {source.confidence:.0%}). "
        "AVR grading uses cross-compile + register-level static analysis "
        "(hardware behavior is not simulated)."
    )
    if warnings:
        comments.append(f"Compiler warnings: {len(warnings)} (review recommended).")
    failed = [t for t in result.tests if not t.passed]
    for t in failed:
        comments.append(f"Check '{t.name}' failed: {t.detail}")
    if result.score >= 10:
        comments.append("Full marks — code structure matches ATmega328P requirements.")
    elif result.score >= 7:
        comments.append("Good register-level approach — address failed checks for full marks.")
    elif result.score > 0:
        comments.append("Partial credit — review datasheet register usage.")
    return comments


def evaluate_avr_all(
    questions: list[Question],
    sources: dict[int, CodeSource],
    work_root: Path | None = None,
) -> list[QuestionResult]:
    root = work_root or Path(tempfile.mkdtemp(prefix="assigneval_avr_run_"))
    return [
        evaluate_avr_question(q, sources.get(q.number), root) for q in questions
    ]
