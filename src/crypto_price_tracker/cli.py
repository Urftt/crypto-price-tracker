import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="crypto",
        description="Cryptocurrency price tracker — live prices from the Bitvavo API",
    )

    subparsers = parser.add_subparsers(dest="command")
    # Future subcommands: prices, watch, info
    # Registered here as placeholders so help shows the {command} group
    subparsers.add_parser("prices", help="Display top crypto prices (coming soon)")
    subparsers.add_parser("watch", help="Live auto-refreshing price view (coming soon)")
    subparsers.add_parser("info", help="Single coin detail view (coming soon)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        raise SystemExit(0)


if __name__ == "__main__":
    main()
