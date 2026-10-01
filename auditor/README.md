# Auditor

Version 1.0.2. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that audits your project one part at a time, then audits the whole thing together. It checks that each part works under real use, and that the tests would catch it if it didn't.

**Branch audit** ("audit the search part"):

1. **Time estimate first.** It tells you how long it will take, for example "about 20 minutes".
2. **Every question up front.** Access to a site, a folder, installs, running a server, long load tests: it asks them all in its first message, so you can leave while it works.
3. **Maps the branch:** entry points, what it depends on, how data moves, where state lives.
4. **Tests the tests.** It runs them 3 times to find flaky ones, breaks the code on purpose in a copy to see if they notice, and measures coverage. If tests are missing, it writes them from what the code is meant to do.
5. **Audits the branch:**
   - Simulated users: normal, confused, careless and hostile, then many at once.
   - A load ramp to find where it breaks.
   - A long run sampling memory, to catch leaks.
   - Open files, sockets and threads that pile up.
   - Security basics and performance.
6. **Writes a report** in `audit/` with every finding, its severity and the real evidence.

**Final audit** ("final audit"): reads every branch report, re-checks each earlier finding, and runs real user journeys, load and long runs across the whole system. It looks for problems that only show when the parts run together, and checks that each fix has a test and holds up under load.

It reports and adds tests. It doesn't change your code unless you say yes to a specific fix. It never load-tests a live site or someone else's system unless you name it and confirm.

## Example

[examples/notesapp](examples/notesapp/ANSWER-KEY.md) is a small notes web app written to test the auditor, with 7 planted problems.

- Two branch audits, run at the same time, found all 7, plus real problems that weren't planted, such as login tokens that never expire.
- Their tests caught every deliberate code break the auditors tried (16 of 16 on the login code), where the original tests caught 1 of 16.
- After 4 of the problems were fixed, including one fix that was deliberately flawed, the final audit confirmed the 3 good fixes and found that the flawed one crashes under concurrent use and had no test. It also found a new race that only shows when notes and search run together.

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [auditor-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/auditor-claude-app.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

The Claude app can't run servers or load tests, so audits there are limited to reading code. Claude Code is the better fit.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/auditor.zip -o /tmp/auditor.zip && unzip -oq /tmp/auditor.zip -d ~/.claude/skills && rm /tmp/auditor.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

The two downloads hold the same skill. The Claude Code one also has Claude Code settings (an argument hint, and a setting so it only runs when you ask), which the Claude app doesn't accept.
It only runs when you type `/auditor`, so Claude never starts it on its own.

## Use

- "Audit the auth part"
- "Audit src/search"
- "Final audit"

Works well with [kick-start](../kick-start/): the auditor starts from kick-start's Architecture section if your README has one.

## Limits

- Time estimates are rough on the first audit. Once a project has earlier reports, it estimates from their real times.
- Load and long tests run on your machine, so numbers depend on it. They show where things break, not production capacity.
- It can only test what it can run. If a part needs a service you don't give it access to, it uses the fallback it told you about and lists what it couldn't check.

## Similar projects

- [audit-tests](https://gist.github.com/jeremylongshore/1380a7abde36037b90603a05bea6a80b): finds and runs tests, measures their quality and does mutation testing.
- [claude-audit](https://github.com/itsmesherry/claude-audit): a one-command codebase audit across performance, testing and more.

The auditor works one branch at a time, asks for everything up front, simulates real users, and finishes with a final audit that re-checks every fix across the whole system.
