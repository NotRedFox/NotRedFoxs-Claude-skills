# dom-testing-library waitFor
Link: https://github.com/testing-library/dom-testing-library (src/wait-for.js)
Date read: 2026-10-01 (shallow clone, HEAD dated 2026-09-13)
Status: opened
Licence: MIT. Last activity: 2026-09-13.

## What it does
`waitFor(callback, options)` retries a callback until it stops throwing or a timeout hits. Small and readable (about 200 lines).

## Excerpts that matter
- Defaults: `interval = 50`, `timeout = getConfig().asyncUtilTimeout`.
- `mutationObserverOptions = {subtree: true, childList: true, attributes: true, characterData: true}`.
- Real timers path: `setInterval(check, interval)` plus `MutationObserver(check)` on the container; `onDone` clears the interval and calls `observer.disconnect()`.
- Overall `setTimeout(handleTimeout, timeout)` rejects with the last error.

## Borrow
Pattern: observer + interval fallback + hard timeout + cleanup in one `onDone`. Replace the callback with a stability check (no mutations for N ms) to get DOM-quiet detection.

## Avoid / limits
It waits for a caller-supplied condition, not for "main content". No built-in quiet-period logic; observing attributes and characterData on the whole document is heavy on busy pages. Large Jest fake-timer branch is irrelevant to an extension.

Verified: yes (re-read src/wait-for.js on 2026-10-01: interval 50, timeout from asyncUtilTimeout, observer options, setInterval + MutationObserver, onDone cleanup, 200-line eslint cap all match)
