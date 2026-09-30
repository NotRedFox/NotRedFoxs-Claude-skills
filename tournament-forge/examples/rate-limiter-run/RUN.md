# Real run: per-key rate limiter (Quick tier, test mode on)

This is a **real, recorded run** of Tournament Forge, not an illustration. Every file in this folder was produced during the run, and every number below was measured.

**Task:** [BRIEF.md](BRIEF.md). Build an exact rolling-window rate limiter in Python with a fixed interface, 9 rules (3 of them HARD), and a rubric locked before any code existed.

## Result

| | |
|---|---|
| Contenders | 4 |
| Subagent calls | 9 (plus 1 retry caused by a prompt mistake) |
| Subagent tokens | ~521k (about 57k per call) |
| Final answer | [limiter.py](limiter.py), passes 15/15 tests |
| Brute-force fuzz | 0 mismatches in 3,000 scenarios x 40 requests |

## What happened, stage by stage

**Stage 0b: spec-first tests.** A test writer saw only the brief and wrote [test_spec.py](test_spec.py) (11 tests, including a thread test, a speed test and a randomized brute-force property test).

**Stage 1 and 2: four blind builds.**

| | Approach | Spec tests |
|---|---|---|
| A | Sliding log (deque + running sum) | 11/11 |
| B | Token bucket (common) | 4/11 |
| C | Ring buffer of unit timestamps (long shot) | 11/11 |
| D | Bucketed sliding window (long shot) | 11/11 |

**Stage 3: gate.**
- **B out:** it fails the HARD rolling-window tests. A token bucket can't enforce an exact rolling window. The tests proved it; nobody had to argue.
- **Differential fuzz:** A, C and D had identical test results, so the orchestrator ran them against a brute-force oracle ([differential_fuzz.py](differential_fuzz.py)). **D over-blocked 20 times.** It was shrunk to a 3-request reproduction: limit 7, window 1s, admit cost 4 at 0.032036 and cost 1 at 0.041815, then cost 4 at 1.035956 must be allowed but D denied it. D is out on HARD rule R2.

**Stage 4: final, A vs C** (labelled only as "A" and "B" for the judges, and swapped for the second judge).
- The critic (Pessimistic Auditor) verified by running code:
  - C preallocates `limit` slots per key: **800 MB** for 1,000 keys at limit 100,000, versus 1.6 MB for A.
  - A's denied requests scan the whole log under the global lock: **~1000x slower** than C on large-cost denials.
- Two strong judges, opposite orders. Both picked the sliding log, clear margin (89 vs 71, and 90 vs 75).

**Stage 5: forge.** Champion: sliding log. Grafts:
- From C (ring buffer): sorted arrays plus binary search, so denied calls became O(log n). 200 denied calls went from 0.445 s to 0.0002 s.
- From D (bucketed window): bounded memory over time, via sweeping idle keys.

Memory at limit 100,000 dropped to 0.7 MB.

**Red-team.** A fresh agent found a real floating-point bug: a call at exactly `now + retry_after` could land one ulp short of the cutoff and still be denied (rule R4). The same bug was in the champion and in C. It was fixed and kept as [test_redteam.py](test_redteam.py).

Every upheld attack became a test in [test_regressions.py](test_regressions.py).

## What the run taught us (already folded back into the skill)

1. **Identical test results don't mean identical answers.** The first version of the skill would have stopped early here. Now a differential fuzz runs first.
2. **The cheapest, most decisive step was running code, not calling a model.** The orchestrator's fuzz against a brute-force oracle cost zero subagent calls and eliminated a contender.
3. **Shrink failing inputs before turning them into tests.** The first regression test copied a partial history and didn't reproduce the bug.
4. **Per-call overhead dominates cost.** Each subagent call cost ~57k tokens in this environment, mostly fixed overhead. Fewer calls matters more than shorter prompts, so the orchestrator now does the brief, the enumeration and the forge itself.

## Reproduce

```
pip install pytest
python -m pytest -q test_spec.py test_regressions.py test_redteam.py
python differential_fuzz.py
```
