# Working with parallel agents

Most of SearchedBy was built by Claude Code sessions running at the same time: one coordinating, others on a language, a UX pass, a security review, a set of evaluation cases. That only works if each one gets a real brief and returns a real deliverable.

## The brief

Every sub-task starts with a written brief:

- **goal** in one or two sentences;
- **base**: which commit or folder to copy from, and that production is not touched;
- **scope**: what is in, what is out;
- **budget**: estimated cost, usually US$ 0 (no scans, no paid APIs, no emails);
- **deliverable**: where it lands and in what form.

## The deliverable

A sub-task never deploys. It returns:

- a working copy with the change, built on a named base and reproducible with a script;
- a deploy checklist with the file list against production, test counts on both Python versions, and its open decisions for me;
- a short report: what it did, what it did not do, what it could not verify.

The coordinating session deploys, after my OK, one change at a time.

## Conflicts between parallel changes

- File lists are computed against production, so two changes that touch different files can go in any order.
- When two changes touch the same file, the second one is re-applied as an edit plan on the new production tree and its suites run again.
- Each checklist has a section "watch the order" naming the other pending changes it overlaps with.

## Shared files

Diary, backlog and decision log are shared by every session. Rules: append only, with an anchored edit, re-reading the end of the file right before writing; never rewrite the whole file; each session prefixes its diary lines with its name.

## Cloud sessions

They work on their own branches of a private repository and never on main. Their reports and patches come back to my machine automatically; their code reaches production only through the same checklist as everything else ([ADR-0008](adr/0008-cloud-sessions-on-branches.md)).
