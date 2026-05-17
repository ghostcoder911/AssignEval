"""Generate evaluation reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from assigneval.evaluator import QuestionResult


def total_score(results: list[QuestionResult]) -> float:
    return round(sum(r.score for r in results), 1)


def format_text_report(
    results: list[QuestionResult],
    repo_label: str,
    max_total: float = 270.0,
) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("ASSIGNMENT EVALUATION REPORT")
    lines.append("=" * 72)
    lines.append(f"Repository : {repo_label}")
    lines.append(f"Evaluated  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Total score: {total_score(results)} / {max_total}")
    lines.append("")

    for r in sorted(results, key=lambda x: x.question.number):
        lines.append("-" * 72)
        lines.append(f"Q{r.question.number:02d} | Score: {r.score:.1f} / {r.max_score:.0f}")
        title = r.question.title
        if len(title) > 68:
            title = title[:65] + "..."
        lines.append(f"     {title}")
        if r.source:
            lines.append(f"     Source: {r.source.origin} (confidence {r.source.confidence:.0%})")
        else:
            lines.append("     Source: NOT FOUND")
        if not r.compile_ok and r.source:
            lines.append(f"     Compile: FAILED — {r.compile_message[:120]}")
        elif r.source:
            lines.append(
                f"     Tests: {r.passed_count}/{r.total_tests} passed"
                if r.total_tests
                else "     Tests: n/a"
            )
        lines.append("     Review:")
        for c in r.review_comments:
            for wrap in _wrap(c, 65):
                lines.append(f"       • {wrap}")
        lines.append("")

    lines.append("=" * 72)
    summary = _summary_stats(results)
    lines.append(
        f"Summary: {summary['full_marks']} full marks | "
        f"{summary['partial']} partial | "
        f"{summary['missing']} missing | "
        f"{summary['compile_fail']} compile errors"
    )
    lines.append("=" * 72)
    return "\n".join(lines)


def _summary_stats(results: list[QuestionResult]) -> dict[str, int]:
    full = partial = missing = compile_fail = 0
    for r in results:
        if r.source is None:
            missing += 1
        elif not r.compile_ok:
            compile_fail += 1
        elif r.score >= 10:
            full += 1
        else:
            partial += 1
    return {
        "full_marks": full,
        "partial": partial,
        "missing": missing,
        "compile_fail": compile_fail,
    }


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for w in words:
        if length + len(w) + 1 > width and current:
            lines.append(" ".join(current))
            current = [w]
            length = len(w)
        else:
            current.append(w)
            length += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def write_json_report(
    path: Path,
    results: list[QuestionResult],
    repo_label: str,
) -> None:
    payload = {
        "repository": repo_label,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_score": total_score(results),
        "max_total": 270.0,
        "questions": [
            {
                "number": r.question.number,
                "title": r.question.title,
                "score": r.score,
                "max_score": r.max_score,
                "source": r.source.origin if r.source else None,
                "confidence": r.source.confidence if r.source else 0,
                "compile_ok": r.compile_ok,
                "tests_passed": r.passed_count,
                "tests_total": r.total_tests,
                "review_comments": r.review_comments,
                "test_details": [
                    {"name": t.name, "passed": t.passed, "detail": t.detail}
                    for t in r.tests
                ],
            }
            for r in results
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_html_report(
    path: Path,
    results: list[QuestionResult],
    repo_label: str,
) -> None:
    rows = []
    for r in sorted(results, key=lambda x: x.question.number):
        status = "missing"
        if r.source and r.compile_ok and r.score >= 10:
            status = "pass"
        elif r.source and r.compile_ok:
            status = "partial"
        elif r.source:
            status = "fail"
        comments = "<br>".join(r.review_comments)
        rows.append(
            f"<tr class='{status}'><td>Q{r.question.number}</td>"
            f"<td>{r.score:.1f}</td>"
            f"<td>{r.source.origin if r.source else '—'}</td>"
            f"<td>{r.passed_count}/{r.total_tests}</td>"
            f"<td>{comments}</td></tr>"
        )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AssignEval Report</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
tr.pass td:nth-child(2) {{ color: #0a0; }}
tr.partial td:nth-child(2) {{ color: #a60; }}
tr.fail td:nth-child(2), tr.missing td:nth-child(2) {{ color: #c00; }}
h1 {{ margin-bottom: 0.2rem; }}
</style></head><body>
<h1>Assignment Evaluation</h1>
<p><strong>Repo:</strong> {repo_label}<br>
<strong>Total:</strong> {total_score(results)} / 270</p>
<table>
<thead><tr><th>Q#</th><th>Score</th><th>Source</th><th>Tests</th><th>Review</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</body></html>"""
    path.write_text(html, encoding="utf-8")


def _status_from_question(q: dict) -> str:
    if not q.get("source"):
        return "missing"
    if not q.get("compile_ok"):
        return "fail"
    if q.get("score", 0) >= 10:
        return "pass"
    if q.get("score", 0) > 0:
        return "partial"
    return "fail"


