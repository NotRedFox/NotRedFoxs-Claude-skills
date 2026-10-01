"""A simple invoice with line items, one discount and sales tax."""

from decimal import Decimal

from money import to_cents, fmt, round_cents

TAX_RATE = Decimal("0.0825")


class Invoice:
    """An invoice for one customer.

    Attributes:
        customer: Name shown in the summary.
        lines: List of ``(description, unit_price, qty)`` tuples. Prices are
            in dollars.
        discount_pct: Discount as a fraction of the subtotal, 0.10 for 10%.
    """

    def __init__(self, customer):
        self.customer = customer
        self.lines = []
        self.discount_pct = 0

    def add(self, description, unit_price, qty=1):
        """Add a line item. ``unit_price`` is in dollars."""
        self.lines.append((description, unit_price, qty))

    def subtotal(self):
        """Return the sum of all lines in cents, before discount and tax."""
        return sum(to_cents(price) * qty for _, price, qty in self.lines)

    def breakdown(self):
        """Return each step of the total in cents.

        The discount comes off the subtotal first and tax is charged on what
        is left. Each step is rounded half up to the cent, so the result
        matches a line-by-line hand calculation.

        Returns:
            dict: ``subtotal``, ``discount``, ``tax`` and ``total`` as ints.
            ``discount`` is the positive amount taken off.

        Raises:
            ValueError: If ``discount_pct`` is outside 0 to 1.
        """
        pct = Decimal(str(self.discount_pct))
        # A value like 10 meaning 10% would produce a negative total (B4).
        if not 0 <= pct <= 1:
            raise ValueError(
                f"discount_pct must be a fraction from 0 to 1, got {self.discount_pct}"
            )
        sub = self.subtotal()
        # Discount before tax, rounding each step. Taxing first and rounding
        # can land a cent lower, e.g. $1.01 at 10% off gives $0.98, not $0.99 (B3).
        discount = round_cents(sub * pct)
        discounted = sub - discount
        tax = round_cents(discounted * TAX_RATE)
        return {
            "subtotal": sub,
            "discount": discount,
            "tax": tax,
            "total": discounted + tax,
        }

    def total(self):
        """Return the amount due in cents. See ``breakdown`` for the steps.

        Raises:
            ValueError: If ``discount_pct`` is outside 0 to 1.
        """
        return self.breakdown()["total"]

    def summary(self):
        """Return ``"<customer>: $<total>"``."""
        return f"{self.customer}: {fmt(self.total())}"
