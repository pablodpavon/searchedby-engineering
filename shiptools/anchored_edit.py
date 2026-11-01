"""Apply a reviewed set of text edits to a working copy, safely and only once.

An edit plan is a JSON list of {"file", "anchor", "replacement"} objects.
Before anything is written, every anchor must appear exactly once in its
file, and no replacement may already be present. If any check fails, no file
is touched. This makes a change reproducible on top of a newer base: when
production moves, you re-apply the same plan to a fresh copy instead of
copying files over each other.

    python -m shiptools.anchored_edit PLAN.json ROOT [--dry-run]

Exit code 0 when applied (or would apply), 1 when a check failed, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Edit:
    file: str
    anchor: str
    replacement: str


class PlanError(Exception):
    """The plan cannot be applied as written; nothing was changed."""


def load_plan(path: Path | str) -> list[Edit]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("plan must be a JSON list")
    edits = []
    for i, item in enumerate(raw):
        try:
            e = Edit(str(item["file"]), str(item["anchor"]), str(item["replacement"]))
        except (KeyError, TypeError) as exc:
            raise ValueError(f"edit #{i}: needs file, anchor and replacement") from exc
        if not e.anchor:
            raise ValueError(f"edit #{i}: empty anchor")
        if e.anchor == e.replacement:
            raise ValueError(f"edit #{i}: replacement equals anchor")
        edits.append(e)
    return edits


def _safe_path(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if root.resolve() not in p.parents:
        raise PlanError(f"{rel}: path leaves the working copy")
    return p


def check(edits: list[Edit], root: Path | str) -> dict[Path, str]:
    """Validate the whole plan and return the new content per file. Writes nothing."""
    root = Path(root)
    contents: dict[Path, str] = {}
    problems: list[str] = []
    for e in edits:
        p = _safe_path(root, e.file)
        if p not in contents:
            if not p.is_file():
                problems.append(f"{e.file}: file not found")
                continue
            contents[p] = p.read_text(encoding="utf-8")
        text = contents[p]
        n = text.count(e.anchor)
        if e.replacement and e.replacement in text:
            # Conservative on purpose: if the new text is already there, the plan
            # was probably applied before. Refuse rather than apply it twice.
            problems.append(f"{e.file}: replacement already present (plan applied twice?)")
            continue
        if n != 1:
            problems.append(f"{e.file}: anchor found {n} times, expected 1: {e.anchor[:60]!r}")
            continue
        contents[p] = text.replace(e.anchor, e.replacement, 1)
    if problems:
        raise PlanError("; ".join(problems))
    return contents


def apply(edits: list[Edit], root: Path | str, dry_run: bool = False) -> list[Path]:
    """Check everything first, then write. Returns the files that changed."""
    new = check(edits, root)
    if not dry_run:
        for p, text in new.items():
            p.write_text(text, encoding="utf-8")
    return sorted(new)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="shiptools.anchored_edit", description=__doc__.splitlines()[0])
    ap.add_argument("plan", help="JSON edit plan")
    ap.add_argument("root", help="working copy the plan applies to")
    ap.add_argument("--dry-run", action="store_true", help="check only, write nothing")
    args = ap.parse_args(argv)
    try:
        edits = load_plan(args.plan)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        changed = apply(edits, args.root, dry_run=args.dry_run)
    except PlanError as exc:
        print(f"NOT APPLIED: {exc}", file=sys.stderr)
        return 1
    verb = "would change" if args.dry_run else "changed"
    print(f"{len(edits)} edits OK, {verb} {len(changed)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
