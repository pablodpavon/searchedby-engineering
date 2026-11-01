# Decision records

I keep one numbered decision log for all my projects, SearchedBy included (155 entries by 1 Nov 2026). Each entry has a number, a date and time, what was decided, why, and the source: either my own words, quoted, or "technical decision" when the agent decided within rules I had set.

The eight records below are rewritten from real entries in ADR format. Product specifics (rules, thresholds, prompts) are removed; the reasoning and the numbers that matter for the process are kept.

| ADR | Title | From log entry |
|---|---|---|
| [0001](0001-numbered-decision-log.md) | Every decision gets a number, a date and a source | D83 |
| [0002](0002-tests-first-two-python-versions.md) | Tests first, and every suite passes on two Python versions | product rule 4, 28 Oct |
| [0003](0003-never-edit-production-in-place.md) | Production is never edited in place | product rule 4, D121 |
| [0004](0004-server-equals-mac-by-md5.md) | After a deploy, the server must equal my machine by md5 | product rule 3, D83 |
| [0005](0005-blind-sets-run-once.md) | Measure changes on blind sets, written first and run once | D96, D103, D104 |
| [0006](0006-native-review-before-a-language-ships.md) | No language ships without a native reader | D117, D125 |
| [0007](0007-cost-before-acting.md) | State the cost before spending, record the real cost after | D96 |
| [0008](0008-cloud-sessions-on-branches.md) | Cloud sessions work on branches and never reach production alone | D108, D109, D121 |

## Format

```
# ADR-NNNN: <title>
Status · Date · Log entry
## Context
## Decision
## Consequences
```
