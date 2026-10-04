# NotRedFox's Claude Skills

Skills for Claude (Claude Code and the Claude app). Every skill was tested on real tasks, and each one's example is real output from those runs. [See them all on the website](https://notredfox.github.io/NotRedFoxs-Claude-skills/).

## Why these exist

These are Claude skills I made because I wanted them and couldn't find ones that did what I was after. Each one started as "I wish Claude would just do this properly", got researched, then got tested on real code before going up here. They're built for how I use Claude, and you're welcome to use them, fork them or pull ideas out of them.

## Skills

| Skill | Version | What it does |
|---|---|---|
| [tournament-forge](tournament-forge/) | 1.0.4 | Makes solutions that work in different ways fight 1v1 in a bracket, settles code matches with spec-first tests, then merges the winner with the losers' best ideas. About 10 subagent calls on the default quick tier. [Real run included](tournament-forge/examples/rate-limiter-run/RUN.md). |
| [shadow-and-teach](shadow-and-teach/) | 1.0.4 | Turns Claude into a pair-programming teacher for beginners. Maps any repo into areas you can click into and drill down through, replays what the agent did on a prompt, commit or PR as a step-by-step lesson, and explains each action as it works. Built on learning-science research. [Live examples](shadow-and-teach/README.md#examples), including [a map of Flask's own source code](https://notredfox.github.io/NotRedFoxs-Claude-skills/shadow-and-teach/examples/flask-internals-map.html). |
| [kick-start](kick-start/) | 1.1.2 | Keeps your project's memory in files as you work: a log of every approach and whether it worked, a bug log Claude rereads so it doesn't repeat mistakes, and an always-current Architecture section in your README. Adds tests that check what you asked for, writes professional comments and removes personal info. [Example included](kick-start/examples/invoice/). |
| [research-solving](research-solving/) | 1.1.0 | Researches what you're building with three researchers working in parallel: open-source code to borrow from, papers from your field, and ideas from far-off fields like quant research, biometrics and browser signals. Rates each idea for real signal versus hype and ends with cheap first tests. [Example included](research-solving/examples/procrastination-extension-team/research/2026-10-01-procrastination-nudge-extension.md). |
| [problem-solve](problem-solve/) | 1.0.1 | For problems with no obvious route, like no API. Climbs from obvious to more creative approaches, tests each one for real instead of stopping at "impossible", uses odd resources you suggest, and writes a ChatGPT prompt with everything tried so far. [Example included](problem-solve/examples/washing-machine/problem-solve/2026-10-01-washing-machine-done.md). |
| [claim-check](claim-check/) | 1.0.3 | Checks whether your README and docs are true. Lists every claim (numbers, commands, behaviour, links, comparisons), checks each by running or reading the code, and fixes the docs where they're wrong. It found 11 false or partly true claims in this repo's own READMEs. [Examples included](claim-check/). |
| [auditor](auditor/) | 1.0.3 | Audits one part of your project at a time, then the whole thing together. Gives a time estimate and asks every question up front, tests your tests, simulates real users, load and long runs, and looks for memory leaks. Found all 7 planted problems in a test app. [Example included](auditor/examples/notesapp/ANSWER-KEY.md). |
| [let-me-sleep](let-me-sleep/) | 1.0.0 | For long tasks you want to walk away from. Before starting, it tells you how long the task will take and every permission prompt it will need, gets them approved at once, then works without stopping to ask. Missed 0 prompts in 6 test runs. [Test results](let-me-sleep/README.md#how-accurate-is-it). |

## How they fit together

| When | Use |
|---|---|
| Before you build | `/research-solving` to see what already exists |
| While you build | kick-start, to keep the log, the bug list and the architecture up to date |
| When you're stuck | problem-solve for blocked routes, `/tournament-forge` when several approaches are worth comparing |
| Before you ship | `/auditor` on each part and then a final audit, `/claim-check` on the docs |
| Learning a codebase | shadow-and-teach |
| Leaving it to run | `/let-me-sleep` with the task |

These are general methods that work on any project, so they're longer than a skill written for one job. If you do the same task again and again in one project (adding an API route, deploying, writing a migration), a small skill written for that task will use far fewer tokens. Use both: these for the methods, small ones for your repeated jobs.

## Also in this repo

[token-meter](mods/token-meter/): a Claude Code mod that shows tokens per second, per minute and per hour live in the status line. Install it with:

```
claude plugin marketplace add NotRedFox/NotRedFoxs-Claude-skills
claude plugin install token-meter@notredfox
```

Mods need Claude Code v2.1.287 or later. [More about it](mods/token-meter/).

[research-workspace](research-workspace/): a ready-made Claude Code project folder for research, with four specialised agents and hooks that log every step, keep every check script, and won't let Claude finish without a written report. An alternative to research-solving if you'd rather keep research in its own folder.

## Install

Pick a skill, then follow the steps for where you use Claude.

| Skill | Claude app | Claude Code |
|---|---|---|
| tournament-forge | [tournament-forge-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge-claude-app.zip) | [tournament-forge.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge.zip) |
| shadow-and-teach | [shadow-and-teach-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach-claude-app.zip) | [shadow-and-teach.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach.zip) |
| kick-start | [kick-start-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start-claude-app.zip) | [kick-start.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip) |
| research-solving | [research-solving-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-solving-claude-app.zip) | [research-solving.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-solving.zip) |
| problem-solve | [problem-solve-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/problem-solve-claude-app.zip) | [problem-solve.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/problem-solve.zip) |
| claim-check | [claim-check-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/claim-check-claude-app.zip) | [claim-check.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/claim-check.zip) |
| auditor | [auditor-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/auditor-claude-app.zip) | [auditor.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/auditor.zip) |
| let-me-sleep | [let-me-sleep-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/let-me-sleep-claude-app.zip) | [let-me-sleep.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/let-me-sleep.zip) |

### Claude app (claude.ai, desktop or phone)

1. Download the Claude app zip from the table above. Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste one of these into your terminal (Mac or Linux), then restart Claude Code.

tournament-forge:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge.zip -o /tmp/tournament-forge.zip && unzip -oq /tmp/tournament-forge.zip -d ~/.claude/skills && rm /tmp/tournament-forge.zip
```

shadow-and-teach:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach.zip -o /tmp/shadow-and-teach.zip && unzip -oq /tmp/shadow-and-teach.zip -d ~/.claude/skills && rm /tmp/shadow-and-teach.zip
```

kick-start:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip -o /tmp/kick-start.zip && unzip -oq /tmp/kick-start.zip -d ~/.claude/skills && rm /tmp/kick-start.zip
```

research-solving:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-solving.zip -o /tmp/research-solving.zip && unzip -oq /tmp/research-solving.zip -d ~/.claude/skills && rm /tmp/research-solving.zip
```

problem-solve:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/problem-solve.zip -o /tmp/problem-solve.zip && unzip -oq /tmp/problem-solve.zip -d ~/.claude/skills && rm /tmp/problem-solve.zip
```

claim-check:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/claim-check.zip -o /tmp/claim-check.zip && unzip -oq /tmp/claim-check.zip -d ~/.claude/skills && rm /tmp/claim-check.zip
```

auditor:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/auditor.zip -o /tmp/auditor.zip && unzip -oq /tmp/auditor.zip -d ~/.claude/skills && rm /tmp/auditor.zip
```

let-me-sleep:

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/let-me-sleep.zip -o /tmp/let-me-sleep.zip && unzip -oq /tmp/let-me-sleep.zip -d ~/.claude/skills && rm /tmp/let-me-sleep.zip
```

On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update a skill later, do the same steps again.

## Settings

The Claude Code zips use Claude Code's extra settings. tournament-forge, research-solving, claim-check, auditor and let-me-sleep only run when you type their slash command, because they use a lot of calls or change files. The others can start on their own when your request matches. The Claude app only accepts six settings fields, so its zips leave the extra ones out. Both are built from the same `SKILL.md`.

## Versions

Each skill has a version in its `SKILL.md` and a `CHANGELOG.md`. Versions follow MAJOR.MINOR.PATCH: PATCH for fixes, MINOR for new features, MAJOR for changes that break how the skill is used.

## License

MIT
