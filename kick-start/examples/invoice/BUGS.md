# Bugs

Read this before changing code. Each entry is a bug that was found and fixed, and what to do differently.

## Patterns
- Money must never pass through a float or `int()`. Keep it as integer cents, do any fractional maths in `Decimal`, and round half up to the cent at each step that a person would round on paper. A float quantity also counts: it turns the cents into a float. (B1, B2, B5, B6)

## Bugs

### B6: Fractional quantity crashes the total
- Found: 2026-10-01, while testing edge cases for the CSV export.
- Where: `invoice.py`, `Invoice.subtotal` (crash shows in `Invoice.breakdown`, `total`, `summary` and `invoice_csv.csv_rows`)
- Symptom: `add("Hours", 85.00, 1.5)` makes `subtotal()` return `12750.0` (a float). `total()` then raises `TypeError: unsupported operand type(s) for *: 'float' and 'decimal.Decimal'`. Same on the code before this conversation.
- Cause (checked): `to_cents(price) * qty` with a float `qty` gives a float, and float times `Decimal` is not allowed.
- Fix: none yet. How to round a fractional line (per line or on the subtotal) is a business rule that has not been decided.
- Test: `test_invoice.py::test_fractional_quantity`, `test_invoice_csv.py::test_fractional_quantity_row` (both `xfail(strict=True)`)
- Lesson: check the type of every input that is multiplied into money, quantities as well as prices.
- Status: Open
- Log: kickstart/2026-10-01-invoice-csv-export.md, problem 2

### B5: Summary drops the trailing zero
- Found: 2026-10-01, customer report in notes.txt: summary showed `$64.9` instead of `$64.90`.
- Where: `money.py`, `fmt`
- Symptom: `fmt(6490)` returned `$64.9`. `fmt(0)` returned `$0.0`.
- Cause (checked): `str(cents / 100)` prints the float's shortest form, which has no fixed number of decimals.
- Fix: split cents with `divmod` and pad the remainder to two digits.
- Test: `test_money.py::test_fmt_always_two_decimals`, `test_invoice.py::test_summary_two_decimals`
- Lesson: format money from integer cents, never from a float.
- Status: Fixed
- Log: kickstart/2026-10-01-invoice-totals.md, approach 3.1

### B4: Discount of 10 gives a negative total
- Found: 2026-10-01, while reproducing the Hollis & Co complaint.
- Where: `invoice.py`, `Invoice.total`
- Symptom: 200.00 with `discount_pct = 10` gave `-194850` cents, with no error.
- Cause (checked): `discount_pct` is a fraction (0.10 for 10%) but nothing enforced it, and the name reads like a percent.
- Fix: `total` raises `ValueError` if `discount_pct` is outside 0 to 1.
- Test: `test_invoice.py::test_discount_outside_fraction_range_is_rejected`
- Lesson: check the range of any rate or percentage at the point it is used.
- Status: Fixed
- Log: kickstart/2026-10-01-invoice-totals.md, approach 2.2

### B3: Discount applied after tax
- Found: 2026-10-01, customer report in notes.txt (Hollis & Co): total lower than the spreadsheet, which does discount first, then tax.
- Where: `invoice.py`, `Invoice.total`
- Symptom: $1.01 at 10% off came to 98 cents taxing first (rounded), where discount first gives 99 cents. The exact Hollis invoice (200.00, 10%) did not reproduce: it gave 194.85 on the old code.
- Cause (checked for the $1.01 case): tax was charged on the full subtotal and the discount taken off the taxed amount. With rounding between steps, the order changes the result in 33114 of the subtotals from 1.00 to 999.99. Which input Hollis & Co hit is not confirmed.
- Fix: take the rounded discount off the subtotal, then charge tax on the remainder.
- Test: `test_invoice.py::test_discount_applied_before_tax_rounding`, `test_invoice.py::test_hollis_discount_before_tax`
- Lesson: when a business rule names an order of steps, follow it in code, even when the maths looks commutative.
- Status: Fixed
- Log: kickstart/2026-10-01-invoice-totals.md, approach 2.1

### B2: Tax truncated instead of rounded
- Found: 2026-10-01, customer report in notes.txt (Acme): $64.91 shown, $64.92 expected.
- Where: `invoice.py`, `Invoice.total`
- Symptom: 3 x 19.99 with correct line prices gave 6491 cents. 5997 x 1.0825 = 6491.7525, which should round to 6492.
- Cause (checked): `int()` on the taxed amount drops the fraction.
- Fix: round discount and tax half up with `money.round_cents` (Decimal).
- Test: `test_invoice.py::test_acme_three_items_at_19_99`, `test_invoice.py::test_tax_rounds_half_cent_up`
- Lesson: round money, never truncate it.
- Status: Fixed
- Log: kickstart/2026-10-01-invoice-totals.md, approach 1.2

### B1: Prices lose a cent when converted to cents
- Found: 2026-10-01, while reproducing the Acme complaint.
- Where: `money.py`, `to_cents`
- Symptom: `to_cents(19.99)` returned 1998. `to_cents(0.29)` returned 28. The Acme invoice came to $64.88 on the committed code.
- Cause (checked): 19.99 as a float is 19.98999..., and `int(amount * 100)` truncates.
- Fix: convert through `Decimal(str(amount))` and round half up.
- Test: `test_money.py::test_to_cents_keeps_written_value`, `test_invoice.py::test_acme_three_items_at_19_99`
- Lesson: never multiply a float price and truncate. Parse through `str` into `Decimal`.
- Status: Fixed
- Log: kickstart/2026-10-01-invoice-totals.md, approach 1.1
