# ADR-0008: Cloud sessions work on branches and never reach production alone

Accepted · 30 Oct 2026 · log entries D108, D109, D121

## Context

Cloud sessions of Claude Code can run long reviews in parallel with local work, but they need the code in a repository, and they have no access to my machine or the server.

## Decision

- The product folder is a private repository. My machine is the source: a sync job commits local changes to the main branch every five minutes.
- Cloud sessions branch from main and work on their own branches. They never push to main.
- The same sync job brings their reports and code changes back as a patch into a folder on my machine, with an index. Nothing from a cloud branch is applied automatically.
- A cloud branch reaches production only through the normal path: integration in a working copy, both suites, deploy checklist, my OK, md5 parity.
- The sync stops if a change looks like it contains a key or a file larger than 10 MB.

## Consequences

- The independent security review ran this way: a cloud session audited, a second one fixed on a branch, and the integration was deployed after my OK (see [security review](../security-review.md)).
- Integration is a real step with its own checklist, not a merge button.
