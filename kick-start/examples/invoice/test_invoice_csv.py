"""Tests for invoice_csv.py. Expected rows are worked out by hand at 8.25% tax."""

import csv
import io

import pytest

from invoice import Invoice
from invoice_csv import csv_rows, write_csv

HEADER = ["Description", "Unit price", "Qty", "Line total"]


def sample():
    inv = Invoice("Example Studio")
    inv.add("Logo design", 450.00, 1)
    inv.add("Business cards", 19.99, 3)
    inv.discount_pct = 0.10
    return inv


def test_rows_for_lines_then_totals():
    # 450.00 + 59.97 = 509.97. Discount 50.997 -> 51.00, leaves 458.97.
    # Tax 458.97 x 0.0825 = 37.865025 -> 37.87. Total 496.84.
    assert csv_rows(sample()) == [
        HEADER,
        ["Logo design", "450.00", "1", "450.00"],
        ["Business cards", "19.99", "3", "59.97"],
        ["Subtotal", "", "", "509.97"],
        ["Discount", "", "", "-51.00"],
        ["Tax", "", "", "37.87"],
        ["Total", "", "", "496.84"],
    ]


def test_csv_total_matches_invoice_total():
    assert csv_rows(sample())[-1][3] == "496.84"
    assert sample().total() == 49684


def test_float_prices_keep_their_cents():
    # B1: 19.99 and 0.29 must not lose a cent on the way to text.
    # 0.29 x 3 = 0.87. 0.87 + tax 0.071775 -> 0.07 = 0.94.
    inv = Invoice("X")
    inv.add("Clip", 0.29, 3)
    rows = csv_rows(inv)
    assert rows[1] == ["Clip", "0.29", "3", "0.87"]
    assert rows[-1] == ["Total", "", "", "0.94"]


def test_two_decimals_on_round_amounts():
    # B5: 64.90 must not become 64.9. 20.00 x 3 = 60.00, -0.05 credit,
    # 59.95 + tax 4.945875 -> 4.95 = 64.90.
    inv = Invoice("X")
    inv.add("Widget", 20.00, 3)
    inv.add("Credit", -0.05, 1)
    rows = csv_rows(inv)
    assert rows[1] == ["Widget", "20.00", "3", "60.00"]
    assert rows[2] == ["Credit", "-0.05", "1", "-0.05"]
    assert rows[-1] == ["Total", "", "", "64.90"]


def test_tax_rounds_half_cent_up():
    # B2: 2.00 x 0.0825 = 0.165 -> 0.17.
    inv = Invoice("X")
    inv.add("Item", 2.00)
    assert csv_rows(inv)[-2] == ["Tax", "", "", "0.17"]


def test_discount_taken_before_tax():
    # B3: 1.01 - 0.10 = 0.91, tax 0.075075 -> 0.08, total 0.99.
    inv = Invoice("X")
    inv.add("Item", 1.01)
    inv.discount_pct = 0.10
    assert csv_rows(inv)[-4:] == [
        ["Subtotal", "", "", "1.01"],
        ["Discount", "", "", "-0.10"],
        ["Tax", "", "", "0.08"],
        ["Total", "", "", "0.99"],
    ]


def test_empty_invoice_has_zero_totals():
    assert csv_rows(Invoice("X")) == [
        HEADER,
        ["Subtotal", "", "", "0.00"],
        ["Discount", "", "", "0.00"],
        ["Tax", "", "", "0.00"],
        ["Total", "", "", "0.00"],
    ]


def test_large_invoice():
    # 1000 x 99999.99 = 99999990.00, tax 8249999.175 -> 8249999.18.
    inv = Invoice("X")
    inv.add("Bulk", 99999.99, 1000)
    rows = csv_rows(inv)
    assert rows[1] == ["Bulk", "99999.99", "1000", "99999990.00"]
    assert rows[-1] == ["Total", "", "", "108249989.18"]


def test_bad_discount_is_rejected():
    # B4: 10 meant as 10% must not produce a file with a negative total.
    inv = sample()
    inv.discount_pct = 10
    with pytest.raises(ValueError):
        csv_rows(inv)


@pytest.mark.parametrize(
    "description, cell",
    [
        ("=HYPERLINK(\"x\")", "'=HYPERLINK(\"x\")"),
        ("+1 extra", "'+1 extra"),
        ("-5% promo", "'-5% promo"),
        ("@sum", "'@sum"),
        ("Plain text", "Plain text"),
    ],
)
def test_formula_like_descriptions_are_not_run_by_excel(description, cell):
    inv = Invoice("X")
    inv.add(description, 1.00)
    assert csv_rows(inv)[1][0] == cell


def test_written_file_opens_in_excel(tmp_path):
    inv = Invoice("X")
    inv.add('Café, "deluxe"\nset', 3.50, 2)  # 7.00 + 0.5775 -> 0.58 = 7.58
    path = tmp_path / "invoice.csv"
    write_csv(inv, path)
    raw = path.read_bytes()
    # Excel reads a CSV as the local code page unless it starts with a UTF-8 BOM.
    assert raw.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" in raw
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    assert rows[0] == HEADER
    assert rows[1] == ['Café, "deluxe"\nset', "3.50", "2", "7.00"]
    assert rows[-1] == ["Total", "", "", "7.58"]


def test_write_csv_accepts_open_file():
    buf = io.StringIO(newline="")
    write_csv(sample(), buf)
    assert buf.getvalue().splitlines()[-1] == "Total,,,496.84"


@pytest.mark.xfail(strict=True, raises=TypeError, reason="B6: fractional qty is not supported yet")
def test_fractional_quantity_row():
    # 85.00 x 1.5 = 127.50, tax 10.51875 -> 10.52, total 138.02
    inv = Invoice("X")
    inv.add("Hours", 85.00, 1.5)
    rows = csv_rows(inv)
    assert rows[1] == ["Hours", "85.00", "1.5", "127.50"]
    assert rows[-1] == ["Total", "", "", "138.02"]
