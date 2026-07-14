"""Binance Futures Testnet client wrapper."""

from collections.abc import Callable, Mapping
from time import perf_counter, sleep
from typing import Any, TypeVar
import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import requests

from bot.config import Settings
from bot.exceptions import AuthenticationError, BinanceAPIError, NetworkError


T = TypeVar("T")


class BinanceFuturesClient:
    """Centralized Binance Futures Testnet API communication wrapper."""

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        """Create an authenticated Binance client configured for futures testnet."""

        self._settings = settings
        self._logger = logger
        self._client = Client(
            api_key=settings.api_key,
            api_secret=settings.api_secret,
            testnet=True,
            requests_params={"timeout": settings.request_timeout_seconds},
        )
        self._client.FUTURES_URL = settings.testnet_url

    def place_futures_order(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Place a futures order through the wrapped request executor."""

        request_payload = dict(payload)
        return self._execute_request(
            endpoint="POST /fapi/v1/order",
            payload=request_payload,
            request=lambda: self._client.futures_create_order(**request_payload),
        )

    def ping(self) -> dict[str, Any]:
        """Verify connectivity to Binance Futures Testnet."""

        return self._execute_request(
            endpoint="GET /fapi/v1/ping",
            payload={},
            request=self._client.futures_ping,
        )

    def _execute_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
        request: Callable[[], T],
    ) -> T:
        """Execute an API request with retry, timing, and structured logging."""

        last_error: Exception | None = None
        for attempt in range(1, self._settings.max_retries + 1):
            started_at = perf_counter()
            try:
                response = request()
                execution_time_ms = (perf_counter() - started_at) * 1000
                self._logger.info(
                    (
                        "endpoint=%s attempt=%s order_type=%s side=%s quantity=%s "
                        "price=%s payload=%s response=%s execution_time_ms=%.2f"
                    ),
                    endpoint,
                    attempt,
                    payload.get("type", "N/A"),
                    payload.get("side", "N/A"),
                    payload.get("quantity", "N/A"),
                    payload.get("price", "N/A"),
                    payload,
                    response,
                    execution_time_ms,
                )
                return response
            except BinanceAPIException as exc:
                execution_time_ms = (perf_counter() - started_at) * 1000
                self._logger.error(
                    (
                        "endpoint=%s attempt=%s order_type=%s side=%s quantity=%s "
                        "price=%s payload=%s api_error=%s execution_time_ms=%.2f"
                    ),
                    endpoint,
                    attempt,
                    payload.get("type", "N/A"),
                    payload.get("side", "N/A"),
                    payload.get("quantity", "N/A"),
                    payload.get("price", "N/A"),
                    payload,
                    exc.message,
                    execution_time_ms,
                )
                if exc.status_code in {401, 403}:
                    raise AuthenticationError(
                        "Binance rejected the API credentials or permissions."
                    ) from exc
                raise BinanceAPIError(f"Binance API error: {exc.message}") from exc
            except (BinanceRequestException, requests.RequestException, TimeoutError) as exc:
                last_error = exc
                execution_time_ms = (perf_counter() - started_at) * 1000
                self._logger.warning(
                    (
                        "endpoint=%s attempt=%s order_type=%s side=%s quantity=%s "
                        "price=%s payload=%s network_error=%s execution_time_ms=%.2f"
                    ),
                    endpoint,
                    attempt,
                    payload.get("type", "N/A"),
                    payload.get("side", "N/A"),
                    payload.get("quantity", "N/A"),
                    payload.get("price", "N/A"),
                    payload,
                    exc,
                    execution_time_ms,
                )
                if attempt < self._settings.max_retries:
                    sleep(self._settings.retry_backoff_seconds * attempt)

        raise NetworkError(
            f"Network request failed after {self._settings.max_retries} attempts: {last_error}"
        )
