# Procrastination nudge browser extension

Researched 2026-10-01.

## Target

**Outcome:** notice when I drift off my work in the browser and bring me back, without sending anything to a server.

**Constraints (assumed, no answer from the user):**
- Platform: desktop Chrome or Firefox, Manifest V3 WebExtension.
- Language: JavaScript, beginner to intermediate level. No build step at first.
- Privacy: all data stays in `browser.storage.local` or IndexedDB. No cloud calls, no accounts.
- Budget: zero. Must run on an ordinary laptop.
- "Procrastinating" means: the active tab is off-task for a sustained stretch while the user is at the keyboard. It does not mean idle or away.

**Already tried or known:** nothing stated. Assumed the user knows site blockers exist.

**Search terms used:** procrastination detection, off-task browsing, digital self-control tools, attention monitoring, idle detection, task switching, tab relevance semantic similarity, behaviour change interventions browser, change point detection.

**Network note:** this research ran behind a proxy that allowed github.com, raw.githubusercontent.com, registry.npmjs.org and pypi.org, and blocked every paper host tried (arxiv.org, dl.acm.org, semanticscholar.org, api.openalex.org, researchgate.net, hci.stanford.edu, ncbi.nlm.nih.gov, ora.ox.ac.uk, dblp.org, core.ac.uk, link.springer.com) plus developer.chrome.com, developer.mozilla.org, wikipedia.org and huggingface.co. MDN pages were read from their source on GitHub instead. No paper could be opened, so Ring 2 is marked unverified throughout.

## Top things to try

| # | Try this | Rating | First test | Cost |
|---|---|---|---|---|
| 1 | Logger: active tab domain + title, `idle` state, tab switches, written to local storage | High | Install unpacked, work 1 day, export JSON; pass if at least 90% of your active minutes are logged with a domain | 2 to 4 h, free |
| 2 | Rule scorer: work domains, distraction domains, task keywords from a "what are you working on" prompt | High | Run `first-test/keyword-baseline.mjs` on 40+ of your own labelled titles; pass at 80% accuracy | 1 h, free (run on sample data: 95%) |
| 3 | Dwell rule before nudging: off-task for N minutes while `idle` says active | High | Replay day-1 log with N = 2, 5, 10 min; pass if nudges per hour of work is under 2 and you agree with 4 of 5 | 1 to 2 h |
| 4 | Gentle nudge first, block never by default: notification or toolbar colour, with a countdown warning | Medium | One week, count nudges and how many you obeyed within 1 min; pass if over 50% | 1 h build, 1 week use |
| 5 | Rotate between 3 nudge styles and log which ones bring you back | Medium | Two weeks, random style per nudge; pass if one style beats the others by 20 points in return rate | 2 h build |
| 6 | Local sentence embeddings (MiniLM via Transformers.js) for titles the rules cannot classify | Medium | Compare against #2 on the same labelled titles; pass if it fixes over half of #2's errors | half a day, ~23 MB model download once |
| 7 | Change point detection (CUSUM) on a rolling relevance score instead of a fixed threshold | Low | Replay logs; pass if it flags drift at least 1 min earlier than #3 with no more false nudges | half a day |
| 8 | Typing rhythm or mouse features as a focus signal | Low | Skip until 1 to 6 work; only with explicit consent | days, privacy cost |

## Ring 1: existing code

Licence note: four of the useful projects are MPL-2.0 or GPL-3.0. MPL-2.0 lets you copy a file if that file stays MPL-2.0 and its source stays available. GPL-3.0 would make your whole extension GPL-3.0 if you copy code. Reading for ideas is fine in all cases.

