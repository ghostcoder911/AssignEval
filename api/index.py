"""Vercel serverless entrypoint for AssignEval Flask app."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assigneval.web.app import app  # noqa: E402
