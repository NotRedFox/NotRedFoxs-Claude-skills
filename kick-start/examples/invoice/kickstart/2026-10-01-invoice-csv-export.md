# Invoice CSV export

Started 2026-10-01. Last updated 2026-10-01.

## Summary
- Goal: "add a way to export an invoice to CSV, one row per line item with description, unit price, qty and line total, then rows for subtotal, discount, tax and total. i want to open it in excel."
- Works now (checked): `invoice_csv.write_csv(invoice, path)` writes the rows asked for. A sample (450.00, 3 x 19.99, 2 x 3.50, 10% off) gives Total 503.65, the same as `summary()` and the hand calculation. Full suite: 42 passed, 2 xfailed.
- Still broken (checked): a fractional quantity such as 1.5 hours crashes the total and the export with `TypeError` (B6, open, was already there before this work).
- Believed but not checked: Excel opens the file with the right characters and reads the amounts as numbers. There is no Excel here. The file has a UTF-8 BOM, CRLF line ends and bare decimals like `19.99`, which is what Excel needs for that in a US or UK locale. In locales that use a comma for decimals Excel expects `;` between fields, so it would put each row in one column.

Read before starting: `BUGS.md` (B1 to B5, Patterns), README Architecture, `kickstart/2026-10-01-invoice-totals.md`. Bugs from this conversation: B6 in `BUGS.md`.

| Problem | Approaches tried | What ended up working |
|---|---|---|
| 1. CSV export | 1.1 `breakdown` on `Invoice` plus `invoice_csv.py` | 1.1 |
| 2. Fractional quantity crashes (B6) | none, logged as open | Not fixed |

## Problems and approaches

### Problem 1: CSV export

Hand calculation for the main test (8.25% tax, discount first, each step rounded half up): 450.00 + 3 x 19.99 = 509.97. Discount 10% = 50.997, rounds to 51.00, leaves 458.97. Tax 37.865025 rounds to 37.87. Total 496.84.

Choices made because nobody was there to ask (also under Open questions):
- Amounts are bare decimals with two places (`19.99`, not `$19.99`) so Excel reads them as numbers. New `money.plain` does this from integer cents with `divmod`, the same way as `fmt` (B5).
- The Discount row is negative (`-51.00`), since it is taken off.
- Labels sit in the Description column and amounts in the Line total column, with the two middle cells empty.
- Descriptions starting with `=`, `+`, `-`, `@`, tab or CR get a leading `'` so Excel does not run them as formulas.
- No customer name row, since the request did not list one.

#### Approach 1.1: `Invoice.breakdown` plus a new `invoice_csv.py`. Worked
- What was done: split `Invoice.total` into `breakdown` (returns subtotal, discount, tax and total in cents) and a `total` that reads from it. New `invoice_csv.py` with `csv_rows(invoice)` and `write_csv(invoice, target)`. A path is written with `utf-8-sig` (BOM) and `newline=""` so the `csv` module's CRLF line ends are kept. Rows are built before the file opens, so a bad discount leaves no file.
- Why it was chosen: the CSV needs the discount and tax amounts, which `total` worked out but did not return. Recomputing them in the exporter would make a second copy of the logic behind B2, B3 and B4 that could drift. `breakdown` keeps the range check (B4), discount before tax (B3) and half-up rounding (B2) in one place. Line totals use `to_cents` like `subtotal` (B1), so the lines add up to the Subtotal row.
- Evidence: `python3 -B -m pytest -q` gives `42 passed in 0.05s`. Sample file (`cat -A`):
  ```
  M-oM-;M-?Description,Unit price,Qty,Line total^M$
  Logo design,450.00,1,450.00^M$
  Business cards,19.99,3,59.97^M$
  "CafM-CM-), ""deluxe""",3.50,2,7.00^M$
  Subtotal,,,516.97^M$
  Discount,,,-51.70^M$
  Tax,,,38.38^M$
  Total,,,503.65^M$
  ```
  By hand: 516.97 less 51.697 (51.70) = 465.27, tax 38.384775 (38.38), total 503.65. `summary()` gives `Acme: $503.65`.
- Why it worked: every amount comes from integer cents and the same `breakdown` the summary uses.
- Kept or undone: Kept.

### Problem 2: Fractional quantity crashes the total (B6)

