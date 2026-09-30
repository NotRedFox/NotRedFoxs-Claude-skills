from limiter import RateLimiter


def test_retry_after_lands_on_allowed_float_boundary():
    # R4: calling at now + retry_after must be allowed.
    rl = RateLimiter({"p": (1, 0.3)})
    assert rl.allow("k", "p", 4095.838).allowed
    d = rl.allow("k", "p", 4095.938)
    assert not d.allowed
    assert rl.allow("k", "p", 4095.938 + d.retry_after).allowed
