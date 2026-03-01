"""CLI entry point for the crypto price tracker.

Provides three subcommands:
  prices  -- Display top cryptocurrency prices once and exit.
  watch   -- Auto-refresh prices at a configurable interval.
  info    -- Show detailed info for a single coin by symbol.
"""

from __future__ import annotations

import argparse
import sys
import time

import httpx

from crypto_price_tracker.api import get_top_coins
from crypto_price_tracker.display import render_coin_detail, render_price_table


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

    args = parser.parse_args()

    if args.command == "prices":
        cmd_prices(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "web":
        cmd_web(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
