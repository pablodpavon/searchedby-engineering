# Cost model

## What costs money in a scan

| Part | Model or service | Marginal cost |
|---|---|---|
| Technical checks, rendering, report | none (code and templates) | US$ 0 |
| AI sample: ChatGPT, Perplexity, Claude | each engine's API | per run: tokens plus search fees |
| Google AI Overviews / AI Mode | a SERP data provider | per query |
| My review of the result | interactive session | outside the per-scan cost |

## Estimate first

On 24 Oct 2026, before the first real scan, the estimate used official list prices (checked that day on each provider's pricing page) and token volumes marked as assumptions. Result: US$ 0.08–0.16 for a scan with 10 engine runs. The main driver was the fixed search fee per call, not tokens.

## Then the real number

Every engine run logs tokens in, tokens out, search calls and cost. A real scan with 15 engine runs on 1 Nov 2026 cost **US$ 0.2333**.

## Guards in code

- A cost cap per scan and a daily cap across all scans.
- Anti-abuse limits, email verification and a bot check before any paid call.

## Cost of building

- Any scan, paid API call or review by agents gets an estimated cost first.
- At most one independent review and one blind set per deploy.
- Long reviews run as cloud sessions on prepaid credit when it is available, local work continues meanwhile (see [agents](agents.md)).
