# Tournament Forge

Version 1.0.3. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that makes several solutions that work in different ways to a hard problem fight 1v1 in a bracket. For code, matches are settled by **running tests**, not by opinion. The winner is merged with the best ideas from the losers into one audited answer.

| | Tournament Forge (standard) | arena-skill (full) |
|---|---|---|
| Subagent calls | ~22 | 595 |
| Estimated tokens | ~1.3M | ~34M |

**Tested for real:** see [examples/rate-limiter-run](examples/rate-limiter-run/RUN.md). 4 approaches, 9 subagent calls, ~521k tokens (measured). The spec tests knocked out one contender and the brute-force fuzz knocked out another, the red-team found a real float bug, and the final code passes 15/15 tests plus 3,000 brute-force fuzz scenarios.

![Example run](https://raw.githubusercontent.com/NotRedFox/NotRedFoxs-Claude-skills/main/tournament-forge/assets/example-desktop.png)

> The image is an **illustrative example**. For a real recorded run, see [examples/rate-limiter-run](examples/rate-limiter-run/RUN.md). [Open the clickable version](https://notredfox.github.io/NotRedFoxs-Claude-skills/tournament-forge/assets/example.html) in your browser.

## Why another debate skill?

Plenty of "make agents argue" skills exist, and this one borrows from several (see [Credits](#credits)). But research on multi-agent debate keeps finding the same failure modes:

| Problem the research found | What Tournament Forge does |
|---|---|
| Most gains from debate come from simple voting. Arguing alone doesn't improve accuracy. | Cheap checks and tests run first. If the survivors give the same answer in substance, the bracket is skipped. |
| Copies of the same model give near-identical answers, even with personas. | Diversity comes from different **mechanisms**. A third of approaches must be long shots. |
| LLM judges favour the first answer, longer answers, and their own writing. | Contenders are only "A" and "B". Close calls are re-judged with the order swapped. Length doesn't count. |
| Agents cave to peers. | Nobody knows who wrote what. Builders never see each other's work. |
| Models can't reliably fix their own reasoning without an outside signal. | An attack only counts if it names a concrete failure. For code, it has to become a test. |
| Tests written after seeing buggy code tend to approve the bug. | Tests are written from the spec only, before any code exists, by an agent that never sees solutions. |
| Elimination throws away good ideas. | The losers' best surviving ideas are kept as "grafts" and merged in. |

## How it works

```
Stage 0   Sharpen      Restate the problem, lock constraints and a weighted rubric
Stage 0b  Tests        (code only) Write tests from the spec, before any solution
Stage 1   Enumerate    List 2N approaches with probabilities, keep the N most distinct
Stage 2   Build        Each approach is built in parallel, blind to the others
Stage 3   Run + gate   Run the tests, fuzz against a brute-force oracle, cut HARD failures, stop early on real consensus
Stage 4   Bracket      1v1 matches: distinguishing inputs, lens critic, judge, order swap, harvest grafts
Stage 5   Forge        Champion + grafts, regression tests, one red-team pass
```

### Test mode (automatic for software)

If the answer is code, a script, a config, a query or an API, test mode turns on:

1. **Tests from the spec first.** A separate agent writes 5 to 12 tests from the brief only. Hard constraints are tagged `HARD`.
2. **Tests check the solutions, and the solutions check the tests.** If most builds fail a test, a reviewer checks that test against the spec. It can be kept, fixed or downgraded ([CodeT](https://arxiv.org/abs/2207.10397) idea).
3. **Distinguishing inputs.** When two finalists pass the same tests, an agent looks for an input where they behave differently, and both get run on it ([S*](https://arxiv.org/abs/2502.14382) idea).
4. **You get the tests.** The final answer ships with the suite, plus a regression test for every attack that was upheld.

If code can't run in your environment, the tests are traced by hand and clearly marked `traced`, not `run`.

### Critic lenses

- **Pessimistic Auditor**: failure modes, security, edge cases
- **Simplicity / UX Architect**: what a human has to understand and maintain
- **Cost Economist**: tokens, compute, money, operational load
- **Reality Checker**: does it meet every hard constraint?

### Budget tiers

| Tier | Contenders | Subagent calls | Estimated tokens |
|---|---|---|---|
| Quick | 4 | ~10 | ~0.55M (measured: 521k) |
| Standard (default) | 8 | ~22 | ~1.3M |
| Deep | 16 | ~45 | ~2.6M |

For comparison, arena-skill's `--quick` mode is 91 calls (~5.2M tokens) and its full run is 595 calls (~34M tokens).

**How tokens are estimated:** from a measured cost per call. In the real run each subagent call cost about 57k tokens, mostly fixed overhead that doesn't depend on prompt size. The same 57k per call is applied to every tool, so the comparison comes down to call counts. Your numbers will differ by environment, but the ratio holds.

Cheap models do screening and early judging. The orchestrator writes the brief, lists the approaches and does the synthesis, and strong models judge the final.

### What you get back

1. The forged answer or blueprint
2. Why it won (rubric, attacks survived, tests passed)
3. Ideas grafted in from losing approaches
4. One line on each eliminated approach
5. The test suite and results (code only)
6. Remaining risks and how to verify them
7. Run stats

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [tournament-forge-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge-claude-app.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge.zip -o /tmp/tournament-forge.zip && unzip -oq /tmp/tournament-forge.zip -d ~/.claude/skills && rm /tmp/tournament-forge.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

The two downloads hold the same skill. The Claude Code one also has Claude Code settings (an argument hint, and a setting so it only runs when you ask), which the Claude app doesn't accept.
It only runs when you type `/tournament-forge`, so Claude never starts it on its own.

Then ask something like:

> Use tournament-forge on: how should we add rate limiting to our public API?

It works best with subagents. Without them, it runs in a lower-fidelity single-context mode and says so. For simple questions it tells you the tournament would waste tokens and answers directly.

## Credits

- [arena-skill](https://github.com/Jakeschincariol/arena-skill) by Jakeschincariol: the 100-agent bracket this started from
- [llm-council](https://github.com/karpathy/llm-council) by Andrej Karpathy: anonymous peer review plus a synthesising chairman
- [agent-review-panel](https://github.com/wan-huiyan/agent-review-panel) by wan-huiyan: verification and anti-groupthink checks
- [llm-tournament](https://github.com/Dicklesworthstone/llm-tournament) by Dicklesworthstone: merging the strongest features across rounds

## Research

- Choi et al., [Debate or Vote: Which Yields Better Decisions in Multi-Agent LLMs?](https://arxiv.org/abs/2508.17536) (NeurIPS 2025)
- Jiang et al., [Artificial Hivemind: The Open-Ended Homogeneity of Language Models](https://arxiv.org/abs/2510.22954)
- Zhang et al., [Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity](https://arxiv.org/abs/2510.01171)
- Li et al., [Rethinking Mixture-of-Agents: Is Mixing Different LLMs Beneficial?](https://arxiv.org/abs/2502.00674)
- [When Identity Skews Debate: Anonymization for Bias-Reduced Multi-Agent Reasoning](https://arxiv.org/abs/2510.07517)
- Huang et al., [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) (ICLR 2024)
- Chen et al., [CodeT: Code Generation with Generated Tests](https://arxiv.org/abs/2207.10397) (ICLR 2023)
- Li et al., [S*: Test Time Scaling for Code Generation](https://arxiv.org/abs/2502.14382) (EMNLP Findings 2025)
- [Evaluating and Mitigating the Misguidance Effect of Buggy Code in LLM-Generated Unit Tests](https://arxiv.org/abs/2607.22883)
- Google Research, [Towards an AI co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/)
- Li et al., [Improving Multi-Agent Debate with Sparse Communication Topology](https://arxiv.org/abs/2406.11776)
- Liu et al., [Pairwise RM: Best-of-N Sampling with Knockout Tournament](https://huggingface.co/papers/2501.13007)

## License

MIT
