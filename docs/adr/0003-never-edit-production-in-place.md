# ADR-0003: Production is never edited in place

Accepted · 30 Oct 2026 · project rule 4, log entry D121

## Context

Several changes were in progress at once: a new interface language, a new AI engine, a redesigned result page, security fixes. Each lived in its own working copy. When one copy was deployed and the next was built on an older base, files from the first change could be silently reverted.

## Decision

- The folder that matches production is touched only at deploy time. All work happens in a dated working copy made from it.
- Before a deploy copies anything into production, the originals of every file it touches are copied to a folder named with the date, time and reason.
- The list of files a deploy changes is always computed against production, never against another working copy (`shiptools.deploylist` does this).
- A change that must survive a moving base is written as an anchored edit plan (`shiptools.anchored_edit`): if production moved, the plan is re-applied to a fresh copy and the suites run again.

## Consequences

- Rolling back a file is a copy from a named folder, without archaeology.
- The deploy checklist carries the exact list with the md5 on both sides, so the person running it can check what goes up.
- More disk use and more folders. Worth it.
