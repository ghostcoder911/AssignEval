"""Shared evaluation pipeline for CLI and web UI."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from assigneval.discovery import (
    clone_repo,
    find_c_assignment_roots,
    resolve_search_root,
    use_local_path,
)
from assigneval.evaluator import QuestionResult, evaluate_all
from assigneval.matcher import build_sources_for_repo
from assigneval.questions import parse_questions
from assigneval.repo_urls import parse_repo_input
from assigneval.report import total_score


@dataclass
class DiscoveryInfo:
    question_number: int
    origin: str
    confidence: float


@dataclass
class EvaluationReport:
    repo: str
    total_score: float
    max_total: float
    questions_parsed: int
    matched_count: int
    discovery: list[DiscoveryInfo]
    results: list[QuestionResult]
    summary: dict[str, int]
    search_path: str | None = None
    repo_label: str = ""


class EvaluationError(Exception):
    """Raised when evaluation cannot be completed."""


def default_questions_path() -> Path:
    return Path(__file__).resolve().parent.parent / "C Assignment Questions BASIC REFRESHER.md"


def run_evaluation(
    repo: str,
    questions_path: Path | None = None,
) -> EvaluationReport:
    questions_path = questions_path or default_questions_path()
    if not questions_path.is_file():
        raise EvaluationError(f"Questions file not found: {questions_path}")

    try:
        target = parse_repo_input(repo)
    except ValueError as exc:
        raise EvaluationError(str(exc)) from exc

    questions = parse_questions(questions_path)
    cleanup_path: Path | None = None

    try:
        if target.clone_url:
            clone_dest = Path(tempfile.mkdtemp(prefix="assigneval_clone_"))
            cleanup_path = clone_dest
            try:
                repo_root = clone_repo(
                    target.clone_url,
                    clone_dest / "repo",
                    branch=target.branch,
                )
            except subprocess.CalledProcessError as exc:
                msg = (exc.stderr or exc.stdout or str(exc)).strip()
                if target.branch:
                    msg += (
                        f"\nCould not clone branch '{target.branch}'. "
                        "Check that the branch name in your link is correct."
                    )
                raise EvaluationError(f"Failed to clone repository: {msg}") from exc
        else:
            repo_root = use_local_path(target.original_url)

        scoped = bool(target.subpath)
        if scoped:
            try:
                search_root = resolve_search_root(repo_root, target.subpath)
            except FileNotFoundError as exc:
                raise EvaluationError(str(exc)) from exc
        else:
            search_root = repo_root

        roots = find_c_assignment_roots(
            repo_root,
            scope=search_root if scoped else None,
        )
        sources = build_sources_for_repo(
            repo_root,
            questions,
            roots,
            scoped=scoped,
        )
        results = evaluate_all(questions, sources)

        discovery = [
            DiscoveryInfo(n, sources[n].origin, sources[n].confidence)
            for n in sorted(sources)
        ]

        summary = {"full_marks": 0, "partial": 0, "missing": 0, "compile_fail": 0}
        for r in results:
            if r.source is None:
                summary["missing"] += 1
            elif not r.compile_ok:
                summary["compile_fail"] += 1
            elif r.score >= 10:
                summary["full_marks"] += 1
            else:
                summary["partial"] += 1

        search_display = None
        if scoped:
            search_display = target.subpath

        return EvaluationReport(
            repo=repo,
            repo_label=target.display_label,
            search_path=search_display,
            total_score=total_score(results),
            max_total=27 * 10.0,
            questions_parsed=len(questions),
            matched_count=len(sources),
            discovery=discovery,
            results=results,
            summary=summary,
        )
    finally:
        if cleanup_path:
            shutil.rmtree(cleanup_path, ignore_errors=True)


def report_to_dict(report: EvaluationReport) -> dict:
    from datetime import datetime, timezone

    return {
        "repo": report.repo,
        "repo_label": report.repo_label or report.repo,
        "search_path": report.search_path,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_score": report.total_score,
        "max_total": report.max_total,
        "questions_parsed": report.questions_parsed,
        "matched_count": report.matched_count,
        "summary": report.summary,
        "discovery": [
            {"question": d.question_number, "origin": d.origin, "confidence": d.confidence}
            for d in report.discovery
        ],
        "questions": [
            {
                "number": r.question.number,
                "title": r.question.title,
                "category": r.question.category,
                "score": r.score,
                "max_score": r.max_score,
                "source": r.source.origin if r.source else None,
                "confidence": r.source.confidence if r.source else 0,
                "compile_ok": r.compile_ok,
                "compile_message": r.compile_message,
                "tests_passed": r.passed_count,
                "tests_total": r.total_tests,
                "review_comments": r.review_comments,
                "tests": [
                    {"name": t.name, "passed": t.passed, "detail": t.detail}
                    for t in r.tests
                ],
            }
            for r in report.results
        ],
    }
