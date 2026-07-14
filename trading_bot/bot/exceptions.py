"""Custom exceptions used by the trading bot."""


class TradingBotError(Exception):
    """Base exception for all expected trading bot failures."""


class ValidationError(TradingBotError):
    """Raised when user input fails validation."""


class AuthenticationError(TradingBotError):
    """Raised when API credentials are missing or rejected."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API-level error."""


class NetworkError(TradingBotError):
    """Raised when communication with Binance fails after retries."""
