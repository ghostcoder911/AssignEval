"""Cross-compile AVR submissions for ATmega328P."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AvrCompileResult:
    success: bool
    message: str
    warnings: list[str]


def _strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
    return code


def _ensure_avr_includes(code: str) -> str:
    if "#include" in code and ("avr/io" in code or "avr/io.h" in code):
        return code
    header = (
        "#include <avr/io.h>\n"
        "#include <avr/interrupt.h>\n"
        "#include <util/delay.h>\n"
    )
    return header + code


def _stub_main_if_missing(code: str) -> str:
    if re.search(r"\bmain\s*\(", code):
        return code
    return code + "\nint main(void) { while(1) {} return 0; }\n"


def compile_avr_source(code: str, work_dir: Path | None = None) -> AvrCompileResult:
    if not shutil.which("avr-gcc"):
        return AvrCompileResult(
            False,
            "avr-gcc not installed. Install: sudo apt install gcc-avr avr-libc",
            [],
        )

    cleanup = work_dir is None
    if work_dir is None:
        work_dir = Path(tempfile.mkdtemp(prefix="assigneval_avr_"))

    src = work_dir / "submission.c"
    patched = _stub_main_if_missing(_ensure_avr_includes(code))
    src.write_text(patched, encoding="utf-8")

    cmd = [
        "avr-gcc",
        "-mmcu=atmega328p",
        "-Wall",
        "-Wextra",
        "-Os",
        "-c",
        str(src),
        "-o",
        str(work_dir / "submission.o"),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        result = AvrCompileResult(False, "Compilation timed out.", [])
    else:
        out = (proc.stderr or "") + (proc.stdout or "")
        warnings = [ln for ln in out.splitlines() if "warning:" in ln.lower()]
        if proc.returncode != 0:
            err = out.strip() or "AVR compilation failed."
            result = AvrCompileResult(False, err[:2500], warnings)
        else:
            result = AvrCompileResult(True, "Compiles for ATmega328P.", warnings)

    if cleanup:
        import shutil as sh

        sh.rmtree(work_dir, ignore_errors=True)
    return result
