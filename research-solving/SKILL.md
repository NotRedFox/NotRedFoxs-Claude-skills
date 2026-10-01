---
name: research-solving
description: "Researches what a user is building with a team of three parallel researchers. Similar open-source projects and code, papers from the user's own field, then ideas from far-off fields (quant research, biometrics, browser signals, local assistants), each rated for real signal versus hype. Ends with a ranked list of cheap experiments."
argument-hint: "<what you are building>"
disable-model-invocation: true
license: MIT
compatibility: "Needs web search and web fetch. Uses many searches, so it only runs when you type /research-solving."
metadata:
  version: "1.1.0"
  author: NotRedFox
---

# Research Solving

Find what already exists, what the research says, and which ideas from other fields could carry over. Three researchers work at the same time, one per ring, and you (the lead) check their sources and rank the results. Every claim gets a source someone opened, and every idea gets an honest rating. The user leaves with a short list of things to try and a cheap first test for each.

Output: `research/<YYYY-MM-DD>-<topic>.md` in the project, plus a short summary in chat.

## Step 1. Pin down the target (lead)

Before searching, write a short brief:

- **What the user is building**, in one sentence, as an outcome ("tell me when I'm procrastinating"), not a method.
- **Constraints**: platform, language, budget, privacy, offline or not, skill level.
- **What they already tried or know about.**
- **Search terms**: 4 to 8 phrases, including the words other fields use for the same problem. For example "procrastination detection" is also "task switching", "attention monitoring", "idle detection", "engagement prediction".

If the target is unclear, ask one question before starting. Otherwise state your assumptions and go.

## Step 2. Launch the research team

Start three subagents in one message so they run in parallel. Give each one the brief from Step 1, its ring's instructions below, and the shared rules. Use a general-purpose agent with web search and fetch.

Ask each to return **only** a compact result, at most about 600 words: a list of findings in the format its ring asks for, each with its link and a source status (`opened`, `abstract only` or `unverified`), plus one line on what it searched and any sites that were blocked. No preamble, no raw search output.

If you can't start subagents, run the three rings yourself, one after another, using the same instructions.

### Shared rules for every researcher

- **Never cite from memory.** Models invent sources. Only list something after opening its page, or resolving its DOI or arXiv ID. If only the abstract was readable, say `abstract only`. If the page could not be opened at all, mark it `unverified`.
- Say which sites were blocked.
- Don't collect personal info about anyone.

### Ring 1 brief: code that already exists

Search GitHub, package registries (PyPI, npm, crates.io and so on) and the web for projects that solve the same or a close problem. Return the 3 to 8 most useful, picked for variety (one mature project, one small and readable one, one with an unusual approach). For each:
- Name, link, licence, last activity (from the commits or releases page), rough size or popularity if shown.
- What it does, and **what to borrow**: a specific file, function, data format or design choice. Open the repo and read at least the README and the core file before saying what it does.
- What to avoid, if anything (abandoned, licence that doesn't fit, known issues).

### Ring 2 brief: research in the user's field

Search for papers, benchmarks and datasets: Semantic Scholar, arXiv, OpenAlex, Google Scholar, or web search with `site:arxiv.org`. Prefer recent surveys and well-cited work, and include at least one paper that disagrees with the rest if one exists. For each:
- Title, authors, year, link, source status.
- The claim, in one sentence.
- How strong the evidence is: sample size, real users or lab, replicated or not, effect size if given.
- How it applies to what the user is building.

### Ring 3 brief: look sideways

Most good ideas come from a field that solved the same shape of problem with different words. Pick 5 to 8 fields where the problem has a clear counterpart. Consider, among others:

- **Quantitative research**: finding a weak signal in noisy data, backtesting, guarding against overfitting.
- **Biometrics and behavioural signals**: typing rhythm, mouse movement, heart rate, eye or posture tracking.
- **Signals a browser can see**: tab focus and visibility, idle detection, scroll and input timing, device motion, battery, network, with the user's permission.
- **Local and offline assistants**: on-device models, local speech recognition, privacy-first designs.
- **Open-source "Jarvis" style assistants**: how they handle wake words, memory, tools and routines.
- **Any other field** where the same problem appears: medicine, games, logistics, sports science, manufacturing, ecology.

For each idea return: the field, the idea there, the idea here (the bridge), the evidence it works there with its source, and a proposed rating:

| Rating | Meaning |
|---|---|
| **High** | Works in its home field with solid evidence, and the bridge is direct |
| **Medium** | Works there, but the bridge needs a real assumption to hold |
| **Low** | Weak evidence, or the bridge is a stretch |
| **Hype** | Mostly marketing, demos or anecdotes |

Mark an idea Hype or Low when the only evidence is demo videos or vendor claims, nobody has repeated the result, the data is tiny or self-selected, many signals were tested and only the best one reported, or it only holds in a lab. Flag anything that collects biometric or behavioural data: it needs the user's clear consent and may fall under privacy law (GDPR treats biometric data as a special category).

## Step 3. Check the team's work (lead)

Researchers can be wrong too. Before ranking:

- **Open the sources behind every idea you might put in the top 5** and confirm they say what the researcher claimed. Fix or drop anything that doesn't hold up.
- Set the final ratings yourself. An idea that rests only on `unverified` sources is rated Medium at most.
- Merge duplicates across rings, and note where rings agree (a project from ring 1 that implements a finding from ring 2 is a strong sign).

## Step 4. Rank what to try (lead)

Combine the rings into a ranked list of 5 to 10 things to try. Rank by signal, then by how cheap it is to test. For each:

- What to try, in one sentence.
- Why: the sources behind it.
- **A first test that takes under a day of work to set up**, with a clear pass or fail result. If the result needs longer to collect (a week of normal use), say how long, and add a smaller check that gives a result the same day.
- Rough cost: time, money, data needed.

If the top idea can be tested cheaply here (a small script, a public dataset, an API call), run it and include the real result. Mark every result as `run` or `not run`.

## Step 5. Write the report (lead)

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
Things that looked promising and why they were dropped, including anything the lead's check overturned.
## Sources
Every link, marked `opened`, `abstract only` or `unverified`.
```

## Step 6. Check before saving

- Every source in the report was opened or resolved, or is marked `unverified`.
- No personal info about the user or anyone else.
- Writing rules: no em or en dashes, no emoji, no exclamation marks, no filler (genuinely, actually, really, simply, just, basically), no inflated words (delve, robust, leverage, seamless, comprehensive, crucial, cutting-edge, game-changer, landscape, journey), no stock phrases ("it's worth noting", "in conclusion", "in today's world"). Plain sentences and real numbers.

Run this from the project root. Quoted paper titles and code are exempt.

```
grep -nEi '—|–|!( |$)|\b(genuinely|actually|really|truly|simply|just|basically|delv\w*|robust|leverag\w*|seamless|comprehensive|crucial|pivotal|utiliz\w*|cutting.edge|game.changer|landscape|journey|furthermore|moreover)\b|worth noting|in conclusion|in today.s' research/*.md research/**/*.* 2>/dev/null
```

## Step 7. Tell the user

In chat, give the top 3 things to try with their first tests, say how many sources were checked and how many the lead's check changed, and link the report. Do not commit unless the user asks.
