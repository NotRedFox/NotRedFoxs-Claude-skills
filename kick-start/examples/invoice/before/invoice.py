from money import to_cents, fmt

TAX_RATE = 0.0825


class Invoice:
    def __init__(self, customer):
        self.customer = customer
        self.lines = []
        self.discount_pct = 0

    def add(self, description, unit_price, qty=1):
        self.lines.append((description, unit_price, qty))

    def subtotal(self):
        return sum(to_cents(price) * qty for _, price, qty in self.lines)

    def total(self):
        sub = self.subtotal()
        taxed = sub + sub * TAX_RATE
        return int(taxed - taxed * self.discount_pct)

    def summary(self):
        return f"{self.customer}: {fmt(self.total())}"
