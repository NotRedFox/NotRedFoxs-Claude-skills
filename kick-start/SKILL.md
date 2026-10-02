---
name: kick-start
description: "Keeps a project's memory up to date as you work. Logs every approach in the conversation, keeps a bug log the agent rereads and learns from, keeps the README architecture section current, writes tests that check the goal, and writes plain, professional comments. Use when the user says kick start, log this, or what have we tried."
license: MIT
compatibility: "Claude Code recommended, since it writes files and runs tests. Works in the Claude app with less checking."
metadata:
  version: "1.1.2"
  author: NotRedFox
---

# Kick Start

Keep the project's memory in files, so nothing depends on what the agent remembers. Once turned on, this skill stays on for the rest of the conversation.

It maintains four things:

| File | Covers | Lifetime |
|---|---|---|
| `kickstart/<YYYY-MM-DD>-<topic>.md` | Every problem and approach in this conversation | One per conversation |
| `BUGS.md` | Every bug found and fixed, with the lesson | Permanent, grows over time |
| `README.md`, Architecture section | How the project is built, as it is now | Permanent, kept current |
| Tests | The goal, so fixed bugs stay fixed | Permanent |

**Searching code:** use `rg` (ripgrep) when it's installed. It skips `.git`, `node_modules` and other ignored files, and returns only the matching lines, so it uses far fewer tokens than `cat`, `find` or `grep -r`. Read only the part of a file you need. Fall back to `grep -rn` if `rg` isn't there.

## When to run

- The user says "kick start", "log this", "what have we tried", "write up what worked and what didn't" or similar.
- Once on, keep everything below up to date for the rest of the conversation without being asked again.

## Step 1. Read before you work

At the start of the conversation, and again whenever you are unsure what was done before (for example after the conversation is compacted), read:

1. `BUGS.md`, especially the Patterns section at the top.
2. The Architecture section of `README.md`.
3. The newest file in `kickstart/`.

Before changing a file, check `BUGS.md` for entries that name it. If an earlier bug in that file came from a pattern you are about to repeat, change course and say which entry you are following.

## Step 2. Start the conversation log

Create `kickstart/<YYYY-MM-DD>-<short-topic>.md`. If the conversation already has one, keep using it.

If the skill is turned on partway through, backfill first: go back to the start of the conversation and log every problem and approach so far, from the commands, outputs and diffs you can see. Then keep logging live.

## Step 3. Log every approach as it finishes

Update the log each time an approach finishes, whether it worked or not. Do not save it up for the end. Long conversations get compacted and the details are lost.

Group approaches under the problem they were for, in the order they were tried. For each one record:

- **What was done**, in one or two sentences.
- **Why it was chosen.**
- **Result**: `Worked`, `Failed`, or `Partly worked`.
- **Evidence**: the command or test that showed the result, with the real output trimmed to the lines that matter. Never write "it worked" without saying how you know.
- **Why** it worked or failed. If the cause was not confirmed, write `Cause not confirmed` and label your guess as a guess.
- **Kept or undone**: is this change still in the code?

Approaches that worked first time still get logged.

Keep two kinds of claim apart:
- **Checked**: you ran something and saw it.
- **Believed**: you think it is true but did not check.

Refresh the summary and table at the top every time you log an approach, so they never show an approach as in progress after it finished. Structure:

```markdown
# <Topic>

Started <YYYY-MM-DD>. Last updated <YYYY-MM-DD>.

## Summary
- Goal: what the user wanted, in their words.
- Works now (checked): ...
- Still broken (checked): ...
- Believed but not checked: ...

| Problem | Approaches tried | What ended up working |
|---|---|---|

## Problems and approaches

### Problem 1: <name>

#### Approach 1.1: <name>. Failed
- What was done: ...
- Why it was chosen: ...
- Evidence: ...
- Why it failed: ...
- Kept or undone: Undone

## What worked
## What didn't, do not retry
## Tests added
| Test | Protects against | Status |
|---|---|---|
## Next steps
## Open questions
```

## Step 4. Keep BUGS.md

`BUGS.md` sits in the project root and is never reset. Create it the first time a bug is found. Add an entry every time a bug is found, whether it was in the existing code or introduced by you during the conversation. Newest entries go at the top of the Bugs section.

