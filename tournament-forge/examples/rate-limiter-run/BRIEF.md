# Brief: per-key rate limiter (Python 3.11, stdlib only)

Build an in-memory rate limiter for a Python web API.

## Interface (every solution must provide exactly this, in a file `limiter.py`)

```python
from dataclasses import dataclass

@dataclass
class Decision:
    allowed: bool
    remaining: int       # units still available right now after this call (>= 0)
    retry_after: float   # 0.0 if allowed; otherwise seconds until this same request would be allowed

class RateLimiter:
    def __init__(self, plans: dict[str, tuple[int, float]]):
        """plans maps plan name -> (limit, window_seconds)."""
    def allow(self, key: str, plan: str, now: float, cost: int = 1) -> Decision:
        ...
```

## Rules
- R1 (HARD): For each key, the total cost of ALLOWED requests in ANY rolling time interval of length `window` (half-open (t - window, t]) must never exceed `limit`.
- R2 (HARD): A request must be allowed if allowing it would not break R1. No over-blocking.
- R3: Denied requests consume nothing.
- R4: `retry_after` must be exact to within 1e-6: calling again at `now + retry_after` with the same key and cost is allowed (assuming no other calls in between), and any earlier time is not.
- R5: Keys are independent. Different plans have independent limits.
- R6: `cost < 1` or `cost > limit` raises ValueError. Unknown plan raises KeyError.
- R7: `now` never decreases between calls (callers guarantee this).
- R8: Must be safe to call from multiple threads at once.
- R9: Performance: 200,000 calls spread over 1,000 keys must finish in under 2 seconds on a normal laptop.

## Out of scope
Persistence, distributed/multi-process limiting, async.

## Rubric (fixed now, weights sum to 100)
- Correctness vs R1 to R6: 40
- Robustness (threads, edge cases, R8): 20
- Memory and speed (R9, memory per key): 20
- Simplicity / readability: 20