Found while testing wrong-type inputs for the export. `add("Hours", 85.00, 1.5)` gives `subtotal()` of `12750.0` and then `TypeError: unsupported operand type(s) for *: 'float' and 'decimal.Decimal'`. The same happens on the code from before this conversation (checked with `git stash`).

Not fixed. Rounding a fractional line per line or on the subtotal is a business rule, and the request was for an export. Strict xfail tests hold the expected result: 85.00 x 1.5 = 127.50, tax 10.51875 rounds to 10.52, total 138.02. A throwaway fix (round each line half up with `Decimal(str(qty))`) made both tests XPASS, so the expected values are reachable. The throwaway fix was removed.

## What worked
- `breakdown` as the single place that works out the steps of the total, with the exporter and `total` both reading from it (1.1).
- `money.plain` from integer cents for spreadsheet amounts (1.1).

## What didn't, do not retry
- Nothing failed in the code. One check went wrong: the first mutation for "tax before discount" (M4) was not a faithful tax-first version and did not trip `test_discount_taken_before_tax`. A direct tax-first rewrite (M4b) did. When proving a test, write the broken version the way someone would write it.

## Tests added
New file `test_invoice_csv.py`, plus one test in `test_invoice.py`. Each was checked by putting one broken line back, running the suite and restoring.

| Test | Protects against | Status |
|---|---|---|
| `test_rows_for_lines_then_totals` | Row layout, B2, B3 | Fails on float `plain` (M1), `int(price * 100)` lines (M2), truncated tax (M3), tax first (M4b), positive discount (M8). Passes now |
| `test_csv_total_matches_invoice_total` | CSV and invoice disagreeing | Fails on truncated tax (M3). Passes now |
| `test_float_prices_keep_their_cents` | B1 | Fails on `int(price * 100)` (M2). Passes now |
| `test_two_decimals_on_round_amounts` | B5, negative credit line | Fails on float `plain` (M1) and truncated tax (M3). Passes now |
| `test_tax_rounds_half_cent_up` | B2 | Fails on truncated tax (M3). Passes now |
| `test_discount_taken_before_tax` | B3 | Fails on tax first (M4b) and positive discount (M8). Passes now |
| `test_empty_invoice_has_zero_totals` | Empty input, `-0.00` | Fails on float `plain` (M1). Passes now |
| `test_large_invoice` | Large input | Fails on float `plain` (M1) and truncated tax (M3). Passes now |
| `test_bad_discount_is_rejected` | B4 | Fails without the range check (M5). Passes now |
| `test_formula_like_descriptions_are_not_run_by_excel` (5 cases) | Formula injection | 4 cases fail without the guard (M6). Passes now |
| `test_written_file_opens_in_excel` | BOM, CRLF, quoting of comma, quote, newline, non-ASCII | Fails without BOM (M7). Passes now |
| `test_write_csv_accepts_open_file` | Open file target | Fails when the file branch writes nothing (M9). Passes now |
| `test_invoice_csv.py::test_fractional_quantity_row` | B6 | xfail strict. XPASS(strict) with a throwaway fix |
| `test_invoice.py::test_fractional_quantity` | B6 | xfail strict. XPASS(strict) with a throwaway fix |

Latest run: `python3 -B -m pytest -q` gives `42 passed, 2 xfailed in 0.07s`.

## Next steps
- Decide the rounding rule for fractional quantities and fix B6.
- Open a real export in Excel once to confirm the BOM, number cells and the `'` prefix look right.

## Open questions
- Should the Discount row be negative (`-51.00`, chosen) or positive with the label saying it is taken off?
- Should the file start with a customer name or invoice number row? Left out, since the request listed only line and total rows.
- Is a `'` prefix the right guard for descriptions like `-5% promo`? Believed, not checked: Excel shows the `'` as part of the text when it opens a CSV. The other choice is a leading space.
- Is the file used in a locale where Excel expects `;` and decimal commas? If so, the delimiter and number format need an option.
- How should a fractional quantity round (B6): per line or on the subtotal?
- Where should exports go? `config.py` has `EXPORT_DIR`, but it is a home folder path (`~/`) on one machine and nothing imports it, so `write_csv` takes the path from the caller. The payment key in `config.py` is still committed (see the earlier log) and should be revoked.
