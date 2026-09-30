# NotRedFox's Claude Skills

Skills for Claude (Claude Code and the Claude app).

## Why these exist

These are Claude skills I made because I wanted them and couldn't find ones that did what I was after. Each one started as "I wish Claude would just do this properly", got researched, then got tested on real code before going up here. They're built for how I use Claude, and you're welcome to use them, fork them or pull ideas out of them.

## Skills

| Skill | What it does |
|---|---|
| [tournament-forge](tournament-forge/) | Makes genuinely different solutions fight 1v1 in a bracket, settles code matches with spec-first tests, then merges the winner with the losers' best ideas. About 22 subagent calls for a standard run. [Real run included](tournament-forge/examples/rate-limiter-run/RUN.md). |
| [shadow-and-teach](shadow-and-teach/) | Turns Claude into a pair-programming teacher for beginners. Maps any repo into areas you can click into and drill down through, replays what the agent did on a prompt, commit or PR as a step-by-step lesson, and explains each action as it works. Built on learning-science research. [Examples included](shadow-and-teach/examples/), including a map of Flask's own source code. |

## Install

Copy a skill folder into `~/.claude/skills/` for Claude Code, or zip the folder and upload it in the Claude app under Settings > Capabilities > Skills.

## License

MIT
