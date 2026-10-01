# Phone alert when the washing machine finishes

Started 2026-10-01. Last updated 2026-10-01.

## Outcome wanted

Know, on my main phone, when the washing machine has finished, without standing next to it.

## Best answer so far

Put the old Android phone on top of the washer and let it watch the vibration. When the machine has done a long hard spin and then stays still for 6 minutes, the old phone sends a push notification to the main phone through ntfy.

- Script: `problem-solve/phone_watch.py` (runs in Termux on the old phone).
- Reliability so far: 200 of 200 synthetic cycles alerted after the real end and none early, median 5.8 minutes late, max 6.1. The full pipeline (sensor stream format, detector, HTTP notification) worked on 3 of 3 synthetic cycles against a local stand-in server. **No real washer data yet.** The numbers above come from a model of a washer I wrote, not a recording.
- What would make it fail: a machine whose final spin is weaker than 0.2 g on the lid, a refill pause after a rinse spin longer than 6 minutes, the phone sliding off during the spin, Android killing Termux in the background, or no Wi-Fi at the machine.
- Setup:
  1. Old phone: install Termux and Termux:API (F-Droid builds), then `pkg install python termux-api`. Copy `phone_watch.py` over.
  2. Main phone: install the ntfy app and subscribe to a long random topic, for example `wash-<random 12 chars>`.
  3. Old phone: plug in the charger, turn off battery optimisation for Termux, run `termux-wake-lock`, then `termux-sensor -s accelerometer -d 50 | python phone_watch.py --topic <YOUR_TOPIC>`.
  4. Put the phone flat on the lid on a rubber mat or in a small box taped to the lid so it cannot walk off during the spin.
  5. Run the on-device tests in "Next tests" before trusting it.

Fallback if the machine has an end beep and the phone sits in a cupboard far from the lid: the beep listener (3.2), synthetic results below.

## Constraints

- Real:
  - The washer is old: no Wi-Fi, no app, no API, no data port I can assume.
  - Hardware on hand: one old Android phone, one Raspberry Pi (model unknown).
  - The alert has to reach the main phone, so something near the washer needs network access.
- Assumed, and challenged:
  - "It needs to talk to the machine." No, it can read the effect of the machine finishing: vibration stops, a beep, a light, power draw drops.
  - "It must be exact to the second." A few minutes late is fine for laundry. That allows a long quiet window, which removes most false alerts.
  - "The Pi is needed." The old phone already has an accelerometer, a microphone, Wi-Fi and a battery. The Pi is a backup or a second sensor.
  - "It must detect the start too." Not needed if the user taps start, see 4.1. The script detects start anyway.
  - "Buying nothing." Not stated by the user. The best answer buys nothing. Options that need a part are marked.

## Resources

The user was not available for questions. What they said, and what I assumed:

| Resource | Source | Used by |
|---|---|---|
| Old Android phone (accelerometer, microphone, camera, Wi-Fi) | User said | 3.1, 3.2, 3.3, 4.1, 4.2, 5.1 |
| Raspberry Pi in a drawer | User said | 5.2, 5.3 |
| Main phone that gets the alert | Assumed | all |
| Home Wi-Fi reaches the washer | Assumed | all that notify |
| A charger and socket near the washer | Assumed | 3.1, 3.2, 5.x |
| Physical access to the machine, it is the user's own | Assumed | 3.x, 5.x |
| An electricity supplier smart meter | Assumed, not known | 2.1 |
| Small budget for a 2 to 15 unit part | Assumed, not known | 3.4, 5.2 |

## Ladder

### Level 1: Obvious

#### 1.1 Vendor app or API for this machine. Failed

- Uses: nothing.
- Test: the user's own statement (no Wi-Fi, no app, no API).
- Result: Failed. There is no door.
- Learned: the official route is closed by the hardware, not by a missing key. Nothing to unlock.

#### 1.2 An existing Play Store app that does this with a phone on the washer. Failed

- Uses: old Android phone.
- Test: two web searches on 2026-10-01 for Android apps that watch the accelerometer and alert when laundry is done.
- Result: Failed. Found LaundryMinder (Windows Phone 7, unmaintained), Play Store "laundry" apps that need a vendor Wi-Fi adapter (laundrify) or are for shared laundry rooms (LaundryAlert), and many DIY builds (Instructables accelerometer sensor, Home Assistant smart plug and vibration sensor guides). No maintained app that does the whole thing with a spare phone.
- Learned: the idea is well known and works for others, so the missing piece is a small script, not research. Vibration and power draw are the two signals other people use.

### Level 2: Sideways in the same system

#### 2.1 Electricity supplier smart meter data. Not run

