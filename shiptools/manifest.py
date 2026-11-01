"""Build an md5 manifest of a directory tree.

A manifest maps each file's POSIX path (relative to the tree root) to the md5
of its bytes. It is the shared input of `parity` and `deploylist`.

Only regular files are hashed. Symbolic links are skipped, so a link that
points outside the tree never pulls foreign files into the manifest.
"""
from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path
from typing import Iterable

# Never part of what gets deployed or compared.
DEFAULT_EXCLUDES: tuple[str, ...] = (
    ".git",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".venv",
    "venv",
    ".DS_Store",
    ".env",
    ".env.*",
)

CHUNK = 1 << 16


def md5_file(path: Path) -> str:
    h = hashlib.md5()  # integrity check between two copies, not a security boundary
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _excluded(rel_parts: tuple[str, ...], patterns: Iterable[str]) -> bool:
    for part in rel_parts:
        for pat in patterns:
            if fnmatch.fnmatchcase(part, pat):
                return True
    return False


def build_manifest(root: Path | str, excludes: Iterable[str] = DEFAULT_EXCLUDES,
                   include: Iterable[str] | None = None) -> dict[str, str]:
    """Return {relative_posix_path: md5} for every regular file under root.

    excludes: glob patterns matched against every path component.
    include:  optional top-level folders or files to restrict the manifest to
              (for example ("app", "tests")). Paths are relative to root.
    """
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")
    patterns = tuple(excludes)
    starts = [root / p for p in include] if include else [root]
    out: dict[str, str] = {}
    for start in starts:
        if start.is_symlink():
            continue
        if start.is_file():
            candidates = [start]
        elif start.is_dir():
            candidates = sorted(start.rglob("*"))
        else:
            raise FileNotFoundError(f"include path not found: {start}")
        for p in candidates:
            if p.is_symlink() or not p.is_file():
                continue
            rel = p.relative_to(root)
            if _excluded(rel.parts, patterns):
                continue
            out[rel.as_posix()] = md5_file(p)
    return dict(sorted(out.items()))


def write_manifest(manifest: dict[str, str], dest: Path | str) -> None:
    """Write the manifest in the same format as `md5sum` (hash, two spaces, path)."""
    lines = [f"{digest}  {path}" for path, digest in sorted(manifest.items())]
    Path(dest).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_manifest(src: Path | str) -> dict[str, str]:
    """Read a manifest written by `write_manifest` or by `md5sum` / `md5 -r`."""
    out: dict[str, str] = {}
    for n, line in enumerate(Path(src).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        digest, sep, path = line.partition(" ")
        path = path.lstrip(" *")  # md5sum marks binary mode with '*'
        if not sep or len(digest) != 32 or not path:
            raise ValueError(f"{src}:{n}: not a manifest line: {line!r}")
        out[path] = digest.lower()
    return out
