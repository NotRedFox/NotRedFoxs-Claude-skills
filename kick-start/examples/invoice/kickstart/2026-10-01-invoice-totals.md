# Invoice totals

Started 2026-10-01. Last updated 2026-10-01.

## Summary
- Goal: "customers are complaining about invoice totals, see notes.txt. sort it out."
- Works now (checked): Acme (3 x 19.99) totals $64.92. Hollis & Co (200.00, 10% off) totals $194.85 with discount before tax. Summaries print two decimals (`$64.90`). Full suite: 26 passed.
- Still broken (checked): nothing known.
- Believed but not checked: the Hollis & Co invoice that was complained about had a subtotal where rounding order matters, or a discount entered as 10. The exact invoice is not in notes.txt, so this could not be confirmed.

Bugs from this conversation: B1 to B5 in `BUGS.md`.

| Problem | Approaches tried | What ended up working |
|---|---|---|
| 1. Totals off by cents | 1.1 Decimal `to_cents` (partly), 1.2 round each step half up | 1.1 and 1.2 together (B1, B2) |
| 2. Discount order | 2.1 discount before tax, 2.2 range check on discount | Both (B3, B4) |
| 3. Money formatting | 3.1 format from integer cents | 3.1 (B5) |

## Problems and approaches

Reproduction before any change (`python3 -B -c ...` against the committed code):

```
acme 5994 6488 Acme: $64.88
hollis frac 19485 H: $194.85
hollis 10 -194850
to_cents(19.99)=1998  to_cents(0.29)=28  to_cents(1.15)=114  fmt(6490)='$64.9'
```

notes.txt says Acme saw $64.91. The committed code gives $64.88. Both are wrong, since the hand calculation gives $64.92. Approach 1.1 shows that $64.91 is what you get with correct line prices and truncated tax. Why the customer's invoice had correct line prices is not confirmed (guess: the price was entered as a string or a different version of the code was used).

### Problem 1: Totals off by cents

Hand calculation for Acme: 3 x 19.99 = 59.97. Tax 59.97 x 0.0825 = 4.947525, rounds to 4.95. Total 64.92.

#### Approach 1.1: Exact cents conversion with Decimal. Partly worked
- What was done: `money.to_cents` now converts through `Decimal(str(amount))` and rounds half up, in place of `int(amount * 100)`.
- Why it was chosen: `to_cents(19.99)` returned 1998. 19.99 as a float is 19.98999..., and `int()` truncates.
- Evidence: after the change, `to_cents(19.99), to_cents(0.29), to_cents(1.15)` gives `1999 29 115`. Acme: `acme 5997 6491 Acme: $64.91`.
- Why it partly worked: the subtotal is right now (5997). The total is still one cent low because `Invoice.total` truncates 6491.7525 with `int()`. This also explains the $64.91 in notes.txt: it is what you get with correct line prices and truncated tax. Bug B1.
- Kept or undone: Kept.

#### Approach 1.2: Round each step half up in `Invoice.total`. Worked
- What was done: `total` now rounds the discount and the tax to whole cents with `money.round_cents` (Decimal, `ROUND_HALF_UP`) and adds them as integers. `TAX_RATE` is now `Decimal("0.0825")`.
- Why it was chosen: `int(taxed - ...)` truncates, so 6491.7525 became 6491.
- Evidence: `acme 5997 6492 Acme: $64.92`, which matches the hand calculation. Bug B2.
- Why it worked: tax of 494.7525 cents rounds to 495, not 494.
- Kept or undone: Kept.

### Problem 2: Discount applied after tax

Hand calculation for Hollis & Co: 200.00 less 10% = 180.00. Tax 180.00 x 0.0825 = 14.85. Total 194.85.

The committed code with `discount_pct = 0.10` already gives 19485 for this invoice, because without rounding the order does not matter (200 x 1.0825 x 0.9 = 200 x 0.9 x 1.0825). So the exact complaint did not reproduce. Two things can make it come out lower:
- Rounding between steps. Searching subtotals 1.00 to 999.99 found 33114 where tax-then-discount (each rounded) differs from discount-then-tax. First one: $1.01 at 10% off gives 98 cents taxed first, 99 cents discounted first. By hand: 1.01 - 0.10 = 0.91, tax 0.075075 rounds to 0.08, total 0.99.
- `discount_pct = 10` (reading "pct" as a percent) gives `-194850`. The committed code accepts it silently.

Which of these Hollis & Co hit is not confirmed. Guess: their invoice had a subtotal or line prices other than a flat 200.00.

#### Approach 2.1: Discount first, then tax. Worked
- What was done: `total` takes the rounded discount off the subtotal, then charges tax on what is left, the same order as the spreadsheet.
- Why it was chosen: notes.txt says the spreadsheet does "discount first, then tax".
- Evidence: `hollis 19485 H: $194.85`. $1.01 at 10% off now gives 99 cents (checked in the test run below). Bug B3.
- Why it worked: tax is charged on the discounted amount, so the rounding happens where the spreadsheet does it.
- Kept or undone: Kept.

