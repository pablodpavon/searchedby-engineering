# ADR-0007: State the cost before spending, record the real cost after

Accepted · 25 Oct 2026 · log entry D96

## Context

Agent reviews, blind sets and real scans all spend money. In the days before the first launch, review rounds kept finding smaller and smaller details.

## Decision

- Before any scan, paid API call or review by agents, the agent states the estimated cost first.
- At most one independent review and one blind set per deploy. If the candidate clearly beats production and has no serious errors, it ships and edge cases go to the backlog.
- Every engine run logs tokens in and out, search calls and cost, so estimates can be replaced by real numbers.
- Caps per scan and per day are enforced in code.

## Consequences

- The first estimate, from official list prices with token volumes marked as assumptions, put a 10-run scan at US$ 0.08–0.16. A real scan with 15 engine runs on 1 Nov 2026 cost US$ 0.2333. Real runs are logged, so the next estimate starts from them.
- "Close the scope" became a rule of its own: define it, test it, ship it.
