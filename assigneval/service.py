"""Shared evaluation pipeline for CLI and web UI."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from assigneval.avr_evaluator import evaluate_avr_all
from assigneval.avr_matcher import build_avr_sources_for_repo
from assigneval.avr_questions import parse_avr_questions
from assigneval.question_paths import resolve_questions_path
from assigneval.discovery import (
    clone_repo,
    find_assignment_roots,
    resolve_search_root,
    use_local_path,
)
from assigneval.evaluator import QuestionResult, evaluate_all
from assigneval.matcher import build_sources_for_repo
from assigneval.questions import parse_questions
from assigneval.repo_urls import parse_repo_input
from assigneval.report import total_score

TRACK_C = "c"
TRACK_AVR = "avr"

TRACK_CONFIG = {
    TRACK_C: {
        "label": "C Programming",
        "parse": parse_questions,
        "max_total": 270.0,
    },
    TRACK_AVR: {
        "label": "AVR ATmega328P Bare Metal",
        "parse": parse_avr_questions,
        "max_total": 150.0,
    },
}


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
    track: str = TRACK_C
    track_label: str = "C Programming"
    questions_source: str = ""
    search_path: str | None = None
    repo_label: str = ""


class EvaluationError(Exception):
    """Raised when evaluation cannot be completed."""


def default_questions_path(track: str = TRACK_C) -> Path:
    return resolve_questions_path(track)


def _validate_host_tools(track: str) -> None:
    if not shutil.which("git"):
        raise EvaluationError(
            "Git is not available in this hosting environment. "
            "Run AssignEval locally (./run-ui.sh) or on a VPS with git installed."
        )
    if track == TRACK_AVR:
        if not shutil.which("avr-gcc"):
            raise EvaluationError(
                "avr-gcc is not available. Install: sudo apt install gcc-avr avr-libc"
            )
    elif not shutil.which("gcc"):
        raise EvaluationError(
            "gcc is not available in this hosting environment. "
            "Use local ./run-ui.sh or a server with build-essential installed."
        )


def run_evaluation(
    repo: str,
    questions_path: Path | None = None,
    track: str = TRACK_C,
) -> EvaluationReport:
    track = track.lower().strip()
    if track not in TRACK_CONFIG:
        raise EvaluationError(f"Unknown track '{track}'. Use 'c' or 'avr'.")

    cfg = TRACK_CONFIG[track]
    try:
        questions_path = resolve_questions_path(track, questions_path)
    except FileNotFoundError as exc:
        raise EvaluationError(str(exc)) from exc

    try:
        target = parse_repo_input(repo)
    except ValueError as exc:
        raise EvaluationError(str(exc)) from exc

    questions = cfg["parse"](questions_path)
    cleanup_path: Path | None = None

    try:
        if target.clone_url:
            _validate_host_tools(track)
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

        roots = find_assignment_roots(
            repo_root,
            scope=search_root if scoped else None,
            track=track,
        )

        if track == TRACK_AVR:
            sources = build_avr_sources_for_repo(
                repo_root, questions, roots, scoped=scoped
            )
            results = evaluate_avr_all(questions, sources)
        else:
            sources = build_sources_for_repo(
                repo_root, questions, roots, scoped=scoped
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

        return EvaluationReport(
            repo=repo,
            repo_label=target.display_label,
            search_path=target.subpath if scoped else None,
            track=track,
            track_label=cfg["label"],
            questions_source=str(questions_path.name),
            total_score=total_score(results),
            max_total=cfg["max_total"],
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
        "track": report.track,
        "track_label": report.track_label,
        "questions_source": report.questions_source,
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
