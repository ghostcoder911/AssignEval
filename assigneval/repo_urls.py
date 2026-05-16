"""Parse GitHub repository and folder URLs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import unquote, urlparse


@dataclass(frozen=True)
class RepoTarget:
    """Resolved clone target and optional in-repo subfolder."""

    original_url: str
    clone_url: str
    owner: str
    repo: str
    branch: str | None
    subpath: str  # relative path inside repo (may be empty)
    display_label: str


_GITHUB_HOSTS = {"github.com", "www.github.com"}

# github.com/owner/repo/tree/branch/path/to/folder
_TREE_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)/tree/(?P<branch>[^/]+)(?:/(?P<subpath>.*))?$",
    re.IGNORECASE,
)

# github.com/owner/repo/blob/branch/path/to/file.c
_BLOB_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)/blob/(?P<branch>[^/]+)(?:/(?P<subpath>.*))?$",
    re.IGNORECASE,
)

# github.com/owner/repo  (no tree/blob)
_ROOT_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)/?$",
    re.IGNORECASE,
)


def parse_repo_input(raw: str) -> RepoTarget:
    """Parse a GitHub repo URL, tree folder URL, blob file URL, or local path."""
    text = raw.strip().rstrip("/")
    if not text:
        raise ValueError("Empty repository URL.")

    # Local path
    if text.startswith(("/", "~")) or re.match(r"^[a-zA-Z]:\\", text):
        return RepoTarget(
            original_url=text,
            clone_url="",
            owner="",
            repo="",
            branch=None,
            subpath="",
            display_label=text,
        )

    if text.startswith("git@"):
        # git@github.com:owner/repo.git
        m = re.match(r"git@github\.com:(?P<owner>[^/]+)/(?P<repo>.*?)(?:\.git)?$", text)
        if not m:
            raise ValueError("Unsupported git@ URL format.")
        owner, repo = m.group("owner"), m.group("repo").removesuffix(".git")
        clone = f"https://github.com/{owner}/{repo}.git"
        return RepoTarget(text, clone, owner, repo, None, "", clone)

    parsed = urlparse(text)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")

    host = (parsed.netloc or "").lower().removeprefix("www.")
    if host not in _GITHUB_HOSTS:
        raise ValueError("Only github.com URLs are supported for remote evaluation.")

    path = unquote(parsed.path or "").strip("/")
    # strip trailing .git from path segments if user pasted clone URL
    path = re.sub(r"\.git$", "", path, flags=re.IGNORECASE)

    for pattern, is_blob in ((_TREE_RE, False), (_BLOB_RE, True), (_ROOT_RE, False)):
        m = pattern.search(f"github.com/{path}")
        if not m:
            continue
        owner = m.group("owner")
        repo = m.group("repo").removesuffix(".git")
        branch = m.groupdict().get("branch")
        subpath = (m.groupdict().get("subpath") or "").strip("/")

        if is_blob and subpath:
            leaf = subpath.rsplit("/", 1)[-1]
            # If user links to a single .c file, search its parent folder
            if "." in leaf and leaf.lower().endswith(".c"):
                parts = subpath.split("/")
                subpath = "/".join(parts[:-1]) if len(parts) > 1 else ""

        clone = f"https://github.com/{owner}/{repo}.git"
        label = f"{owner}/{repo}"
        if branch and subpath:
            label += f" @ {branch}/{subpath}"
        elif branch:
            label += f" @ {branch}"
        return RepoTarget(text, clone, owner, repo, branch, subpath, label)

    raise ValueError(
        "Unrecognized GitHub URL. Use a repo link or a folder link like "
        "https://github.com/user/repo/tree/main/path/to/Src"
    )


def PathLeaf(path: str) -> str:
    return path.rsplit("/", 1)[-1]
