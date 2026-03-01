"""Terminal display module for rendering cryptocurrency data."""

from __future__ import annotations

import rich.box
from rich.console import Console
from rich.table import Table

from crypto_price_tracker.models import CoinData


def render_price_table(coins: list[CoinData], console: Console | None = None) -> None:
    """Render a list of CoinData objects as a formatted terminal price table.

    Args:
        coins:   List of CoinData objects to display.
        console: Optional Rich Console instance for output capture (e.g. in tests).
                 Defaults to a standard Console() if not provided.
    """
    if console is None:
        console = Console()

    table = Table(title="Crypto Prices (EUR)", show_lines=False)

    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Name", justify="left")
    table.add_column("Price (EUR)", justify="right")
    table.add_column("24h %", justify="right")
    table.add_column("Volume (EUR)", justify="right")

    for rank, coin in enumerate(coins, start=1):
        price_str = f"EUR {coin.price:,.2f}"
        change_str = f"{coin.change_24h:+.2f}%"
        if coin.change_24h >= 0:
            change_colored = f"[green]{change_str}[/green]"
        else:
            change_colored = f"[red]{change_str}[/red]"
        volume_str = f"EUR {coin.volume_eur:,.0f}"

        table.add_row(str(rank), coin.symbol, coin.name, price_str, change_colored, volume_str)

    console.print(table)


def render_coin_detail(coin: CoinData, console: Console | None = None) -> None:
    """Render a single CoinData object as a detailed single-coin view.

    Args:
        coin:    CoinData object to display.
        console: Optional Rich Console instance for output capture (e.g. in tests).
                 Defaults to a standard Console() if not provided.
    """
    if console is None:
        console = Console()

    console.print(f"\n[bold]{coin.symbol}[/bold] — {coin.name}\n")

    table = Table(show_header=False, box=rich.box.SIMPLE, padding=(0, 2))
    table.add_column("Label", justify="left")
    table.add_column("Value", justify="left")

    price_str = f"EUR {coin.price:,.2f}"

    change_str = f"{coin.change_24h:+.2f}%"
    if coin.change_24h >= 0:
        change_colored = f"[green]{change_str}[/green]"
    else:
        change_colored = f"[red]{change_str}[/red]"

    volume_str = f"{coin.volume:,.4f}"
    volume_eur_str = f"EUR {coin.volume_eur:,.0f}"

    table.add_row("Price", price_str)
    table.add_row("24h Change", change_colored)
    table.add_row("Volume", volume_str)
    table.add_row("Volume (EUR)", volume_eur_str)

    console.print(table)
