"""Order business services for Binance Futures Testnet."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from bot.client import BinanceFuturesClient
from bot.exceptions import ValidationError
from bot.utils import decimal_to_api_string
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """Validated order request used by the order service."""

    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None

    @classmethod
    def from_user_input(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
    ) -> "OrderRequest":
        """Create an OrderRequest from raw user input."""

        normalized_order_type = validate_order_type(order_type)
        return cls(
            symbol=validate_symbol(symbol),
            side=validate_side(side),
            order_type=normalized_order_type,
            quantity=validate_quantity(quantity),
            price=validate_price(price, normalized_order_type),
        )

    def to_payload(self) -> dict[str, Any]:
        """Convert this order request to a Binance futures order payload."""

        payload: dict[str, Any] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": decimal_to_api_string(self.quantity),
        }

        if self.order_type == "LIMIT":
            if self.price is None:
                raise ValidationError("Price is required for LIMIT orders.")
            payload["price"] = decimal_to_api_string(self.price)
            payload["timeInForce"] = "GTC"

        return payload

    def to_summary(self) -> dict[str, str]:
        """Return display-ready order details."""

        return {
            "Symbol": self.symbol,
            "Side": self.side,
            "Order Type": self.order_type,
            "Quantity": decimal_to_api_string(self.quantity),
            "Price": decimal_to_api_string(self.price) if self.price else "N/A",
        }


class OrderService:
    """Application service responsible for order placement and formatting."""

    def __init__(self, client: BinanceFuturesClient) -> None:
        """Create an order service using a Binance client wrapper."""

        self._client = client

    def place_order(self, order_request: OrderRequest) -> dict[str, Any]:
        """Place either a market or limit futures order."""

        return self._client.place_futures_order(order_request.to_payload())

    @staticmethod
    def format_response(response: dict[str, Any]) -> dict[str, Any]:
        """Format the most useful response fields for console display."""

        preferred_keys = [
            "orderId",
            "symbol",
            "status",
            "clientOrderId",
            "price",
            "avgPrice",
            "origQty",
            "executedQty",
            "side",
            "type",
            "timeInForce",
            "updateTime",
        ]
        formatted = {
            key: response[key]
            for key in preferred_keys
            if key in response and response[key] is not None
        }
        return formatted or response
