import random
import threading
import time

import pytest

from limiter import Decision, RateLimiter

PLANS = {"small": (3, 10.0), "mid": (5, 10.0), "big": (100, 10.0)}


def make():
    return RateLimiter(dict(PLANS))


def test_happy_path():
    """Happy path: decisions carry allowed/remaining/retry_after and are Decision objects."""
    rl = make()
    ds = [rl.allow("k", "small", 0.0) for _ in range(3)]
    assert all(isinstance(d, Decision) for d in ds)
    assert [d.allowed for d in ds] == [True, True, True]
    assert [d.remaining for d in ds] == [2, 1, 0]
    assert all(d.retry_after == 0.0 for d in ds)
    d = rl.allow("k", "small", 1.0)
    assert d.allowed is False
    assert d.remaining == 0
    assert d.retry_after == pytest.approx(9.0, abs=1e-6)


def test_hard_r1_burst_at_window_edge():
    """R1: a burst right at the window edge; (t-window, t] is half-open so t=0 expires exactly at t=10."""
    rl = make()
    assert all(rl.allow("k", "small", 0.0).allowed for _ in range(3))
    assert not rl.allow("k", "small", 9.999).allowed  # still inside window
    ds = [rl.allow("k", "small", 10.0) for _ in range(4)]
    assert [d.allowed for d in ds] == [True, True, True, False]
    # Old burst at 0 and new burst at 10 must never be counted together.
    assert not rl.allow("k", "small", 19.999).allowed
    assert rl.allow("k", "small", 20.0).allowed


def test_hard_r1_spread_across_boundary():
    """R1: requests spread across a window boundary; every sliding window (not fixed buckets) is bounded."""
    rl = RateLimiter({"p": (4, 10.0)})
    assert rl.allow("k", "p", 0.0, 2).allowed
    assert rl.allow("k", "p", 5.0, 2).allowed
    assert not rl.allow("k", "p", 9.0, 1).allowed
    assert rl.allow("k", "p", 10.0, 2).allowed  # t=0 expired, t=5 still counts
    assert not rl.allow("k", "p", 10.0, 1).allowed  # (0,10] holds 2+2
    assert not rl.allow("k", "p", 14.99, 1).allowed  # 5 and 10 both in window
    assert rl.allow("k", "p", 15.0, 2).allowed  # 5 expires exactly now
    assert not rl.allow("k", "p", 19.0, 1).allowed  # 10 and 15 in window


def test_hard_r2_no_over_blocking():
    """R2: a request that fits must be allowed (exact fill, partial expiry, mixed costs)."""
    rl = make()
    d = rl.allow("a", "mid", 0.0, 5)  # exactly the limit
    assert d.allowed and d.remaining == 0
    assert rl.allow("a", "mid", 10.0, 5).allowed  # fully expired
    rl2 = make()
    assert rl2.allow("k", "mid", 0.0, 4).allowed
    assert rl2.allow("k", "mid", 6.0, 1).allowed
    d = rl2.allow("k", "mid", 10.0, 4)  # only the cost-1 at t=6 remains
    assert d.allowed and d.remaining == 0
    rl3 = make()
    assert rl3.allow("k", "mid", 0.0, 2).allowed
    assert rl3.allow("k", "mid", 1.0, 3).allowed
    assert not rl3.allow("k", "mid", 2.0, 1).allowed
    assert rl3.allow("k", "mid", 10.0, 2).allowed  # t=0 gone, 2 units free


def test_r3_denied_consumes_nothing():
    """R3: denied requests consume nothing (no capacity used, no window extension)."""
    rl = make()
    assert rl.allow("k", "mid", 0.0, 3).allowed
    for t in (1.0, 1.0, 2.0, 3.0):
        d = rl.allow("k", "mid", t, 3)
        assert not d.allowed and d.remaining == 2
    assert rl.allow("k", "mid", 3.0, 2).allowed  # would fail if denials consumed
    assert rl.allow("k", "mid", 10.0, 3).allowed  # denials did not delay recovery


