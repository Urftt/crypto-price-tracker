"""Terminal display module for rendering cryptocurrency data."""

from __future__ import annotations

import rich.box
from rich.console import Console
from rich.table import Table

from crypto_price_tracker.models import CoinData, Holding
from crypto_price_tracker.portfolio import PortfolioRow, PortfolioSummary


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


def render_portfolio_table(summary: PortfolioSummary, console: Console | None = None) -> None:
    """Render an aggregated portfolio view as a Rich table with P&L and allocation.

    Args:
        summary: PortfolioSummary from aggregate_portfolio().
        console: Optional Rich Console instance for output capture.
    """
    if console is None:
        console = Console()

    table = Table(title="Portfolio (EUR)", show_lines=False)
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Amount", justify="right")
    table.add_column("Avg Buy", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("P&L", justify="right")
    table.add_column("%", justify="right")
    table.add_column("Alloc", justify="right")

    for row in summary.rows:
        amount_str = f"{row.total_amount:,.4f}"
        avg_buy_str = f"EUR {row.avg_buy_price:,.2f}"

        if row.current_price is None:
            value_str = "N/A"
            pnl_str = "N/A"
            pct_str = "N/A"
            alloc_str = "N/A"
        else:
            value_str = f"EUR {row.current_value:,.2f}"
            pnl_str = f"EUR {row.pnl_eur:+,.2f}"
            if row.pnl_eur >= 0:
                pnl_str = f"[green]{pnl_str}[/green]"
            else:
                pnl_str = f"[red]{pnl_str}[/red]"
            pct_str = f"{row.pnl_pct:+.2f}%"
            if row.pnl_pct >= 0:
                pct_str = f"[green]{pct_str}[/green]"
            else:
                pct_str = f"[red]{pct_str}[/red]"
            alloc_str = f"{row.allocation_pct:.1f}%" if row.allocation_pct is not None else "N/A"

        table.add_row(row.symbol, amount_str, avg_buy_str, value_str, pnl_str, pct_str, alloc_str)

    console.print(table)

    # Summary totals
    total_value_str = f"EUR {summary.total_value:,.2f}"
    total_pnl_str = f"EUR {summary.total_pnl_eur:+,.2f}"
    if summary.total_pnl_eur >= 0:
        total_pnl_colored = f"[green]{total_pnl_str}[/green]"
    else:
        total_pnl_colored = f"[red]{total_pnl_str}[/red]"
    console.print(f"\n  Total Value: {total_value_str}  |  P&L: {total_pnl_colored}")


def render_portfolio_lots(symbol: str, lots: list[Holding], console: Console | None = None) -> None:
    """Render individual lots for a single coin.

    Args:
        symbol: The coin symbol (e.g. "BTC").
        lots:   List of Holding objects for that symbol.
        console: Optional Rich Console instance for output capture.
    """
    if console is None:
        console = Console()

    table = Table(title=f"{symbol} \u2014 Individual Lots", show_lines=False)
    table.add_column("ID", justify="right")
    table.add_column("Amount", justify="right")
    table.add_column("Buy Price", justify="right")
    table.add_column("Date", justify="left")

    for lot in lots:
        table.add_row(
            str(lot.id),
            f"{lot.amount:,.4f}",
            f"EUR {lot.buy_price:,.2f}",
            lot.buy_date,
        )

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
