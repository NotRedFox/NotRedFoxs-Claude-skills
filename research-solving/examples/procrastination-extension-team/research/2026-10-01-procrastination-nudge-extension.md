# Procrastination nudge extension

Researched 2026-10-01 with research-solving 1.1.0: three researchers in parallel (code, papers, other fields), then a lead check of the sources behind the top ideas.

## Target
- Building: a browser extension that notices when the user is procrastinating and nudges them back to work.
- Constraints: runs locally, no cloud. Chrome and Firefox extension in JavaScript. The user knows a bit of JavaScript. Privacy matters.
- Assumed: the user wants nudges, not hard blocking, and is happy to label a few days of their own browsing.

## Top things to try
| # | Try this | Rating | First test | Cost |
|---|---|---|---|---|
| 1 | Log three local signals: tab switches per minute, time away from the work tab, and the `idle` state | High | Build a logger with `tabs.onActivated`, `idle` and `visibilitychange`, use it for one working day, export JSON. Pass if at least 90% of active minutes have a domain and a state. | 2 to 4 h |
| 2 | Put the "back to work" cue on the work tab, showing where the user left off | High | Two days with the cue, two without. Compare median time to return to the work tab. Pass if it drops. | 3 h, 4 days of use |
| 3 | Gentle, opt-in nudges, with no hard blocking by default | High | Ship nudges only. After 3 days, ask "did this annoy you?" (1 to 5). Pass at 3 or under. | 1 h |
| 4 | A short pause with a clear "go back" button before sites the user lists | Medium | Add a 5 second pause page on the user's own list. Count how often they go back. Pass if over 20%. | 2 h, 1 week of use |
| 5 | Rotate between a few nudge styles, and say why they change | Medium | Three styles, picked at random per nudge, logged. Same-day check: confirm all three fire and are logged. Two weeks for which works best. | 2 h, 2 weeks |
| 6 | Judge any detector on held-out days, and count how many variants were tried | High (method) | Tune thresholds on days 1 to 3, test on days 4 to 5. Pass if accuracy on days 4 to 5 is within 10 points of days 1 to 3. | 1 h, after 5 days of labels |
| 7 | Classify unknown page titles as work or not with a small on-device model | Medium | Run a zero-shot model with Transformers.js on 50 of the user's own labelled titles. Pass if it fixes over half of what the domain rules get wrong. | Half a day, one model download |
| 8 | Typing rhythm or mouse movement as a focus signal | Low | Skip until 1 to 6 work. Opt-in only. | Days, privacy cost |

## Ring 1: existing code

All 7 repositories were cloned and read (README and core files).

