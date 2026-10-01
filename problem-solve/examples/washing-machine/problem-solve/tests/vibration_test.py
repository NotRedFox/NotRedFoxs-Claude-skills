"""Approach 3.1 test: phone on the washer, accelerometer decides when the cycle ends.

ALL DATA HERE IS SYNTHETIC. No real washer or phone was recorded.
The model of a cycle: fill (still), wash tumbling in bursts, soak pauses,
drain, rinse spins with refill pauses after them, final spin, then still.
Phone sensor noise and people walking past are added.

Two detectors are compared:
  naive:    done = no vibration for QUIET_MIN minutes after the cycle started.
  combined: done = no vibration for QUIET_MIN minutes AND the last active
            stretch was a high energy spin (two weak signals together).
"""
import numpy as np

FS = 20  # Hz, a normal Android SENSOR_DELAY_GAME rate is about 50, 20 is enough
G = 9.81


def synth_cycle(rng, mid_spin_g=0.15):
    segs = []  # (seconds, kind)
    segs.append((rng.uniform(60, 180), "still"))              # waiting before start
    segs.append((rng.uniform(120, 240), "fill"))
    wash = rng.uniform(15, 40) * 60
    t = 0
    while t < wash:
        on = rng.uniform(8, 15); off = rng.uniform(3, 8)
        segs.append((on, "tumble")); segs.append((off, "still")); t += on + off
        if rng.random() < 0.01:                              # soak pause
            p = rng.uniform(120, 600); segs.append((p, "still")); t += p
    for r in range(rng.integers(1, 4)):                       # rinses
        segs.append((rng.uniform(60, 120), "drain"))
        segs.append((rng.uniform(60, 240), "spin_mid"))
        segs.append((rng.uniform(120, 300), "fill"))          # quiet refill after a spin
        for _ in range(int(rng.uniform(20, 40))):
            segs.append((rng.uniform(8, 15), "tumble")); segs.append((rng.uniform(3, 8), "still"))
    segs.append((rng.uniform(60, 120), "drain"))
    segs.append((rng.uniform(300, 600), "spin_final"))
    end_t = sum(s for s, _ in segs)
    segs.append((rng.uniform(900, 1800), "still"))            # after the end
    sig = []
    for dur, kind in segs:
        n = int(dur * FS); tt = np.arange(n) / FS
        if kind == "tumble":
            x = 0.04 * G * np.sin(2 * np.pi * 0.8 * tt) + 0.02 * G * rng.standard_normal(n)
        elif kind == "spin_mid":
            x = mid_spin_g * G * rng.standard_normal(n)
        elif kind == "spin_final":
            x = 0.25 * G * rng.standard_normal(n)
        elif kind in ("drain", "fill"):
            x = 0.004 * G * rng.standard_normal(n)            # pump or valve hum, barely visible
        else:
            x = np.zeros(n)
        sig.append(x)
    x = np.concatenate(sig)
    x += 0.003 * G * rng.standard_normal(len(x))              # phone sensor noise
    for _ in range(rng.integers(0, 6)):                       # footsteps or a door slam
        i = rng.integers(0, len(x) - FS * 3)
        x[i:i + FS * 2] += 0.08 * G * rng.standard_normal(FS * 2)
    return x, end_t


def detect(x, quiet_min, need_spin, spin_level=0.20, spin_windows=12):
    """Return the alert time in seconds, or None.

    Works on 5 s windows. A burst shorter than 15 s (3 windows) is treated as
    noise: a footstep or a door, not the machine. A run counts as a spin when
    at least spin_windows windows (1 minute) in it are above spin_level.
    """
    win = FS * 5
    n = len(x) // win
    s = x[: n * win].reshape(n, win).std(axis=1) / G           # one value per 5 s
    active = s > 0.012
    started = False; active_total = 0
    quiet = 0; run_len = 0; run_spin = 0; last_run_spin = False
    for i in range(n):
        if active[i]:
            run_len += 1; run_spin += s[i] > spin_level
            active_total += 1
            if active_total >= 24:                             # 2 minutes of activity in total
                started = True
            continue
        if run_len:                                            # a run has ended
            if run_len >= 3:
                last_run_spin = run_spin >= spin_windows
                quiet = 0
            run_len = 0; run_spin = 0
        quiet += 1
        ok_spin = (not need_spin) or last_run_spin
        if started and quiet * 5 >= quiet_min * 60 and ok_spin:
            return i * 5
    return None


def run(cycles, title):
    print(title)
    print(f"{'detector':<22}{'correct':>8}{'early':>7}{'missed':>8}{'median delay min':>18}{'max delay min':>15}")
    for name, q, spin in [("naive quiet 3 min", 3, False), ("naive quiet 6 min", 6, False),
                          ("naive quiet 10 min", 10, False),
                          ("spin+quiet 2 min", 2, True), ("spin+quiet 6 min", 6, True)]:
        ok = early = miss = 0; delays = []
        for x, end in cycles:
            t = detect(x, q, spin)
            if t is None:
                miss += 1
            elif t < end:
                early += 1
            else:
                ok += 1; delays.append((t - end) / 60)
        med = np.median(delays) if delays else float("nan")
        mx = max(delays) if delays else float("nan")
        print(f"{name:<22}{ok:>8}{early:>7}{miss:>8}{med:>18.1f}{mx:>15.1f}")
    print()


def main():
    rng = np.random.default_rng(1)
    run([synth_cycle(rng) for _ in range(100)],
        "Scenario A: 100 SYNTHETIC cycles, rinse spins weaker than the final spin. Early = alert before the real end.")
    rng = np.random.default_rng(2)
    run([synth_cycle(rng, mid_spin_g=0.25) for _ in range(100)],
        "Scenario B: 100 SYNTHETIC cycles, rinse spins as hard as the final spin (harder case).")


if __name__ == "__main__":
    main()
