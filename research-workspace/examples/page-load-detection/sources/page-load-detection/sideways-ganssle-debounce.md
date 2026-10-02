# Switch debouncing: N consecutive stable readings (embedded electronics)

- Link: https://www.ganssle.com/debouncing-pt2.htm
- Date read: 2026-10-01
- Status: unverified (page fetch blocked by egress proxy, 403; only the web search result summary was seen, not the page)
- Field: embedded electronics. Mechanical switch contacts bounce, then settle.

## Excerpts (from search summary, not the page itself)
- "Most people use a fairly simple approach that looks for n sequential stable readings of the switch." If the state is not stable, the counter resets.
- Ganssle's shift-register variant: shift the input into a variable each tick; only a fully-zero or fully-one value is trusted. Any bounce "spoils" the variable.
- Ganssle measured 18 switches: 16 averaged 1557 microseconds of bounce, max 6200 microseconds (as reported by the summary; the page was not opened to confirm).

## Bridge to page-load detection
Declare "loaded" only after the DOM-mutation/network signal has been quiet for N consecutive ticks, and reset the counter on any activity. Choose the quiet window from measured worst-case noise, not a guess.

Verified: could not open (ganssle.com refused by egress proxy, 403 CONNECT; the 18-switch / 1557 us / 6200 us figures are unconfirmed, do not cite)
