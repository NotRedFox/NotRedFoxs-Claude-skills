# Settling time: tolerance band over N consecutive samples (signal measurement)

- Link: https://arxiv.org/pdf/2603.26147 (VolTune, FPGA runtime voltage control)
- Date read: 2026-10-01
- Status: unverified (arXiv fetch blocked by egress proxy, 403; only search result summary seen). Weak source: it is one applied paper, not a reference on the method.
- Field: analog/ADC and power measurement.

## Excerpts (from search summary, not the paper itself)
- Stable value = average of the last N samples; stability band = that average +/- x%.
- Settled = the first index from which N consecutive samples all fall inside the band.
- Settling time = elapsed time from t=0 to that index. General definition: earliest instant after which all samples stay in the band.

## Bridge to page-load detection
Define the final state from the tail of the stream (e.g. final DOM size or text length), then report the first moment the metric stayed within a band of it for N samples. Works as an offline test harness to measure when pages "really" settled and to tune the live quiet window. Not usable live as written, since the final value is unknown until later.

Verified: could not open (arxiv.org blocked by egress proxy, CONNECT 403 organization policy, on 2026-10-01; excerpts remain unconfirmed, do not cite)