def test_r4_retry_after_exact():
    """R4: retry_after exact to 1e-6: allowed at now+retry_after, denied 1e-3 earlier."""
    cases = []
    for cost, at in ((3, 7.0), (2, 7.0), (5, 7.0), (1, 6.5)):
        rl = make()
        assert rl.allow("k", "mid", 0.0, 2).allowed
        assert rl.allow("k", "mid", 3.0, 2).allowed
        assert rl.allow("k", "mid", 6.0, 1).allowed
        d = rl.allow("k", "mid", at, cost)
        assert not d.allowed and d.retry_after > 0
        cases.append((cost, at, d.retry_after))
        assert not rl.allow("k", "mid", at + d.retry_after - 1e-3, cost).allowed
        assert rl.allow("k", "mid", at + d.retry_after + 1e-7, cost).allowed
    # Hand-computed: cost 3 needs t=13 (used 1 after), cost 2 needs t=10, cost 5 needs t=16.
    got = {c: r for c, a, r in cases if a == 7.0}
    assert got[3] == pytest.approx(6.0, abs=1e-6)
    assert got[2] == pytest.approx(3.0, abs=1e-6)
    assert got[5] == pytest.approx(9.0, abs=1e-6)


def test_r5_keys_and_plans_independent():
    """R5: different keys and different plans never share capacity."""
    rl = make()
    assert all(rl.allow("a", "small", 0.0).allowed for _ in range(3))
    assert not rl.allow("a", "small", 0.0).allowed
    assert rl.allow("b", "small", 0.0).allowed  # other key unaffected
    assert rl.allow("a", "mid", 0.0, 5).allowed  # same key, other plan unaffected
    assert not rl.allow("a", "small", 0.0).allowed


def test_r6_validation():
    """R6: cost < 1 or > limit raises ValueError; unknown plan raises KeyError; rejects consume nothing."""
    rl = make()
    for bad in (0, -1, 4):
        with pytest.raises(ValueError):
            rl.allow("k", "small", 0.0, bad)
    with pytest.raises(KeyError):
        rl.allow("k", "nope", 0.0)
    assert rl.allow("k", "small", 0.0, 3).allowed  # limit-sized cost is valid, state untouched


def test_r8_threads_single_key_fixed_now():
    """R8: 8 threads on one key at one fixed now; total allowed cost equals limit exactly."""
    rl = make()
    barrier = threading.Barrier(8)
    totals = [0] * 8
    errors = []

    def work(i):
        try:
            barrier.wait()
            for _ in range(200):
                d = rl.allow("hot", "big", 50.0, 1)
                if d.allowed:
                    totals[i] += 1
        except Exception as e:  # pragma: no cover
            errors.append(e)

    ts = [threading.Thread(target=work, args=(i,)) for i in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert not errors
    assert sum(totals) == 100  # 1600 attempts, limit 100
    assert not rl.allow("hot", "big", 50.0).allowed


def test_r9_performance():
    """R9: 200,000 calls over 1,000 keys finish in under 2.0 seconds."""
    rl = make()
    keys = [f"key{i}" for i in range(1000)]
    n = 200_000
    start = time.perf_counter()
    for i in range(n):
        rl.allow(keys[i % 1000], "big", i * 0.01)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"took {elapsed:.2f}s"


def test_hard_property_r1_r2_bruteforce():
    """R1+R2: seeded random costs/times; brute-force check of every decision against full history."""
    rng = random.Random(20240607)
    limit, window = 10, 8.0
    rl = RateLimiter({"p": (limit, window)})
    steps = [0.0, 0.0, 0.25, 0.5, 1.0, 2.0, 3.5, 8.0]  # exact in binary floats
    hist = {"a": [], "b": []}  # (t, cost, allowed)
    t = 0.0
    for _ in range(3000):
        t += rng.choice(steps)
        key = rng.choice("ab")
        cost = rng.choice([1, 1, 1, 2, 3, 5, 7, 10])
        d = rl.allow(key, "p", t, cost)
        h = hist[key]
        used = sum(c for (ts, c, ok) in h if ok and ts > t - window)
        fits = used + cost <= limit
        assert d.allowed == fits, f"R2/R1 violated at t={t} key={key} cost={cost} used={used}"
        assert d.remaining >= 0
        if d.allowed:
            assert d.retry_after == 0.0
            assert d.remaining == limit - used - cost
        else:
            assert d.retry_after > 0
        h.append((t, cost, d.allowed))
    # Independent final R1 sweep over all windows ending at any allowed event.
    for h in hist.values():
        ev = [(ts, c) for ts, c, ok in h if ok]
        for te, _ in ev:
            assert sum(c for ts, c in ev if te - window < ts <= te) <= limit
