"""Forged rate limiter.

Champion: sliding log (exact, memory proportional to real usage).
Graft from ring buffer: sorted arrays + binary search, so denied calls are O(log n), not O(n).
Graft from bucketed window: bounded memory over time, via idle-key sweeping.
"""
import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from threading import Lock

_SWEEP_EVERY = 4096


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: float


class _Log:
    __slots__ = ("ts", "cum", "head")

    def __init__(self):
        self.ts: list[float] = []   # admit times, non-decreasing
        self.cum: list[int] = []    # cum[i] = total cost admitted up to and including i
        self.head = 0               # index of the oldest live entry

    def base(self) -> int:
        return self.cum[self.head - 1] if self.head else 0

    def used(self) -> int:
        return (self.cum[-1] - self.base()) if self.cum else 0

    def evict(self, cutoff: float) -> None:
        self.head = bisect_right(self.ts, cutoff, self.head)
        if self.head > 64 and self.head * 2 > len(self.ts):   # amortised compaction
            b = self.base()
            self.ts = self.ts[self.head:]
            self.cum = [c - b for c in self.cum[self.head:]]
            self.head = 0


class RateLimiter:
    def __init__(self, plans: dict[str, tuple[int, float]]):
        self._plans = dict(plans)
        self._logs: dict[tuple[str, str], _Log] = {}
        self._lock = Lock()
        self._calls = 0

    def allow(self, key: str, plan: str, now: float, cost: int = 1) -> Decision:
        limit, window = self._plans[plan]  # KeyError for unknown plan (R6)
        if cost < 1 or cost > limit:
            raise ValueError(f"cost must be in [1, {limit}], got {cost}")

        with self._lock:
            self._calls += 1
            if self._calls % _SWEEP_EVERY == 0:
                self._sweep(now)

            log = self._logs.get((plan, key))
            if log is None:
                log = self._logs[(plan, key)] = _Log()
            log.evict(now - window)                      # window is (now - window, now]
            used = log.used()

            if used + cost <= limit:                     # R1 + R2: exact
                total = (log.cum[-1] if log.cum else 0) + cost
                log.ts.append(now)
                log.cum.append(total)
                return Decision(True, limit - used - cost, 0.0)

            # Denied (R3: no state change). Earliest entry whose expiry frees enough room, O(log n).
            need = used + cost - limit
            j = bisect_left(log.cum, log.base() + need, log.head)
            t_free = log.ts[j]
            retry = t_free + window - now
            # R4: float rounding can land one ulp short of the eviction cutoff; nudge up until
            # a call at exactly now + retry really evicts that entry. (Found by the red-team.)
            while (now + retry) - window < t_free:
                retry = math.nextafter(retry, math.inf)
            return Decision(False, limit - used, retry)

    def _sweep(self, now: float) -> None:
        """Drop keys with no live entries so idle keys don't hold memory forever."""
        dead = [k for k, lg in self._logs.items()
                if not lg.ts or lg.ts[-1] <= now - self._plans[k[0]][1]]
        for k in dead:
            del self._logs[k]
