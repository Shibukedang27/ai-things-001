"""Interactive CLI entrypoint for the Binance Futures Trading Bot."""

from typing import NoReturn
import sys

import typer
from rich.prompt import Confirm, Prompt

from bot.client import BinanceFuturesClient
from bot.config import load_settings
from bot.exceptions import (
    AuthenticationError,
    BinanceAPIError,
    NetworkError,
    TradingBotError,
    ValidationError,
)
from bot.logging_config import get_logger
from bot.orders import OrderRequest, OrderService
from bot.utils import build_table, console, print_api_response, print_panel


app = typer.Typer(add_completion=False, help="Binance Futures Testnet trading bot.")


def _exit_success() -> NoReturn:
    """Exit the CLI successfully."""

    raise typer.Exit(code=0)


def _prompt_order(order_type: str) -> OrderRequest:
    """Collect and validate order fields from the user."""

    while True:
        try:
            symbol = Prompt.ask("Symbol", default="BTCUSDT")
            side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
            quantity = Prompt.ask("Quantity")
            price = Prompt.ask("Price") if order_type == "LIMIT" else None
            return OrderRequest.from_user_input(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )
        except ValidationError as exc:
            console.print(f"[bold red]Validation error:[/bold red] {exc}")


def _place_order(order_service: OrderService, order_request: OrderRequest) -> None:
    """Display confirmation, place the order, and render the result."""

    console.print(build_table("Order Request Summary", order_request.to_summary()))
    if not Confirm.ask("Place this order on Binance Futures Testnet?", default=False):
        console.print("[yellow]Order cancelled.[/yellow]")
        return

    try:
        response = order_service.place_order(order_request)
        formatted_response = order_service.format_response(response)
        print_api_response(formatted_response)
        print_panel("Order placed successfully.", "Success", "green")
    except (AuthenticationError, BinanceAPIError, NetworkError) as exc:
        print_panel(str(exc), "Failure", "red")
    except Exception as exc:
        get_logger().exception("Unexpected exception while placing order")
        print_panel(f"Unexpected error: {exc}", "Failure", "red")


def _build_order_service() -> OrderService:
    """Initialize dependencies for order placement."""

    logger = get_logger()
    settings = load_settings()
    client = BinanceFuturesClient(settings=settings, logger=logger)
    return OrderService(client=client)


@app.command()
def main() -> None:
    """Run the interactive trading bot menu."""

    print_panel("Binance Futures Trading Bot", "USDT-M Testnet", "cyan")
    logger = get_logger()

    try:
        order_service = _build_order_service()
    except AuthenticationError as exc:
        print_panel(str(exc), "Configuration Error", "red")
        _exit_success()
    except Exception as exc:
        logger.exception("Unexpected startup exception")
        print_panel(f"Startup failed: {exc}", "Configuration Error", "red")
        _exit_success()

    while True:
        console.print("\n[bold cyan]1.[/bold cyan] Market Order")
        console.print("[bold cyan]2.[/bold cyan] Limit Order")
        console.print("[bold cyan]3.[/bold cyan] Exit")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"], default="1")

        if choice == "3":
            console.print("[green]Goodbye.[/green]")
            _exit_success()

        order_type = "MARKET" if choice == "1" else "LIMIT"
        try:
            order_request = _prompt_order(order_type)
            _place_order(order_service, order_request)
        except TradingBotError as exc:
            print_panel(str(exc), "Failure", "red")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session ended by user.[/yellow]")
            _exit_success()


if __name__ == "__main__":
    try:
        app()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Session ended by user.[/yellow]")
        sys.exit(0)
