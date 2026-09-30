"""Per-key token-bucket rate limiter: O(1) memory per key, thread-safe."""
import threading
from dataclasses import dataclass


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: float


class RateLimiter:
    def __init__(self, plans: dict[str, tuple[int, float]]):
        self._plans = {p: (int(l), float(w), l / w) for p, (l, w) in plans.items()}
        self._buckets: dict[tuple[str, str], list[float]] = {}  # -> [tokens, last]
        self._lock = threading.Lock()

    def allow(self, key: str, plan: str, now: float, cost: int = 1) -> Decision:
        limit, _, rate = self._plans[plan]  # KeyError for unknown plan
        if cost < 1 or cost > limit:
            raise ValueError("cost must be in [1, limit]")
        with self._lock:
            b = self._buckets.get((plan, key))
            if b is None:
                b = self._buckets[(plan, key)] = [float(limit), now]
            tokens = min(float(limit), b[0] + (now - b[1]) * rate)
            b[1] = now
            if tokens >= cost:
                tokens -= cost
                b[0] = tokens
                return Decision(True, int(tokens + 1e-9), 0.0)
            b[0] = tokens
            return Decision(False, int(tokens + 1e-9), (cost - tokens) / rate)
