---
name: let-me-sleep
description: "Before a long task, tells the user how long it will take and every permission prompt it will need, gets them all approved at the start, then works without stopping to ask. Ends with what it did, the real time against the estimate, and anything left waiting."
argument-hint: "<the task to do while you're away>"
disable-model-invocation: true
license: MIT
compatibility: "Claude Code. Writes temporary allow rules to .claude/settings.local.json and removes them at the end. Keeps its notes in .let-me-sleep/."
metadata:
  version: "1.0.1"
  author: NotRedFox
---

# Let Me Sleep

The user wants to start a task and walk away. Your first message tells them two things: how long it will take, and every permission prompt it will need. Then you get all of those approved at once, so nothing stops while they're gone.

Do not start the real work until Step 4 is done. Until then, nothing you run may ask for permission: use one simple read-only command at a time (`ls`, `cat`, `rg`, `git status`, `git log`), with no `&&`, pipes into other programs, redirects to files, or paths outside the project. Combined commands and files outside the project ask for permission even when each part is read-only.

Keep your own files in `.let-me-sleep/` in the project root. Never put them under `.claude/` or `.git/`: those folders always ask, even when an allow rule covers them.

## Step 1. Plan the work

Read enough of the project to plan: the README, the files the task touches, the test setup. Use the Read, Grep and Glob tools, or single read-only commands.

Write the plan as numbered steps. For each step, list the exact actions it takes: the shell commands, the files it creates, edits or deletes, the websites it fetches. Be concrete: `npm test`, `rm -rf dist/`, edit `src/config.ts`. If a later step depends on what an earlier one finds, list the likely actions and mark them `maybe`.

## Step 2. Estimate the time

You work much faster than a person, so don't estimate in human time. Estimate from what you'll actually do:

1. **Count your tool calls.** Measured on real runs, each read, edit, search or short command takes about 1.5 seconds, including thinking. A file you have to understand before changing it is 2 or 3 calls. A bug you have to diagnose is about 5. Writing a longer file (a page of docs, a test file) is about 5 seconds. Count every call, including the `date +%s` commands and each write to `.let-me-sleep/`.
2. **Add the commands that take real time.** Tests, builds, installs and downloads take as long as they take. If the project records how long they take (a CI log, a README, an earlier run), use that. Otherwise estimate from their size, and plan to re-time them on the first approved run.
3. **Don't pad it.** No slack, buffer or retry time, and no rounding up. Give your best estimate, not a safe one. The history in the next step corrects it over time.
4. **Scale by history.** If `.let-me-sleep/history.md` exists, it has earlier work estimates and real work times for this project. Work out the ratio of real to estimated for each line that has both. With one or two lines, move halfway toward their average ratio. With three or more, use the average. Never go below 1 second per tool call.
5. **Add the wrap-up.** The final report, the history line and the settings restore take about 10 seconds after the clock stops. Add them after scaling, since history doesn't time them.

Write the work estimate (before the wrap-up) in seconds in `run.md` in Step 4, since that's what history compares against. Give the user one number and a finish time: "About 4 minutes, done around 23:10." Add a short breakdown by step. After the first approved run of a slow command, write the real time to `.let-me-sleep/run.md`, and if the estimate is now off by more than half, say so in the final report.

## Step 3. Forecast every permission prompt

Go through every action in the plan and decide whether it will stop and ask. Use these rules from Claude Code's permission system:

| Action | Asks? |
|---|---|
| Reading files, `Grep`, `Glob` inside the project | No |
| Read-only shell commands (`ls`, `cat`, `head`, `tail`, `grep`, `rg`, `find` without `-exec` or `-delete`, `wc`, `git status`, `git log`, `git diff`) | No |
| Any other shell command (installs, tests, builds, `rm`, `mv`, `git commit`, `git push`, scripts) | Yes, unless an allow rule covers it |
| Creating or editing files | Yes in Manual mode. No in accept-edits mode, for files inside the project |
| Anything under `.git/` or `.claude/` | Yes, in every mode except bypass |
| Fetching a web page | Yes, per domain, unless allowed (a few documentation sites are pre-approved) |
| Web search | Yes, unless allowed |
| MCP tools | Yes, unless allowed |

Before deciding, read the allow and deny rules in `.claude/settings.json` and `.claude/settings.local.json`. An action an allow rule already covers won't ask. An action a deny rule covers can't be done at all: say so now and plan around it. Don't read `~/.claude/settings.json`: it's outside the project, so reading it asks. Instead, say the forecast assumes Manual mode with no personal allow rules, and that it may ask less if they have some.

Then list the ones that will ask, in order, with when they happen:

```
This will need you 5 times. I'd like to get them all approved now:
1. pip install -r requirements.txt (about 1 min in)
2. Edit files in src/ and tests/ (from about 2 min in)
3. python -m pytest (about 5 min in, and again at the end)
4. rm -rf build/ (about 20 min in). DELETES the build folder.
5. git commit (at the end). No push.
```

Call out anything that deletes, overwrites, pushes, sends or costs money, in capitals as above, on its own line.

## Step 4. Get everything approved at once

Offer to turn the list into allow rules for this task only:

- Write exact rules where you can (`Bash(rm -rf build/)`), and narrow wildcards only where the command varies (`Bash(python -m pytest *)`). Never `Bash(*)`, and never a wildcard on a delete or a push.
- For file edits, either ask the user to switch to accept-edits mode (Shift+Tab), or add `Edit(./src/**)`-style rules for the folders you'll change.
- Add `Edit(./.let-me-sleep/**)` so your log and history files don't ask.

Show the exact rules. When the user says yes, write the work estimate in seconds and the forecast prompt count to `.let-me-sleep/run.md` first, so the history can compare them later even if the run continues in a new session. Then save a copy of the current `.claude/settings.local.json` (or `{}` if there is none) to `.let-me-sleep/settings.before.json`, then write the rules into `.claude/settings.local.json` under `permissions.allow`. Writing to `.claude/` always asks, so this is the one prompt they answer now. Then tell them they can go.

Removing the rules at the end also writes to `.claude/`, so it asks too. Say so in the forecast: it's one last prompt after all the work is done, and they can answer it whenever they're back. Count it in the total.

If the user would rather not add rules, tell them which prompts will still appear and when, so they know when to come back.

## Step 5. Do the work without stopping

- Run `date +%s` before the first step and write it to `.let-me-sleep/run.md`. You can't feel time passing, so the clock is the only accurate measure.
- Do only what was approved. If you need an action that isn't on the list and would ask for permission, don't run it. Add it to a "Waiting for you" list with the reason, and carry on with everything that doesn't depend on it.
- If a step fails, try to fix it within the approved actions. If you can't, record why and move on.
- Keep a short log in `.let-me-sleep/run.md`: time, step, result.

## Step 6. Clean up and report

1. Run `date +%s` again and work out the real time from the start time in `run.md`. Add a line to `.let-me-sleep/history.md`: date, task, work estimate in seconds, real seconds, prompts forecast, any prompts that appeared anyway.
2. Tell the user, briefly:
   - What got done, step by step.
   - Estimated time against real time.
   - Whether any permission prompt appeared that wasn't forecast, and why.
   - The "Waiting for you" list, if anything is on it.
3. Last of all, restore `.claude/settings.local.json` from `.let-me-sleep/settings.before.json` so the temporary rules are gone. This asks for permission, so do it after the report. If it's declined, tell them the rules are still there and exactly which lines to delete.

Writing rules for everything you show the user: no em or en dashes, no filler, plain sentences, real numbers.
