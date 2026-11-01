"""Check that two copies of a codebase are byte-identical, file by file.

Typical use after a deploy: write a manifest on the server, copy it back, and
compare it with the tree on your machine. The check passes only if both sides
hold exactly the same set of files with the same md5.

    python -m shiptools.parity LEFT RIGHT [--include app tests] [--exclude PATTERN ...]

LEFT and RIGHT can each be a directory or a manifest file. Exit code 0 means
parity, 1 means a difference, 2 means bad input.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import DEFAULT_EXCLUDES, build_manifest, read_manifest


@dataclass
class ParityReport:
    matched: list[str] = field(default_factory=list)
    differ: list[str] = field(default_factory=list)
    only_left: list[str] = field(default_factory=list)
    only_right: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.differ or self.only_left or self.only_right)

    @property
    def total(self) -> int:
        return len(self.matched) + len(self.differ) + len(self.only_left) + len(self.only_right)

    def summary(self) -> str:
        head = f"{len(self.matched)}/{self.total} identical"
        if self.ok:
            return f"PARITY OK: {head}"
        return (f"PARITY FAILED: {head}; {len(self.differ)} differ, "
                f"{len(self.only_left)} only left, {len(self.only_right)} only right")


def compare(left: dict[str, str], right: dict[str, str]) -> ParityReport:
    rep = ParityReport()
    for path in sorted(set(left) | set(right)):
        if path not in right:
            rep.only_left.append(path)
        elif path not in left:
            rep.only_right.append(path)
        elif left[path] == right[path]:
            rep.matched.append(path)
        else:
            rep.differ.append(path)
    return rep


def load(side: str, include, excludes) -> dict[str, str]:
    p = Path(side)
    if p.is_dir():
        return build_manifest(p, excludes=excludes, include=include)
    if p.is_file():
        m = read_manifest(p)
        if include:
            prefixes = tuple(i.rstrip("/") for i in include)
            m = {k: v for k, v in m.items()
                 if any(k == pre or k.startswith(pre + "/") for pre in prefixes)}
        return m
    raise FileNotFoundError(side)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="shiptools.parity", description=__doc__.splitlines()[0])
    ap.add_argument("left", help="directory or manifest file")
    ap.add_argument("right", help="directory or manifest file")
    ap.add_argument("--include", nargs="*", default=None, help="top-level paths to compare")
    ap.add_argument("--exclude", nargs="*", default=None, help="extra glob patterns to skip")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args(argv)
    excludes = DEFAULT_EXCLUDES + tuple(args.exclude or ())
    try:
        left = load(args.left, args.include, excludes)
        right = load(args.right, args.include, excludes)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rep = compare(left, right)
    if not args.quiet:
        for label, items in (("DIFFER", rep.differ), ("ONLY LEFT", rep.only_left),
                             ("ONLY RIGHT", rep.only_right)):
            for item in items:
                print(f"{label:<10}  {item}")
    print(rep.summary())
    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