def format_text_report_from_dict(report: dict) -> str:
    repo_label = report.get("repo_label") or report.get("repo", "")
    if report.get("search_path"):
        repo_label += f" → {report['search_path']}"
    max_total = report.get("max_total", 270.0)
    lines: list[str] = [
        "=" * 72,
        "C ASSIGNMENT EVALUATION REPORT",
        "=" * 72,
        f"Repository : {repo_label}",
        f"Evaluated  : {report.get('evaluated_at', 'n/a')}",
        f"Total score: {report.get('total_score', 0)} / {max_total}",
        "",
    ]
    for q in sorted(report.get("questions", []), key=lambda x: x["number"]):
        lines.append("-" * 72)
        lines.append(
            f"Q{q['number']:02d} | Score: {q['score']:.1f} / {q.get('max_score', 10):.0f}"
        )
        title = q.get("title", "")
        if len(title) > 68:
            title = title[:65] + "..."
        lines.append(f"     {title}")
        if q.get("source"):
            conf = q.get("confidence", 0)
            lines.append(f"     Source: {q['source']} (confidence {conf:.0%})")
        else:
            lines.append("     Source: NOT FOUND")
        if q.get("source") and not q.get("compile_ok"):
            msg = (q.get("compile_message") or "")[:120]
            lines.append(f"     Compile: FAILED — {msg}")
        elif q.get("source"):
            lines.append(
                f"     Tests: {q.get('tests_passed', 0)}/{q.get('tests_total', 0)} passed"
            )
        lines.append("     Review:")
        for c in q.get("review_comments", []):
            for wrap in _wrap(c, 65):
                lines.append(f"       • {wrap}")
        lines.append("")

    summary = report.get("summary", {})
    lines.extend(
        [
            "=" * 72,
            (
                f"Summary: {summary.get('full_marks', 0)} full marks | "
                f"{summary.get('partial', 0)} partial | "
                f"{summary.get('missing', 0)} missing | "
                f"{summary.get('compile_fail', 0)} compile errors"
            ),
            "=" * 72,
        ]
    )
    return "\n".join(lines)


def format_html_report_from_dict(report: dict) -> str:
    import html as html_module

    repo_label = html_module.escape(report.get("repo_label") or report.get("repo", ""))
    search = report.get("search_path")
    if search:
        repo_label += f" → {html_module.escape(search)}"
    rows = []
    for q in sorted(report.get("questions", []), key=lambda x: x["number"]):
        status = _status_from_question(q)
        comments = "<br>".join(html_module.escape(c) for c in q.get("review_comments", []))
        src = html_module.escape(q.get("source") or "—")
        rows.append(
            f"<tr class='{status}'><td>Q{q['number']}</td>"
            f"<td>{q['score']:.1f}</td>"
            f"<td>{src}</td>"
            f"<td>{q.get('tests_passed', 0)}/{q.get('tests_total', 0)}</td>"
            f"<td>{comments}</td></tr>"
        )
    total = report.get("total_score", 0)
    max_total = report.get("max_total", 270)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AssignEval Report</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 1100px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
tr.pass td:nth-child(2) {{ color: #0a0; font-weight: 600; }}
tr.partial td:nth-child(2) {{ color: #a60; font-weight: 600; }}
tr.fail td:nth-child(2), tr.missing td:nth-child(2) {{ color: #c00; font-weight: 600; }}
.meta {{ color: #555; margin-bottom: 1.5rem; }}
</style></head><body>
<h1>Assignment Evaluation Report</h1>
<p class="meta"><strong>Repository:</strong> {repo_label}<br>
<strong>Evaluated:</strong> {html_module.escape(str(report.get('evaluated_at', 'n/a')))}<br>
<strong>Total score:</strong> {total} / {max_total}</p>
<table>
<thead><tr><th>Q#</th><th>Score</th><th>Source</th><th>Tests</th><th>Review</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</body></html>"""


def format_csv_report_from_dict(report: dict) -> str:
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Question",
            "Title",
            "Score",
            "Max Score",
            "Source",
            "Tests Passed",
            "Tests Total",
            "Compile OK",
            "Review Comments",
        ]
    )
    for q in sorted(report.get("questions", []), key=lambda x: x["number"]):
        writer.writerow(
            [
                q["number"],
                q.get("title", ""),
                q.get("score", 0),
                q.get("max_score", 10),
                q.get("source") or "",
                q.get("tests_passed", 0),
                q.get("tests_total", 0),
                q.get("compile_ok", False),
                " | ".join(q.get("review_comments", [])),
            ]
        )
    writer.writerow([])
    writer.writerow(["Total Score", report.get("total_score", 0)])
    writer.writerow(["Max Total", report.get("max_total", 270)])
    writer.writerow(["Repository", report.get("repo_label") or report.get("repo", "")])
    return buf.getvalue()


def export_report(report: dict, fmt: str) -> tuple[str, str, str]:
    """Return (content, mime_type, filename_suffix) for download."""
    slug = _filename_slug(report.get("repo_label") or report.get("repo", "report"))
    if fmt == "json":
        return json.dumps(report, indent=2), "application/json", f"{slug}.json"
    if fmt == "html":
        return format_html_report_from_dict(report), "text/html", f"{slug}.html"
    if fmt == "csv":
        return format_csv_report_from_dict(report), "text/csv", f"{slug}.csv"
    if fmt == "txt":
        return format_text_report_from_dict(report), "text/plain", f"{slug}.txt"
    raise ValueError(f"Unsupported format: {fmt}")


def _filename_slug(label: str) -> str:
    import re

    s = re.sub(r"https?://", "", label)
    s = re.sub(r"[^\w.\-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:80] or "assigneval_report")
