"""Regression tests added by the tournament from upheld attacks and deciding inputs."""
import time, tracemalloc
from limiter import RateLimiter


def test_reg_distinguishing_input_no_overblock():
    """R2: input that knocked out the bucketed-window build (over-blocking)."""
    rl = RateLimiter({"p": (7, 1.0)})
    assert rl.allow("k", "p", 0.032036, 4).allowed
    assert rl.allow("k", "p", 0.041815, 1).allowed
    # At t=1.035956 the first request (cost 4) has expired, so 1 + 4 <= 7 must be allowed.
    assert rl.allow("k", "p", 1.035956, 4).allowed


def test_reg_memory_scales_with_usage_not_limit():
    """Memory: attack upheld against the ring-buffer build (800 MB at limit=100000)."""
    tracemalloc.start()
    rl = RateLimiter({"p": (100000, 60.0)})
    for k in range(1000):
        for i in range(10):
            rl.allow(f"k{k}", "p", i * 0.5, 1)
    cur, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert cur < 20_000_000


def test_reg_denied_calls_are_fast():
    """Robustness: attack upheld against the champion (O(n) scan under the global lock)."""
    rl = RateLimiter({"p": (100000, 60.0)})
    for i in range(100000):
        rl.allow("k", "p", i * 1e-4, 1)
    t = time.perf_counter()
    for _ in range(200):
        assert not rl.allow("k", "p", 10.0, 100000).allowed
    assert time.perf_counter() - t < 0.05
