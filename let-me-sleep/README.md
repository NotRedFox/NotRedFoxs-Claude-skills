# Let Me Sleep

Version 1.0.1. See [CHANGELOG.md](CHANGELOG.md).

A Claude Code skill for starting a long task and walking away. Before it does anything, it tells you:

- **How long it will take**, as one number and a finish time.
- **Every permission prompt it will need, and when**, with anything that deletes, pushes or costs money called out in capitals.

Then it turns that list into temporary allow rules for this task only. You approve them once, and it works without stopping to ask. When it's done, it tells you what it did, the real time against the estimate, anything left waiting for you, and removes the temporary rules.

It only runs when you type `/let-me-sleep <task>`.

## How accurate is it?

Tested with real Claude Code sessions on three projects: a Python calculator (fix failing tests, delete a build folder, update the changelog, commit), a Python CLI (add a flag with tests, set up a virtual environment, install packages, delete a folder, update the README, commit) and a Node.js converter (fix a test, add a function with a test, delete a logs folder, bump the version, commit). Each forecast was run in Manual mode, the rules it proposed were approved exactly as written, then the task ran in Manual mode, where anything it failed to forecast would have stopped and asked.

| | Result |
|---|---|
| Permission prompts during planning | 0 in all 20 runs since the first fix (the first version caused 3) |
| Prompts the forecast missed | 0 in all 20 runs. The only prompt during the work was the one it always warns about: removing the temporary rules at the end. |
| Tasks done correctly | All of them: tests pass, folders deleted, commits made |
| Time estimate, first run in a project | About 1.5 times too long (35 seconds forecast against 22 and 24 seconds real) |
| Time estimate, second run, using history | 25 seconds forecast against 22 real, and 23 against 25 |

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
