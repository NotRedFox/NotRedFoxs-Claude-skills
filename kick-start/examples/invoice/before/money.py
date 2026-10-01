def to_cents(amount):
    return int(amount * 100)


def fmt(cents):
    return "$" + str(cents / 100)
