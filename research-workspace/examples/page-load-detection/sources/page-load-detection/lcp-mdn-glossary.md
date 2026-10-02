# Largest Contentful Paint (LCP) - MDN Glossary

- Link: https://developer.mozilla.org/en-US/docs/Glossary/Largest_contentful_paint
- Date read: 2026-10-01 (search result listing only, page never opened)
- Status: unverified
- Evidence strength: reference documentation, not a study. No sample size, no replication.

## Claim (one sentence)
LCP reports the render time of the largest image or text block visible in the viewport and can be observed with a PerformanceObserver on the `largest-contentful-paint` entry type.

## Excerpts
These are NOT verbatim page text. They come from a WebSearch tool summary that blended several results (MDN, Request Metrics, others). WebFetch of this page, web.dev/articles/lcp, the W3C LCP spec, Playwright docs and the MDN API page all failed with "proxy refused the connection". Every line below must be re-checked against the opened page.

- Summary text: "The Largest Contentful Paint (LCP) performance metric provides the render time of the largest image or text block visible within the viewport, recorded from when the page first begins to load."
- Summary code: `new PerformanceObserver(entryList => { console.log(entryList.getEntries()); }).observe({ type: "largest-contentful-paint", buffered: true });`
- Summary text: "The following elements are considered contentful when determining the LCP: <img> elements, <image> elements inside an SVG, the poster images of <video> elements, elements with a background-image, and groups of text nodes."
- Summary text: "A good LCP score is under 2.5 seconds."

## Relevance to brief
LCP fits server-rendered pages. Not yet confirmed from an opened source: whether it works for SPA soft navigations, and when the browser stops emitting candidates (for example after user input). Those points need the web.dev or W3C spec pages.

Verified: could not open (MDN fetch refused by egress proxy, 403 CONNECT; every excerpt remains unconfirmed search-summary text, do not cite)