#### Approach 2.2: Reject a discount outside 0 to 1. Worked
- What was done: `total` raises `ValueError` when `discount_pct` is below 0 or above 1.
- Why it was chosen: a discount of 10 produced a negative invoice with no error. Bug B4.
- Evidence: `ValueError: discount_pct must be a fraction from 0 to 1, got 10`.
- Why it worked: the bad value is caught before any arithmetic.
- Kept or undone: Kept. Whether 10 should mean 10% is an open question.

### Problem 3: Summary shows one decimal place

6490 cents must print as `$64.90`.

#### Approach 3.1: Format from integer cents with two digits. Worked
- What was done: `money.fmt` splits cents with `divmod` and pads the remainder to two digits. Negative amounts print as `-$0.05`.
- Why it was chosen: `str(cents / 100)` prints a float, which drops the trailing zero. Bug B5.
- Evidence: `fmt(6490), fmt(5), fmt(0), fmt(-5)` gives `$64.90 $0.05 $0.00 -$0.05`. Summary: `Acme: $64.92`.
- Why it worked: no float is involved, so there is nothing to drop or round.
- Kept or undone: Kept. A first version added thousands separators (`$1,234,567.89`). That was taken out because it changes output nobody asked to change.

## What worked
- Integer cents everywhere, `Decimal` for the fractional steps, half-up rounding at each step (approaches 1.1, 1.2).
- Discount off the subtotal, then tax (2.1). Range check on `discount_pct` (2.2).
- `fmt` built from `divmod` on cents (3.1).

## What didn't, do not retry
- Fixing `to_cents` alone (1.1). The subtotal is right but `int()` in `total` still drops a cent.
- `int(amount * 100)` or `str(cents / 100)` for money. Both go through a float.

## Tests added
New files `test_money.py` and `test_invoice.py` (pytest; the project had no tests). Each fix was taken back out one at a time and the suite run, then restored.

| Test | Protects against | Status |
|---|---|---|
| `test_money.py::test_to_cents_keeps_written_value` | B1 | Fails on `int(amount * 100)` (5 cases), passes now |
| `test_money.py::test_to_cents_rejects_text` | Wrong type returning a number | Fails on `int(amount * 100)`, passes now |
| `test_money.py::test_fmt_always_two_decimals` | B5 | Fails on `str(cents / 100)` (4 cases), passes now |
| `test_invoice.py::test_acme_three_items_at_19_99` | B1, B2 | Fails on approach 1.1 code and on committed code, passes now |
| `test_invoice.py::test_tax_rounds_half_cent_up` | B2 | Fails with truncated tax, passes now |
| `test_invoice.py::test_hollis_discount_before_tax` | B3 (complaint figures) | Passes on committed code too, since 200.00 does not show the order problem. Kept as the customer's own example. |
| `test_invoice.py::test_discount_applied_before_tax_rounding` | B3 | Fails with tax-then-discount, passes now |
| `test_invoice.py::test_full_discount_is_zero` | Boundary of 1 | Passes. Not shown to fail on any reverted fix. |
| `test_invoice.py::test_empty_invoice_is_zero` | Empty input, B5 | Fails on float `fmt`, passes now |
| `test_invoice.py::test_large_invoice` | Large input, B2 | Fails with truncated tax, passes now |
| `test_invoice.py::test_discount_outside_fraction_range_is_rejected` | B4 | Fails without the range check (3 cases), passes now |
| `test_invoice.py::test_summary_two_decimals` | B5, B2 | Fails on float `fmt` and on truncated tax, passes now |
| `test_invoice.py::test_summary_keeps_non_ascii_customer_name` | Odd characters | Passes. Not shown to fail on any reverted fix. |

Latest run: `python3 -B -m pytest -q` gives `26 passed in 0.03s`. The committed code against the same tests: `19 failed, 7 passed`.

## Next steps
- Re-issue or check the Acme and Hollis & Co invoices with the fixed code.
- Rotate the payment key in `config.py` and move it out of the repository (see open questions).

## Open questions
- Should `discount_pct = 10` mean 10%? Chosen for now: it is a fraction (0.10), as the old code treated it, and values outside 0 to 1 raise `ValueError`.
- Rounding rule: half up to the cent at the discount step and the tax step. If the business or tax authority wants banker's rounding or tax per line, `Invoice.total` needs to change.
- notes.txt says Acme saw $64.91, but the committed code gives $64.88. Was the invoice made with a different version of the code or different input?
- `config.py` holds a live-looking payment key (`<SECRET>`), a personal email (`<EMAIL>`) and a home folder path (`~/`). It is committed to git. The key should be revoked and replaced, and read from the environment.
