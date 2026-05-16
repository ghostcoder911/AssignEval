"""Compile and run student C programs."""

from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompileResult:
    success: bool
    binary: Path | None
    message: str
    source_path: Path


@dataclass
class RunResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False


def _ensure_main(code: str) -> str:
    if re.search(r"\bmain\s*\(", code):
        return code
    return code + "\nint main(void){return 0;}\n"


def _patch_void_main(code: str) -> str:
    return re.sub(r"\bvoid\s+main\s*\(", "int main(", code)


def write_source(code: str, directory: Path, name: str = "submission.c") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    patched = _patch_void_main(_ensure_main(code))
    path.write_text(patched, encoding="utf-8")
    return path


def compile_c(source: Path, work_dir: Path) -> CompileResult:
    binary = work_dir / "a.out"
    cmd = [
        "gcc",
        str(source),
        "-o",
        str(binary),
        "-std=c11",
        "-Wall",
        "-Wno-unused-result",
        "-lm",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=work_dir,
        )
    except FileNotFoundError:
        return CompileResult(
            success=False,
            binary=None,
            message="gcc not found. Install build-essential.",
            source_path=source,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(
            success=False,
            binary=None,
            message="Compilation timed out.",
            source_path=source,
        )

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "Compilation failed.").strip()
        return CompileResult(False, None, err[:2000], source)

    return CompileResult(True, binary, "OK", source)


def run_binary(
    binary: Path,
    stdin: str,
    timeout: float = 5.0,
) -> RunResult:
    try:
        proc = subprocess.run(
            [str(binary)],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=binary.parent,
        )
        return RunResult(
            success=proc.returncode == 0 or bool(proc.stdout),
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            returncode=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        return RunResult(False, "", "", -1, timed_out=True)
    except OSError as exc:
        return RunResult(False, "", str(exc), -1)


def run_source_code(
    code: str,
    stdin: str,
    work_dir: Path,
    timeout: float = 5.0,
) -> tuple[CompileResult, RunResult | None]:
    src = write_source(code, work_dir)
    comp = compile_c(src, work_dir)
    if not comp.success or comp.binary is None:
        return comp, None
    run = run_binary(comp.binary, stdin, timeout=timeout)
    return comp, run
