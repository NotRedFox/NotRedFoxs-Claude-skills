# Version Bump

Version 1.0.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude Code skill and hook that keep a four-part version for your project, MAJOR.MINOR.PATCH.TWEAK. Raising one number sets every number to its right back to 0:

| Level | 1.4.2.7 becomes | When |
|---|---|---|
| major | 2.0.0.0 | It breaks how people use it: a removed or renamed command, option, file or setting, or saved data that needs migrating |
| minor | 1.5.0.0 | Something new people can use, with nothing old broken |
| patch | 1.4.3.0 | A fix for something that worked wrongly |
| tweak | 1.4.2.8 | No change in behaviour: docs, comments, typos, formatting, tests only, refactors that behave the same |

## How it works

- **The skill decides.** Claude reads what the commit changes and picks the level by what people using the project would notice, not by how much code changed. It tells you which level it picked and why.
- **A script does the maths.** `bump.py` raises the right number, resets the ones after it, and adds a dated entry to `CHANGELOG.md`, so the numbers are never miscounted.
- **A hook makes sure it happens.** After setup, Claude Code blocks any `git commit` Claude makes that doesn't raise the version, and tells Claude how to pick the level. It also catches a raised version that wasn't added to the commit, and a version that went down.

The hook only acts in projects with a `VERSION` file, so it leaves your other projects alone. It only covers commits Claude makes through Claude Code. Your own commits in a terminal aren't checked.

## Tested

| | Result |
|---|---|
| Picking the level | 8 of 8 right in real Claude Code sessions: a README typo and a new test (tweak), two bug fixes (patch), a new command and a new optional option (minor), a renamed command and a removed command (major). Claude wasn't told about versions in any of them; the hook stopped each commit and Claude picked the level. |
| The hook | 24 of 24 situations handled right, including `git add -A && git commit`, `git commit -am`, bumping and committing in one command or on separate lines, a raised version that wasn't added, a version that went down, and projects with no `VERSION` file |
| The script | All four levels, old three-part versions (1.2.3 is read as 1.2.3.0), and broken or missing `VERSION` files |
| Setup | Keeps existing settings and hooks, doesn't add the hook twice, and stops with a message if `.claude/settings.json` is broken |

## Install

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/version-bump.zip -o /tmp/version-bump.zip && unzip -oq /tmp/version-bump.zip -d ~/.claude/skills && rm /tmp/version-bump.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

There's no Claude app version, because it edits files and installs a hook, which the Claude app can't do.

## Use

In your project:

```
/version-bump setup
```

This installs the hook and creates `VERSION`, starting from your latest git tag, `package.json` or `pyproject.toml` if you have one, or 0.1.0.0. Claude Code asks once before writing to `.claude/`. The hook works from your next session.

After that, just ask Claude to commit as usual. You can also bump by hand:

```
/version-bump              picks the level from your changes
/version-bump minor        uses the level you give
```

To commit without a bump, put `[no bump]` in the commit message. Claude is told never to do this itself.

## Good to know

- **Numbers don't roll over.** 1.4.2.9 plus a tweak is 1.4.2.10, the same as other version numbers.
- **npm and Cargo only accept three numbers.** The skill doesn't touch `package.json` or `Cargo.toml` unless you ask. If you do, it writes the first three numbers there.
