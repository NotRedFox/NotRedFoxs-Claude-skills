---
name: version-bump
description: "Keeps a four-part version (MAJOR.MINOR.PATCH.TWEAK, like 1.4.2.7) for a project. Reads what changed, picks which number to raise and says why, updates VERSION and CHANGELOG.md, and can install a hook that blocks any commit that doesn't raise the version. Use when the user asks to bump, raise or set up a version."
argument-hint: "[setup | major | minor | patch | tweak] [what changed]"
license: MIT
compatibility: "Claude Code with git and python3. Setup writes to .claude/hooks/ and .claude/settings.json."
metadata:
  version: "1.0.0"
  author: NotRedFox
---

# Version Bump

The version has four numbers: MAJOR.MINOR.PATCH.TWEAK. Raising one sets every number to its right back to 0.

| Level | 1.4.2.7 becomes | When |
|---|---|---|
| major | 2.0.0.0 | It breaks how people use it: a removed or renamed command, option, file or setting, or saved data that needs migrating |
| minor | 1.5.0.0 | Something new people can use, with nothing old broken |
| patch | 1.4.3.0 | A fix for something that worked wrongly |
| tweak | 1.4.2.8 | No change in behaviour: docs, comments, typos, formatting, tests only, refactors that behave the same |

Arguments: $ARGUMENTS

- `setup`: go to Setup.
- `major`, `minor`, `patch` or `tweak`: use that level, then go to Bump. If the changes clearly don't fit it, say so once before bumping.
- Nothing, or only a description: go to Pick the level.

## Setup

1. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/setup.py" "${CLAUDE_PROJECT_DIR}"`. It copies `bump.py` and `require_bump.py` into `.claude/hooks/` and adds the hook to `.claude/settings.json`, keeping what's there. Claude Code asks before writing to `.claude/`, so tell the user to expect that.
2. If there's no `VERSION` file, find the current version, in this order: the latest git tag (`git describe --tags --abbrev=0`), then `package.json`, `pyproject.toml`, `Cargo.toml` or a version in the README. Pad it to four numbers (1.2.3 becomes 1.2.3.0). If there's none, use 0.1.0.0. Run `python3 .claude/hooks/bump.py init <version>` and tell the user what you picked and where it came from.
3. Tell the user:
   - From now on, a commit made through Claude Code is blocked until VERSION is raised.
   - The hook loads when Claude Code starts, so it works from the next session.
   - To commit without a bump, they can put `[no bump]` in the commit message.

## Pick the level

1. See what will go in the commit: `git status --short`, `git diff HEAD --stat`, then `git diff HEAD` on the files that matter. If the work is already committed, compare against the last version change: `git log -1 --format=%h -- VERSION` gives the commit, then `git diff <that commit> HEAD`.
2. For each change, ask: does it break how someone uses this? Add something they can use? Fix something that was wrong? Or none of those?
3. The highest level wins. One bump per commit, never two.
4. Judge by what people using the project notice, not by how much code changed. A one-line rename of a command is major. A 500-line refactor that behaves the same is a tweak.

Cases that are easy to get wrong:

- Removing a feature, or dropping support for something (an old Python version, a browser): major.
- Changing a default people rely on: major if the old behaviour is gone, minor if they can still choose it.
- Deprecating something that still works: minor.
- A new optional flag or setting: minor.
- Making something faster with the same results: patch.
- A security fix: patch, or major if the fix has to break something.
- Updating a dependency: tweak if nothing changes for users, patch if it fixes a bug they hit, major if it drops support for something.
- Fixing docs that described the behaviour wrongly: tweak.

## Bump

Run `python3 .claude/hooks/bump.py <level> "<one line on what changed, for people using it>"`. If setup hasn't been run, use `python3 "${CLAUDE_SKILL_DIR}/scripts/bump.py"` instead. Never edit `VERSION` by hand: the script does the arithmetic and writes the CHANGELOG entry.

Then `git add VERSION CHANGELOG.md`. Commit only if the user asked for a commit, with their changes in the same commit.

Tell the user in one or two lines: old version, new version, the level, and why.

## Other version numbers

If the project also has a version in `package.json`, `pyproject.toml`, `Cargo.toml` or similar, leave it alone unless the user asks. npm and Cargo only accept three numbers, so if the user wants them in step, write the first three numbers there.

## Rules

- Never put `[no bump]` in a commit message yourself. It's for the user.
- Never lower a version or skip a number.
- If you can't tell what a change does for users, ask before bumping. When you can't ask, pick the higher level and say why.
