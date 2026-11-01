# Testing strategy

## What the suites cover

Two suites, one per component, all offline:

| Suite | Tests (1 Nov 2026) | What it exercises |
|---|---|---|
| Pipeline | 2,684 | crawler and checks against local fixture sites, reading of AI answers, findings, report text per language, a set of golden control scans |
| Web app | 1,184 | form and email-code flow, anti-abuse limits, result page per language and screen width, admin, legal pages, a headless browser pass |

The suites are built to run offline: no paid API, no real website, no server. Engines are replaced by recorded or synthetic answers, and sites by local fixtures served on 127.0.0.1.

## Rules

1. **Red first.** New tests run against the unchanged copy and must fail for the reason they describe. The count goes into the deploy checklist ("28 new tests on the unchanged copy: 27 fail, 1 passes by design").
2. **Two Python versions.** Every suite passes on Python 3.13 (my machine) and 3.12 (the server), each in its own virtual environment with the same pinned versions.
3. **Re-run before judging a flaky test.** A single failure from timing or browser start-up is repeated once. A second failure counts.
4. **Known gaps stay visible.** Work deferred to a later deploy is kept as expected failures with the reason, so it shows up in every run.
5. **Tests are named after the change.** Each change adds its own test file named with the topic and the date, so the history of a rule can be read from the test folder.
6. **Security fixes come with a test that reproduces the problem.** It fails on the old code and passes on the fix (29 such tests in the pipeline and 16 in the web app for the October review).

## What tests do not prove

- Whether a translation is right. That is [native review](multilingual.md).
- Whether quality improved overall. That is a [blind set](evaluation.md), run once.
- Whether the server runs the tested code. That is the [md5 parity check](deploy.md).
