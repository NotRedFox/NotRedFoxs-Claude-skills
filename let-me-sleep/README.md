# Let Me Sleep

Version 1.0.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude Code skill for starting a long task and walking away. Before it does anything, it tells you:

- **How long it will take**, as one number and a finish time.
- **Every permission prompt it will need, and when**, with anything that deletes, pushes or costs money called out in capitals.

Then it turns that list into temporary allow rules for this task only. You approve them once, and it works without stopping to ask. When it's done, it tells you what it did, the real time against the estimate, anything left waiting for you, and removes the temporary rules.

It only runs when you type `/let-me-sleep <task>`.

## How accurate is it?

Tested with real Claude Code sessions on two tasks: fixing failing tests, deleting a build folder, updating a changelog and committing; and adding a CLI flag with tests, setting up a virtual environment, installing packages, deleting a folder, updating the README and committing. Each forecast was run in Manual mode, the rules it proposed were approved exactly as written, then the task ran in Manual mode, where anything it failed to forecast would have stopped and asked.

| | Result |
|---|---|
| Permission prompts during planning | 0 in the final version (the first version caused 3, now fixed) |
| Prompts the forecast missed | 0 in all 6 runs after the first fix. The only prompts were the two it says will always remain: writing the rules at the start, and removing them at the end. The very first version missed prompts for its own notes in `.claude/`, which is why they now live in `.let-me-sleep/`. |
| Time estimate, first run in a project | About 2 times too long (1 minute forecast against 27 seconds, 1.5 minutes against 40 seconds) |
| Time estimate, with history from earlier runs | 30 seconds forecast for the task that took 27 seconds |

It keeps a history of estimates and real times in `.let-me-sleep/history.md`, measured with the system clock, and scales later estimates by how far off earlier ones were. So it gets closer the more you use it in a project.

## Good to know

- **Two prompts always remain.** Claude Code always asks before writing anything in `.claude/`, even with an allow rule. So writing the temporary rules at the start asks once, while you're there. Removing them at the end asks once more, after all the work is done, so you can answer it whenever you're back.
- **It never runs anything that wasn't approved.** If it finds it needs something new, it puts it on a "Waiting for you" list and carries on with everything else.
- **It assumes Manual mode** unless your project settings say otherwise. If you have personal allow rules or use accept-edits mode, you'll see fewer prompts than forecast, never more.

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [let-me-sleep-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/let-me-sleep-claude-app.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

The Claude app doesn't use permission prompts the same way, so this skill is mainly for Claude Code.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/let-me-sleep.zip -o /tmp/let-me-sleep.zip && unzip -oq /tmp/let-me-sleep.zip -d ~/.claude/skills && rm /tmp/let-me-sleep.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

## Use

```
/let-me-sleep fix the failing tests, update the changelog and commit
```

Add `.let-me-sleep/` to your `.gitignore` if you don't want its notes committed.
