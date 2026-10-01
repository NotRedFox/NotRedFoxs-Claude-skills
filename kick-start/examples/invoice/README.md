# tinyinvoice

Small invoice helper for a freelance business.

## Usage

```python
from invoice import Invoice
inv = Invoice("Acme")
inv.add("Logo design", 450.00)
print(inv.summary())
```

<!-- kick-start:architecture:start -->
## Architecture

Last updated 2026-10-01.

tinyinvoice builds an invoice from line items, returns the amount due and can export it as CSV for Excel. All money is held as integer cents. Fractional steps (discount and 8.25% tax) use `Decimal` and round half up to the cent.

| Path | What it does | Uses |
|---|---|---|
| `invoice.py` | `Invoice` class: holds line items and a discount fraction. `breakdown` returns subtotal, discount, tax and total in cents. `total` and a one-line `summary` read from it. Sets `TAX_RATE`. | `money.py` |
| `invoice_csv.py` | `csv_rows` builds the rows (one per line item, then Subtotal, Discount, Tax, Total). `write_csv` writes them to a path as UTF-8 with a BOM, or to an open file. Prefixes descriptions that start with `=`, `+`, `-` or `@` with `'` so Excel does not run them as formulas. | `invoice.py`, `money.py`, `csv` |
| `money.py` | Converts dollars to cents (`to_cents`), rounds cents (`round_cents`), formats cents as `$12.34` (`fmt`) or `12.34` (`plain`). | `decimal` |
| `config.py` | Holds a payment key, a contact address and an export folder. Nothing imports it. | none |
| `test_invoice.py`, `test_money.py`, `test_invoice_csv.py` | pytest tests with hand-worked expected values. Run `python -m pytest`. | `invoice.py`, `money.py`, `invoice_csv.py` |
| `BUGS.md` | Bugs found, with lessons. | none |
| `kickstart/` | Per-conversation work logs. | none |

How a total is worked out:

1. `Invoice.add` stores `(description, unit_price, qty)` with the price in dollars.
2. `subtotal` converts each price with `to_cents` and multiplies by quantity. A fractional quantity crashes later steps (B6, open).
3. `breakdown` checks `discount_pct` is from 0 to 1, takes the rounded discount off the subtotal, then adds tax on the remainder, rounded half up.
4. `summary` formats the total with `fmt`, for example `Acme: $64.92`.
5. `csv_rows` writes each line as unit price, qty and `to_cents(price) * qty`, then the four `breakdown` amounts with `plain`. The discount is written as a negative number.
<!-- kick-start:architecture:end -->
