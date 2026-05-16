"""Flask web UI for assignment evaluation."""

from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from assigneval.report import export_report
from assigneval.service import EvaluationError, default_questions_path, report_to_dict, run_evaluation

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

_REPO_PATTERN = re.compile(
    r"^(https?://|git@)[^\s]+$|^[/~][^\s]*$|^[a-zA-Z]:\\[^\s]*$",
    re.IGNORECASE,
)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/evaluate")
def evaluate():
    data = request.get_json(silent=True) or {}
    repo = (data.get("repo") or request.form.get("repo") or "").strip()
    if not repo:
        return jsonify({"error": "Please paste a Git repository URL."}), 400
    if not _REPO_PATTERN.match(repo):
        return jsonify({"error": "Invalid repository URL or path."}), 400

    try:
        report = run_evaluation(repo, default_questions_path())
        return jsonify({"ok": True, "report": report_to_dict(report)})
    except EvaluationError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Evaluation failed: {exc}"}), 500


@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    report = data.get("report")
    fmt = (data.get("format") or "json").lower().strip()
    if not report:
        return jsonify({"error": "No report data to download."}), 400
    try:
        content, mime_type, filename = export_report(report, fmt)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return Response(
        content,
        mimetype=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="AssignEval web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    print(f"AssignEval UI → http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
