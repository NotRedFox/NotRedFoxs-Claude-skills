"""Tests for money.py. Expected values are worked out by hand."""

from decimal import InvalidOperation

import pytest

from money import fmt, to_cents


@pytest.mark.parametrize(
    "amount, cents",
    [
        (19.99, 1999),  # B1: float 19.99 is 19.98999...
        (0.29, 29),
        (1.15, 115),
        (450.00, 45000),
        ("19.99", 1999),
        (0, 0),
        (0.005, 1),  # half a cent rounds up
    ],
)
def test_to_cents_keeps_written_value(amount, cents):
    assert to_cents(amount) == cents


def test_to_cents_rejects_text():
    with pytest.raises(InvalidOperation):
        to_cents("abc")


@pytest.mark.parametrize(
    "cents, text",
    [
        (6490, "$64.90"),  # B5
        (100, "$1.00"),
        (5, "$0.05"),
        (0, "$0.00"),
        (-5, "-$0.05"),
        (123456789, "$1234567.89"),
    ],
)
def test_fmt_always_two_decimals(cents, text):
    assert fmt(cents) == text
