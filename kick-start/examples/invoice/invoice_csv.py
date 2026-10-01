"""Export an invoice as CSV that Excel opens with the right characters and numbers."""

import csv

from money import plain, to_cents

HEADER = ["Description", "Unit price", "Qty", "Line total"]

# Excel treats a cell starting with one of these as a formula, so a line
# description could run code or change the sheet when the file is opened.
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def _safe_text(text):
    text = str(text)
    if text.startswith(_FORMULA_START):
        return "'" + text
    return text


def csv_rows(invoice):
    """Build the CSV rows for an invoice.

    One row per line item, then Subtotal, Discount, Tax and Total. Amounts
    are bare decimals with two places. The discount is negative because it
    is taken off.

    Args:
        invoice: An ``Invoice``.

    Returns:
        list[list[str]]: The rows, starting with the header row.

    Raises:
        ValueError: If the invoice's ``discount_pct`` is outside 0 to 1.
    """
    steps = invoice.breakdown()
    rows = [list(HEADER)]
    for description, unit_price, qty in invoice.lines:
        # Same conversion as Invoice.subtotal, so the lines add up to it.
        unit = to_cents(unit_price)
        rows.append([_safe_text(description), plain(unit), str(qty), plain(unit * qty)])
    rows.append(["Subtotal", "", "", plain(steps["subtotal"])])
    rows.append(["Discount", "", "", plain(-steps["discount"])])
    rows.append(["Tax", "", "", plain(steps["tax"])])
    rows.append(["Total", "", "", plain(steps["total"])])
    return rows


def write_csv(invoice, target):
    """Write an invoice as CSV.

    Args:
        invoice: An ``Invoice``.
        target: A file path, or a text file opened with ``newline=""``.
            A path is written as UTF-8 with a byte order mark, which Excel
            needs to show characters like "é" correctly.

    Raises:
        ValueError: If the invoice's ``discount_pct`` is outside 0 to 1.
            Nothing is written in that case.
    """
    # Build the rows before opening the file so a bad discount leaves no
    # half-written file behind.
    rows = csv_rows(invoice)
    if hasattr(target, "write"):
        csv.writer(target).writerows(rows)
        return
    with open(target, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
