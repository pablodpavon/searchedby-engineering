"""Compute the exact list of files a deploy changes, measured against production.

The base is always the tree that is in production (or its manifest), never
another working copy. That keeps two parallel changes from silently undoing
each other: each one lists only what it changes relative to what is live.

    python -m shiptools.deploylist BASE CANDIDATE [--include app tests] [--tsv out.tsv]

Output columns: status (changed / new / removed), path, md5 in base, md5 in
candidate. Exit code 0 when the lists were written, 2 on bad input.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .manifest import DEFAULT_EXCLUDES
from .parity import compare, load

HEADER = ("status", "path", "md5_base", "md5_candidate")


@dataclass(frozen=True)
class Entry:
    status: str  # "changed" | "new" | "removed"
    path: str
    md5_base: str
    md5_candidate: str

    def row(self) -> tuple[str, str, str, str]:
        return (self.status, self.path, self.md5_base, self.md5_candidate)


def deploy_list(base: dict[str, str], candidate: dict[str, str]) -> list[Entry]:
    rep = compare(base, candidate)
    out = [Entry("changed", p, base[p], candidate[p]) for p in rep.differ]
    out += [Entry("new", p, "-", candidate[p]) for p in rep.only_right]
    out += [Entry("removed", p, base[p], "-") for p in rep.only_left]
    order = {"changed": 0, "new": 1, "removed": 2}
    return sorted(out, key=lambda e: (order[e.status], e.path))


def to_tsv(entries: list[Entry]) -> str:
    rows = [HEADER] + [e.row() for e in entries]
    return "\n".join("\t".join(r) for r in rows) + "\n"


def to_table(entries: list[Entry]) -> str:
    """Fixed-width text, ready to paste into a deploy checklist."""
    if not entries:
        return "no differences against the base\n"
    w = max(len(e.path) for e in entries)
    lines = [f"{'status':<8}  {'path':<{w}}  {'md5_base':<32}  md5_candidate"]
    lines += [f"{e.status:<8}  {e.path:<{w}}  {e.md5_base:<32}  {e.md5_candidate}" for e in entries]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="shiptools.deploylist", description=__doc__.splitlines()[0])
    ap.add_argument("base", help="production tree or its manifest")
    ap.add_argument("candidate", help="working copy with the change")
    ap.add_argument("--include", nargs="*", default=None, help="top-level paths to consider")
    ap.add_argument("--exclude", nargs="*", default=None, help="extra glob patterns to skip")
    ap.add_argument("--tsv", help="also write the list as TSV to this file")
    args = ap.parse_args(argv)
    excludes = DEFAULT_EXCLUDES + tuple(args.exclude or ())
    try:
        base = load(args.base, args.include, excludes)
        cand = load(args.candidate, args.include, excludes)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    entries = deploy_list(base, cand)
    sys.stdout.write(to_table(entries))
    counts = {s: sum(e.status == s for e in entries) for s in ("changed", "new", "removed")}
    print(f"{counts['changed']} changed, {counts['new']} new, {counts['removed']} removed")
    if args.tsv:
        Path(args.tsv).write_text(to_tsv(entries), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