```markdown
# Bugs

Read this before changing code. Each entry is a bug that was found, how it was fixed (or why it is still open), and what to do differently.

## Patterns
- <One line per lesson that applies to more than one bug, with the bug numbers.>

## Bugs

### B<n>: <short name>
- Found: <YYYY-MM-DD>, <how it showed up>
- Where: <file and function>
- Symptom: <what went wrong, with a real example input and output>
- Cause: <the root cause, checked or marked as a guess>
- Fix: <what changed>
- Test: <test name that fails if this comes back>
- Lesson: <what to do differently next time>
- Status: Fixed | Open | Fixed, then came back (see B<m>)
```

Rules:
- Number bugs in order and never reuse a number.
- Never delete an entry. If a fixed bug comes back, add a new entry that links the old one and update the old one's Status.
- Every Fixed entry names a test. If there is no test, the Status is `Open`.
- When two or more bugs share a cause, add or update a line in Patterns.
- Link each bug from the conversation log, and the conversation log from the bug.

## Step 5. Keep the README architecture current

Own one section of `README.md`, between these markers. Create it if it is missing. Never change anything outside the markers, except a line that a change made wrong (a command, an option, a file name); fix that line and note it in the log.

```markdown
<!-- kick-start:architecture:start -->
## Architecture

Last updated <YYYY-MM-DD>.

<Two to four sentences: what the project does and how it is put together.>

| Path | What it does | Uses |
|---|---|---|

<How data or a request moves through the parts, as numbered steps or a mermaid diagram.>
<!-- kick-start:architecture:end -->
```

Update it whenever a file or module is added, removed or renamed, a responsibility moves, or a dependency changes. Write it from the code as it is now, never from what was planned. Read the files before describing them.

## Step 6. Add tests that do not agree with the code by default

The risk is tests that pass because they were written to match the agent's own output. Those tests lock the bugs in.

1. **Expected values come from the goal, never from running the code.** Work out each expected value from the request, the docs, a spec or a hand calculation before running anything. Never copy the function's output into an assertion.
2. **One test per bug** in `BUGS.md`, and one per approach that worked, checking the goal it met.
3. **Prove each test can fail.** Put the broken version back briefly (undo the fix, or change one line). For new code with no earlier broken version, make the smallest change that breaks the exact rule the test checks, for example remove one guard or swap two steps. Run the test and confirm it fails. Restore the code and confirm it passes. Record this in the Status column, for example `Fails on approach 1.1 code, passes now`.
4. **Known bugs stay visible.** If something is still broken, write the test for the correct behaviour and mark it as an expected failure with the reason, for example `@pytest.mark.xfail(strict=True, reason="B4")` in Python or `it.failing(...)` in Jest. Never weaken or delete a test to get a pass.
5. **Do not edit a test to match the code** unless the goal was misunderstood. If you do, log it and quote where the goal says so.
6. **Cover the edges the approaches tripped on**: empty input, very large input, odd characters, wrong types, boundaries.
7. **Use the project's existing test setup.** Match its framework, layout and naming.
8. **Run the full suite** whenever you add tests, and log the real result, including failures.

## Step 7. Write code comments like a professional

Comments are for the next developer reading the code, not a record of the conversation.

- Explain why: the constraint, the edge case, the reason the obvious approach does not work. Do not restate what the code does.
- Never mention the user, the prompt, the conversation, Claude or AI. No "as requested", "per the user", "fixed the bug where", "new:", "updated:" or "changed to". History belongs in git and `BUGS.md`.
- Public functions, classes and modules get a docstring or doc comment in the language's standard style: what it does, parameters, return value, errors raised.
- When a line exists because of a bug, a short comment may name it: `# Sharp s has no ASCII form, so map it before NFKD (B3).`
- Match the comment density and style already in the file. No commented-out code. No comment on every line.

Check the lines you added before finishing, and rewrite anything it finds:

```
P='(#|//|/\*|\*|""").*(user|prompt|as requested|asked|claude|\bai\b|chatgpt|fixed the|new:|updated:|changed to|per the)'
git diff -U0 | grep -E '^\+' | grep -nEi "$P"
git ls-files --others --exclude-standard | xargs grep -nEi "$P"
```