- Uses: smart meter (assumed).
- Test for the user: open the supplier app during a wash and see whether it shows usage at 1 minute resolution or finer, and whether it can send alerts.
- Result: Not run. Most supplier apps show 30 minute blocks, sometimes a day late, which cannot tell "finished 5 minutes ago". Some in-home displays show live watts.
- Learned: the washer has no side door of its own. The only "same system" is the house power, and that is level 3 by another name.

### Level 3: Different channel

#### 3.1 Old phone on the lid reads vibration (naive detector). Partly works

- Uses: old Android phone accelerometer.
- Test: `tests/vibration_test.py`, 100 synthetic cycles per scenario. Each cycle: fill, wash in tumble bursts, random soak pauses of 2 to 10 minutes, 1 to 3 rinses each ending in a spin plus a 2 to 5 minute quiet refill, final spin, then still. Footsteps and doors added. Alert = no vibration for N minutes after the cycle started. **Synthetic data.**
- Result (scenario A, rinse spins weaker than final spin):

  | Quiet window | Correct | Early (false alert) | Median delay |
  |---|---|---|---|
  | 3 min | 6 | 94 | 2.9 min |
  | 6 min | 70 | 30 | 5.8 min |
  | 10 min | 93 | 7 | 9.8 min |

- Learned: silence alone is a weak signal. Soak and refill pauses inside the cycle look the same as "done". The first detector version also missed 4 to 12 of 100 because a footstep after the end restarted the logic, fixed by ignoring bursts under 15 s.

#### 3.2 Phone or Pi listens for the end beep. Partly works

- Uses: old Android phone microphone, or the Pi with a USB microphone.
- Test: `tests/beep_test.py`, 40 synthetic 3 minute clips per row at 8 kHz, half with a 3 x 0.5 s beep at 3.2 kHz, plus room noise, TV-like speech bursts and a microwave beeping at 2.0 kHz. Detector: narrow-band energy at the learned beep frequency over whole-band energy, 3 beeps within 6 s. **Synthetic audio.**
- Result (ratio threshold 0.10):

  | Beep level vs room noise | Found | False alerts |
  |---|---|---|
  | +10 dB | 20/20 | 0/40 |
  | 0 dB | 20/20 | 0/40 |
  | -5 dB | 16/20 | 0/40 |
  | -10 dB | 13/20 | 0/40 |
  | -15 dB | 0/20 | 0/40 |

  Threshold 0.35 found only 14/20 at 0 dB, 0.20 found 17/20 (`tests/beep_ratio_sweep_output.txt`).
- Learned: works well if the machine beeps at all and the mic is in the same room. Many older machines with a mechanical dial do not beep, which is why this is the fallback. Needs one real recording of the beep to learn its frequency.

#### 3.3 Phone camera watches the "end" or door-lock light. Not run

- Uses: old Android phone camera.
- Test for the user: does the machine have a light that changes at the end (door lock off, "end" lamp)? If yes, prop the phone facing it, take one photo during the wash and one after, and compare the brightness of that spot.
- Result: Not run. No machine to look at.
- Learned: only worth it if 3.1 fails and the machine has such a light.

#### 3.4 Power draw through a plug-in energy monitor. Not run

- Uses: a smart plug with power metering (a part to buy, 10 to 15 units), or the Pi with a plug-in meter that has a pulse LED.
- Test for the user: with any plug-in watt meter, note the watts during the wash, the final spin, and 2 minutes after the end. Most washers draw under 5 W when finished and 100 W or more while spinning.
- Result: Not run.
- Learned: this is the method most Home Assistant guides use, because power is cleaner than vibration. It costs money and the user asked to use what they have, so it is the second choice.

### Level 4: Reframe

#### 4.1 Do not detect: a timer from the program length. Not run

- Uses: main phone, the user taps start.
- Test for the user: time 3 runs of the usual program from start to the end click. If the spread is under 5 minutes, a phone timer set at start is the whole answer.
- Result: Not run.
- Learned: zero hardware. Weak point: load size and unbalanced loads change the run time on many machines, and the user has to remember to start it.

#### 4.2 Combine two weak signals: a hard spin, then stillness. Works on synthetic data

- Uses: old Android phone accelerometer.
- Test: same `tests/vibration_test.py`. Alert only when the last run of vibration (15 s or longer) had at least 1 minute above 0.2 g, then N minutes still. **Synthetic data.**
- Result:

  | Scenario | Quiet window | Correct | Early | Missed | Median / max delay |
  |---|---|---|---|---|---|
  | A: rinse spins weaker than final | 2 min | 100 | 0 | 0 | 1.8 / 2.1 min |
  | A | 6 min | 100 | 0 | 0 | 5.8 / 6.1 min |
  | B: rinse spins as hard as final | 2 min | 1 | 99 | 0 | 1.8 / 1.8 min |
  | B | 6 min | 100 | 0 | 0 | 5.8 / 6.0 min |

