# Gelman-Rubin R-hat: convergence of MCMC chains (statistics)

- Link: https://arxiv.org/pdf/1903.08008 ("An improved R-hat for assessing convergence of MCMC")
- Date read: 2026-10-01
- Status: unverified (arXiv fetch blocked by egress proxy, 403; only search result summary seen)
- Field: Bayesian statistics. Decide when a noisy sampling process has stopped drifting.

## Excerpts (from search summary, not the paper itself)
- "When R-hat is sufficiently close to 1, the GR diagnostic declares convergence."
- Older cutoff 1.1; modern recommendation 1.01. Quoted in the summary: threshold 1.01 detects trends that account for 2% or more of marginal variance; 1.1 only detects trends of 30% or more.
- The idea: compare variance within several independent chains to variance between them. Agreement means settled.

## Bridge to page-load detection
Compare several independent signals (e.g. DOM mutation rate, network requests in flight, LCP candidate changes) and call it settled only when they agree, with a tight tolerance. A loose threshold hides ongoing drift. Needs an assumption: the signals are independent enough to act as "chains".

Verified: could not open (arxiv.org refused by egress proxy, 403 CONNECT; the 1.01/1.1 and 2%/30% figures are unconfirmed, do not cite)
