# Research workspace

This folder is only for research. Keep it separate from code projects.

## Layout
- `sources/<topic>/`: one Markdown file per source saved by an agent: link, date read, status (`opened`, `abstract only` or `unverified`), and the excerpts that matter. The verifier adds a `Verified:` line to each. A `BRIEF.md` here is fine.
- `checks/`: every script used to verify something. Save it here first, then run it from here.
- `reports/<topic>.md`: the final write-up.
- `logs/actions.log`: written automatically by a hook, one line per action. Don't edit it.
- `logs/notes.log`: yours. One line per step: what you did and what you found.

## How to research
1. Write a short brief: what the user is building, constraints, search terms.
2. Start `code-scout`, `paper-scout` and `sideways-scout` in parallel with the brief.
3. Start `verifier` on their output in `sources/`.
4. Write `reports/<topic>.md` from what the verifier confirmed: what was found, why it matters, ranked things to try with a first test each, and what was dropped.

## Rules
Hooks enforce the first three. You'll be stopped if you skip them.
- Any code that checks something is saved in `checks/` before it runs. Inline `python -c`, `node -e` and heredocs are blocked.
- Every source file has a link and a `Verified:` line before you finish.
- A report in `reports/` is written or updated after the last source changed.
- Never cite from memory. Cite only sources marked `Verified: yes` or `Verified: corrected`.
- Plain writing: no em dashes, no filler, real numbers.
