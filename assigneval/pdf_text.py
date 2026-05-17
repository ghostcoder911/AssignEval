"""Extract text from PDF question documents."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PdfExtractError(Exception):
    """Raised when PDF text cannot be extracted."""


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract plain text from a PDF using pdftotext (poppler-utils)."""
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise PdfExtractError(f"PDF not found: {pdf_path}")

    if not shutil.which("pdftotext"):
        raise PdfExtractError(
            "pdftotext is not installed. Install with: sudo apt install poppler-utils"
        )

    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        msg = (exc.stderr or exc.stdout or "pdftotext failed").strip()
        raise PdfExtractError(msg) from exc
    except subprocess.TimeoutExpired as exc:
        raise PdfExtractError("PDF extraction timed out.") from exc

    text = proc.stdout or ""
    if len(text.strip()) < 50:
        raise PdfExtractError("PDF appears empty or could not be read.")
    return text


def load_document_text(path: Path) -> str:
    """Load question document text from .pdf or .md."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return extract_pdf_text(path)
    return path.read_text(encoding="utf-8", errors="replace")
