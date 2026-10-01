---
name: research-solving
description: "Researches what a user is building in three rings. Similar open-source projects and code, papers from the user's own field, then ideas from far-off fields (quant research, biometrics, browser signals, local assistants), each rated for real signal versus hype. Ends with a ranked list of cheap experiments. Use when the user says research solving, what's out there for this, or find ideas for what I'm building."
argument-hint: "<what you are building>"
disable-model-invocation: true
license: MIT
compatibility: "Needs web search and web fetch. Uses many searches, so it only runs when you type /research-solving."
metadata:
  version: "1.0.2"
  author: NotRedFox
---

# Research Solving

Find what already exists, what the research says, and which ideas from other fields could carry over. Every claim gets a source you opened, and every idea gets an honest rating. The user leaves with a short list of things to try and a cheap first test for each.

Output: `research/<YYYY-MM-DD>-<topic>.md` in the project, plus a short summary in chat.

## Step 1. Pin down the target

Before searching, write down:

- **What the user is building**, in one sentence, as an outcome ("tell me when I'm procrastinating"), not a method.
- **Constraints**: platform, language, budget, privacy, offline or not, skill level.
- **What they already tried or know about.**
- **Search terms**: 4 to 8 phrases, including the words other fields use for the same problem. For example "procrastination detection" is also "task switching", "attention monitoring", "idle detection", "engagement prediction".

If the target is unclear, ask one question before starting. Otherwise state your assumptions and go.

## Step 2. Ring 1: code that already exists

Search GitHub, package registries (PyPI, npm, crates.io and so on) and the web for projects that solve the same or a close problem.

For the 3 to 8 most useful, record:
- Name, link, licence, last activity (from the commits or releases page), rough size or popularity if shown.
- What it does, and **what to borrow**: a specific file, function, data format or design choice. Open the repo and read at least the README and the core file before saying what it does.
- What to avoid, if anything (abandoned, wrong licence for the user's use, known issues).

Pick for variety: one mature project, one small and readable one, one with an unusual approach. Before suggesting any code is copied, check that its licence allows the user's use.

## Step 3. Ring 2: research in the user's field

Search for papers, benchmarks and datasets. Use Semantic Scholar, arXiv, OpenAlex, Google Scholar, or plain web search with `site:arxiv.org`.

**Never cite from memory.** Models invent citations. Only list a paper after opening its page or resolving its DOI or arXiv ID. If you could only read the abstract, say "abstract only".

For each paper record:
- Title, authors, year, link.
- The claim, in one sentence.
- How strong the evidence is: sample size, real users or lab, replicated or not, effect size if given.
- How it applies to what the user is building.

If no paper page can be opened (blocked sites, paywalls), list what search results show and mark each one `unverified`. An idea that rests only on unverified papers is rated Medium at most. Tell the user which sites were blocked so they can check those papers themselves.

Prefer recent surveys and well-cited work, and include at least one paper that disagrees with the rest if one exists.

## Step 4. Ring 3: look sideways

Most good ideas come from a field that solved the same shape of problem with different words. Pick 5 to 8 fields where the problem has a clear counterpart. Consider, among others:

- **Quantitative research**: finding a weak signal in noisy data, backtesting, guarding against overfitting.
- **Biometrics and behavioural signals**: typing rhythm, mouse movement, heart rate, eye or posture tracking.
- **Signals a browser can see**: tab focus and visibility, idle detection, scroll and input timing, device motion, battery, network, with the user's permission.
- **Local and offline assistants**: on-device models, local speech recognition, privacy-first designs.
- **Open-source "Jarvis" style assistants**: how they handle wake words, memory, tools and routines.
- **Any other field** where the same problem appears: medicine, games, logistics, sports science, manufacturing, ecology.

For each idea, write down the bridge (what the idea is there, and what it would be here). Then rate it:

| Rating | Meaning |
|---|---|
| **High** | Works in its home field with solid evidence, and the bridge is direct |
| **Medium** | Works there, but the bridge needs a real assumption to hold |
| **Low** | Weak evidence, or the bridge is a stretch |
| **Hype** | Mostly marketing, demos or anecdotes |

Mark an idea as Hype or Low when you see: only demo videos or vendor claims, no independent replication, tiny or self-selected data, many signals tested with only the best one reported, or results that only hold in a lab.

Flag anything that collects biometric or behavioural data: it needs the user's clear consent and may fall under privacy law (GDPR treats biometric data as a special category).

## Step 5. Rank what to try

Combine the three rings into a ranked list of 5 to 10 things to try. Rank by signal, then by how cheap it is to test. For each:

- What to try, in one sentence.
- Why: the sources behind it.
- **A first test that takes under a day of work to set up**, with a clear pass or fail result. If the result needs longer to collect (a week of normal use), say how long, and add a smaller check that gives a result the same day.
- Rough cost: time, money, data needed.

If the top idea can be tested cheaply here (a small script, a public dataset, an API call), run it and include the real result. Mark every result as `run` or `not run`.

## Step 6. Write the report

`research/<YYYY-MM-DD>-<topic>.md`:

```markdown
# <Topic>

Researched <YYYY-MM-DD>.

## Target
## Top things to try
| # | Try this | Rating | First test | Cost |
|---|---|---|---|---|
## Ring 1: existing code
## Ring 2: research
## Ring 3: ideas from other fields
| Field | Idea there | Idea here | Rating | Why |
|---|---|---|---|---|
## First tests
Each test, marked `run` or `not run`, with the real output for those that ran.
## Dead ends
Things that looked promising and why they were dropped.
## Sources
Every link, marked `opened`, `abstract only` or `unverified`.
```

## Step 7. Check before saving

- Every source in the report was opened or resolved, or is marked `unverified`.
- No personal info about the user or anyone else.
- Writing rules: no em or en dashes, no emoji, no exclamation marks, no filler (genuinely, actually, really, simply, just, basically), no inflated words (delve, robust, leverage, seamless, comprehensive, crucial, cutting-edge, game-changer, landscape, journey), no stock phrases ("it's worth noting", "in conclusion", "in today's world"). Plain sentences and real numbers.

Run this from the project root. Quoted paper titles and code are exempt.

```
grep -nEi '—|–|!( |$)|\b(genuinely|actually|really|truly|simply|just|basically|delv\w*|robust|leverag\w*|seamless|comprehensive|crucial|pivotal|utiliz\w*|cutting.edge|game.changer|landscape|journey|furthermore|moreover)\b|worth noting|in conclusion|in today.s' research/*.md research/**/*.* 2>/dev/null
```

## Step 8. Tell the user

In chat, give the top 3 things to try with their first tests, say how many sources were checked, and link the report. Do not commit unless the user asks.
