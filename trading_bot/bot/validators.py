"""Validation helpers for order input."""

from decimal import Decimal, InvalidOperation
import re

from bot.exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def validate_symbol(symbol: str) -> str:
    """Validate and normalize a Binance futures symbol."""

    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise ValidationError("Symbol is required.")
    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise ValidationError(
            "Symbol must be 5-20 uppercase letters or numbers, for example BTCUSDT."
        )
    if not normalized_symbol.endswith("USDT"):
        raise ValidationError("This bot supports USDT-M futures symbols ending in USDT.")
    return normalized_symbol


def validate_side(side: str) -> str:
    """Validate and normalize an order side."""

    normalized_side = side.strip().upper()
    if normalized_side not in VALID_SIDES:
        raise ValidationError("Side must be BUY or SELL.")
    return normalized_side


def validate_order_type(order_type: str) -> str:
    """Validate and normalize an order type."""

    normalized_order_type = order_type.strip().upper()
    if normalized_order_type not in VALID_ORDER_TYPES:
        raise ValidationError("Order type must be MARKET or LIMIT.")
    return normalized_order_type


def _parse_positive_decimal(value: str, field_name: str) -> Decimal:
    """Parse a positive Decimal and return a clear validation error on failure."""

    try:
        parsed_value = Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValidationError(f"{field_name} must be a valid decimal number.") from exc

    if parsed_value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return parsed_value.normalize()


def validate_quantity(quantity: str) -> Decimal:
    """Validate an order quantity."""

    return _parse_positive_decimal(quantity, "Quantity")


def validate_price(price: str | None, order_type: str) -> Decimal | None:
    """Validate a limit price and ensure market orders do not require one."""

    normalized_order_type = validate_order_type(order_type)
    if normalized_order_type == "MARKET":
        return None

    if price is None or not price.strip():
        raise ValidationError("Price is required for LIMIT orders.")
    return _parse_positive_decimal(price, "Price")
