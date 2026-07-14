"""Unit tests for the order service."""

from typing import Any

from bot.orders import OrderRequest, OrderService


class FakeClient:
    """Simple fake Binance client for service-level tests."""

    def __init__(self) -> None:
        """Initialize an empty request recorder."""

        self.payload: dict[str, Any] | None = None

    def place_futures_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Record the payload and return a representative API response."""

        self.payload = payload
        return {
            "orderId": 123,
            "symbol": payload["symbol"],
            "status": "NEW",
            "side": payload["side"],
            "type": payload["type"],
            "origQty": payload["quantity"],
        }


def test_order_service_places_order() -> None:
    """Order service delegates placement to the Binance client wrapper."""

    client = FakeClient()
    service = OrderService(client)  # type: ignore[arg-type]
    order = OrderRequest.from_user_input("BTCUSDT", "BUY", "MARKET", "0.01")

    response = service.place_order(order)

    assert client.payload == order.to_payload()
    assert response["orderId"] == 123


def test_format_response_keeps_preferred_fields() -> None:
    """Response formatting keeps important fields in display order."""

    response = OrderService.format_response(
        {
            "ignored": "value",
            "orderId": 123,
            "symbol": "BTCUSDT",
            "status": "NEW",
            "side": "BUY",
            "type": "MARKET",
        }
    )

    assert list(response.keys()) == ["orderId", "symbol", "status", "side", "type"]
