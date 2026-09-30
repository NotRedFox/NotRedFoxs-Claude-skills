---
name: tournament-forge
description: Run a budget-aware bracket tournament of genuinely different solution approaches (blind builds, grounded attacks, bias-controlled judging, spec-first tests for software, graft-merge synthesis) for hard problems where one answer isn't enough.
---

# Tournament Forge

Make several *genuinely different* solutions to a hard problem fight 1v1 in a bracket, with grounded attacks and bias-controlled judging, then forge the survivor plus the best parts of the losers into one audited blueprint. For software, the fights are settled by running tests wherever possible, not by opinion. Built to be cheaper and more trustworthy than "spawn N agents and let them argue".

## Why it is designed this way (research this skill is built on)

Follow these rules because each one fixes a known failure of naive multi-agent debate:

1. **Debate alone barely helps; voting and verification do.** Choi et al., *Debate or Vote* (NeurIPS 2025): most of multi-agent debate's gains come from majority voting; free-form debate is a martingale (no expected improvement) unless updates are biased toward *correction*. So attacks must be concrete and checkable, real checks run wherever possible, and convergence is used as a cheap early exit.
2. **Same-model agents think alike ("Artificial Hivemind", Jiang et al. 2025).** Persona labels mostly change tone, not substance. So diversity is forced at the *approach* level (different mechanism or architecture), generated in one enumeration call, deduplicated, and built blind. Never anchor all contenders on one premium draft first; that collapses diversity before the tournament starts.
3. **Ask for the distribution, not one answer (Verbalized Sampling, Zhang et al. 2025).** Asking for several approaches *with rough probabilities*, including low-probability ones, recovers 2 to 3x more diversity.
4. **Heterogeneity helps, but quality matters more.** Mixed-model debate beats same-model debate, but *Rethinking Mixture-of-Agents* (Li et al. 2025) found mixing in weaker models often hurts. So cheap models screen and judge early rounds; strong models build hard solutions and judge late rounds.
5. **Judges are biased** (position, verbosity, self-preference; Zheng et al. 2023 and follow-ups). So: anonymize, swap order on close calls, forbid length as a criterion, judge is never the author, rubric fixed *before* anyone sees answers.
6. **Agents cave to peers (identity-driven sycophancy; *When Identity Skews Debate*, 2025).** So contenders are labelled A and B only.
7. **Models can't reliably self-correct without an external signal (Huang et al., ICLR 2024).** So a critique only counts if it names a concrete failure scenario that can be checked.
8. **Execution beats judgment for code.** CodeT (Chen et al., ICLR 2023) picks code by agreement between generated tests and multiple solutions; S* (Li et al. 2025) settles pairwise matches by synthesizing an input where two programs differ and running both. So software matches use tests and distinguishing inputs first, opinion second.
9. **Tests written after seeing buggy code tend to bless the bug** (misguidance effect, 2026 study on LLM-generated unit tests). So tests are written from the spec only, by an agent that never sees any solution.
10. **Good tournaments evolve, not just eliminate** (Google AI Co-Scientist: generate, reflect, Elo tournament, evolve; Dicklesworthstone/llm-tournament merges strongest features across rounds). So losers' uniquely good ideas are harvested as *grafts*.
11. **Measured lesson from a real run:** identical spec-test results hid an over-blocking bug that only a brute-force differential fuzz exposed, and that fuzz cost zero model calls. Running code is the cheapest and most decisive judge available.
12. **Sparse communication saves tokens without losing accuracy** (Li et al. 2024). So each match sees only two candidates plus the rubric, never the history.

## When to use

Use for hard, open problems with several credible approaches: architecture and system design, tricky bugs with several hypotheses, algorithm choices, product or strategy decisions, plans. Do NOT use for simple factual questions or tasks with one obvious answer; answer those directly and tell the user the tournament would waste tokens.

## Budget tiers

Pick a tier (default **Standard**). If the user said nothing, choose from problem difficulty and say which you picked.

| Tier | Contenders | Rounds | Approx. subagent calls |
|---|---|---|---|
| Quick | 4 | SF, Final | about 9 to 12 |
| Standard | 8 | QF, SF, Final | about 18 to 25 |
| Deep | 16 | R16, QF, SF, Final | about 38 to 52 |

Test mode adds 1 to 3 calls (test writer, test review, distinguishing inputs) and some tool runs; it often *saves* calls because failing builds are cut at the gate.

**Calls are the cost that matters.** In a measured run each subagent call cost about 57k tokens, mostly fixed overhead, regardless of prompt size. So: do Stage 0 (brief), Stage 1 (enumeration) and Stage 5 (forge) yourself as the orchestrator instead of spawning agents for them, prefer running code over calling a model, and skip any optional call that can't change the outcome.

