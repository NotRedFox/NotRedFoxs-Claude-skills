# web-vitals (GoogleChrome)
Link: https://github.com/GoogleChrome/web-vitals
Date read: 2026-10-01 (shallow clone, HEAD dated 2026-10-01)
Status: opened
Licence: Apache-2.0. Last activity: 2026-10-01.

## What it does
Library for Core Web Vitals. `onLCP` (src/onLCP.ts) wraps a `PerformanceObserver` for `largest-contentful-paint` and reports a final value.

## Excerpts that matter
- LCP is finalized on the first trusted `keydown`, `click` or `visibilitychange` (capture listeners), run inside `whenIdleOrHidden`. The browser stops emitting entries on input, but the page cannot see that directly.
- Entries are ignored if `renderTime >= visibilityWatcher.firstHiddenTime` (page was hidden first).
- Soft navigations: `checkSoftNavsEnabled(opts)` adds `soft-navigation` and `interaction-contentful-paint` entry types (src/lib/softNavs.ts). It is opt-in and depends on a Chrome experiment.
- bfcache restore handled via `onBFCacheRestore` + `doubleRAF`.

## Borrow
`observe()` in src/lib/observe.ts, `whenIdleOrHidden.ts`, and the finalize-on-input pattern in `onLCP.ts`.

## Avoid / limits
LCP has no "done" event; it is a guess made at first input or hide. For a content script this means a page that is never touched never finalizes. Soft-nav support is experimental. Not a signal for "all content loaded".

Verified: corrected (onLCP finalize events, firstHiddenTime check, softNavs entry types, bfcache + doubleRAF confirmed; observe file is observe.ts not observe.js. Note checkSoftNavsEnabled also requires opts.reportSoftNavs true and browser support, not only a Chrome experiment)
