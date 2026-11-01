# ADR-0001: Every decision gets a number, a date and a source

Accepted · 25 Oct 2026 · log entry D83

## Context

Most of the code is written by an AI agent across many sessions. A session can be compacted or end at any moment, and with it goes whatever was only in the conversation. Documenting only at the end of a session left that risk open for the whole session.

## Decision

After every action, and before answering me, the agent writes things down:

- a line in the day's diary with the Berlin time: what was done, the state it was left in, and the next step;
- each decision, mine or technical, in the decision log with a number, date, time and source;
- open items that appear, change or close, in the backlog;
- each message I send, with its time and status.

A log entry looks like this (sanitized):

```
D96 (25 Oct 2026, 18:42–18:50). Close the scope of deploy A; rule against overspending.
  In: fixes D01–D08, D10–D13, D19–D24, each with a test written first.
  Out: D09, D14–D18 (details), marked as pending in the tests.
  Measurement: blind set 3, run once on the final copy.
    precision 0.56 -> 0.80, recall 0.53 -> 0.74 against production.
  New rule: state the cost before any review by agents; at most one independent
    review and one blind set per deploy; if the candidate clearly beats production
    and has no serious errors, it ships and edge cases go to the backlog.
  Source: owner, 18:42 ("launch deploy A now").
```

## Consequences

- Any session, local or in the cloud, can pick up the work by reading the folder.
- Answers take a minute or two longer. I accepted that in writing: losing an hour of work to a lost context costs more.
- When two entries collide (two sessions take the same number), the later one is renumbered and says so in the entry.