The second line covers new files that git is not tracking yet.

## Step 8. Remove personal info

Before every save, scrub every file this skill writes and every new test. Replace with a placeholder in angle brackets:

| Remove | Replace with |
|---|---|
| Names of real people | `<NAME>`, or their role, like "the reviewer" |
| Email addresses, phone numbers, street addresses | `<EMAIL>`, `<PHONE>`, `<ADDRESS>` |
| API keys, tokens, passwords, connection strings | `<SECRET>`. Also tell the user it was exposed and should be changed. |
| Home folder paths like `/Users/sam/` or `C:\Users\sam\` | `~/` |
| Private URLs, internal hostnames, IP addresses | `<INTERNAL_URL>`, `<IP>` |
| Customer or user data from logs or databases | Made-up values with the same shape |

Test data must be made up. Never copy real records into a test.

If you see a secret or personal info in a project file this skill did not write (a config file, a log), do not copy it anywhere. Tell the user once which file it is in and that a key should be changed, and list it under Open questions with a placeholder.

```
grep -rnEi '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|/Users/[^/ ]+|/home/[^/ ]+|C:\\Users\\|(api[_-]?key|secret|token|password)\s*[:=]|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' kickstart/ BUGS.md README.md <new test files>
```

## Step 9. Write like a person

This applies to the log, `BUGS.md`, the README section, comments and chat.

- No em dashes or en dashes. Use a comma, full stop, colon or brackets.
- No emoji, and no exclamation marks.
- No filler words used for emphasis: genuinely, actually, really, truly, simply, just, basically, essentially, definitely, incredibly.
- No inflated words: delve, robust, leverage, seamless, comprehensive, crucial, pivotal, vital, paramount, utilize, streamline, facilitate, empower, elevate, harness, unlock, enhance, foster, holistic, synergy, paradigm, cutting-edge, state-of-the-art, game-changer, ever-evolving, landscape, realm, tapestry, testament, intricate, meticulous, embark, journey, boasts.
- No stock phrases: "it's worth noting", "it's important to note", "in today's", "in conclusion", "in summary", "furthermore", "moreover", "plays a key role", "a wide range of", "whether you're", "navigate the", "I hope this helps", "great question", "certainly", "absolutely", "let's dive in".
- No patterns: "not only X but also Y", lists of three for rhythm, a closing paragraph that repeats what was said, a heading over a two-line section, bold on every other phrase, hedges stacked together ("may potentially").
- Plain verbs, short sentences, real numbers. Say what happened and stop.

Check before saving, and rewrite anything it finds:

```
grep -rnEi '—|–|!( |$)|\b(genuinely|actually|really|truly|simply|just|basically|essentially|definitely|incredibly|delv\w*|robust|leverag\w*|seamless\w*|comprehensive|crucial|pivotal|vital|paramount|utiliz\w*|streamlin\w*|facilitat\w*|empower\w*|elevat\w*|harness\w*|unlock\w*|enhanc\w*|foster\w*|holistic|synerg\w*|paradigm|cutting.edge|state.of.the.art|game.changer|ever.evolving|landscape|realm|tapestry|testament|intricate|meticulous\w*|embark\w*|journey|boasts?|furthermore|moreover|certainly|absolutely)\b|worth noting|important to note|in today.s|in conclusion|in summary|key role|wide range of|whether you.re|navigate the|hope this helps|great question|dive in|not only' kickstart/ BUGS.md README.md
```

Run the same pattern on the comment lines you added to code (the lines found by the Step 7 check). Code inside backticks can trip the check (for example `!=`). Leave those.

## Step 10. Tell the user

When the skill turns on, say in one line which files it keeps. After that, do not announce every update. When the user asks, or the conversation is wrapping up, tell them:
- Where the log is, and how many problems and approaches it covers.
- Bugs added to `BUGS.md` this conversation, by number.
- Whether the README architecture changed.
- Which tests were added, and the latest test result.
- Anything that needs them: open questions, a secret to change.

Do not commit unless the user asks.
