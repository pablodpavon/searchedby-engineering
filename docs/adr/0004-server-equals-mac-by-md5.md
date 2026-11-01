# ADR-0004: After a deploy, the server must equal my machine by md5

Accepted · 25 Oct 2026 · project rule 3, log entry D83

## Context

The suites prove the code on my machine. They prove nothing about the server if a file was missed, copied twice from different copies, or edited on the server during a fix.

## Decision

- Every deploy ends with an md5 comparison of all code files between the server and my machine, not only the files that changed.
- Anything that changes on the server is copied back to my machine at once and verified by md5. The local folder stays the single source of truth.
- The result is written in the deploy record: for example 178 of 178 files on 30 Oct after the security deploy, and 197 of 197 later that day.

## Consequences

- A partial upload is caught in seconds instead of when a user hits the missing file.
- `shiptools.parity` is the generic version of this check.
