# ADR-0002: Tests first, and every suite passes on two Python versions

Accepted · 28 Oct 2026 · project rule 4 for the product

## Context

The agent writes code fast and confidently. A green suite after the change says little if the new tests would also have passed before the change. Separately, my machine runs Python 3.13 and the server runs 3.12, so "it works here" was not evidence for production.

## Decision

- New tests are written first and run against the unchanged copy. They must fail there for the right reason. The count is recorded: for a UX change on 1 Nov, 28 new tests ran on the unchanged copy, 27 failed and 1 passed (the one that asserts other pages keep their examples, which is meant to pass). After the change, 28 of 28 passed.
- The full suites run on Python 3.13 and on 3.12, in separate virtual environments with the same pinned package versions.
- A test that fails once because of timing or browser start-up is re-run before it is judged. If it fails again, it is a failure.

## Consequences

- The suites grew from about 440 pipeline tests and 216 web app tests on 25 Oct to 2,684 and 1,184 on 1 Nov 2026.
- Known gaps left for a later deploy stay in the suite as expected failures, with the reason.
