"""Per-key rate limiter: bucketed sliding window (bounded memory per key)."""
import threading
from collections import deque
from dataclasses import dataclass

BUCKETS = 64  # sub-buckets per window -> at most BUCKETS + 1 entries per key


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: float


class _State:
    __slots__ = ("entries", "used")

    def __init__(self):
        self.entries = deque()  # [bucket_id, newest_ts, cost]; oldest first
        self.used = 0


class RateLimiter:
    """Costs are aggregated per window/64 bucket. A bucket expires when its
    NEWEST event expires, so R1 always holds; events at distinct times inside
    one bucket may be over-blocked by up to window/64 (identical timestamps
    and gaps wider than a bucket are exact)."""

    def __init__(self, plans):
        self._plans = dict(plans)
        self._states = {}
        self._lock = threading.Lock()

    def allow(self, key, plan, now, cost=1):
        limit, window = self._plans[plan]  # KeyError for unknown plan
        if cost < 1 or cost > limit:
            raise ValueError("cost must be in [1, limit]")
        width = window / BUCKETS
        with self._lock:
            st = self._states.get((plan, key))
            if st is None:
                st = self._states[(plan, key)] = _State()
            entries = st.entries
            while entries and entries[0][1] + window <= now:
                st.used -= entries.popleft()[2]
            if st.used + cost <= limit:
                bid = int(now // width)
                if entries and entries[-1][0] == bid:
                    entries[-1][1] = now
                    entries[-1][2] += cost
                else:
                    entries.append([bid, now, cost])
                st.used += cost
                return Decision(True, limit - st.used, 0.0)
            need = st.used + cost - limit  # units that must expire
            freed = 0
            for _, ts, c in entries:
                freed += c
                if freed >= need:
                    return Decision(False, limit - st.used, ts + window - now)
            raise AssertionError("unreachable")
