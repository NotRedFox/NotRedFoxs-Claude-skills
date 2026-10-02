# Brief: page-load-detection

Building: a browser extension (content script) that waits until a web page's main content has finished loading, then runs.
Constraints: must work on SPAs and server-rendered pages, no page-specific selectors, low overhead, Manifest V3.
Question: how to detect "main content finished loading" reliably.
Limit: at most 3 sources per scout. Save each to sources/page-load-detection/ with link, date read, status, excerpts.
Search terms: largest contentful paint PerformanceObserver, MutationObserver DOM stability idle, network idle detection, document.readyState, SPA soft navigation, Playwright networkidle, web-vitals.
