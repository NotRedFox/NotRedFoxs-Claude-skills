# Changelog

## 0.2.0

- Speed is timed from when the request is sent. Timing from the first piece of text showed 2.5k tok/s on replies where Claude thought for seconds and then sent everything at once.
- The live `~` estimate starts at 3 characters per token and learns the real ratio from finished replies. It now reads within about 15% of the exact speed, down from 30 to 40% low.
- No live estimate while thinking is hidden, since hidden thinking costs tokens but shows no text.

## 0.1.0

First release.
