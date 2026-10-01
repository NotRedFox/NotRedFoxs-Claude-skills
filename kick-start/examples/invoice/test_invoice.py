"""Tests for invoice.py. Expected totals are worked out by hand at 8.25% tax."""

import pytest

from invoice import Invoice


def make(*lines, discount=0):
    inv = Invoice("Test Customer")
    for price, qty in lines:
        inv.add("item", price, qty)
    inv.discount_pct = discount
    return inv


def test_acme_three_items_at_19_99():
    # B1, B2: 59.97 + tax 4.947525 -> 4.95 = 64.92
    inv = make((19.99, 3))
    assert inv.subtotal() == 5997
    assert inv.total() == 6492


def test_tax_rounds_half_cent_up():
    # B2: 2.00 x 0.0825 = 0.165 -> 0.17
    assert make((2.00, 1)).total() == 217


def test_hollis_discount_before_tax():
    # 200.00 - 20.00 = 180.00, tax 14.85, total 194.85
    assert make((200.00, 1), discount=0.10).total() == 19485


def test_discount_applied_before_tax_rounding():
    # B3: 1.01 - 0.10 = 0.91, tax 0.075075 -> 0.08, total 0.99.
    # Taxing first gives 1.09 - 0.11 = 0.98.
    assert make((1.01, 1), discount=0.10).total() == 99


def test_full_discount_is_zero():
    assert make((50.00, 2), discount=1).total() == 0


def test_empty_invoice_is_zero():
    inv = make()
    assert inv.total() == 0
    assert inv.summary() == "Test Customer: $0.00"


def test_large_invoice():
    # 1000 x 99999.99 = 9999999000 cents, tax 824999917.5 -> 824999918
    assert make((99999.99, 1000)).total() == 10824998918


@pytest.mark.parametrize("bad", [10, -0.1, 1.5])
def test_discount_outside_fraction_range_is_rejected(bad):
    # B4: 10 used to give -194850
    with pytest.raises(ValueError):
        make((200.00, 1), discount=bad).total()


def test_summary_two_decimals():
    # B5: 64.90 printed as $64.9
    inv = Invoice("Acme")
    inv.add("Widget", 20.00, 3)  # 60.00 + 4.95 = 64.95
    inv.add("Credit", -0.05, 1)  # 59.95 + 4.945875 -> 4.95 = 64.90
    assert inv.summary() == "Acme: $64.90"


def test_summary_keeps_non_ascii_customer_name():
    inv = Invoice("Café & Söhne")
    inv.add("Item", 1.00)  # 1.00 + 0.0825 -> 0.08 = 1.08
    assert inv.summary() == "Café & Söhne: $1.08"


@pytest.mark.xfail(strict=True, raises=TypeError, reason="B6: fractional qty is not supported yet")
def test_fractional_quantity():
    # 85.00 x 1.5 = 127.50, tax 10.51875 -> 10.52, total 138.02
    inv = make((85.00, 1.5))
    assert inv.subtotal() == 12750
    assert inv.total() == 13802
