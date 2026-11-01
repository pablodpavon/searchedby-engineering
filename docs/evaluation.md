# Evaluation with blind sets

Unit tests check that each rule does what it says. They cannot tell whether a change made the product better on cases nobody looked at. For that I use blind sets.

## Method

1. **A separate agent writes the set**, with a short brief: the task in plain words, the languages and how many cases per language, and the labels to produce. It does not see the code, the error analysis or earlier sets.
2. **The set is frozen.** Its sha256 is recorded before the first run.
3. **One run, at the end.** The final candidate and production are measured on the same set, once. No fixing and re-running.
4. **Precision and recall, per language**, compared with a target set in advance.
5. **A spent set is not reused.** The next round of work gets a new set.

## Example: reading which businesses an AI answer recommends

| Round | Set | Production | Candidate | Outcome |
|---|---|---|---|---|
| Deploy A, 25 Oct 2026 | set 3 | P 0.56 · R 0.53 | P 0.80 · R 0.74 | shipped |
| First block, 28 Oct | set 4, 70 cases (es 15, en 15, de 25, he 15) | | P 0.88 · R 0.80, German 0.79 | below target, second block built from its errors |
| Second block, 28 Oct | set 5, 70 new cases | P 0.84 · R 0.83 | P 0.90 · R 0.85, German 0.77 → 0.85 | target met |

German got more cases in set 4 because it was the weakest language.

## Limits

- Sets are small (70 cases). They detect clear improvements and regressions, not differences of a point or two.
- The cases are written by a model. A native speaker reviews the language-specific parts of the product, not every case in every set.
- No client data is used to build sets.
