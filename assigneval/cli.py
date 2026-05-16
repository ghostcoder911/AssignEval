#!/usr/bin/env python3
"""Command-line interface for AssignEval."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assigneval import __version__
from assigneval.report import format_text_report, write_html_report, write_json_report
from assigneval.service import EvaluationError, default_questions_path, run_evaluation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate student C programming assignments from a Git repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  assigneval https://github.com/Karthikmg25/Embedded-System.git
  assigneval "https://github.com/user/repo/tree/main/C programming/Src"
  assigneval /path/to/local/repo --questions "C Assignment Questions BASIC REFRESHER.md"
  assigneval https://github.com/user/repo.git -o report.json --format json
        """,
    )
    parser.add_argument(
        "repo",
        help="GitHub repo URL, GitHub folder URL (/tree/branch/path), or local directory",
    )
    parser.add_argument(
        "-q",
        "--questions",
        default="C Assignment Questions BASIC REFRESHER.md",
        help="Path to questions markdown file (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write report to this file (extension sets format: .json, .html, else text)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "html"),
        help="Report format (default: infer from -o or text)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print discovery details",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)
    questions_path = Path(args.questions)
    if not questions_path.is_file():
        print(f"Error: questions file not found: {questions_path}", file=sys.stderr)
        return 1

    try:
        report = run_evaluation(args.repo, questions_path)
    except EvaluationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        if report.search_path:
            print(f"Search folder: {report.search_path}", file=sys.stderr)
        print(f"Matched {report.matched_count}/{report.questions_parsed} questions", file=sys.stderr)
        for d in report.discovery:
            print(f"  Q{d.question_number:02d}: {d.origin} ({d.confidence:.0%})", file=sys.stderr)

    repo_label = report.repo_label or args.repo
    report_text = format_text_report(report.results, repo_label)

    fmt = args.format
    if args.output:
        ext = Path(args.output).suffix.lower()
        if fmt is None:
            fmt = {".json": "json", ".html": "html", ".htm": "html"}.get(ext, "text")
    fmt = fmt or "text"

    if args.output:
        out = Path(args.output)
        if fmt == "json":
            from assigneval.service import report_to_dict
            import json

            out.write_text(
                json.dumps(report_to_dict(report), indent=2),
                encoding="utf-8",
            )
        elif fmt == "html":
            write_html_report(out, report.results, repo_label)
        else:
            out.write_text(report_text, encoding="utf-8")
        print(f"Report written to {out}")
    else:
        print(report_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
