"""Discover C assignment sources inside a cloned repository."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class CodeSource:
    """A C program candidate mapped to a question."""

    question_number: int | None
    path: Path | None  # None if extracted to temp only
    code: str
    origin: str  # e.g. "file:assignment1.c", "readme:section-3"
    confidence: float = 0.0


C_FOLDER_HINTS = (
    "c programming",
    "c_programming",
    "c-programming",
    "c assignments",
    "c_assignments",
    "c basics",
    "assignments",
)

README_NAMES = ("readme.md", "README.md", "Readme.md", "assignments.md")


def clone_repo(
    repo_url: str,
    dest: Path | None = None,
    branch: str | None = None,
) -> Path:
    parsed = urlparse(repo_url)
    if parsed.scheme not in ("http", "https", "git", ""):
        raise ValueError(f"Unsupported repo URL: {repo_url}")
    url = repo_url if repo_url.endswith(".git") else repo_url.rstrip("/") + ".git"
    if dest is None:
        tmp = tempfile.mkdtemp(prefix="assigneval_")
        dest = Path(tmp) / "repo"
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)

    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch, "--single-branch"])
    cmd.extend([url, str(dest)])

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return dest


def resolve_search_root(repo_root: Path, subpath: str) -> Path:
    """Resolve optional in-repo subfolder from a GitHub tree URL."""
    if not subpath:
        return repo_root
    target = repo_root / subpath
    if target.is_dir():
        return target
    # case-insensitive match (helps on case-sensitive filesystems)
    sub_lower = subpath.lower()
    for candidate in repo_root.rglob("*"):
        if candidate.is_dir():
            rel = str(candidate.relative_to(repo_root)).replace("\\", "/")
            if rel.lower() == sub_lower:
                return candidate
    raise FileNotFoundError(
        f"Folder not found in repository: {subpath}\n"
        "Check that the branch and path in your GitHub link are correct."
    )


def use_local_path(path: str | Path) -> Path:
    p = Path(path).resolve()
    if not p.is_dir():
        raise FileNotFoundError(f"Not a directory: {p}")
    return p


def find_c_assignment_roots(repo_root: Path, scope: Path | None = None) -> list[Path]:
    """Find folders that likely contain assignment .c files.

    If *scope* is set (from a GitHub tree/folder URL), search only under it
    and always include the scope directory itself.
    """
    base = scope if scope is not None else repo_root
    if not base.is_dir():
        raise FileNotFoundError(f"Search path is not a directory: {base}")

    roots: list[Path] = []
    # When user points to a specific folder, treat it as the primary root.
    if scope is not None:
        roots.append(scope)

    search_in = base
    for path in search_in.rglob("*"):
        if not path.is_dir():
            continue
        if scope is not None and scope not in path.parents and path != scope:
            continue
        name = path.name.lower()
        if any(h in name for h in C_FOLDER_HINTS):
            roots.append(path)

    roots.sort(
        key=lambda p: (
            0 if scope is not None and p == scope else 1,
            0 if "c programming" in p.name.lower() else 1,
            len(str(p)),
        )
    )

    if not roots or (scope is not None and len(roots) == 1):
        for path in base.rglob("*.c"):
            if _is_likely_assignment(path):
                roots.append(path.parent)
        roots = list(dict.fromkeys(roots))

    if scope is not None and scope not in roots:
        roots.insert(0, scope)

    return roots or [base]


def _is_likely_assignment(path: Path) -> bool:
    skip = ("stm32", "esp32", "avr", "driver", "hal", "cmsis", "node_modules")
    low = str(path).lower()
    return path.suffix == ".c" and not any(s in low for s in skip)


def collect_c_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        for path in root.rglob("*.c"):
            if not _is_likely_assignment(path):
                continue
            rp = path.resolve()
            if rp not in seen:
                seen.add(rp)
                files.append(path)
    return files


def extract_readme_sections(root: Path, scoped: bool = False) -> dict[int, str]:
    """Parse README numbered sections with embedded C code blocks."""
    sections: dict[int, str] = {}
    for readme_name in README_NAMES:
        for readme in root.rglob(readme_name):
            if not _path_under_assignment_area(readme, scoped=scoped):
                continue
            text = readme.read_text(encoding="utf-8", errors="replace")
            sections.update(_parse_numbered_sections(text, str(readme)))
    return sections


def _path_under_assignment_area(path: Path, scoped: bool = False) -> bool:
    if scoped:
        return path.name.lower() in {n.lower() for n in README_NAMES}
    low = str(path).lower()
    if any(h.replace(" ", "") in low.replace(" ", "") for h in C_FOLDER_HINTS):
        return True
    if "c programming" in low or "c assignment" in low:
        return True
    if path.parent.name.lower() in ("src", "source", "sources", "c", "code"):
        return path.name.lower() in {n.lower() for n in README_NAMES}
    return path.name.lower() in README_NAMES and path.parent.name.lower() in (
        "c programming",
        "c assignments",
        "assignments",
    )


_SECTION_HEADER = re.compile(
    r"^#+\s*(\d{1,2})\s*[\.\)]\s*", re.MULTILINE
)
_CODE_BLOCK = re.compile(r"```(?:c)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _parse_numbered_sections(text: str, origin: str) -> dict[int, str]:
    result: dict[int, str] = {}
    # split by ## N. headers
    parts = re.split(r"(?m)^#+\s*(\d{1,2})\s*[\.\)]\s*", text)
    if len(parts) < 3:
        return result
    # parts[0] is preamble, then pairs (num, content)
    i = 1
    while i + 1 < len(parts):
        try:
            num = int(parts[i])
        except ValueError:
            i += 2
            continue
        content = parts[i + 1]
        blocks = _CODE_BLOCK.findall(content)
        for block in blocks:
            if "#include" in block and "main" in block:
                result[num] = block.strip()
                break
        i += 2
    return result


def read_file_sources(files: list[Path]) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for f in files:
        try:
            code = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "#include" in code or "main" in code or "void " in code:
            out.append((f, code))
    return out


def guess_question_from_filename(path: Path) -> int | None:
    name = path.stem.strip().lower()
    patterns = [
        r"^(\d{1,2})[_\s]",  # 1_Even or Odd, 10_String of Digits...
        r"^(\d{1,2})(?=[A-Za-z])",  # 2Prime Number, 22SecondLargest...
        r"(?:assignment|assign|q|question|prob|ex)[_\s-]*(\d{1,2})",
        r"^(\d{1,2})$",
        r"^q(\d{1,2})$",
    ]
    for pat in patterns:
        m = re.search(pat, name)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 27:
                return n
    return None
