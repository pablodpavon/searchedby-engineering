# ADR-0005: Measure changes on blind sets, written first and run once

Accepted · 25–28 Oct 2026 · log entries D96, D103, D104

## Context

One part of the scan reads AI answers and decides which businesses they recommend. The agent fixed errors case by case, and every fix passed its own test. Measured only on the cases the fixes were built from, quality looks better than it is.

## Decision

- Before any code changes, a separate agent writes a new blind set. It sees neither the code, nor the analysis of the errors, nor earlier sets.
- The set file is hashed (sha256) before the first run, so it cannot be adjusted after seeing results.
- It runs once, on the final candidate and on production, and both numbers are reported.
- A set that has been run is spent. The next round gets a new one.

## Consequences

| Set | Cases | Production | Candidate |
|---|---|---|---|
| 3 | — | precision 0.56, recall 0.53 | precision 0.80, recall 0.74 |
| 4 | 70 (es 15, en 15, de 25, he 15) | | precision 0.88, recall 0.80; German 0.79, below target |
| 5 | 70, new | precision 0.84, recall 0.83 | precision 0.90, recall 0.85; German 0.77 -> 0.85, target met |

- Set 4 missing its target is the reason a second round of fixes existed.
- Writing a set costs an agent run, so it falls under ADR-0007: at most one blind set per deploy.
