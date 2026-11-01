# Deploy and verification

Every deploy has a checklist written before it and a record written after it. By 1 Nov 2026 there were over 70 of them. The agent prepares the checklist; the deploy runs only after my explicit OK.

## The checklist

Written in the working copy, before anything touches production.

1. **What goes in and what does not.** Scope in plain language, including items explicitly left out and why.
2. **File list against production.** Computed against the production tree, never against another copy, with the md5 on both sides:

   ```
   status    path                          md5_production    md5_candidate
   changed   src/module_a.py               1a2b3c4d…         5e6f7a8b…
   changed   templates/page_a.html         9c8d7e6f…         0a1b2c3d…
   new       src/module_b.py               -                 4d5e6f7a…
   new       tests/test_module_b.py        -                 8b9c0d1e…
   ```

   `shiptools.deploylist` produces this table.
3. **Already done, with evidence.** Red tests on the unchanged copy, suites green on both Python versions with their counts, browser walkthrough before and after if the change is visible, and the cost so far (often US$ 0).
4. **Order and conflicts.** Which other pending changes touch the same files, and what to do if one lands first (usually: re-apply the edit plan on the new base and run the suites again).
5. **Open decisions for me.** For example, whether phrases without native review go out now or wait.

## The deploy

1. Originals of every file to be replaced are copied to a folder named with date, time and reason.
2. Files are copied into the production tree and their md5 compared with the table.
3. Suites run once more on the production tree.
4. Backup on the server, then deploy. Both steps print an explicit success marker; the checklist does not move on without it.

## After

1. Health check.
2. **md5 parity of all code files**, server against my machine. The record states the count: 178 of 178 after the security deploy on 30 Oct 2026, 197 of 197 later the same day.
3. Functional checks that cost nothing: pages, languages, the form up to the step before anything paid is triggered.
4. The record: what went up, who gave the OK and with which words, times of backup and deploy, parity result, and how to roll back.

## Rollback

The record names the server-side copy taken before the deploy and the local folder with the originals. Rolling back is a copy, followed by the same parity check.
