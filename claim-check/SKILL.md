---
name: claim-check
description: Audits a README or docs against the real project. Lists every checkable claim (numbers, commands, behaviour, file names, links, comparisons, outside facts), checks each by running or reading the code, then fixes the docs where they are wrong. Use when the user says claim check, check the README, are the docs true, or before a release.
metadata:
  version: "1.0.0"
---

# Claim Check

Docs drift. A number was true once, a command was renamed, an example stopped running, a link moved. Find every claim the docs make, check each one with evidence, and fix the docs where they are wrong.

Output: `claim-check/<YYYY-MM-DD>.md` (the ledger), plus fixes to the docs.

## Step 1. Decide the scope

Default: `README.md` at the root and in each top-level folder, plus `docs/`. Files inside `examples/` are sample output, so leave them out unless the user includes them. Include other files the user names (CHANGELOG, SKILL.md, docstrings, the website). Write the list of files at the top of the ledger. Config and code files (`pyproject.toml`, `package.json`, source) are evidence, not claim sources.

## Step 2. List every claim

Read each file line by line and pull out every sentence that could be true or false. Skip opinions ("easy to use") and plans ("coming soon"), but note them as `Opinion` so the count is honest.

| Type | Examples |
|---|---|
| Number | "15 tests", "17 areas", "about 22 calls", "3x faster", "under 50 KB" |
| Command | Install steps, `npm run build`, CLI flags |
| Code example | A code block that should run or produce shown output |
| Behaviour | "Raises an error on empty input", "retries 3 times", "defaults to UTF-8" |
| Name or path | File, folder, function, option or setting names |
| Link | URLs, relative links, `#anchors` |
| Comparison | "Fewer calls than X", "faster than Y" |
| Outside fact | A version, a paper's finding, another project's numbers |
| Past result | "In our run, 4 of 9 failed": check it against the saved record of that run |

Give each claim an ID (C1, C2, ...) and record the file, line and exact quote.

## Step 3. Check each claim

Pick the strongest check available, in this order: run it, count it, read the code, fetch the source. Record the exact command or file you used and the real output, trimmed to what matters.

- **Numbers**: count from the files or re-run what produced them. For a measured figure (time, tokens), check it against the saved record (raw logs, or a written summary of the run such as a RUN.md). If no record exists, mark it `Can't check`.
- **Commands and examples**: run them in a scratch copy or a virtual environment, never in a way that changes the user's real setup. Compare the output with what the docs show.
- **Behaviour**: write the smallest script that shows it, and run it. If that's not possible, read the code path and quote the lines.
- **Names, paths and links**: check that each file, function and option exists. Fetch external links. For relative links and `#anchors`, check the target exists.
- **Comparisons and outside facts**: open the source the claim relies on. Never confirm one from memory.

Before running anything that installs system packages, costs money, sends messages, writes outside a scratch area or changes data, ask first.

Then give each claim one verdict:

| Verdict | Meaning |
|---|---|
| `True` | Evidence matches |
| `False` | Evidence contradicts it |
| `Partly true` | Part holds, part doesn't, or the wording overstates it |
| `Out of date` | It was true for an older version |
| `Can't check` | No way to check it here. Say why, and what would check it. |
| `Opinion` | Not a factual claim |

Never mark a claim `True` without evidence in the ledger. Be as strict with claims that sound right as with ones that look wrong.

## Step 4. Fix the docs

For every `False`, `Partly true` and `Out of date` claim:

- **Change the docs to match reality**, not the code to match the docs. If the code looks like the bug (the docs describe the intended behaviour), don't edit either one: list it under "Possible code bugs" for the user.
- If it's unclear which side is wrong, fix the docs to match what the code does now, and also list it under "Possible code bugs" marked `intent unclear`, so the user can decide.
- Make the smallest edit that makes the sentence true. Keep the author's voice and formatting.
- Re-check the new wording with the same evidence.
- If you can't edit the files (no permission), write each fix as exact replacement text in the ledger and mark it `proposed, not applied`.
- Fix broken examples so they run, and run them again.
- For `Can't check`, soften the wording only if it reads as checked when it isn't (for example "measured" with no record). Otherwise leave it and list it.

## Step 5. Write the ledger

`claim-check/<YYYY-MM-DD>.md`:

```markdown
# Claim check

Checked <YYYY-MM-DD>. Files: ...

## Summary
| Verdict | Count |
|---|---|
| True | |
| False (fixed) | |
| Partly true (fixed) | |
| Left for the user (possible code bug) | |
| Fix proposed, not applied | |
| Out of date (fixed) | |
| Can't check | |
| Opinion | |

## Fixes made
| ID | File:line | Was | Now | Evidence |
|---|---|---|---|---|

## Possible code bugs
Places where the docs look right and the code looks wrong.

## Can't check
| ID | Claim | Why | What would check it |
|---|---|---|---|

## All claims
| ID | File:line | Claim | Type | Check | Verdict |
|---|---|---|---|---|---|
```

Keep the evidence for each claim short but real: the command and the lines of output that decide it.

## Step 6. Check your own writing

The ledger and every doc edit follow these rules: no em or en dashes, no emoji, no exclamation marks, no filler (genuinely, actually, really, simply, just, basically), no inflated words (robust, leverage, seamless, comprehensive, crucial, cutting-edge, game-changer), no stock phrases ("it's worth noting", "in conclusion"). Don't copy personal info (emails, keys, home folder paths, names of private people) from the project into the ledger. Public project names and handles in URLs are fine.

Run from the project root:

```
grep -nEi '—|–|!( |$)|\b(genuinely|actually|really|simply|just|basically|robust|leverag\w*|seamless|comprehensive|crucial|cutting.edge|game.changer|furthermore|moreover)\b|worth noting|in conclusion' claim-check/*.md
```

Quoted claims from the original docs are exempt.

## Step 7. Tell the user

In chat: the counts by verdict, every fix in one line each, any possible code bugs, and the `Can't check` items they could confirm. Do not commit unless the user asks.
