"""CLI entry point for the crypto price tracker.

Provides three subcommands:
  prices  -- Display top cryptocurrency prices once and exit.
  watch   -- Auto-refresh prices at a configurable interval.
  info    -- Show detailed info for a single coin by symbol.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time

import httpx

from crypto_price_tracker.alerts import check_alerts
from crypto_price_tracker.alerts_db import (
    add_alert,
    clear_triggered_alerts,
    get_active_alerts,
    get_all_alerts,
    mark_triggered,
    remove_alert as remove_alert_db,
)
from crypto_price_tracker.api import get_candles
from crypto_price_tracker.exchange import get_top_coins_with_fallback
from crypto_price_tracker.display import (
    render_alert_banner,
    render_alert_list,
    render_chart_detail,
    render_chart_table,
    render_coin_detail,
    render_portfolio_lots,
    render_portfolio_table,
    render_price_table,
    sparkline,
)
from rich.console import Console
from crypto_price_tracker.portfolio import aggregate_portfolio, export_csv, export_json
from crypto_price_tracker.portfolio_db import (
    add_holding,
    get_all_holdings,
    get_holdings_by_symbol,
    remove_holding,
    update_holding,
)


def cmd_prices(args: argparse.Namespace) -> None:
    """Fetch top coins and render a price table, then exit."""
    try:
        coins, source = get_top_coins_with_fallback(exchange=args.exchange, top_n=args.top)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)
    # Passive alert checking
    active = get_active_alerts()
    triggered = check_alerts(coins, active)
    for alert in triggered:
        mark_triggered(alert.id)
    triggered_symbols = {a.symbol for a in triggered}
    if triggered:
        render_alert_banner(triggered)
    render_price_table(coins, triggered_symbols=triggered_symbols, source=source)


def cmd_watch(args: argparse.Namespace) -> None:
    """Continuously refresh the price table at the given interval."""
    print(f"Refreshing every {args.interval}s (Ctrl+C to stop)")
    try:
        while True:
            print("\033[2J\033[H", end="")
            try:
                coins, source = get_top_coins_with_fallback(exchange=args.exchange, top_n=args.top)
                # Passive alert checking (flash once — mark_triggered prevents repeats)
                active = get_active_alerts()
                triggered = check_alerts(coins, active)
                for alert in triggered:
                    mark_triggered(alert.id)
                triggered_symbols = {a.symbol for a in triggered}
                if triggered:
                    render_alert_banner(triggered)
                render_price_table(coins, triggered_symbols=triggered_symbols, source=source)
            except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                print(f"Error fetching data: {e}", file=sys.stderr)
            print(f"\nRefreshing every {args.interval}s \u2014 Ctrl+C to stop")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def cmd_web(args: argparse.Namespace) -> None:
    """Start the web dashboard server."""
    from crypto_price_tracker.web import app, run_server

    app.state.default_exchange = getattr(args, "exchange", "bitvavo")
    print(f"Starting web dashboard at http://localhost:{args.port}")
    run_server(host=args.host, port=args.port)


def cmd_info(args: argparse.Namespace) -> None:
    """Fetch coins and display detailed info for the requested symbol."""
    symbol = args.symbol.upper()
    try:
        coins, source = get_top_coins_with_fallback(exchange=args.exchange, top_n=100)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)
    match = next((c for c in coins if c.symbol == symbol), None)
    if match is None:
        print(
            f"Coin '{symbol}' not found in top 100 pairs on {source}.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"via {source}")
    render_coin_detail(match)


def cmd_portfolio_add(args: argparse.Namespace) -> None:
    """Add a new holding to the portfolio."""
    try:
        row_id = add_holding(args.symbol, args.amount, args.buy_price, args.date)
    except ValueError as e:
        print(f"Invalid date: {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.IntegrityError as e:
        print(f"Constraint error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Added {args.symbol.upper()} holding (lot #{row_id})")


def cmd_portfolio_remove(args: argparse.Namespace) -> None:
    """Remove a holding by lot ID."""
    if remove_holding(args.id):
        print(f"Removed lot #{args.id}")
    else:
        print(f"Lot #{args.id} not found.", file=sys.stderr)
        sys.exit(1)


def cmd_portfolio_edit(args: argparse.Namespace) -> None:
    """Edit fields of a holding by lot ID."""
    kwargs: dict[str, object] = {}
    if args.amount is not None:
        kwargs["amount"] = args.amount
    if args.buy_price is not None:
        kwargs["buy_price"] = args.buy_price
    if args.date is not None:
        kwargs["buy_date"] = args.date
    if not kwargs:
        print("No fields to update.", file=sys.stderr)
        sys.exit(1)
    if not update_holding(args.id, **kwargs):
        print(f"Lot #{args.id} not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Updated lot #{args.id}")


def cmd_portfolio_list(args: argparse.Namespace) -> None:
    """Show aggregated portfolio view with live prices."""
    holdings = get_all_holdings()
    if not holdings:
        print("No holdings in portfolio.")
        return
    # Fetch live prices (best-effort)
    prices: dict = {}
    try:
        coins_list, _ = get_top_coins_with_fallback(top_n=100)
        prices = {c.symbol: c for c in coins_list}
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Warning: could not fetch live prices: {e}", file=sys.stderr)
    summary = aggregate_portfolio(holdings, prices)
    render_portfolio_table(summary)


def cmd_portfolio_lots(args: argparse.Namespace) -> None:
    """Show individual lots for a coin."""
    symbol = args.symbol.upper()
    lots = get_holdings_by_symbol(symbol)
    if not lots:
        print(f"No holdings found for {symbol}.", file=sys.stderr)
        sys.exit(1)
    render_portfolio_lots(symbol, lots)


def cmd_portfolio_export(args: argparse.Namespace) -> None:
    """Export holdings to CSV or JSON."""
    holdings = get_all_holdings()
    if args.export_format == "json":
        data = export_json(holdings)
    else:
        data = export_csv(holdings)
    if args.output:
        with open(args.output, "w") as f:
            f.write(data)
        print(f"Exported to {args.output}")
    else:
        print(data, end="")


def cmd_alert_add(args: argparse.Namespace) -> None:
    """Add a new price alert."""
    try:
        alert_id = add_alert(args.symbol, args.target_price, args.direction)
    except ValueError as e:
        print(f"Invalid direction: {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.IntegrityError as e:
        print(f"Constraint error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Alert #{alert_id}: {args.symbol.upper()} {args.direction} EUR {args.target_price:,.2f}")


def cmd_alert_list(args: argparse.Namespace) -> None:
    """List all alerts."""
    alerts = get_all_alerts()
    render_alert_list(alerts)


def cmd_alert_remove(args: argparse.Namespace) -> None:
    """Remove an alert by ID."""
    if remove_alert_db(args.id):
        print(f"Removed alert #{args.id}")
    else:
        print(f"Alert #{args.id} not found.", file=sys.stderr)
        sys.exit(1)


def cmd_alert_check(args: argparse.Namespace) -> None:
    """Check alerts against current prices."""
    try:
        coins, _ = get_top_coins_with_fallback(top_n=100)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)
    active = get_active_alerts()
    if not active:
        print("No active alerts.")
        sys.exit(0)
    triggered = check_alerts(coins, active)
    for alert in triggered:
        mark_triggered(alert.id)
    if triggered:
        render_alert_banner(triggered)
        sys.exit(1)
    else:
        print("No alerts triggered.")
        sys.exit(0)


def cmd_chart(args: argparse.Namespace) -> None:
    """Show price history charts with sparklines.

    If a symbol is provided, show detailed single-coin view.
    Otherwise, show compact sparkline overview for all top coins.
    """
    console = Console()

    if args.symbol:
        # Single coin detail mode
        symbol = args.symbol.upper()
        try:
            coins, source = get_top_coins_with_fallback(
                exchange=getattr(args, "exchange", "bitvavo"), top_n=100,
            )
        except (httpx.HTTPStatusError, httpx.ConnectError) as e:
            print(f"Error fetching data: {e}", file=sys.stderr)
            sys.exit(1)

        match = next((c for c in coins if c.symbol == symbol), None)
        if match is None:
            print(
                f"Coin '{symbol}' not found in top 100 pairs on {source}.",
                file=sys.stderr,
            )
            sys.exit(1)

        market = f"{symbol}-EUR"
        try:
            candles_7d = get_candles(market, interval="4h", limit=42)
        except (httpx.HTTPStatusError, httpx.ConnectError):
            candles_7d = []
        try:
            candles_30d = get_candles(market, interval="1d", limit=30)
        except (httpx.HTTPStatusError, httpx.ConnectError):
            candles_30d = []

        render_chart_detail(match, candles_7d, candles_30d, console=console)
    else:
        # All coins overview mode
        try:
            coins, _ = get_top_coins_with_fallback(
                exchange=getattr(args, "exchange", "bitvavo"), top_n=args.top,
            )
        except (httpx.HTTPStatusError, httpx.ConnectError) as e:
            print(f"Error fetching data: {e}", file=sys.stderr)
            sys.exit(1)

        sparklines_7d: dict[str, str] = {}
        sparklines_30d: dict[str, str] = {}

        with console.status("Fetching chart data..."):
            for coin in coins:
                market = f"{coin.symbol}-EUR"
                try:
                    candles_7d = get_candles(market, interval="4h", limit=42)
                    candles_30d = get_candles(market, interval="1d", limit=30)
                except (httpx.HTTPStatusError, httpx.ConnectError):
                    candles_7d, candles_30d = [], []
                sparklines_7d[coin.symbol] = sparkline(
                    [c.close for c in candles_7d]
                )
                sparklines_30d[coin.symbol] = sparkline(
                    [c.close for c in candles_30d]
                )

        render_chart_table(coins, sparklines_7d, sparklines_30d, console=console)


def main() -> None:
    """Entry point -- parse arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        prog="crypto",
        description="Cryptocurrency price tracker -- live prices from the Bitvavo API",
    )

    subparsers = parser.add_subparsers(dest="command")

    # prices subcommand
    prices_parser = subparsers.add_parser("prices", help="Display top cryptocurrency prices")
    prices_parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="Number of top coins to display (default: 20)",
    )
    prices_parser.add_argument(
        "--exchange",
        type=str,
        choices=["bitvavo", "binance"],
        default="bitvavo",
        help="Exchange to fetch prices from (default: bitvavo)",
    )

    # watch subcommand
    watch_parser = subparsers.add_parser("watch", help="Auto-refresh cryptocurrency prices")
    watch_parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="Number of top coins to display (default: 20)",
    )
    watch_parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=30,
        help="Refresh interval in seconds (default: 30)",
    )
    watch_parser.add_argument(
        "--exchange",
        type=str,
        choices=["bitvavo", "binance"],
        default="bitvavo",
        help="Exchange to fetch prices from (default: bitvavo)",
    )

    # info subcommand
    info_parser = subparsers.add_parser("info", help="Show detailed info for a single coin")
    info_parser.add_argument(
        "symbol",
        type=str,
        help="Coin symbol (e.g., BTC, ETH)",
    )
    info_parser.add_argument(
        "--exchange",
        type=str,
        choices=["bitvavo", "binance"],
        default="bitvavo",
        help="Exchange to fetch prices from (default: bitvavo)",
    )

    # web subcommand
    web_parser = subparsers.add_parser("web", help="Start the web dashboard server")
    web_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    web_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    web_parser.add_argument(
        "--exchange",
        type=str,
        choices=["bitvavo", "binance"],
        default="bitvavo",
        help="Default exchange for the web dashboard (default: bitvavo)",
    )

    # portfolio subcommand group
    portfolio_parser = subparsers.add_parser("portfolio", help="Manage portfolio holdings")
    portfolio_sub = portfolio_parser.add_subparsers(dest="portfolio_command")

    # portfolio add
    add_parser = portfolio_sub.add_parser("add", help="Add a holding")
    add_parser.add_argument("symbol", type=str, help="Coin symbol (e.g. BTC)")
    add_parser.add_argument("amount", type=float, help="Amount purchased")
    add_parser.add_argument("buy_price", type=float, help="Buy price per unit in EUR")
    add_parser.add_argument(
        "--date", type=str, default=None, help="Buy date YYYY-MM-DD (default: today)"
    )

    # portfolio remove
    remove_parser = portfolio_sub.add_parser("remove", help="Remove a holding by lot ID")
    remove_parser.add_argument("id", type=int, help="Lot ID to remove")

    # portfolio edit
    edit_parser = portfolio_sub.add_parser("edit", help="Edit a holding by lot ID")
    edit_parser.add_argument("id", type=int, help="Lot ID to edit")
    edit_parser.add_argument("--amount", type=float, default=None, help="New amount")
    edit_parser.add_argument(
        "--buy-price",
        type=float,
        default=None,
        dest="buy_price",
        help="New buy price in EUR",
    )
    edit_parser.add_argument(
        "--date", type=str, default=None, help="New buy date YYYY-MM-DD"
    )

    # portfolio list
    portfolio_sub.add_parser("list", help="Show aggregated portfolio view")

    # portfolio lots
    lots_parser = portfolio_sub.add_parser("lots", help="Show individual lots for a coin")
    lots_parser.add_argument("symbol", type=str, help="Coin symbol (e.g. BTC)")

    # portfolio export
    export_parser = portfolio_sub.add_parser(
        "export", help="Export holdings to CSV or JSON"
    )
    export_parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        dest="export_format",
        help="Export format (default: csv)",
    )
    export_parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output file path (default: stdout)"
    )

    # alert subcommand group
    alert_parser = subparsers.add_parser("alert", help="Manage price alerts")
    alert_sub = alert_parser.add_subparsers(dest="alert_command")

    # alert add
    alert_add_parser = alert_sub.add_parser("add", help="Add a price alert")
    alert_add_parser.add_argument("symbol", type=str, help="Coin symbol (e.g. BTC)")
    alert_add_parser.add_argument("target_price", type=float, help="Target price in EUR")
    direction_group = alert_add_parser.add_mutually_exclusive_group()
    direction_group.add_argument(
        "--above", dest="direction", action="store_const",
        const="above", help="Alert when price goes above target (default)",
    )
    direction_group.add_argument(
        "--below", dest="direction", action="store_const",
        const="below", help="Alert when price goes below target",
    )
    alert_add_parser.set_defaults(direction="above")

    # alert list
    alert_sub.add_parser("list", help="List all alerts")

    # alert remove
    alert_remove_parser = alert_sub.add_parser("remove", help="Remove an alert by ID")
    alert_remove_parser.add_argument("id", type=int, help="Alert ID to remove")

    # alert check
    alert_sub.add_parser("check", help="Check alerts against current prices")

    # chart subcommand
    chart_parser = subparsers.add_parser("chart", help="Show price history charts")
    chart_parser.add_argument(
        "symbol",
        type=str,
        nargs="?",
        default=None,
        help="Coin symbol (e.g. BTC). Omit for all top coins.",
    )
    chart_parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="Number of top coins to chart (default: 20, ignored if symbol given)",
    )
    chart_parser.add_argument(
        "--exchange",
        type=str,
        choices=["bitvavo", "binance"],
        default="bitvavo",
        help="Exchange to fetch prices from (default: bitvavo)",
    )

    args = parser.parse_args()

    if args.command == "prices":
        cmd_prices(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "web":
        cmd_web(args)
    elif args.command == "portfolio":
        if not hasattr(args, "portfolio_command") or args.portfolio_command is None:
            portfolio_parser.print_help()
        elif args.portfolio_command == "add":
            cmd_portfolio_add(args)
        elif args.portfolio_command == "remove":
            cmd_portfolio_remove(args)
        elif args.portfolio_command == "edit":
            cmd_portfolio_edit(args)
        elif args.portfolio_command == "list":
            cmd_portfolio_list(args)
        elif args.portfolio_command == "lots":
            cmd_portfolio_lots(args)
        elif args.portfolio_command == "export":
            cmd_portfolio_export(args)
    elif args.command == "alert":
        if not hasattr(args, "alert_command") or args.alert_command is None:
            alert_parser.print_help()
        elif args.alert_command == "add":
            cmd_alert_add(args)
        elif args.alert_command == "remove":
            cmd_alert_remove(args)
        elif args.alert_command == "list":
            cmd_alert_list(args)
        elif args.alert_command == "check":
            cmd_alert_check(args)
    elif args.command == "chart":
        cmd_chart(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
