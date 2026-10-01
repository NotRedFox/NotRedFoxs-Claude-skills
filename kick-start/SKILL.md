---
name: kick-start
description: Keeps a running log for the whole conversation of every approach tried, what worked, what failed and why, so the next session starts where this one stopped. Adds tests written from the goal, not the code, and scrubs personal info. Use when the user says kick start, log this session, or what have we tried.
metadata:
  version: "1.0.0"
---

# Kick Start

Keep one file that covers the whole conversation from start to finish: every problem worked on, every approach taken for it, whether it worked, and why. Someone opening it later should see the full path, not just where things ended up.

The output is one log file per conversation in `kickstart/`, plus any new tests.

## When to run

- The user says "kick start", "log this session", "what have we tried", "write up what worked and what didn't" or similar.
- Once on, stay on for the rest of the conversation. Do not wait to be asked again.

## Step 1. Start the log

Create `kickstart/<YYYY-MM-DD>-<short-topic>.md`. If the conversation already has one, keep using it.

If the skill is turned on partway through, backfill first: go back to the start of the conversation and log every problem and approach so far, using the commands, outputs and diffs you can see. Then carry on logging live.

## Step 2. Log every approach as it finishes

Update the file each time an approach finishes, whether it worked or not. Do not save it all up for the end. Long conversations get compacted and the details are lost.

Group approaches under the problem they were trying to solve, in the order they were tried. For each one record:

- **What was done**, in one or two sentences.
- **Why it was chosen.**
- **Result**: `Worked`, `Failed`, or `Partly worked`.
- **Evidence**: the command or test that showed the result, with the real output trimmed to the lines that matter. Never write "it worked" without saying how you know.
- **Why** it worked or failed. If the cause was not confirmed, write `Cause not confirmed` and label your guess as a guess.
- **Kept or undone**: is this change still in the code?

Approaches that worked first time still get logged. The point is the full record, not just the mistakes.

Keep two kinds of claim apart:
- **Checked**: you ran something and saw it.
- **Believed**: you think it is true but did not check.

## Step 3. Keep the summary at the top current

After each update, refresh the summary at the top so a reader gets the state in under a minute.

Use this structure:

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

#### Approach 1.2: <name>. Worked
...

## What worked
One line per approach that worked, with the reason.

## What didn't, do not retry
One line per dead end, with the reason.

## Tests added
| Test | Protects against | Status |
|---|---|---|

## Next steps
Numbered, smallest useful step first.

## Open questions
Things only the user can answer.
```

## Step 4. Add tests that do not just agree with the code

The risk is tests that pass because they were written to match the agent's own output. Those tests lock the bugs in. Add tests as approaches finish, following every rule here.

1. **Expected values come from the goal, never from running the code.** Work out each expected value from the user's request, the docs, a spec or a hand calculation before running anything. Never run the function, copy its output and paste it into an assertion.
2. **One test per approach that failed because of a bug**, so that mistake can't come back. One test per approach that worked, checking the goal it met.
3. **Prove each test can fail.** Briefly put the broken version back (undo the fix, or change one line), run the test and confirm it fails. Restore the code and confirm it passes. A test you have never seen fail proves nothing. Record this in the Status column, for example `Fails on approach 1.1 code, passes now`.
4. **Known bugs stay visible.** If something is still broken, write the test for the correct behaviour and mark it as an expected failure with the reason, for example `@pytest.mark.xfail(strict=True, reason="...")` in Python or `it.failing(...)` in Jest. Never weaken an assertion or delete a test to get a pass.
5. **Do not edit a test to match the code** unless the goal itself was misunderstood. If you do, log it and quote where the goal says so.
6. **Cover the edges the approaches tripped on**: empty input, very large input, odd characters, wrong types, boundaries.
7. **Use the project's existing test setup.** Match its framework, layout and naming. If there is none, use the standard one for the language and say so in the log.
8. **Run the full suite** whenever you add tests, and log the real result, including failures.

## Step 5. Remove personal info

Before every save, scrub the log and every new test file. Replace with a placeholder in angle brackets:

| Remove | Replace with |
|---|---|
| Names of real people | `<NAME>`, or their role, like "the reviewer" |
| Email addresses, phone numbers, street addresses | `<EMAIL>`, `<PHONE>`, `<ADDRESS>` |
| API keys, tokens, passwords, connection strings | `<SECRET>`. Also tell the user it was exposed and should be changed. |
| Home folder paths like `/Users/sam/` or `C:\Users\sam\` | `~/` |
| Private URLs, internal hostnames, IP addresses | `<INTERNAL_URL>`, `<IP>` |
| Customer or user data from logs or databases | Made-up values with the same shape |

Test data must be made up. Never copy real records into a test.

Run this check and fix anything it finds:

```
grep -nEi '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|/Users/[^/ ]+|/home/[^/ ]+|C:\\Users\\|(api[_-]?key|secret|token|password)\s*[:=]|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' kickstart/ <new test files>
```

## Step 6. Write like a person

- No em dashes or en dashes. Use a comma, full stop, colon or brackets.
- No emoji.
- None of these: delve, robust, leverage, seamless, comprehensive, crucial, pivotal, utilize, streamline, "it's worth noting", "in conclusion", "I hope this helps", "great question", "let's dive in", "game-changer".
- No "not only X but also Y", no lists of three for rhythm, no closing paragraph that repeats what was said.
- Plain verbs, short sentences, real numbers.

Check before saving, and fix anything it finds:

```
grep -rnEi '—|–|delve|robust|leverag|seamless|comprehensive|crucial|pivotal|utiliz|streamline|worth noting|in conclusion|hope this helps|great question|dive in|game.changer' kickstart/
```

## Step 7. Tell the user

When the skill turns on, say in one line where the log is. After that, do not announce every update. When the user asks, or the conversation is wrapping up, tell them:
- Where the log is.
- How many problems and approaches it covers, and how many worked.
- Which tests were added, and the latest test result.
- Anything that needs them: open questions, a secret to change.

At the start of a new conversation in the same project, read the newest file in `kickstart/` before starting work.

Do not commit unless the user asks.
