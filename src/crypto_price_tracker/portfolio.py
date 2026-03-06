"""Portfolio aggregation service and export utilities.

This module computes aggregated portfolio views (per-coin summaries with P&L)
and handles CSV/JSON export.  It does **not** touch the database directly --
it takes ``list[Holding]`` as input.
"""

from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from dataclasses import asdict, dataclass

from crypto_price_tracker.models import CoinData, Holding


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PortfolioRow:
    """Aggregated view of one coin across all lots."""

    symbol: str
    total_amount: float
    avg_buy_price: float
    current_price: float | None
    total_cost: float
    current_value: float | None
    pnl_eur: float | None
    pnl_pct: float | None
    allocation_pct: float | None
    change_24h: float | None


@dataclass(slots=True)
class PortfolioSummary:
    """Complete portfolio aggregation result."""

    rows: list[PortfolioRow]
    total_value: float
    total_cost: float
    total_pnl_eur: float
    total_pnl_pct: float


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_portfolio(
    holdings: list[Holding],
    prices: dict[str, CoinData],
) -> PortfolioSummary:
    """Aggregate holdings into per-coin rows with P&L calculations."""
    if not holdings:
        return PortfolioSummary(rows=[], total_value=0, total_cost=0, total_pnl_eur=0, total_pnl_pct=0)

    # Group by symbol
    groups: dict[str, list[Holding]] = defaultdict(list)
    for h in holdings:
        groups[h.symbol].append(h)

    priced_rows: list[PortfolioRow] = []
    unpriced_rows: list[PortfolioRow] = []
    total_cost = 0.0
    total_priced_value = 0.0
    total_unpriced_cost = 0.0

    for symbol, lots in groups.items():
        total_amount = sum(h.amount for h in lots)
        cost = sum(h.amount * h.buy_price for h in lots)
        avg_buy = cost / total_amount if total_amount else 0.0
        total_cost += cost

        if symbol in prices:
            coin = prices[symbol]
            current_value = round(total_amount * coin.price, 2)
            pnl_eur = round(current_value - cost, 2)
            pnl_pct = round((pnl_eur / cost) * 100, 2) if cost else 0.0
            total_priced_value += current_value
            priced_rows.append(
                PortfolioRow(
                    symbol=symbol,
                    total_amount=round(total_amount, 2),
                    avg_buy_price=round(avg_buy, 2),
                    current_price=coin.price,
                    total_cost=round(cost, 2),
                    current_value=current_value,
                    pnl_eur=pnl_eur,
                    pnl_pct=pnl_pct,
                    allocation_pct=None,  # computed after totals known
                    change_24h=coin.change_24h,
                )
            )
        else:
            total_unpriced_cost += cost
            unpriced_rows.append(
                PortfolioRow(
                    symbol=symbol,
                    total_amount=round(total_amount, 2),
                    avg_buy_price=round(avg_buy, 2),
                    current_price=None,
                    total_cost=round(cost, 2),
                    current_value=None,
                    pnl_eur=None,
                    pnl_pct=None,
                    allocation_pct=None,
                    change_24h=None,
                )
            )

    total_value = round(total_priced_value + total_unpriced_cost, 2)
    total_cost = round(total_cost, 2)

    # Compute allocation percentages for priced rows
    if total_value:
        for row in priced_rows:
            row.allocation_pct = round((row.current_value / total_value) * 100, 2)

    # Sort: priced by current_value desc, then unpriced by total_cost desc
    priced_rows.sort(key=lambda r: r.current_value, reverse=True)
    unpriced_rows.sort(key=lambda r: r.total_cost, reverse=True)

    rows = priced_rows + unpriced_rows
    total_pnl_eur = round(total_value - total_cost, 2)
    total_pnl_pct = round((total_pnl_eur / total_cost) * 100, 2) if total_cost else 0.0

    return PortfolioSummary(
        rows=rows,
        total_value=total_value,
        total_cost=total_cost,
        total_pnl_eur=total_pnl_eur,
        total_pnl_pct=total_pnl_pct,
    )


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_csv(holdings: list[Holding]) -> str:
    """Export holdings as a CSV string."""
    output = io.StringIO()
    fieldnames = ["id", "symbol", "amount", "buy_price", "buy_date"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for h in holdings:
        writer.writerow(asdict(h))
    return output.getvalue()


def export_json(holdings: list[Holding]) -> str:
    """Export holdings as a JSON string."""
    return json.dumps([asdict(h) for h in holdings], indent=2)
