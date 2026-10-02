# Detecting when a page's main content has finished loading

Date: 2026-10-01. Scope: MV3 content script, SPAs and server-rendered pages, no per-site selectors.

## What was found (verified sources only)

1. **web-vitals (GoogleChrome/web-vitals, `src/onLCP.ts`, `src/lib/observe.ts`)**: Verified: corrected.
   - Uses a `PerformanceObserver` on LCP entries. There is no "done" event. LCP is finalized on the first `keydown`, `click` or `visibilitychange`, scheduled through `whenIdleOrHidden`.
   - Ignores the page if it was hidden before load (`firstHiddenTime`), and handles bfcache restores with `doubleRAF`.
   - Soft-navigation entry types are supported only when the browser supports them and `reportSoftNavs` is true.
2. **Puppeteer `waitForNetworkIdle`**: Verified: corrected.
   - Default idle time is 500 ms (`NETWORK_IDLE_TIME = 500`), default concurrency 0 (`networkidle0`; `networkidle2` allows 2 in flight).
   - The in-flight count is mapped to a boolean ("at or under the limit") with `distinctUntilChanged`, so the 500 ms timer restarts only when the count crosses the limit.
   - It relies on CDP, so it cannot run in a content script. The idea has to be rebuilt from `PerformanceObserver` resource entries and wrapped `fetch`/XHR.
3. **dom-testing-library `waitFor`**: Verified: yes.
   - Combines a `MutationObserver`, a 50 ms `setInterval` fallback, a hard timeout (`asyncUtilTimeout`) and a single cleanup path (`onDone`).
   - It has no quiet-period logic. It checks a condition, not "nothing changed for N ms".

## Why it matters

No single browser event means "main content done". `load` fires too early for SPAs, and LCP can keep updating until the user interacts. The verified sources point to a combination: LCP as the content signal, a quiet period on DOM and network as the settle signal, and a hard timeout as the fallback.

## Ranked things to try

1. **LCP plus finalize, with a timeout.** Observe `largest-contentful-paint` with `buffered: true`. Resolve on first input, on hide, or after the quiet window below. First test: log LCP time against the resolve time on 10 pages, and count how often the resolve comes before the final LCP candidate.
2. **DOM quiet window.** Use a `MutationObserver` on `document.documentElement` and resolve after N ms with no mutations, restarted on each one. Add the waitFor-style interval and hard timeout. First test: try N = 300, 500 and 1000 ms on a server-rendered page and a SPA, and record false early resolves and added delay.
3. **Network quiet window.** Count in-flight requests with wrapped `fetch`/XHR plus resource timing, and use the Puppeteer rule: restart a 500 ms timer only when the count crosses the limit (allow 2 in flight, as `networkidle2` does, to ignore long-polling). First test: a page with a polling endpoint, to confirm it still resolves.
4. **Soft navigations.** Enable soft-navigation reporting only if the browser supports it, otherwise reset the detector on `history` changes. First test: a client-routed site, check the detector re-arms after a route change.

Combine 1 to 3 as "LCP seen AND DOM quiet AND network quiet, or timeout". The quiet window length and timeout values are untested guesses from the borrowed defaults (500 ms, 50 ms), not measured numbers.

## What was dropped

All dropped because they could not be opened (egress proxy returned 403, or the fetch was refused), so none is cited:
- `lcp-mdn-glossary.md` (MDN LCP): Verified: could not open. Written from a search summary.
- `sideways-ganssle-debounce.md` (debounce, N stable readings): Verified: could not open. The idea matches the quiet window above but the figures are unconfirmed.
- `sideways-rhat-convergence.md` (R-hat, multiple signals agreeing): Verified: could not open.
- `sideways-settling-time-band.md` (settling band): Verified: could not open.

## Gaps

- Not covered by any opened source: Playwright `networkidle` caveats, the W3C LCP spec, and the soft-navigations proposal. The hosts (web.dev, w3c.github.io, github.com/WICG, playwright.dev, MDN, arxiv.org, ganssle.com) need to be allowed to close these.
- The paper scout returned one unopened source rather than three, so there is no academic evidence in this report.
