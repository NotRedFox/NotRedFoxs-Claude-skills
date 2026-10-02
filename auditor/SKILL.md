---
name: auditor
description: "Audits one branch of a project's architecture at a time, then runs a final audit across the whole thing. Gives a time estimate first, asks for every permission up front, tests the existing tests (or writes them), simulates real users, load and long runs, looks for memory leaks, and writes a report."
argument-hint: "[branch path | final]"
disable-model-invocation: true
license: MIT
compatibility: "Built for Claude Code. It runs tests, servers and load tests, and takes a while, so it only runs when you type /auditor."
metadata:
  version: "1.0.3"
  author: NotRedFox
---

# Auditor

Check that one part of a project works, under real use, and that its tests would catch it if it didn't. Then, once the parts are audited, check that everything works together.

Two modes:

| Mode | User says | Output |
|---|---|---|
| **Branch audit** | "audit the auth part", "audit src/search" | `audit/<YYYY-MM-DD>-<branch>.md` |
| **Final audit** | "final audit", "audit everything together" | `audit/<YYYY-MM-DD>-final.md` |

A branch is one part of the architecture: a folder, a service, a module and what it depends on, or a user-facing feature.

The auditor reports. It adds tests, but does not change the project's code unless the user says yes to a specific fix.

**Searching code:** use `rg` (ripgrep) when it's installed. It skips `.git`, `node_modules` and other ignored files, and returns only the matching lines, so it uses far fewer tokens than `cat`, `find` or `grep -r`. Read only the part of a file you need. Fall back to `grep -rn` if `rg` isn't there.

## Step 1. Estimate the time and say it first

Before anything else, size the work and tell the user how long it will take, for example "This branch will take about 1 hour."

