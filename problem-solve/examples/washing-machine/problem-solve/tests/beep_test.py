"""Approach 3.2 test: the phone or Pi listens for the machine's end-of-cycle beep.

ALL AUDIO HERE IS SYNTHETIC. No real washer was recorded.
Each trial is 3 minutes of audio at 8 kHz: machine and room noise, TV-like
speech bursts, a microwave beeping at 2.0 kHz (distractor), and in half the
trials the washer's end beep: 3 tones of 0.5 s at 3.2 kHz, 0.5 s apart.

Detector: per 32 ms frame, energy in a narrow band at the learned beep
frequency divided by energy in the whole 300-3800 Hz band. A beep is a run of
loud frames 0.25 to 1.2 s long. Alert when 3 beeps start within 6 s.
"""
import numpy as np
from scipy import signal

FS = 8000
BEEP_HZ = 3200.0
FRAME = 256  # 32 ms


def tone(f, dur, amp, rng):
    t = np.arange(int(dur * FS)) / FS
    env = np.minimum(1, np.minimum(t, dur - t) / 0.01)        # 10 ms fade in and out
    return amp * env * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))


def synth(rng, with_beep, snr_db):
    n = FS * 180
    b, a = signal.butter(2, [60 / (FS / 2), 1500 / (FS / 2)], "band")
    x = signal.lfilter(b, a, rng.standard_normal(n)) * 1.0           # machine and room noise
    b2, a2 = signal.butter(4, [300 / (FS / 2), 3400 / (FS / 2)], "band")
    for _ in range(20):                                                # TV or talking
        i = rng.integers(0, n - FS * 3); L = int(rng.uniform(0.5, 3) * FS)
        x[i:i + L] += signal.lfilter(b2, a2, rng.standard_normal(L)) * rng.uniform(0.5, 2)
    if rng.random() < 0.5:                                             # microwave beeps
        i = rng.integers(0, n - FS * 5)
        for k in range(3):
            seg = tone(2000, 0.4, 1.0, rng); j = i + k * FS
            x[j:j + len(seg)] += seg
    noise_rms = np.sqrt(np.mean(x ** 2))
    amp = noise_rms * 10 ** (snr_db / 20) * np.sqrt(2)
    t_beep = None
    if with_beep:
        i = rng.integers(FS * 10, n - FS * 10); t_beep = i / FS
        for k in range(3):
            seg = tone(BEEP_HZ * rng.uniform(0.99, 1.01), 0.5, amp, rng); j = i + k * FS
            x[j:j + len(seg)] += seg
    return x, t_beep


def detect(x, f0=BEEP_HZ, ratio=0.10):
    n = len(x) // FRAME
    fr = x[: n * FRAME].reshape(n, FRAME) * np.hanning(FRAME)
    spec = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    freqs = np.fft.rfftfreq(FRAME, 1 / FS)
    band = (freqs > f0 - 60) & (freqs < f0 + 60)
    wide = (freqs > 300) & (freqs < 3800)
    r = spec[:, band].sum(1) / (spec[:, wide].sum(1) + 1e-12)
    on = r > ratio
    starts = []; i = 0; fdur = FRAME / FS
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            if 0.25 <= (j - i) * fdur <= 1.2:
                starts.append(i * fdur)
            i = j
        else:
            i += 1
    for k in range(len(starts) - 2):
        if starts[k + 2] - starts[k] <= 6:
            return starts[k]
    return None


def main():
    rng = np.random.default_rng(7)
    print("40 SYNTHETIC 3-minute clips per row, 20 with the end beep and 20 without.")
    print(f"{'beep SNR dB':>12}{'found':>8}{'missed':>8}{'false alerts':>14}")
    for snr in [10, 0, -5, -10, -15]:
        found = miss = false = 0
        for k in range(40):
            wb = k % 2 == 0
            x, tb = synth(rng, wb, snr)
            t = detect(x)
            if wb:
                if t is not None and abs(t - tb) < 1.5:
                    found += 1
                else:
                    miss += 1
                    if t is not None:
                        false += 1
            elif t is not None:
                false += 1
        print(f"{snr:>12}{found:>5}/20{miss:>8}{false:>11}/40")


if __name__ == "__main__":
    main()
