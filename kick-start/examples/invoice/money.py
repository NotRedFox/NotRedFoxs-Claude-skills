"""Helpers for converting and formatting money held as integer cents."""

from decimal import Decimal, ROUND_HALF_UP


def round_cents(value):
    """Round a cent amount to a whole number of cents, half away from zero.

    Args:
        value: Cents as an int, float or Decimal. Floats go through ``str``
            so that their shortest decimal form is used.

    Returns:
        int: The rounded number of cents.
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def to_cents(amount):
    """Convert a dollar amount to integer cents.

    Args:
        amount: Dollars as an int, float, str or Decimal, for example 19.99.

    Returns:
        int: The amount in cents, rounded half up.
    """
    # 19.99 is stored as 19.989999..., so float multiplication followed by
    # int() drops a cent (B1). Going through str keeps the written value.
    return round_cents(Decimal(str(amount)) * 100)


def fmt(cents):
    """Format integer cents as dollars with two decimals.

    Args:
        cents: Amount in cents as an int, for example 6490.

    Returns:
        str: The amount as dollars, for example "$64.90" or "-$0.05".
    """
    # cents / 100 is a float, which prints 6490 as "64.9" (B5).
    sign = "-" if cents < 0 else ""
    dollars, rem = divmod(abs(cents), 100)
    return f"{sign}${dollars}.{rem:02d}"


def plain(cents):
    """Format integer cents as a bare decimal with two places.

    Spreadsheets read this as a number, where ``fmt``'s dollar sign would
    make some of them treat the cell as text.

    Args:
        cents: Amount in cents as an int, for example 6490.

    Returns:
        str: The amount, for example "64.90" or "-0.05".
    """
    sign = "-" if cents < 0 else ""
    dollars, rem = divmod(abs(cents), 100)
    return f"{sign}{dollars}.{rem:02d}"
