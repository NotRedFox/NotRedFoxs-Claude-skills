# Research Solving

Version 1.1.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill for when you're building something and want to know what's already out there. It researches in three rings and ends with a short list of things to try, each with a cheap first test.

| Ring | What it looks for |
|---|---|
| 1. Existing code | Open-source projects that solve the same or a close problem, what to borrow from each, and whether the licence allows it |
| 2. Research | Papers, benchmarks and datasets from your field, with how strong the evidence is |
| 3. Other fields | Ideas from places that solved the same kind of problem with different words: quant research, biometrics, signals a browser can see, local assistants, open-source "Jarvis" style assistants and more |

Every idea from another field is rated **High**, **Medium**, **Low** or **Hype**, with the reason. It marks ideas down when the only evidence is demos, vendor claims, tiny data or results nobody has repeated.

It never cites a paper from memory. Models make up citations (one study found 18% of GPT-4's and 55% of GPT-3.5's were fabricated), so every source in the report is one it opened, or is marked `unverified`.

## How it works

Three researchers run at the same time, one per ring, each in its own subagent so their searching doesn't fill up your conversation. Then the lead (your main Claude) opens the sources behind the top ideas, fixes anything that doesn't hold up, sets the final ratings and writes the report. Without subagents it runs the rings one after another.

## Example

[examples/procrastination-extension-team](examples/procrastination-extension-team/research/2026-10-01-procrastination-nudge-extension.md) is a real run of the agent team on: "I want to build a browser extension that notices when I'm procrastinating and nudges me back to work. Runs locally, no cloud."

- The three researchers returned 7 open-source projects (all cloned and read), 9 papers and 9 ideas from other fields.
- The lead's check changed two things. A researcher said people take about 8.5 minutes to get back to work after an email alert; the paper's figure is 16 minutes 33 seconds (8 minutes 48 seconds was the reply time for chat alerts). And one idea was cut from High to Medium because its paper couldn't be opened.
- It ranks 8 things to try, from a local activity logger (High) down to typing-rhythm signals (Low, and only with consent).
- It ran where most paper websites were blocked, so 8 sources are marked `unverified`. On a normal connection the researchers open and check each one.

For comparison, [examples/procrastination-extension](examples/procrastination-extension/research/2026-10-01-procrastination-nudge-extension.md) is the same request run by version 1.0, one agent working alone. It could open no papers; the team opened 5.

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [research-solving-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-solving-claude-app.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-solving.zip -o /tmp/research-solving.zip && unzip -oq /tmp/research-solving.zip -d ~/.claude/skills && rm /tmp/research-solving.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

The two downloads hold the same skill. The Claude Code one also has Claude Code settings (an argument hint, and a setting so it only runs when you ask), which the Claude app doesn't accept.
It only runs when you type `/research-solving`, so Claude never starts it on its own.

## Use

- "Research solving: I want to build <thing>"
- "What's out there for <problem>?"
- "Find ideas from other fields for <thing>"

The report goes in `research/<date>-<topic>.md` in your project.

## Limits

- It can only read what's reachable from where Claude runs. Paywalled papers are read from the abstract and marked that way.
- Ratings are a judgement from the evidence it found, not a guarantee. The first tests are there so you can check cheaply.
- Ideas that use biometric or behavioural data are flagged, because they need clear consent and may fall under privacy law.

## Similar projects

- [prior-art](https://github.com/kvadou/prior-art): surveys open-source projects, APIs and some related research before you build. Doesn't look at other fields.
- [GPT Researcher](https://github.com/assafelovic/gpt-researcher): writes cited research reports on any topic. Doesn't search code or rank things to try.
- [claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill): a multi-step research pipeline with source scoring, inside one field.
- [STORM](https://github.com/stanford-oval/storm) ([paper](https://arxiv.org/abs/2402.14207)): asks questions from several perspectives before writing. The idea behind ring 3.

## Research

- Walters and Wilder, [Fabrication and errors in the bibliographic citations generated by ChatGPT](https://www.nature.com/articles/s41598-023-41032-5) (Scientific Reports, 2023)
- Hope, Chan, Kittur and Shahaf, [Accelerating Innovation Through Analogy Mining](https://dl.acm.org/doi/10.1145/3097983.3098038) (KDD 2017): ideas from distant analogies
- Harvey, Liu and Zhu, [... and the Cross-Section of Expected Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314): why most published "signals" don't hold up after many tests
