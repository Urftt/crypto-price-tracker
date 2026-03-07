"""Terminal display module for rendering cryptocurrency data."""

from __future__ import annotations

import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from crypto_price_tracker.models import Candle, CoinData, Holding, PriceAlert
from crypto_price_tracker.portfolio import PortfolioRow, PortfolioSummary

SPARK_CHARS = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"


def sparkline(values: list[float]) -> str:
    """Convert numeric values to a Unicode sparkline string.

    Maps values linearly across 8 Unicode block characters (U+2581..U+2588).
    Returns empty string for empty input, uniform mid-height bars for constant values.

    Args:
        values: List of numeric values to render.

    Returns:
        A string of Unicode block characters representing the data.
    """
    if not values:
        return ""
    mn, mx = min(values), max(values)
    if mn == mx:
        return SPARK_CHARS[3] * len(values)
    extent = mx - mn
    return "".join(
        SPARK_CHARS[min(7, int((v - mn) / extent * 8))]
        for v in values
    )


def render_price_table(
    coins: list[CoinData],
    console: Console | None = None,
    triggered_symbols: set[str] | None = None,
    source: str | None = None,
) -> None:
    """Render a list of CoinData objects as a formatted terminal price table.

    Args:
        coins:   List of CoinData objects to display.
        console: Optional Rich Console instance for output capture (e.g. in tests).
                 Defaults to a standard Console() if not provided.
        triggered_symbols: Set of symbols with triggered alerts (highlighted in table).
        source: Optional exchange source label (e.g. "Bitvavo", "Binance").
    """
    if console is None:
        console = Console()
    if triggered_symbols is None:
        triggered_symbols = set()

    table = Table(title="Crypto Prices (EUR)", show_lines=False)
    if source:
        table.caption = f"via {source}"
        table.caption_style = "dim"

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

        symbol_str = coin.symbol
        if coin.symbol in triggered_symbols:
            symbol_str = f"[bold yellow]\u26a0 {coin.symbol}[/bold yellow]"

        table.add_row(str(rank), symbol_str, coin.name, price_str, change_colored, volume_str)

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


def render_alert_banner(triggered: list[PriceAlert], console: Console | None = None) -> None:
    """Render a warning banner for triggered alerts."""
    if console is None:
        console = Console()
    lines = []
    for a in triggered:
        lines.append(
            f"[bold yellow]\u26a0[/bold yellow] {a.symbol} hit EUR {a.target_price:,.2f} ({a.direction} target)"
        )
    text = "\n".join(lines)
    console.print(
        Panel(
            text,
            title="[bold yellow]ALERTS TRIGGERED[/bold yellow]",
            border_style="yellow",
            expand=True,
        )
    )


def render_alert_list(alerts: list[PriceAlert], console: Console | None = None) -> None:
    """Render all alerts as a Rich table with active and triggered sections."""
    if console is None:
        console = Console()

    active = [a for a in alerts if a.status == "active"]
    triggered = [a for a in alerts if a.status == "triggered"]

    if not active and not triggered:
        console.print("No alerts set.")
        return

    table = Table(title="Price Alerts", show_lines=False)
    table.add_column("ID", justify="right")
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Target (EUR)", justify="right")
    table.add_column("Direction", justify="left")
    table.add_column("Status", justify="left")
    table.add_column("Created", justify="left")
    table.add_column("Triggered", justify="left")

    for a in active:
        table.add_row(
            str(a.id),
            a.symbol,
            f"EUR {a.target_price:,.2f}",
            a.direction,
            "[green]active[/green]",
            a.created_at,
            "",
        )

    if triggered:
        table.add_section()
        for a in triggered:
            table.add_row(
                str(a.id),
                a.symbol,
                f"EUR {a.target_price:,.2f}",
                a.direction,
                "[yellow]triggered[/yellow]",
                a.created_at,
                a.triggered_at or "",
            )

    console.print(table)


def render_chart_table(
    coins: list[CoinData],
    sparklines_7d: dict[str, str],
    sparklines_30d: dict[str, str],
    console: Console | None = None,
) -> None:
    """Render a compact sparkline overview table for all coins.

    Args:
        coins:          List of CoinData objects (determines row order).
        sparklines_7d:  Dict mapping symbol -> 7-day sparkline string.
        sparklines_30d: Dict mapping symbol -> 30-day sparkline string.
        console:        Optional Rich Console instance for output capture.
    """
    if console is None:
        console = Console()

    table = Table(title="Price Charts (EUR)", show_lines=False)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("7d", justify="left")
    table.add_column("30d", justify="left")

    for rank, coin in enumerate(coins, start=1):
        table.add_row(
            str(rank),
            coin.symbol,
            sparklines_7d.get(coin.symbol, ""),
            sparklines_30d.get(coin.symbol, ""),
        )

    console.print(table)


def render_chart_detail(
    coin: CoinData,
    candles_7d: list[Candle],
    candles_30d: list[Candle],
    console: Console | None = None,
) -> None:
    """Render a detailed single-coin chart view with sparklines and stats.

    Shows both 7-day and 30-day sparklines with open, close, high, low,
    and change % statistics. Stats are color-coded green/red.

    Args:
        coin:        CoinData object for the coin header.
        candles_7d:  List of 7-day Candle objects (chronological).
        candles_30d: List of 30-day Candle objects (chronological).
        console:     Optional Rich Console instance for output capture.
    """
    if console is None:
        console = Console()

    console.print(f"\n[bold]{coin.symbol}[/bold] \u2014 {coin.name}\n")

    for label, candles in [("7-Day", candles_7d), ("30-Day", candles_30d)]:
        if not candles:
            console.print(f"  {label}: No data available")
            continue

        spark = sparkline([c.close for c in candles])
        o = candles[0].open
        c = candles[-1].close
        hi = max(c_.high for c_ in candles)
        lo = min(c_.low for c_ in candles)
        change = ((c - o) / o) * 100 if o else 0

        console.print(f"  [bold]{label}[/bold]  {spark}")
        change_str = f"{change:+.2f}%"
        color = "green" if change >= 0 else "red"
        console.print(
            f"    Open: EUR {o:,.2f}  Close: EUR {c:,.2f}  "
            f"High: EUR {hi:,.2f}  Low: EUR {lo:,.2f}  "
            f"Change: [{color}]{change_str}[/{color}]"
        )

    console.print()
