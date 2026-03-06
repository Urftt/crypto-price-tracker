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

from crypto_price_tracker.api import get_top_coins
from crypto_price_tracker.display import (
    render_coin_detail,
    render_portfolio_lots,
    render_portfolio_table,
    render_price_table,
)
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
        coins = get_top_coins(top_n=args.top)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)
    render_price_table(coins)


def cmd_watch(args: argparse.Namespace) -> None:
    """Continuously refresh the price table at the given interval."""
    print(f"Refreshing every {args.interval}s (Ctrl+C to stop)")
    try:
        while True:
            print("\033[2J\033[H", end="")
            try:
                coins = get_top_coins(top_n=args.top)
                render_price_table(coins)
            except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                print(f"Error fetching data: {e}", file=sys.stderr)
            print(f"\nRefreshing every {args.interval}s \u2014 Ctrl+C to stop")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def cmd_web(args: argparse.Namespace) -> None:
    """Start the web dashboard server."""
    from crypto_price_tracker.web import run_server

    print(f"Starting web dashboard at http://localhost:{args.port}")
    run_server(host=args.host, port=args.port)


def cmd_info(args: argparse.Namespace) -> None:
    """Fetch coins and display detailed info for the requested symbol."""
    symbol = args.symbol.upper()
    try:
        coins = get_top_coins(top_n=100)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)
    match = next((c for c in coins if c.symbol == symbol), None)
    if match is None:
        print(
            f"Coin '{symbol}' not found in top 100 EUR pairs on Bitvavo.",
            file=sys.stderr,
        )
        sys.exit(1)
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
        coins = get_top_coins(top_n=100)
        prices = {c.symbol: c for c in coins}
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

    # info subcommand
    info_parser = subparsers.add_parser("info", help="Show detailed info for a single coin")
    info_parser.add_argument(
        "symbol",
        type=str,
        help="Coin symbol (e.g., BTC, ETH)",
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
