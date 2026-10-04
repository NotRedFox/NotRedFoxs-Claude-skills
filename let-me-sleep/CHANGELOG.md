# Changelog

## 1.0.1

- Time estimates are closer: about 1.5 seconds per tool call instead of 2, every call counted, and no slack or rounding up. First-run estimates went from about 3 times too long to about 1.5 times.
- History now compares only the timed work, adds the wrap-up separately, and moves halfway toward the ratio until there are three runs. One earlier run used to pull an estimate down to 12 seconds for a task that took 27.

## 1.0.0

First release.
