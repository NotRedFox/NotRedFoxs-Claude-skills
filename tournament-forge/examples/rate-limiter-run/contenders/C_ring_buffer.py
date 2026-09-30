"""Sliding-window rate limiter using a per-key ring buffer of unit timestamps."""
import threading
from bisect import bisect_right
from dataclasses import dataclass

_EMPTY = float("-inf")


@dataclass
class Decision:
    allowed: bool
    remaining: int       # units still available right now after this call (>= 0)
    retry_after: float   # 0.0 if allowed; otherwise seconds until this same request would be allowed


class RateLimiter:
    def __init__(self, plans: dict[str, tuple[int, float]]):
        self._plans = dict(plans)
        self._state: dict[tuple[str, str], list] = {}  # (plan, key) -> [ring, head]
        self._lock = threading.Lock()

    def allow(self, key: str, plan: str, now: float, cost: int = 1) -> Decision:
        limit, window = self._plans[plan]  # KeyError for unknown plan
        if cost < 1 or cost > limit:
            raise ValueError(f"cost must be in [1, {limit}]")
        cutoff = now - window
        with self._lock:
            st = self._state.get((plan, key))
            if st is None:
                st = self._state[(plan, key)] = [[_EMPTY] * limit, 0]
            ring, head = st
            # Slots run oldest->newest starting at head, so times are non-decreasing:
            # the number of expired (free) slots is found by binary search.
            free = bisect_right(range(limit), cutoff,
                                key=lambda i: ring[(head + i) % limit])
            if free < cost:
                # The cost-th oldest slot must expire before we fit.
                oldest = ring[(head + cost - 1) % limit]
                return Decision(False, free, oldest + window - now)
            for i in range(cost):
                ring[(head + i) % limit] = now
            st[1] = (head + cost) % limit
            return Decision(True, free - cost, 0.0)
