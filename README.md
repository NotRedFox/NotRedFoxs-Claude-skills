# NotRedFox's Claude Skills

Skills for Claude (Claude Code and the Claude app).

| Skill | What it does |
|---|---|
| [tournament-forge](tournament-forge/) | Makes genuinely different solutions fight 1v1 in a bracket, settles code matches with spec-first tests, then merges the winner with the losers' best ideas. About 22 subagent calls for a standard run. [Real run included](tournament-forge/examples/rate-limiter-run/RUN.md). |
| [shadow-and-teach](shadow-and-teach/) | Turns Claude into a pair-programming teacher. Maps any repo into areas you can click into and drill down through, replays what the agent did on a prompt, commit or PR as a step-by-step lesson, and explains each action as it works. Built on learning-science research. [Examples included](shadow-and-teach/examples/), including a map of Flask's own source code. |

## Install

Copy a skill folder into `~/.claude/skills/` for Claude Code, or zip the folder and upload it in the Claude app under Settings > Capabilities > Skills.

## License

MIT
