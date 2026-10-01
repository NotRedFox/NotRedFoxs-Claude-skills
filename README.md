# NotRedFox's Claude Skills

Skills for Claude (Claude Code and the Claude app).

## Why these exist

These are Claude skills I made because I wanted them and couldn't find ones that did what I was after. Each one started as "I wish Claude would just do this properly", got researched, then got tested on real code before going up here. They're built for how I use Claude, and you're welcome to use them, fork them or pull ideas out of them.

## Skills

| Skill | Version | What it does |
|---|---|---|
| [tournament-forge](tournament-forge/) | 1.0.2 | Makes solutions that work in different ways fight 1v1 in a bracket, settles code matches with spec-first tests, then merges the winner with the losers' best ideas. About 22 subagent calls for a standard run. [Real run included](tournament-forge/examples/rate-limiter-run/RUN.md). |
| [shadow-and-teach](shadow-and-teach/) | 1.0.2 | Turns Claude into a pair-programming teacher for beginners. Maps any repo into areas you can click into and drill down through, replays what the agent did on a prompt, commit or PR as a step-by-step lesson, and explains each action as it works. Built on learning-science research. [Live examples](shadow-and-teach/README.md#examples), including [a map of Flask's own source code](https://notredfox.github.io/NotRedFoxs-Claude-skills/shadow-and-teach/examples/flask-internals-map.html). |
| [kick-start](kick-start/) | 1.1.0 | Keeps your project's memory in files as you work: a log of every approach and whether it worked, a bug log Claude rereads so it doesn't repeat mistakes, and an always-current Architecture section in your README. Adds tests that check what you asked for, writes professional comments and removes personal info. [Example included](kick-start/examples/slugify/). |

## Install

Pick a skill, then follow the steps for where you use Claude.

| Skill | Download |
|---|---|
| tournament-forge | [tournament-forge.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/tournament-forge.zip) |
| shadow-and-teach | [shadow-and-teach.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach.zip) |
| kick-start | [kick-start.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip) |

### Claude app (claude.ai, desktop or phone)

1. Download the zip from the table above. Don't unzip it.
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

On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update a skill later, do the same steps again.

## Versions

Each skill has a version in its `SKILL.md` and a `CHANGELOG.md`. Versions follow MAJOR.MINOR.PATCH: PATCH for fixes, MINOR for new features, MAJOR for changes that break how the skill is used.

## License

MIT
