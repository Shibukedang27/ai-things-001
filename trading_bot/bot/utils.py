"""Reusable formatting and console output helpers."""

from collections.abc import Mapping
from decimal import Decimal
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def decimal_to_api_string(value: Decimal) -> str:
    """Convert a Decimal to Binance's expected plain string format."""

    return format(value.normalize(), "f")


def build_table(title: str, values: Mapping[str, Any]) -> Table:
    """Build a two-column Rich table for structured values."""

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in values.items():
        table.add_row(str(key), str(value))
    return table


def print_panel(message: str, title: str, style: str = "cyan") -> None:
    """Print a Rich panel with a consistent style."""

    console.print(Panel(message, title=title, border_style=style))


def print_api_response(response: Mapping[str, Any]) -> None:
    """Display a formatted API response."""

    console.print(build_table("API Response", response))
