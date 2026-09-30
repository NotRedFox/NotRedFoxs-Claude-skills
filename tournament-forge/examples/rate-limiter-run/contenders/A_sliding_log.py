"""Sliding-log rate limiter: per (plan, key) deque of admitted (timestamp, cost)."""
from collections import deque
from dataclasses import dataclass
from threading import Lock


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: float


class _Log:
    __slots__ = ("events", "used")

    def __init__(self):
        self.events = deque()  # (timestamp, cost) of admitted requests, oldest first
        self.used = 0          # running sum of costs in events


class RateLimiter:
    def __init__(self, plans: dict[str, tuple[int, float]]):
        self._plans = dict(plans)
        self._logs: dict[tuple[str, str], _Log] = {}
        self._lock = Lock()

    def allow(self, key: str, plan: str, now: float, cost: int = 1) -> Decision:
        limit, window = self._plans[plan]  # KeyError for unknown plan
        if cost < 1 or cost > limit:
            raise ValueError(f"cost must be in [1, {limit}], got {cost}")

        with self._lock:
            log = self._logs.get((plan, key))
            if log is None:
                log = self._logs[(plan, key)] = _Log()
            events = log.events

            # Evict entries outside the half-open window (now - window, now].
            cutoff = now - window
            while events and events[0][0] <= cutoff:
                log.used -= events.popleft()[1]

            if log.used + cost <= limit:
                events.append((now, cost))
                log.used += cost
                return Decision(True, limit - log.used, 0.0)

            # Denied: find the earliest expiry that frees enough capacity.
            need = log.used + cost - limit
            freed = 0
            retry = 0.0
            for t, c in events:
                freed += c
                if freed >= need:
                    retry = t + window - now
                    break
            return Decision(False, limit - log.used, retry)
