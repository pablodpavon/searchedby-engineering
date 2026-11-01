# Languages and native review

The interface is in English, Spanish, German and Hebrew, and each market is asked questions in its own language. Nobody on the project is a native speaker of German or Hebrew, so the process assumes my own judgement is useless there.

## 1. Corpus before glossary

Before writing interface text in a language, the agent reads real pages in that language from businesses in the same field: agencies, local tools, press, and the official help pages of the search engines. For Hebrew the first corpus was 42 pages from 32 domains. Sources are ranked: native local businesses for tone and commercial terms, official help pages for canonical technical terms, translated international sites only as proof that a term is understood.

## 2. Versioned glossary and style guide

Each term gets a choice, its alternatives, the evidence, and a confidence level (high, medium, low). Low-confidence terms go to the reviewer no matter what. Versions are never overwritten; by 1 Nov 2026: Hebrew v7, German v3, Spanish v2.

## 3. Native review

- Review packages are written in the reviewer's language, as numbered questions.
- Answers are integrated into a new glossary version, counted ("17 confirm, 24 change, 7 doubtful" in one Hebrew round).
- When two reviewers disagree with each other or with production, the conflicts go to me as a short list of decisions.
- A language stays hidden until its first native review. After that, new phrases without review are listed for the next round, and I decide whether they can go out before it.

## 4. Into the code

Glossary changes are a normal deploy: tests that pin the new wording per language, both suites, a checklist, my OK, md5 parity. Right-to-left layout is checked in a headless browser at desktop and phone widths.

## Variants

Spanish has a neutral version and a regional one for Argentina, built as an overlay on top of the neutral text, so a change in the base reaches both.
