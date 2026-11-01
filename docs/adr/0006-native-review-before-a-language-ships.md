# ADR-0006: No language ships without a native reader

Accepted · 25–30 Oct 2026 · log entries D117, D125

## Context

The interface is in English, Spanish, German and Hebrew. A model translates well enough to look right to someone who does not speak the language, which is exactly the risk: nobody on the project could judge the Hebrew or the German.

## Decision

- Each language has a versioned glossary and style guide. Terms are chosen from real pages in that language before any text is written: the Hebrew guide started from 42 Hebrew pages on 32 domains, each term marked high, medium or low confidence.
- A language stays hidden until a native speaker has reviewed it. The Hebrew interface was off until its first native review, and parts of German stayed hidden for the same reason.
- After that first review, new phrases without review go on a list for the next round, and I decide case by case whether they can go out before it.
- Review packages are written in the reviewer's own language.
- When reviewers disagree, the conflicts go to me as a short list of decisions, not into the code.
- Glossary versions are never overwritten. By 1 Nov 2026: Hebrew v7, German v3, Spanish v2.

## Consequences

- Languages ship later than the code that supports them.
- Glossary changes reach the code as a normal deploy, with tests and a checklist.
