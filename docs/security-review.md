# Security review

On 30 Oct 2026, before opening the beta wider, a Claude Code session in the cloud ran an independent static review of the web app and the deploy scripts. It worked from the repository only, with no access to the server, and was asked to prove each finding with a local proof of concept or a test, and to list what it looked for and did not find.

## Result

14 findings: 2 high, 6 medium, 6 low.

| Class | Severity | How it was closed |
|---|---|---|
| Outbound requests from the scanner could be steered to internal addresses | high | every outbound connection, including the headless browser's, goes through one validating path that resolves once and connects to the validated address; tests reproduce the old behaviour and pass on the fix |
| No hard limit on size and time per download | high | hard caps on bytes and total time per fetch, and a failed job is not re-queued forever; tests with oversized and slow responses |
| Name resolution checked separately from the connection | medium | closed by the same validating path |
| Missing rate limits on invitation and admin endpoints | medium | per-network limits with a lock-out window, tested |
| A secret could fall back to a weaker one | medium | the secret is mandatory; the app refuses to start without it |
| Unlimited feedback submissions triggering email | medium | per-scan limit, tested |
| A few address ranges not blocked by the guard | low | blocked, tested |

The remaining items (one medium, five low) are hardening at the server, CDN and backup level. They were written up as recommendations; this page does not claim them as closed.

## How the fixes were shipped

1. A second cloud session wrote the fixes on its own branch: 29 new tests in the pipeline and 16 in the web app, each failing on the old code and passing on the branch, with both suites green on Python 3.13 and 3.12.
2. The branch was integrated into a local working copy with the normal checklist, after my OK.
3. On the server, after the deploy: md5 parity on all 178 code files and **35 security tests passed** on the server itself.

## Documented versus implemented

The review also compared what the README promised with what the code did, and found five mismatches (limits that were weaker than documented, a setting documented as required that was optional). Three of them were closed by the fixes above; the other two belong to the remaining low-severity items.

## What this page leaves out

Exact file locations, payloads, configuration and anything that would help reproduce an attack on a version that is still running.