Base the estimate on what you can count in a minute or two:
- Files and lines of code in the branch, and how many other parts it touches.
- Existing tests: how many, and how long the suite takes to run (run it once if it's quick).
- Whether it runs as a server, a CLI, a library or a UI, and whether a load or long-running test is needed.

Rough guide, by the lines of code in the branch:

| Branch size | Library or CLI | Server or API | UI |
|---|---|---|---|
| Under 300 lines | 10 min | 15 min | 25 min |
| 300 to 2,000 lines | 30 min | 45 min | 1 hour |
| Over 2,000 lines | 1 hour or more | 1.5 hours or more | 2 hours or more |

Add 5 minutes per extra service to start. A final audit takes about as long as the largest branch audit plus 5 minutes. If earlier audit reports in `audit/` record real times, base the estimate on those instead of the table. Tell the user one number, such as "about 20 minutes".

Record the estimate in the report, and the real time at the end.

## Step 2. Ask for everything up front

The user should be able to leave while the audit runs. So, in the same first message as the estimate, list every permission or input you will need, all at once:

- Access to websites or APIs (staging URLs, test accounts, API keys for a test environment).
- Folders outside the project, or data files.
- Installing tools (a load tester, a profiler, a mutation testing tool).
- Starting servers, databases or containers.
- Running load or long tests that use a lot of CPU or memory, and for how long.
- Anything that sends messages, costs money or touches shared environments.

Number them, say why each is needed, and give a fallback if the answer is no ("without it I'll mock the payment API"). Then wait for the answers once. If the user has said to go ahead without them, use the fallbacks. Do not drip-feed questions later; if something new comes up, note it and use the fallback.

You don't need to ask before writing the report in `audit/` or adding test files. Say that you will.

Never load-test or probe a production system or a third-party site unless the user explicitly names it and confirms.

## Step 3. Map the branch

If the README has an Architecture section (for example one kept by kick-start), start from it. Otherwise read the code and write a short map:

- The branch's entry points: routes, commands, public functions, UI screens.
- What it depends on, and what depends on it.
- How data moves through it, in numbered steps.
- Where state lives: memory, files, database, caches, sessions.

Put the map at the top of the report. List which files you read in full.

## Step 4. Test the tests

1. **Run the existing suite** for the branch. Record pass, fail and time.
2. **Run it 3 times** if it takes under 2 minutes, otherwise once more. A test that changes result between runs is flaky. Record it.
3. **Check the tests can catch bugs.** Work in a temporary copy of the project, never in the user's files. For each important behaviour, make one small breaking change (flip a condition, remove a check, return early) and run the tests. A change no test catches is a gap. You may use a mutation testing tool if one is installed or approved (mutmut, Stryker, PIT), run in the temporary copy; otherwise do 5 to 15 hand mutations on the riskiest code. Mutation tools need a passing suite, so leave out tests that fail because they found a bug. Record the score for the old tests and for old plus new.
4. **Check coverage** if a tool is available, and list the important code no test runs.
5. **If the branch has no tests, or big gaps**, write tests from what the code is meant to do: the docs, the README, function names, the user's description. Never copy current output into an assertion. Use the project's test framework and layout.
6. **Two kinds of new test.** A test that fails on the current code because it found a bug is a *finding test*: link it to the finding, and it should pass once the bug is fixed. A test that passes now must be shown failing on a broken version (in the temporary copy) before it counts.

## Step 5. Audit the branch

Run each check that applies. For each one record what you did, the real output, and the result.

**Correctness**
- Normal use, edge cases (empty, huge, unicode, zero, negative, missing fields), wrong types.
- Error handling: bad input gives a clear error, not a crash or a silent wrong answer.

**Simulated users**
Write scripts that act like real people using the branch, through its real entry point (HTTP requests, the CLI, a browser via Playwright for a UI):
- A normal user doing the main task from start to finish.
- A confused user: wrong order, double clicks, going back, refreshing, leaving halfway.
- A careless or hostile user: very long input, special characters, script tags, SQL-like strings, path tricks like `../`.
- Many users at once: run the journeys in parallel (10, then 50, then more if it holds) and check for errors, wrong data between users, and slowdowns.

**Load and long runs**
- Load: increase requests per second until errors or slowdowns appear. Record the point it breaks.
- Long run: repeat a normal journey many times (for example 10,000 requests or 10 minutes) while sampling memory every few seconds. Give the long run at least half of the time set aside for load and long tests: leaks only show over time.

**Memory and resource leaks**
- Memory that keeps growing during the long run and never levels off is a leak. Show the samples.
- Use the language's tools: `tracemalloc` for Python, heap snapshots or `--inspect` for Node, `pprof` for Go, or the process's resident memory if nothing else.
- Also check for open files, sockets, database connections, threads and timers that pile up.

**Security basics**
- Secrets in code or logs, input that reaches a shell, a query or a file path unchecked, missing auth checks on routes, error messages that leak internals.

**Performance**
- Time the main operations. Look for work repeated per request that could be done once, and for anything that slows down as data grows.

## Step 6. Write the branch report

`audit/<YYYY-MM-DD>-<branch>.md`:

```markdown
# Audit: <branch>

Date <YYYY-MM-DD>. Estimated <time>, took <time>.

## Summary
- Verdict: Ready, Ready with fixes, or Not ready.
- Findings: <n> high, <n> medium, <n> low.
- Tests: <n> existing (<pass>/<fail>, <n> flaky). <n> added: <n> finding tests (fail until fixed), <n> passing tests (each seen failing on a broken version).
- Mutations caught: old tests <n> of <n>, old plus new <n> of <n>.

## Permissions used
What was asked, what was granted, and fallbacks used.

## Map
## Findings
### A1. <title>. High
- Where: file and function
- What happens: real input and real output
- How it was found: the check and its evidence
- Suggested fix
## Tests
## Checks run
| Check | What was done | Result |
|---|---|---|
## Not checked
What could not be checked here, and why.
```

Severity: **High** means wrong results, data loss, a crash under normal use, a leak that grows without limit, or a security hole. **Medium** means it fails under unusual use or load, or a test gap on important code. **Low** is everything else worth fixing.

## Running audits in parallel

If more than one branch audit runs at the same time, each one uses its own test file names (for example `tests/test_<branch>_audit.py`), its own port, and runs only its own tests when timing them. The Step 8 check runs on its own report only.

## Step 7. Final audit

Run this once the branches have reports, or when the user asks.

1. **Read every branch report** in `audit/`. List each High and Medium finding and check whether it is fixed now. Re-run its evidence.
2. **Map the whole system** from the branch maps and the code, and list where branches connect.
3. **Run the full test suite** 3 times, and check how long it takes. If the suite needs ports or resources you are not allowed to use, run it in a temporary copy with those settings changed, and say so.
4. **Simulate real users end to end**: journeys that cross branches (sign up, do the main task, see the result, sign out), with many users at once.
5. **Load and long run across the whole system**, sampling memory and resources for every process. Look for leaks that only show when the parts run together (a cache filled by one branch and never emptied by another).
6. **Check the joins**: hand-mutate the code where branches connect (in a temporary copy) and see whether any test notices. Then check that data passed between branches has the shape each side expects, errors in one branch are handled by its caller, start-up and shut-down work cleanly, and config is consistent.
7. **Write `audit/<YYYY-MM-DD>-final.md`** with the same structure as a branch report, plus a table of every earlier finding and its status: Fixed, Partly fixed, Still open, or Could not re-check. When two branch reports found the same bug, list it once with both IDs. In the Summary, count new findings and still-open earlier findings separately.

Also check the fixes made since the branch audits: each fix has a test, and the fix itself works under concurrent use. A fix in the wrong place, or one that only works through one entry point, is a finding.

## Step 8. Write like a person

Reports follow these rules: no em or en dashes, no emoji, no exclamation marks, no filler (genuinely, actually, really, simply, just, basically), no inflated words (robust, leverage, seamless, comprehensive, crucial, cutting-edge). Real numbers and real output. Don't copy secrets, personal data or real user records into a report; use placeholders.

Run from the project root on your own report:

```
grep -nEi '—|–|!( |$)|\b(genuinely|actually|really|simply|just|basically|robust|leverag\w*|seamless|comprehensive|crucial|cutting.edge|game.changer|furthermore|moreover)\b|worth noting|in conclusion' audit/<your report>.md
```

"Just" meaning "a moment ago" is fine; reword only filler uses.

## Step 9. Tell the user

In chat: the verdict, the High findings in one line each, the estimate against the real time, and where the report is. Clean up anything you started (servers, containers, temp files). Do not commit unless the user asks.