Model routing (use the Agent tool's `model` parameter when available):
- **Strong (opus)**: final judges. The brief, enumeration and forge are done by you, the orchestrator.
- **Mid (sonnet)**: building contenders for hard or technical problems, test writer, semifinal critics and judges, final red-team.
- **Cheap (haiku)**: gate and test review, early-round critics and judges, builds for simple or creative problems.

If the Agent tool is not available, run the stages yourself in-context with strict separation: write the tests before any solution, write each contender fully before reading the next, and judge from the rubric only. Tell the user this is the lower-fidelity mode.

## Pipeline

### Stage 0: Sharpen the input (fixes garbage in, garbage out)

Do this yourself. Produce a compact **Brief**:
- Problem restated in one or two sentences, plus what is explicitly out of scope.
- Hard constraints (must / must-not), soft preferences, and context (stack, scale, budget, audience).
- **Rubric**: 4 to 6 weighted criteria written *now, before any solution exists*. Always include correctness/feasibility and risk; add what the problem needs (simplicity, cost, security, performance, maintainability).
- **Checks**: anything verifiable (numbers to compute, requirements to trace, scenarios to simulate).
- **Mode**: set `test_mode = on` if the deliverable is code, a script, a config, a query, an API, or anything else that can be executed or simulated. Otherwise `off`.
- Open questions. If an answer would change the approach set, ask the user (AskUserQuestion) before continuing; otherwise state the assumption and proceed.

### Stage 0b: Spec-first tests (test_mode only)

One mid call, a **Test Writer** that sees ONLY the Brief. It never sees any solution, now or later.
- Write 5 to 12 tests in the project's language and test framework (detect it from the repo if there is one; otherwise pick the obvious default, such as pytest or vitest).
- Cover: the happy path, each hard constraint (tag these `HARD`), edge cases and boundaries, failure and outage behaviour, and at least one property or invariant test where it fits.
- Each test gets a one-line reason pointing at the Brief line it checks. A test with no Brief line behind it is dropped.
- Tests target a small interface the Brief defines (function names, endpoints, CLI) so every contender can be run against the same suite. Put that interface in the Brief and in every build card.
- If execution is impossible here (no runtime, needs external services), write the tests anyway as precise scenario scripts and mark results as `traced`, not `run`. Say so in the final output.

### Stage 1: Enumerate genuinely different approaches

Do this yourself, following this prompt:
> List {2 x N} distinct approaches to this Brief. Each must differ in *core mechanism* (not wording, tone, or emphasis). For each give: name, one-line mechanism, key bet or assumption, and a rough probability that a typical expert would propose it. At least a third must be below 20% probability. Include at least one "minimal / do-less" approach and one "reframe the problem" approach.

Then you (orchestrator) deduplicate: merge any two whose mechanism is the same. Keep the N most distinct *plausible* ones. If fewer than N survive, shrink the bracket; never pad with near-duplicates.

### Stage 2: Blind builds (parallel)

Launch N subagents in ONE message. Each gets only the Brief, its one approach card, and (test_mode) the shared interface and the test file. Instructions:
- Build the strongest version of THIS approach; do not hedge toward other approaches.
- test_mode: the build must run against the test file. The builder may run the tests and fix its own code once, but may NOT edit the tests.
- Output a fixed compact format, max about 400 words, or code plus 150 words or fewer: `Summary`, `Design/Answer`, `Rubric fit`, `Known weaknesses`, `How to verify` (test_mode: `Test results`).
- No preamble, no restating the problem.

### Stage 3: Gate (cheap filter before any debate)

- test_mode: run the full suite against every build yourself (Bash). Record a pass/fail matrix.
  - **Test review (one cheap call):** any test that most builds fail is suspicious. Show the reviewer the test, its Brief line and the failure outputs (not the code). Verdict: `valid` (keep), `wrong` (fix or drop the test, then re-run), or `ambiguous` (downgrade to soft). This is the CodeT idea: tests and solutions check each other.
  - A build that fails a valid `HARD` test is out. Give it one debug pass first only if it failed on something trivial (import, typo, signature).
- Always: fail anything that breaks a hard constraint, is internally contradictory, or fails a Stage-0 check.
- **Differential check (test_mode, no model call):** if you can write a brute-force oracle or a slow-but-obviously-correct reference from the Brief, run every surviving build against it on a few thousand random inputs yourself. Also run builds against each other and flag any input where they disagree. A mismatch with the oracle on a HARD rule is a verified failure: the build is out. **Shrink** each failing input to the smallest reproduction (drop steps while it still fails) before recording it; unshrunk inputs often don't reproduce in isolation.
- **Convergence exit:** skip the bracket only if survivors are the same answer in substance. In test_mode that means identical results on the spec tests AND on the differential check. Identical spec-test rows alone are not enough; different mechanisms often pass the same tests.
- Also measure what the rubric cares about that tests can't show (memory, speed at scale) with a quick script, and hand the numbers to the critic and judges as evidence.
- **Seed** survivors by test pass rate, then quick rubric score, so the two strongest can't meet before the final. Missing slots become byes for the top seeds.

### Stage 4: Bracket matches

Label contenders only as **A** and **B**. Each match sees only: Brief, rubric, candidate A, candidate B, and (test_mode) both test rows.

Each match gets a **critique lens**; rotate them and add domain lenses as needed:
- **Pessimistic Auditor**: failure modes, security holes, edge cases, wrong assumptions.
- **Simplicity / UX Architect**: what a human has to understand, operate, or maintain.
- **Cost Economist**: tokens, compute, money, time to build, operational burden.
- **Reality Checker**: does it actually satisfy every hard constraint and check?

Match procedure:
1. **test_mode, both pass the same tests: distinguishing input.** One cheap call proposes 1 to 3 inputs where A and B would behave differently (S* style). Run both. Decide which output the Brief says is correct; if the Brief can't decide it, the input is not decisive. A decisive result counts as a verified failure for the loser.
2. **Critic call** (lens assigned): for EACH candidate, up to 3 attacks. Every attack must include a concrete scenario (input or situation, then the specific bad outcome) and the rubric item it hits. Attacks without a concrete scenario are discarded. In test_mode, an attack that can be expressed as a test should be; run it. Also list each candidate's 1 or 2 strongest *unique* ideas.
3. **Rebuttal (only if needed):** if one disputable attack would decide the match, give the targeted builder a single rebuttal of 100 words or fewer. Otherwise skip it.
4. **Judge call:** score both on the rubric using test results and surviving attacks, then pick a winner with a margin (clear or narrow). Rules: executed evidence beats argument; length and polish are not criteria; cite rubric items.
5. **Position swap on close calls:** if the margin is narrow, re-judge with A and B swapped in a fresh call. If the verdicts disagree, it's a tie: advance the one that wins the highest-weighted rubric item.
6. **Harvest grafts:** record the loser's strongest unique ideas that survived critique into a Graft List (idea plus the rubric item it improves). Discard only logic that was actually broken.

Winners carry forward their build plus a note of three lines or fewer: attacks survived, fixes owed. Never carry transcripts.

From semifinals on use a mid model; the final uses a strong judge and ALWAYS runs the position swap.

### Stage 5: Forge (synthesis)

Do this yourself (the orchestrator) with: Brief, champion, finalist, Graft List, unresolved attacks, (test_mode) the test file and every test that any finalist failed.
- Start from the champion; integrate only grafts that improve a rubric item without breaking a hard constraint; fix every upheld attack.
- test_mode: add a regression test for every upheld attack and every distinguishing input that decided a match, using the shrunk reproduction. Check that each regression test fails on the build it knocked out; if it doesn't, it doesn't reproduce the bug yet. Run the whole suite on the forged result. It must pass all valid tests; if not, one fix pass, then report what still fails.
- Then one fresh red-team call (mid model, Auditor lens) on the forged result. In test_mode it must express each finding as a test. Fix anything concrete it finds. Stop there, no loops.

## Final output to the user

Keep it tight. Deliver:
1. **The answer / blueprint**, at production-ready detail for the problem type. Code goes into files.
2. **Why this won**: 3 to 5 bullets tied to rubric items, attacks survived and tests passed.
3. **Grafts adopted**: which ideas came from losing approaches.
4. **Alternatives considered**: one line each for eliminated approaches and why they lost.
5. **test_mode: the test suite** as a file, with the final pass/fail summary, and a note on which tests were `run` versus `traced`.
6. **Remaining risks and how to verify** them.
7. **Run stats**: tier, contenders, calls used, ties, early exits, tests written, tests dropped by review.

If the deliverable is long (a design doc or plan), offer to put it into a document.

## Hard rules

- The rubric and the tests are fixed from the Brief before any solution exists. Tests may only change through the Stage 3 test review, never because a favoured solution failed them.
- The Test Writer never sees solution code.
- Builders may not edit tests.
- Never tell a judge or critic which model or contender wrote what.
- Never let contenders see each other's builds before the bracket.
- Unverifiable criticism doesn't eliminate anything. Executed evidence outranks argument.
- No conversational filler in any subagent output; enforce the formats and word caps.
- Respect the tier's call budget; if a stage would exceed it, shrink the bracket and say so.
- If the problem turns out simple, stop early and just answer.
