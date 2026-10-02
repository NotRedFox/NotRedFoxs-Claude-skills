# Puppeteer waitForNetworkIdle / networkidle lifecycle
Link: https://github.com/puppeteer/puppeteer (packages/puppeteer-core/src/api/Page.ts, cdp/LifecycleWatcher.ts)
Date read: 2026-10-01 (shallow clone, HEAD dated 2026-10-01)
Status: opened
Licence: Apache-2.0. Last activity: 2026-10-01.

## What it does
Automation library. `Page.waitForNetworkIdle({idleTime, concurrency, timeout})` resolves when in-flight requests stay at or below `concurrency` for `idleTime` ms.

## Excerpts that matter
- `NETWORK_IDLE_TIME = 500` (src/common/util.ts line 312). Defaults: `concurrency = 0`.
- Core logic (Page.ts): `#inflight$` stream -> `inflight > concurrency` (boolean) -> `distinctUntilChanged` -> `switchMap` to `timer(idleTime)` when not over, `EMPTY` when over. The timer restarts only when the count crosses the concurrency threshold, not on every count change.
- LifecycleWatcher.ts maps `networkidle0` to `networkIdle` and `networkidle2` to `networkAlmostIdle` (at most 2 in flight).

## Borrow
The debounce-on-in-flight-count design: count requests, start a 500 ms timer when in-flight count drops to the concurrency limit, cancel it when it goes above. A content script cannot see all requests via CDP, but can approximate with a `PerformanceObserver` for `resource` entries plus patched `fetch`/XHR, or ask the service worker via `webRequest` events (MV3 allows observing, not blocking).

## Avoid / limits
Uses CDP; not available in a content script. Networkidle misses long-poll, websockets, analytics beacons, and finishes before client-side rendering completes. Playwright docs discourage `networkidle` for the same reasons (not opened here).

Verified: corrected (500 ms at util.ts line 312, concurrency 0, networkidle0/2 mapping confirmed; fixed the pipeline description: timer restarts only when in-flight crosses the concurrency threshold, not on any change; removed unconfirmed "~2055" line number)
