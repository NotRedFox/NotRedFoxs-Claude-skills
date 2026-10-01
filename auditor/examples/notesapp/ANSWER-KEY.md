# Answer key

This app was written to test the auditor. It had 7 planted problems. The auditors did not see this file.

## Branch audits

Two auditors ran at the same time: one on login and the API ([report](audit/2026-10-01-auth-api.md)), one on notes and search ([report](audit/2026-10-01-notes-search.md)).

| # | Planted problem | Found |
|---|---|---|
| 1 | Passwords lowercased, so they aren't case-sensitive | Yes, login/API audit |
| 2 | Every note shares one `tags` list that keeps growing | Yes, notes audit (memory reached 480 MB in a 4 minute run) |
| 3 | Notes branch has almost no tests | Yes, notes audit (mutation scores before and after) |
| 4 | Note ids race, so notes are lost when many users post at once | Yes, both audits |
| 5 | Search results go stale after a new note | Yes, notes audit |
| 6 | Search cache grows forever, a memory leak | Yes, notes audit, measured with tracemalloc |
| 7 | Error responses include the full traceback | Yes, both audits |

They also found real problems that were not planted: login tokens that never expire and pile up, unsalted password hashes, a crash path in `GET` requests, no request size limits, and the server failing at about 50 users at once.

## Final audit

After the branch audits, 4 problems were fixed ([the diff](fixes-after-branch-audits.diff)): 1, 2, 5 and 7. The fix for 5 was deliberately flawed: it clears the search cache from the API code, while other requests may be using it.

The [final audit](audit/2026-10-01-final.md):
- Marked 1, 2 and 7 as fixed, and the rest as still open.
- Found that the fix for 5 crashes under concurrent use (188 of 200 cache clears failed in-process), only works through the API, and had no test.
- Found a new race that only shows when notes and search run together.

## Time estimates

The first version of the skill estimated 1 hour for each branch audit; they took 14 and 16 minutes. The final audit, with an updated table, estimated 45 minutes and took 17. The table was tightened again after that, and the skill now bases estimates on the real times of earlier audits when it has them.
