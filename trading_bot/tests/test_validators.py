"""Unit tests for user-input validation."""

from decimal import Decimal

import pytest

from bot.exceptions import ValidationError
from bot.orders import OrderRequest
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


def test_validate_symbol_accepts_usdt_symbols() -> None:
    """USDT-M symbols are normalized to uppercase."""

    assert validate_symbol("btcusdt") == "BTCUSDT"


def test_validate_symbol_rejects_non_usdt_symbols() -> None:
    """Non-USDT symbols are rejected."""

    with pytest.raises(ValidationError):
        validate_symbol("BTCBUSD")


def test_validate_side_accepts_buy_and_sell() -> None:
    """Both supported order sides validate successfully."""

    assert validate_side("buy") == "BUY"
    assert validate_side("SELL") == "SELL"


def test_validate_order_type_accepts_market_and_limit() -> None:
    """Both supported order types validate successfully."""

    assert validate_order_type("market") == "MARKET"
    assert validate_order_type("LIMIT") == "LIMIT"


def test_validate_quantity_requires_positive_decimal() -> None:
    """Quantity must be a positive decimal."""

    assert validate_quantity("0.01") == Decimal("0.01")
    with pytest.raises(ValidationError):
        validate_quantity("0")


def test_validate_price_only_required_for_limit_orders() -> None:
    """Limit orders require positive price, market orders do not."""

    assert validate_price(None, "MARKET") is None
    assert validate_price("25000.50", "LIMIT") == Decimal("25000.5")
    with pytest.raises(ValidationError):
        validate_price(None, "LIMIT")


def test_order_request_payloads() -> None:
    """Order requests convert to Binance-compatible payloads."""

    market_order = OrderRequest.from_user_input("BTCUSDT", "BUY", "MARKET", "0.01")
    assert market_order.to_payload() == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": "0.01",
    }

    limit_order = OrderRequest.from_user_input(
        "ETHUSDT",
        "SELL",
        "LIMIT",
        "0.25",
        "3500",
    )
    assert limit_order.to_payload() == {
        "symbol": "ETHUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": "0.25",
        "price": "3500",
        "timeInForce": "GTC",
    }