- Learned: "spin then still" beats "still" alone, but only if the quiet window is longer than the longest refill pause after a rinse spin. In my model that pause is 2 to 5 minutes, so 6 minutes works. On a real machine this one number has to come from a real recording. A first version used the single loudest window to spot a spin and gave 11 early alerts out of 100, because a footstep during a rinse spin pushed one window over the line. Counting a full minute of spin fixed it.

### Level 5: Build the missing piece

#### 5.1 Termux script on the old phone with ntfy push. Partly works

- Uses: old Android phone, main phone.
- Test: `tests/pipeline_test.py` writes 3 synthetic cycles (scenario B) in the pretty-printed JSON shape `termux-sensor` prints, pipes them into `phone_watch.py`, and catches the POST on a local HTTP server standing in for ntfy. Also tried one real POST to ntfy.sh. **Synthetic sensor data.**
- Result:
  - Pipeline: 3 of 3 cycles notified, 356 s, 355 s and 354 s after the real end. The server got `POST /test-topic`, title `Washing machine`, body `The washing machine has finished.` each time.
  - Real ntfy.sh POST: blocked by this sandbox's network proxy (`CONNECT tunnel failed, response 403`). Not a problem with ntfy, this machine cannot reach it. Must be tested on the phone.
  - The termux-sensor flags (`-s`, `-d`, `-n`) were checked against the termux-api-package source. The exact output shape was not, the termux wiki was blocked here. The parser accepts any JSON object holding a `values` list, so small changes in shape should not matter.
- Learned: the logic and the plumbing work together. The unknowns are all on the phone: real vibration levels, Termux staying alive, Wi-Fi.

#### 5.2 Pi with a vibration switch or accelerometer on the lid. Not run

- Uses: Raspberry Pi, plus an SW-420 vibration module (about 2 units) or an ADXL345 / MPU6050 board (about 3 to 5 units).
- Test for the user: wire the SW-420 output to GPIO17, run `python3 -c "import RPi.GPIO as g,time;g.setmode(g.BCM);g.setup(17,g.IN);[print(g.input(17)) or time.sleep(0.2) for _ in range(300)]"` during a spin and when still. If the counts differ clearly, port the logic from `phone_watch.py`.
- Result: Not run.
- Learned: a fixed sensor survives better than a phone sitting on a lid for years, and the Pi does not get killed by Android battery saving. Use it if the phone version works but is a nuisance.

#### 5.3 Pi with a USB microphone runs the beep detector. Not run

- Uses: Raspberry Pi, a USB microphone (part to buy if not in the drawer).
- Test for the user: `arecord -f S16_LE -r 8000 -d 60 beep.wav` across the end of a cycle, then load it with scipy and run `detect()` from `tests/beep_test.py` after setting `BEEP_HZ` to the peak frequency of the beep.
- Result: Not run.

## Lines not crossed

None of the approaches needed anything illegal or anyone else's account. One safety line: I did not suggest opening the washer or splitting its mains cable to clip a current sensor on one wire. The plug-in power meter (3.4) gets the same signal without touching mains wiring.

## ChatGPT rounds

Round 1 handoff written: `2026-10-01-washing-machine-done-chatgpt.md`. No answer yet. When it comes back, its ideas go into the ladder above and get tested.

## Next tests

All on the real machine, all not run:

1. **Record one real cycle** (most important, 1 run). On the old phone: `termux-sensor -s accelerometer -d 50 > wash.json` from before start to 20 minutes after the end, note the end time. Then on any computer, load it and run `detect()` from `tests/vibration_test.py` with `quiet_min` 2, 4, 6. Check: is the final spin above 0.2 g for over a minute, and what is the longest still gap between a rinse spin and the next tumble? Set `--quiet-min` to that gap plus 2 minutes.
2. **ntfy from the phone** (2 minutes). In Termux: `curl -d "test" ntfy.sh/<YOUR_TOPIC>`. Expected: the main phone shows "test" within a few seconds.
3. **Termux stays alive** (1 run). Start `phone_watch.py --verbose`, screen off, charging, wake lock on. After 90 minutes check the last log line is recent.
4. **Live run** (5 washes). Count correct, early, missed, and the delay. Target: 5 of 5 correct, under 8 minutes late.
5. If the machine beeps: one recording for 3.2 to learn the beep frequency.
6. Time 3 runs of the usual program for 4.1.
