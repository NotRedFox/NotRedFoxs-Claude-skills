"""Run on the old Android phone in Termux, with the phone lying on the washer.

    pkg install python termux-api      (and install the Termux:API app)
    termux-sensor -s accelerometer -d 50 | python phone_watch.py --topic <YOUR_TOPIC>

Install the ntfy app on your main phone and subscribe to the same topic.
Pick a long random topic name, anyone who knows it can read it.

Logic (tested on synthetic data only, see tests/vibration_test.py):
5 s windows. A burst under 15 s is ignored (footsteps, doors). The cycle has
started after 2 minutes of vibration in total. The cycle is done when the
last long run of vibration contained at least 1 minute of hard spinning and
the machine has then been still for QUIET_MIN minutes.
"""
import argparse
import json
import math
import sys
import time
import urllib.request

ACTIVE = 0.012 * 9.81   # m/s2 std per window that counts as "moving"
SPIN = 0.20 * 9.81      # m/s2 std per window that counts as "spinning"


def readings(stream):
    """Yield (x, y, z) from termux-sensor's stream of pretty-printed JSON objects."""
    dec = json.JSONDecoder(); buf = ""
    for line in stream:
        buf += line
        while True:
            buf = buf.lstrip()
            if not buf:
                break
            try:
                obj, end = dec.raw_decode(buf)
            except json.JSONDecodeError:
                break
            buf = buf[end:]
            for v in obj.values():
                if isinstance(v, dict) and len(v.get("values", [])) >= 3:
                    yield tuple(v["values"][:3])


def notify(url, msg):
    req = urllib.request.Request(url, data=msg.encode(), method="POST",
                                 headers={"Title": "Washing machine", "Tags": "basket"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--server", default="https://ntfy.sh")
    ap.add_argument("--quiet-min", type=float, default=6)
    ap.add_argument("--fake-rate", type=float, default=0, help="test only: samples per second instead of the clock")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    url = f"{a.server.rstrip('/')}/{a.topic}"

    n = 0; win = []; win_start = None
    started = False; active_total = 0
    quiet = 0; run_len = 0; run_spin = 0; last_run_spin = False
    for xyz in readings(sys.stdin):
        now = n / a.fake_rate if a.fake_rate else time.time(); n += 1
        if win_start is None:
            win_start = now
        win.append(xyz)
        if now - win_start < 5:
            continue
        m = len(win)
        std = math.sqrt(sum(
            sum(p[k] ** 2 for p in win) / m - (sum(p[k] for p in win) / m) ** 2 for k in range(3)))
        win = []; win_start = now
        if a.verbose:
            print(f"t={now:.0f}s std={std / 9.81:.3f}g started={started} quiet={quiet * 5}s", file=sys.stderr)
        if std > ACTIVE:
            run_len += 1; run_spin += std > SPIN; active_total += 1
            started = started or active_total >= 24
            continue
        if run_len:
            if run_len >= 3:
                last_run_spin = run_spin >= 12; quiet = 0
            run_len = 0; run_spin = 0
        quiet += 1
        if started and last_run_spin and quiet * 5 >= a.quiet_min * 60:
            status = notify(url, "The washing machine has finished.")
            print(f"notified at t={now:.0f}s, HTTP {status}")
            started = False; active_total = 0; last_run_spin = False; quiet = 0


if __name__ == "__main__":
    main()