**ActivityWatch aw-watcher-web** ([github.com/ActivityWatch/aw-watcher-web](https://github.com/ActivityWatch/aw-watcher-web)). MPL-2.0, ~563 stars, last commit 8 Sep 2026, TypeScript + Vite. Records active tab URL, title, audible and incognito state and sends them to a local ActivityWatch server.
- Borrow: `src/background/heartbeat.ts`. The "heartbeat" pattern stores only `{url, title, audible, incognito, tabCount}` and merges identical consecutive events, so a day of logs stays small. It listens to `tabs.onActivated`, `tabs.onUpdated` and a `browser.alarms` timer, and serialises writes through a promise queue so fast tab changes do not race. A code comment notes that keeping whole `Tab` objects (with base64 favicons) caused unbounded memory growth (issue #222): copy only the fields you need.
- Borrow: `src/background/main.ts` shows a consent page opened on install before any logging starts.
- Avoid: it needs the ActivityWatch desktop server running. Your version writes to `storage.local` instead.

**LeechBlock NG** ([github.com/proginosko/LeechBlockNG](https://github.com/proginosko/LeechBlockNG)). MPL-2.0, ~1.1k stars, last commit 27 Sep 2026, plain JavaScript with no build step, 2,032-line `background.js`.
- Borrow: `checkWarning()` in `background.js` sends a message to the tab ("will be blocked in N seconds") before it blocks. Its timekeeping (`clockPageTime`, `updateTimeData`) separates seconds a page is open from seconds it has focus, which is the distinction you need.
- Borrow: the flat file layout (`manifest.json`, `background.js`, `content.js`, `popup.html/js`, `options.html/js`, `blocked.html/js`) is a good model for a beginner project.
- Avoid: it is a blocker with schedules, not a detector. Large single file.

**ProcrastiScan** ([github.com/Marc-Pk/ProcrastiScan](https://github.com/Marc-Pk/ProcrastiScan)). MPL-2.0, 56 stars, last commit 28 Mar 2025. The closest match to your idea.
- Borrow: `addon/background.js` loads `Xenova/all-MiniLM-L6-v2` with Transformers.js, embeds your task text, "related content" and "common distractions" once, then scores each tab as `(max sim to task + max sim to related - max sim to distractions + 1) / 2`. `calculateAverageSimilarity()` keeps a 10-minute time-weighted average so one off-task tab does not trigger a nudge. "Theme nudging" turns the Firefox toolbar red.
- Avoid: it sets `env.allowLocalModels = false`, so the model downloads from Hugging Face on first run. That is a network call; bundle the model files in the extension if "no cloud" is strict. The README calls it a proof of concept. The chatbot intervention needs a separate local LLM server (`procrastiscan-server.py`).

**ProcrastiBlock** ([github.com/JoshGaviola/ProcrastiBlock](https://github.com/JoshGaviola/ProcrastiBlock)). 2 stars, no licence shown. Same MiniLM idea; `script.js` has a readable `cosineSimilarity()` and a threshold slider, and `content-script.js` shows a non-blocking toast.
- Avoid copying: no licence means no permission to reuse. It also imports Transformers.js from `cdn.jsdelivr.net` at runtime, which is a network call and is remote code, which Manifest V3 store review does not allow.

**HabitLab** ([github.com/habitlab/habitlab](https://github.com/habitlab/habitlab)). GPL-3.0, 381 stars, last commit 23 Apr 2021, 558 open issues. Stanford research extension that tried many interventions per site and measured which ones cut time spent.
- Borrow: the idea of a library of small nudges with measurement of which works. Its research papers are listed in Ring 2.
- Avoid: unmaintained since 2021, large codebase, GPL-3.0.

**NeuroSkill browser-extension** ([github.com/Jah-yee/browser-extension](https://github.com/Jah-yee/browser-extension)). GPL-3.0, 0 stars, 4 commits. Unusual approach: records tab switches, scroll depth and reversals, mouse distance, clicks per minute and typing (boolean), and blends them into a "focus score" and a 30-minute "procrastination score".
- Borrow: its honesty table. The README labels the browser-only focus score "exploratory, no external validation" and the procrastination score "heuristic, no labelled training data". Use it as a checklist of signals and as a warning.
- Avoid: GPL-3.0; unvalidated scores.

**Angel** ([github.com/shaw029/angel](https://github.com/shaw029/angel)). MIT, 0 stars. Runs Gemma 2B on device via WebGPU (~3.9 GB, 2 to 4 s) or WASM (~2 GB, 8 to 15 s) to give reflective nudges. Shows that an on-device LLM is possible and also how heavy it is.

**Nudge** ([github.com/louisbarclay/nudge](https://github.com/louisbarclay/nudge)). GPL-3.0, 151 stars. Hides feeds and autoplay instead of detecting anything. A different strategy: remove the trigger rather than catch the drift.

## Ring 2: research

**Unverified.** Every paper host was blocked by the network proxy, so none of these could be opened. Details below come from search result snippets only. Open each before relying on it.

- **Kovacs, Gregory, Ma, Wu, Emami, Ray, Bernstein (2019). "Conservation of Procrastination: Do Productivity Interventions Save Time Or Just Redistribute It?" CHI 2019.** Search snippet: HabitLab field data from about 5,230 users; raising intervention frequency on one site did not push time to other sites or to the phone. Evidence (from snippet): large in-the-wild sample, self-selected users of a research extension. Applies: suggests nudging on a few target sites does not move the time elsewhere. Not opened.
- **Kovacs, Wu, Bernstein (2018). "Rotating Online Behavior Change Interventions Increases Effectiveness But Also Increases Attrition." PACM HCI, CSCW. DOI 10.1145/3274364.** Search snippet: three field experiments; rotating nudges reduced time on site more than one fixed nudge, but more users uninstalled; telling users about the rotation at the moment it happens halved attrition. This is the paper that cuts against "more variety is better". Applies to idea 5. Not opened.
- **Lyngs et al. (2019). "Self-Control in Cyberspace: Applying Dual Systems Theory to a Review of Digital Self-Control Tools." CHI 2019. arXiv 1902.00157.** Search snippet: reviewed 367 apps and extensions and grouped their design features (blocking, self-tracking, goal advancement, reward and punishment). Applies: a map of which nudge types exist. Not opened.
- **Monge Roffarello and De Russis (2023). "Achieving Digital Wellbeing Through Digital Self-control Tools: A Systematic Review and Meta-analysis." ACM TOCHI 30(4). DOI 10.1145/3571810.** Search snippet: 37 articles, 43 studies, with a pooled effect size estimate (value not seen). Applies: the best single check of whether tools like this work at all. Not opened.

Gap: no paper was found that validates detecting procrastination from browser signals against ground truth. A Springer chapter titled "Understand and Assess People's Procrastination by Mining Computer Usage Log" appeared in search (Markov chain model on computer logs) but could not be opened and is not listed in Sources.

## Ring 3: ideas from other fields

| Field | Idea there | Idea here | Rating | Why |
|---|---|---|---|---|
| Browser signals | `idle.onStateChanged` reports `active`, `idle` (no input for N s, min 15, default 60) or `locked` | Only count off-task time while state is `active`, so walking away is never "procrastinating" | High | Documented WebExtension API in Chrome and Firefox (MDN source); direct fit |
| Browser signals | Page Visibility API and `tabs.onActivated` show which tab is in front | Measure tab switch rate and dwell per domain from the background script | High | Documented API; used by aw-watcher-web and LeechBlock in production |
| Quantitative research | Backtest on held-out data; distrust a rule tuned on the same data it is scored on | Label one day, tune rules, then score them on a second day you did not look at | High | Standard guard against overfitting; our own first test shows the risk (rules and labels by one author) |
| Quantitative research | Change point detection (CUSUM, `ruptures` library) finds when a noisy series shifts level | Flag drift when the rolling relevance score shifts, not when one tab dips below a line | Low | Method is sound in its home field, but no evidence it beats a plain dwell timer on tab data, and it needs tuning data you do not have yet |
| Local and offline assistants | Small sentence embedding models (MiniLM, ~23 MB) run in the browser via Transformers.js (Apache-2.0, v4.3.0) | Score unknown titles against the stated task, as ProcrastiScan does | Medium | Works in ProcrastiScan's code; the bridge assumes title + domain carries enough meaning, which no source here measured |
| Local and offline assistants | On-device LLM (Gemma 2B via WebGPU, as in Angel) writes a personal nudge | Ask the model "is this tab part of task X" or have it write the nudge | Low | 2 to 3.9 GB download and seconds of latency per call for a yes or no question; no evaluation shown |
| Open-source assistants (Leon, MIT, 17.6k stars) | Layered memory: durable preferences, today's context, recent conversation | Store the session goal ("today: finish popup UI") and per-domain verdicts the user corrected | Medium | Design pattern only; but user corrections give you labelled data for free |
| Behaviour change research (HabitLab) | Rotate interventions, explain the rotation at the moment it happens | Rotate 3 nudge styles, log return rate per style | Medium | Field result is from search snippets only (unverified) |
| Biometrics and behavioural signals | Typing rhythm and mouse dynamics as stress or attention markers | Content script measures keystroke timing and mouse idle | Low | Only unvalidated heuristics found (NeuroSkill README says so itself); needs content script on every page; behavioural data needs clear consent and may count as biometric data under GDPR (special category) |
| Medicine (alarm fatigue) | Too many alarms make clinicians ignore all of them | Cap nudges per hour and require a dwell time before each one | Medium | Well known in clinical settings; no source opened here, so the rating rests on the bridge, not on evidence gathered |

Privacy flag: ideas 1, 2, 3 and 8 record browsing behaviour. Even locally, show a consent page on install (as aw-watcher-web does), never log incognito tabs, and offer one-click delete. Idea 8 collects behavioural data that may count as biometric under GDPR.

## First test that was run

`run`: `research/first-test/keyword-baseline.mjs`, Node 22, no dependencies.

```
n=40 tp=15 tn=23 fp=2 fn=0
accuracy=0.950 precision(on-task)=0.882 recall(on-task)=1.000
FP: Show HN: I built a JavaScript game engine (news.ycombinator.com)
FP: Chrome extension ideas that make money (youtube.com)
RESULT: PASS (>= 0.80)
```

Caveat: the 40 titles and labels were written by the same author as the rules, so 95% is an upper bound, not a real result. Both errors are keyword traps (on-topic words on an off-task page). Rerun with your own day of titles before trusting it.

`not run`: the MiniLM embedding comparison (idea 6). The model host (huggingface.co) and CDN were blocked here, and installing a third-party npm package that bundles the model was not permitted in this session.

`not run`: ideas 1, 3, 4, 5, 7, 8. No browser was available in this environment.

## Dead ends

- **ProcrastiBlock's code:** no licence, and it loads ML code from a CDN at runtime. Not reusable.
- **HabitLab as a base:** unmaintained since April 2021 and GPL-3.0.
- **On-device LLM as the detector:** gigabytes and seconds per call to answer a yes or no question a 23 MB embedding model or a keyword list can answer.
- **Composite "focus scores" from scroll, mouse and clicks:** every one found was a hand-weighted heuristic with no ground truth.
- **Chrome `alarms` faster than 30 s:** MDN notes Chrome fires packed-extension alarms at most every 30 seconds (one minute before Chrome 120). Use tab events for responsiveness and alarms only for the periodic check.

## Sources

Code and docs:
- https://github.com/ActivityWatch/aw-watcher-web (opened)
- https://github.com/ActivityWatch/aw-watcher-web/commits/master (opened)
- https://raw.githubusercontent.com/ActivityWatch/aw-watcher-web/master/src/background/heartbeat.ts (opened)
- https://raw.githubusercontent.com/ActivityWatch/aw-watcher-web/master/src/background/main.ts (opened)
- https://github.com/proginosko/LeechBlockNG (opened)
- https://github.com/proginosko/LeechBlockNG/commits/master (opened)
- https://raw.githubusercontent.com/proginosko/LeechBlockNG/master/background.js (opened)
- https://github.com/Marc-Pk/ProcrastiScan (opened)
- https://github.com/Marc-Pk/ProcrastiScan/commits/main (opened)
- https://raw.githubusercontent.com/Marc-Pk/ProcrastiScan/main/addon/background.js (opened)
- https://github.com/JoshGaviola/ProcrastiBlock (opened)
- https://raw.githubusercontent.com/JoshGaviola/ProcrastiBlock/main/script.js (opened)
- https://github.com/habitlab/habitlab (opened)
- https://github.com/habitlab/habitlab/commits/master (opened)
- https://github.com/Jah-yee/browser-extension (opened)
- https://github.com/shaw029/angel (opened)
- https://github.com/louisbarclay/nudge (opened)
- https://github.com/leon-ai/leon (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/mozilla/add-ons/webextensions/api/idle/index.md (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/mozilla/add-ons/webextensions/api/idle/setdetectioninterval/index.md (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/mozilla/add-ons/webextensions/api/idle/onstatechanged/index.md (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/api/page_visibility_api/index.md (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/mozilla/add-ons/webextensions/api/alarms/create/index.md (opened)
- https://raw.githubusercontent.com/mdn/content/main/files/en-us/mozilla/add-ons/webextensions/api/notifications/create/index.md (opened)
- https://registry.npmjs.org/@huggingface/transformers/latest (opened)
- https://pypi.org/pypi/ruptures/json (opened)

Papers (all unverified, blocked by proxy, metadata from search snippets only):
- https://hci.stanford.edu/publications/2019/conservation/conservation-chi2019-old.pdf (unverified, blocked)
- https://dl.acm.org/doi/10.1145/3274364 (unverified, blocked)
- https://arxiv.org/abs/1902.00157 (unverified, blocked)
- https://dl.acm.org/doi/10.1145/3571810 (unverified, blocked)