- **LeechBlock NG** ([repo](https://github.com/proginosko/LeechBlockNG)). MPL-2.0, active. Borrow `clockPageTime()` in `background.js`, which keeps separate "open" and "focused" timers per tab, and the `delaySecs` delay-before-entry page (idea 4). Copied files must stay MPL.
- **aw-watcher-web** ([repo](https://github.com/ActivityWatch/aw-watcher-web)). MPL-2.0, active. Borrow the heartbeat with `tabs.onActivated` and `onUpdated` in `src/background/heartbeat.ts` (idea 1), and the consent tab shown on install. Needs the ActivityWatch server, so take the pattern, not the dependency.
- **PawBlock** ([repo](https://github.com/dguo/pawblock)). MIT, small and readable. Borrow `storage-schema.json` (stored state with a version for migrations) and the one-time `allowedTabId` bypass. It is Manifest V2, so read it but don't copy it.
- **HabitLab** ([repo](https://github.com/habitlab/habitlab)). GPL-3.0, last commit 2021. Borrow ideas only: `multi_armed_bandit_thompson.ls` picks which nudge to show and learns from the results (idea 5), and `unproductive_domains.json` lists 13,313 domains. Its logs go to a cloud server, which breaks the no-cloud rule.
- **NeuroSkill browser extension** ([repo](https://github.com/Jah-yee/browser-extension)). GPL-3.0. Its README documents distraction and procrastination scores (tab switches against a 7-day baseline, very short visits, time on social sites), and says they are not validated. `src/core/classify.ts` has pure functions that are easy to test.
- **Intention** ([repo](https://github.com/MaybeItsSoftware/intention)). MIT, active. Asks for a reason before each visit. Loosening a rule only takes effect the next day, which is a good pattern (`shared/rules.js`). Its AI coach uses the cloud.
- **Nudge** ([repo](https://github.com/louisbarclay/nudge)). GPL-3.0. Hides feeds instead of whole sites, using a list of CSS selectors that goes stale as sites change.

Licences: only PawBlock and Intention are MIT. Borrow ideas, not code, from the GPL projects.

## Ring 2: research

Five papers were opened and read in full. Four could only be seen as search results.

- **Iqbal and Horvitz, CHI 2007**, [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/CHI_2007_Iqbal_Horvitz-1.pdf), opened. 27 people logged for two weeks. After replying to an email alert straight away, people took 16 minutes 33 seconds on average to get back to the work they left. Keeping the suspended work visible helped. Supports ideas 1 and 2.
- **Mark, Iqbal, Czerwinski and Johns, CSCW 2015**, [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/10/p903-mark.pdf), opened. 32 employees observed for five days. The person's state comes before the distraction, and more screen switching went with feeling less productive. Correlational. Supports idea 1.
- **Mark, Czerwinski and Iqbal, CHI 2018**, [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/02/pn1612-markA.pdf), opened. 32 workers, one week with distracting sites blocked. People low in self-control gained the most focus. People high in self-control reported more workload, and 16 reported more stress. This is the paper that disagrees with the rest: blocking is not good for everyone. Supports idea 3.
- **Mark, Iqbal, Czerwinski and Johns, CHI 2014**, [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Focus20Camera-Ready20Final.pdf), opened. 32 workers, five days. Focus and boredom follow patterns by time of day and day of week. Time of day is a cheap local signal.
- **Iqbal and Horvitz, CSCW 2010**, [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/253n-iqbal.pdf), opened. With alerts off, some people checked email more on their own. Removing cues can backfire. Supports idea 3.
- **Kovacs, Wu and Bernstein, CSCW 2018** (HabitLab), unverified. About 1,654 users. Rotating nudges cut time on distracting sites but raised uninstalls. Explaining the rotation roughly halved the uninstalls. Idea 5.
- **Lyngs et al., CHI 2019**, arXiv 1902.00157, unverified. A review of 367 self-control apps and extensions. Most block, and few were ever evaluated.
- **Monge Roffarello and De Russis, TOCHI 2023**, DOI 10.1145/3571810, unverified. A meta-analysis reporting small to medium effects. Exact figures not seen.
- **CatAlyst, CHI 2023**, arXiv 2302.05678, unverified. Shows the user the continuation of the work they left. Used a cloud model.

## Ring 3: ideas from other fields

| Field | Idea there | Idea here | Rating | Why |
|---|---|---|---|---|
| Behavioural science | The "one sec" app pauses before a distracting app opens, with a way to back out | Pause page with a "go back" button (idea 4) | Medium | The study (PNAS, about 280 people) could not be opened, and the app's founder is a co-author. The pattern is also in LeechBlock and Intention. |
| Behavioural medicine | Just-in-time adaptive interventions: nudge only at chosen moments, and sometimes hold back at random to measure the effect | Hold back some nudges at random and log what happens | Medium | Solid framework (Nahum-Shani et al. 2018, unverified here), mixed results |
| Security design | People stop noticing repeated warnings; varying them slows this | Rotate nudge wording and style, cap how often they appear (idea 5) | Medium | About warnings, not productivity, and unverified here |
| Quantitative finance | Trying many strategies and keeping the best one makes luck look like skill | Tune on some days, test on others, count variants (idea 6) | High | Method is well established; [pypbo](https://github.com/esvhd/pypbo) implements it (opened) |
| Browser APIs and on-device ML | `idle` and Page Visibility give state without reading pages. Transformers.js runs models in the browser | Ideas 1 and 7 | High | Docs opened: [idle](https://github.com/mdn/content/blob/main/files/en-us/mozilla/add-ons/webextensions/api/idle/index.md), [Page Visibility](https://github.com/mdn/content/blob/main/files/en-us/web/api/page_visibility_api/index.md), [Transformers.js](https://github.com/huggingface/transformers.js) |
| Biometrics | Stress shows in how hard people type and grip the mouse | Typing rhythm as a focus signal (idea 8) | Low | Lab study of 24 people with special hardware ([Microsoft Research](https://www.microsoft.com/en-us/research/publication/under-pressure-sensing-stress-of-computer-users/), opened). A browser only sees timing. Behavioural data needs opt-in consent and may fall under GDPR. |
| Mobile computing | Phone usage logs predicted boredom (Pielot et al. 2015) | Tab switching as a boredom signal | Low | 54 users, one study, unverified here |

## First tests

All `not run`. Each one needs a real browser and the user's own browsing over several days, which this environment doesn't have. The same-day checks in the table (logger coverage, all nudge styles firing) are the place to start.

## Dead ends
- **Copying HabitLab:** abandoned since 2021, GPL, and sends logs to a cloud server. Use its ideas and domain list (after checking the licence), not its code.
- **CatAlyst's cloud model** and **Intention's AI coach:** both break the no-cloud rule. Idea 2 is a local version of the same help.
- **Phone-based boredom detection:** small single study, and the signals don't carry over to a browser.

What the lead's check changed:
- Ring 2 reported "about 8.5 minutes to return after an email alert". The paper's 8 minutes 48 seconds is the reply time for delayed chat alerts. The time to return to work after replying to an email straight away is 16 minutes 33 seconds. Corrected.
- Ring 3 rated the pause-before-opening idea High. Its paper could not be opened, so it is capped at Medium.

## Sources

Opened (17): the 7 repositories above, 5 Microsoft Research papers, the Microsoft stress study page, pypbo, the MDN idle and Page Visibility docs, and Transformers.js. In the lead check, the 3 papers behind the top ideas and the key source files named in Ring 1 were opened again and checked.

Unverified (8): Kovacs et al. 2018, Lyngs et al. 2019, Monge Roffarello and De Russis 2023, CatAlyst 2023, the "one sec" PNAS study, Nahum-Shani et al. 2018, the warning habituation studies (Anderson et al. 2015), Pielot et al. 2015. Paper sites (arXiv, ACM, PubMed, PNAS, Stanford) were blocked where this ran.
