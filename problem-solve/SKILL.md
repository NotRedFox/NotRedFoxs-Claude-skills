---
name: problem-solve
description: "For problems where the obvious route is blocked, like no API. Climbs from obvious to more creative approaches and tests each one for real instead of stopping at \"impossible\". Uses odd resources the user suggests, and writes a ChatGPT handoff prompt with everything tried so far. Use when the user says problem solve, there's no API, or I'm stuck."
argument-hint: "<what you want to happen>"
license: MIT
compatibility: "Claude Code recommended, so approaches can be tested. The ChatGPT handoff is a prompt you paste yourself."
metadata:
  version: "1.0.1"
  author: NotRedFox
---

# Problem Solve

Get the user to the outcome they want when the normal route is closed. Try approaches that get more creative step by step, test each one for real, and keep going. Then hand the whole picture to a second model for ideas this one would not think of.

Output:
- `problem-solve/<YYYY-MM-DD>-<topic>.md`: the log of every approach and test.
- `problem-solve/tests/`: the test scripts and their output, so every result can be re-run.
- `problem-solve/<YYYY-MM-DD>-<topic>-chatgpt.md`: a prompt for the user to paste into ChatGPT, also shown in chat in a code block.

## Ground rules

- **"Impossible", "never been done" and "there's no API" are not answers.** Treat each one as a constraint to route around. Record it and look for another path.
- **Creative, not reckless.** Stop only at things that are illegal, break into systems or accounts the user does not own, get around security or paywalls, break a service's terms in a way that harms others, or cross a limit the user set. Say which line it would cross and keep looking for another path.
- **Test, don't speculate.** An approach counts once there is a test with a real result. If it cannot be tested here (hardware, another person's account), write the exact test for the user to run and mark it `not run`.
- **Small tests first.** A test is the smallest thing that proves or kills an approach: one request, a 20-line script, one sample file. Build properly only once something works.

## Step 1. Restate the problem

- **The outcome**, not the method: "know when the washing machine finishes", not "get the washing machine API".
- **Constraints, split in two**: real ones (budget, the device has no network) and assumed ones (it needs an app, it must be exact). Challenge every assumed one.
- **What has already been tried**, and what happened.

## Step 2. Ask for odd resources

Ask the user once, early:

> What do you have that I might not think of? Old phones or tablets, smart speakers, a spare Raspberry Pi, sensors, accounts and exports, email or text notifications the service already sends, a browser that is always open, physical access to the thing, someone who could press a button, anything at all.

Add their answers to the log. Treat every one as a possible building block, and say which approach uses it. If the user is not available, list the resources you assumed.

## Step 3. Climb the ladder

Work up these levels. At each level, list 2 to 4 approaches, test the cheapest first, and log the result. Move up a level once each approach at this level is tested, blocked, or has a written test marked `not run` because it needs something you don't have.

| Level | Kind of approach | Examples |
|---|---|---|
| 1. Obvious | The official route | Official API, SDK, docs, an existing library, the vendor's own integration |
| 2. Sideways in the same system | Another door into the same data | Data export, email or push notifications, RSS, webhooks, calendar feeds, the public endpoints the site's own web page calls, automating the user's own logged-in browser |
| 3. Different channel | Read the effect, not the system | Sound, light, vibration, power draw, screen OCR, camera, phone sensors, file changes, network activity on the user's own network |
| 4. Reframe | Change the problem | Invert it, solve an easier version, combine two weak signals, let a person do one step, borrow an answer from another field, find the contradiction and remove it |
| 5. Build the missing piece | Make what doesn't exist | A small device, a shared dataset, a tiny service, a browser extension |

For each approach log:
- Level, and what it is.
- Which user resource it uses, if any.
- The test: command, script or steps.
- Result: `Works`, `Partly works`, `Failed` or `Not run`, with the real output. If the test used made-up or simulated data, say so next to the result, for example `Works (synthetic data)`.
- What it taught, even if it failed.

When something works, say how reliable it looked (for example 9 of 10 runs), and what would make it fail.

## Step 4. Write the ChatGPT handoff

A different model brings different ideas. Same-model brainstorming tends to repeat itself. Write the handoff once the first round of tests is done, and again after each new round.

`problem-solve/<YYYY-MM-DD>-<topic>-chatgpt.md`, also shown in chat in a code block so the user can copy it:

```markdown
I'm trying to <outcome>. I want creative approaches. Do not tell me it's impossible or has never been done; if one route is blocked, suggest another.

Real constraints:
- ...

What I have to work with:
- ...

Already tried (do not suggest these again):
| Approach | What happened |
|---|---|

What I need from you:
1. Give me 10 approaches I haven't tried. At least 4 should borrow from unrelated fields.
2. For each, give the smallest test that would prove or kill it in under an hour.
3. Rank them by how cheap that test is.
4. Stay legal and within accounts and devices I own.
```

Then tell the user: "Paste this into ChatGPT and paste its answer back here. I'll test the promising ones." When the answer comes back, add those approaches to the ladder at the right level, test them, and update the handoff for another round.

**The handoff goes to a third party.** Before writing it, remove names, emails, addresses, account numbers, keys, passwords, home folder paths and anything else that identifies the user. Use placeholders like `<EMAIL>`.

## Step 5. Report

The log, `problem-solve/<YYYY-MM-DD>-<topic>.md`:

```markdown
# <Problem>

Started <YYYY-MM-DD>. Last updated <YYYY-MM-DD>.

## Outcome wanted
## Best answer so far
What works, how reliable it is, and how to set it up.
## Constraints
- Real: ...
- Assumed, and challenged: ...
## Resources
## Ladder
### Level 1: Obvious
#### 1.1 <approach>. Failed
- Uses: ...
- Test: ...
- Result: ...
- Learned: ...
## Lines not crossed
Approaches skipped because they would break a law, terms or someone else's security, and what was tried instead.
## ChatGPT rounds
What each round suggested and what happened when it was tested.
## Next tests
```

## Step 6. Write like a person

No em or en dashes, no emoji, no exclamation marks, no filler (genuinely, actually, really, simply, just, basically), no inflated words (delve, robust, leverage, seamless, comprehensive, crucial, cutting-edge, game-changer, landscape, journey), no stock phrases ("it's worth noting", "in conclusion"). Plain sentences and real numbers.

Run this from the project root. It covers the log, the handoff and comments in the test scripts. Code and quoted titles are exempt.

```
grep -nEi '—|–|!( |$)|\b(genuinely|actually|really|truly|simply|just|basically|delv\w*|robust|leverag\w*|seamless|comprehensive|crucial|pivotal|utiliz\w*|cutting.edge|game.changer|landscape|journey|furthermore|moreover)\b|worth noting|in conclusion' problem-solve/*.md problem-solve/tests/*.py
```

The ChatGPT prompt is the one place where "do not tell me it's impossible" is fine: it is an instruction, not filler.

Do not commit unless the user asks.
