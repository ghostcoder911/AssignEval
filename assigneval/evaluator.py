"""Evaluate matched sources against test cases."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from assigneval.compiler import compile_c, run_binary, write_source
from assigneval.discovery import CodeSource
from assigneval.questions import Question
from assigneval.test_cases import (
    CUSTOM_CHECKERS,
    QUESTION_TESTS,
    STATIC_CHECKS,
    TestCase,
    check_test,
)


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str


@dataclass
class QuestionResult:
    question: Question
    source: CodeSource | None
    compile_ok: bool
    compile_message: str
    tests: list[TestResult] = field(default_factory=list)
    static_notes: list[str] = field(default_factory=list)
    score: float = 0.0
    max_score: float = 10.0
    review_comments: list[str] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for t in self.tests if t.passed)

    @property
    def total_tests(self) -> int:
        return len(self.tests)


def _run_static_checks(question_num: int, code: str) -> list[str]:
    notes: list[str] = []
    checks = STATIC_CHECKS.get(question_num, [])
    for pattern, message in checks:
        if not re.search(pattern, code, re.IGNORECASE | re.DOTALL):
            notes.append(message)
    return notes


def _evaluate_tests(
    question_num: int,
    stdout: str,
    stderr: str,
    case: TestCase,
) -> tuple[bool, str]:
    custom = CUSTOM_CHECKERS.get(question_num, {}).get(case.name)
    if custom:
        return custom(stdout, stderr)
    return check_test(case, stdout, stderr)


def evaluate_question(
    question: Question,
    source: CodeSource | None,
    work_root: Path | None = None,
) -> QuestionResult:
    result = QuestionResult(
        question=question,
        source=source,
        compile_ok=False,
        compile_message="No submission found for this question.",
    )

    if source is None or not source.code.strip():
        result.review_comments.append(
            "No answer detected. Add a .c file or document your solution in README.md "
            f"under section '## {question.number}.' with a C code block."
        )
        result.score = 0.0
        return result

    tests = QUESTION_TESTS.get(question.number, [])
    if not tests:
        result.review_comments.append("No automated tests configured for this question.")
        result.score = 0.0
        return result

    cleanup = work_root is None
    if work_root is None:
        work_root = Path(tempfile.mkdtemp(prefix="assigneval_q_"))

    qdir = work_root / f"q{question.number:02d}"
    qdir.mkdir(parents=True, exist_ok=True)
    src_path = write_source(source.code, qdir, "submission.c")
    comp = compile_c(src_path, qdir)

    result.compile_ok = comp.success
    result.compile_message = comp.message
    result.static_notes = _run_static_checks(question.number, source.code)

    if not comp.success or comp.binary is None:
        result.review_comments.append(f"Compilation failed: {comp.message[:500]}")
        result.score = 0.0
        if cleanup:
            _safe_rmtree(work_root)
        return result

    total_weight = sum(t.weight for t in tests)
    earned = 0.0

    for case in tests:
        run = run_binary(comp.binary, case.stdin)
        if run.timed_out:
            tr = TestResult(case.name, False, "Program timed out (>5s).")
        elif run.returncode != 0 and not run.stdout:
            tr = TestResult(
                case.name,
                False,
                f"Exit code {run.returncode}. stderr: {run.stderr[:200]}",
            )
        else:
            ok, detail = _evaluate_tests(
                question.number, run.stdout, run.stderr, case
            )
            tr = TestResult(case.name, ok, detail if not ok else "Passed")
        result.tests.append(tr)
        if tr.passed:
            earned += case.weight

    ratio = earned / total_weight if total_weight else 0.0
    result.score = round(ratio * 10.0, 1)

    result.review_comments.extend(_build_review(result, source))
    if cleanup:
        _safe_rmtree(work_root)
    return result


def _build_review(result: QuestionResult, source: CodeSource) -> list[str]:
    comments: list[str] = []
    origin = source.origin
    conf = source.confidence

    if conf < 0.5:
        comments.append(
            f"Low confidence match ({origin}). Verify the correct file was graded."
        )
    elif conf < 0.8:
        comments.append(f"Matched submission via {origin} (confidence {conf:.0%}).")
    else:
        comments.append(f"Matched submission via {origin}.")

    failed = [t for t in result.tests if not t.passed]
    if not failed and not result.static_notes:
        comments.append("All test cases passed. Well done!")
    else:
        for t in failed:
            comments.append(f"Test '{t.name}' failed: {t.detail}")
        for note in result.static_notes:
            comments.append(f"Style/requirement note: {note}")

    if result.score >= 10:
        comments.append("Full marks — solution behaves correctly on tested inputs.")
    elif result.score >= 7:
        comments.append("Good attempt — fix failing cases for full marks.")
    elif result.score >= 4:
        comments.append("Partial credit — core logic may need revision.")
    elif result.score > 0:
        comments.append("Minimal credit — several test cases failed.")
    return comments


def evaluate_all(
    questions: list[Question],
    sources: dict[int, CodeSource],
    work_root: Path | None = None,
) -> list[QuestionResult]:
    results: list[QuestionResult] = []
    root = work_root or Path(tempfile.mkdtemp(prefix="assigneval_run_"))
    for q in questions:
        results.append(evaluate_question(q, sources.get(q.number), root))
    return results


def _safe_rmtree(path: Path) -> None:
    import shutil

    try:
        shutil.rmtree(path)
    except OSError:
        pass
