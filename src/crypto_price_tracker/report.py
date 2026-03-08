"""Report generation module for portfolio PDF export and notification summaries.

Provides HTML report generation, PDF conversion via xhtml2pdf, and
summary builders for Telegram (plain text) and email (HTML) notifications.
"""

from __future__ import annotations

import io
from datetime import datetime

from xhtml2pdf import pisa

from crypto_price_tracker.models import CoinData, PriceAlert, WatchlistEntry
from crypto_price_tracker.portfolio import PortfolioRow, PortfolioSummary


def _pnl_color(value: float | None) -> str:
    """Return green for positive, red for negative, default for None/zero."""
    if value is None:
        return "#333"
    if value > 0:
        return "#3fb950"
    if value < 0:
        return "#f85149"
    return "#333"


def _fmt_eur(value: float | None) -> str:
    """Format a value as EUR with two decimals."""
    if value is None:
        return "N/A"
    return f"EUR {value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    """Format a percentage with two decimals and sign."""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def generate_report_html(
    portfolio: PortfolioSummary,
    coins: list[CoinData],
    watchlist: list[WatchlistEntry],
    alerts: list[PriceAlert],
) -> str:
    """Build a complete HTML report string with inline CSS styling.

    Sections with no data are omitted entirely.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Portfolio Summary ---
    pnl_color = _pnl_color(portfolio.total_pnl_eur)
    portfolio_section = f"""
    <h2>Portfolio Summary</h2>
    <p style="font-size: 12px; font-weight: bold; margin-top: 10px;">
      Total Value: {_fmt_eur(portfolio.total_value)} |
      Total P&amp;L: <span style="color: {pnl_color};">{_fmt_eur(portfolio.total_pnl_eur)} ({_fmt_pct(portfolio.total_pnl_pct)})</span>
    </p>
    """

    # --- Holdings table ---
    holdings_section = ""
    if portfolio.rows:
        rows_html = ""
        for i, row in enumerate(portfolio.rows):
            bg = ' style="background-color: #f6f8fa;"' if i % 2 == 1 else ""
            pnl_c = _pnl_color(row.pnl_eur)
            rows_html += (
                f"<tr{bg}>"
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{row.symbol}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{row.total_amount}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{_fmt_eur(row.avg_buy_price)}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{_fmt_eur(row.current_value)}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right; color: {pnl_c};">{_fmt_eur(row.pnl_eur)} ({_fmt_pct(row.pnl_pct)})</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{_fmt_pct(row.allocation_pct) if row.allocation_pct is not None else "N/A"}</td>'
                f"</tr>"
            )
        holdings_section = f"""
    <h2>Holdings</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
      <tr>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Symbol</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Amount</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Avg Buy</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Value</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">P&amp;L</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Alloc</th>
      </tr>
      {rows_html}
    </table>
    """

    # --- Top Prices table ---
    prices_section = ""
    if coins:
        price_rows = ""
        for i, coin in enumerate(coins):
            bg = ' style="background-color: #f6f8fa;"' if i % 2 == 1 else ""
            change_color = _pnl_color(coin.change_24h)
            price_rows += (
                f"<tr{bg}>"
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{i + 1}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{coin.symbol}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{coin.name}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{_fmt_eur(coin.price)}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right; color: {change_color};">{_fmt_pct(coin.change_24h)}</td>'
                f"</tr>"
            )
        prices_section = f"""
    <h2>Top Prices</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
      <tr>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">#</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Symbol</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Name</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Price (EUR)</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">24h %</th>
      </tr>
      {price_rows}
    </table>
    """

    # --- Watchlist table ---
    watchlist_section = ""
    if watchlist:
        wl_rows = ""
        for i, entry in enumerate(watchlist):
            bg = ' style="background-color: #f6f8fa;"' if i % 2 == 1 else ""
            tags = entry.tags if entry.tags else "-"
            wl_rows += (
                f"<tr{bg}>"
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{entry.symbol}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{tags}</td>'
                f"</tr>"
            )
        watchlist_section = f"""
    <h2>Watchlist</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
      <tr>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Symbol</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Tags</th>
      </tr>
      {wl_rows}
    </table>
    """

    # --- Alerts table ---
    alerts_section = ""
    active_alerts = [a for a in alerts if a.status == "active"]
    if active_alerts:
        alert_rows = ""
        for i, alert in enumerate(active_alerts):
            bg = ' style="background-color: #f6f8fa;"' if i % 2 == 1 else ""
            alert_rows += (
                f"<tr{bg}>"
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{alert.symbol}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px;">{alert.direction}</td>'
                f'<td style="padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; text-align: right;">{_fmt_eur(alert.target_price)}</td>'
                f"</tr>"
            )
        alerts_section = f"""
    <h2>Active Alerts</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
      <tr>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Symbol</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px;">Direction</th>
        <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right; font-size: 10px;">Target Price</th>
      </tr>
      {alert_rows}
    </table>
    """

    html = f"""<html>
<head>
  <style>
    body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11px; color: #333; }}
    h1 {{ font-size: 18px; color: #0d1117; border-bottom: 2px solid #0d1117; padding-bottom: 5px; }}
    h2 {{ font-size: 14px; color: #0d1117; margin-top: 20px; }}
  </style>
</head>
<body>
  <h1>Crypto Portfolio Report</h1>
  <p>Generated: {timestamp}</p>
  {portfolio_section}
  {holdings_section}
  {prices_section}
  {watchlist_section}
  {alerts_section}
</body>
</html>"""
    return html


def html_to_pdf(html: str) -> bytes:
    """Convert an HTML string to PDF bytes using xhtml2pdf.

    Raises RuntimeError if PDF generation encounters errors.
    """
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        raise RuntimeError(f"PDF generation failed with {pisa_status.err} errors")
    return buffer.getvalue()


def build_summary_text(portfolio: PortfolioSummary) -> str:
    """Build a plain-text summary for Telegram notifications.

    Uses HTML tags compatible with Telegram's HTML parse_mode:
    <b>, <i>, <code>, <pre>. Stays under 4096 characters.
    """
    pnl_sign = "+" if portfolio.total_pnl_eur >= 0 else ""
    header = (
        f"<b>Crypto Portfolio Summary</b>\n\n"
        f"Total Value: <b>{_fmt_eur(portfolio.total_value)}</b>\n"
        f"Total P&L: <b>{pnl_sign}{_fmt_eur(portfolio.total_pnl_eur)}</b> ({_fmt_pct(portfolio.total_pnl_pct)})\n"
    )

    if not portfolio.rows:
        return header + "\nNo holdings in portfolio."

    # Sort by current_value desc (already sorted in PortfolioSummary)
    rows = portfolio.rows
    max_display = 5
    shown = rows[:max_display]
    remaining = len(rows) - max_display

    lines = ["\n<pre>"]
    lines.append(f"{'Symbol':<8} {'Value':>14} {'P&L':>14}")
    lines.append("-" * 38)
    for row in shown:
        value_str = _fmt_eur(row.current_value) if row.current_value is not None else _fmt_eur(row.total_cost)
        pnl_str = _fmt_eur(row.pnl_eur) if row.pnl_eur is not None else "N/A"
        lines.append(f"{row.symbol:<8} {value_str:>14} {pnl_str:>14}")

    if remaining > 0:
        lines.append(f"... and {remaining} more")
    lines.append("</pre>")

    result = header + "\n".join(lines)

    # Safety: truncate if somehow over 4096
    if len(result) > 4090:
        result = result[:4086] + "..."

    return result


def build_summary_html(portfolio: PortfolioSummary) -> str:
    """Build an HTML summary for email notifications.

    Simple HTML table with green/red P&L coloring.
    """
    pnl_color = _pnl_color(portfolio.total_pnl_eur)

    rows_html = ""
    for row in portfolio.rows:
        row_pnl_color = _pnl_color(row.pnl_eur)
        rows_html += (
            f"<tr>"
            f'<td style="padding: 4px 8px; border-bottom: 1px solid #ddd;">{row.symbol}</td>'
            f'<td style="padding: 4px 8px; border-bottom: 1px solid #ddd; text-align: right;">{_fmt_eur(row.current_value)}</td>'
            f'<td style="padding: 4px 8px; border-bottom: 1px solid #ddd; text-align: right; color: {row_pnl_color};">{_fmt_eur(row.pnl_eur)}</td>'
            f"</tr>"
        )

    html = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 13px; color: #333;">
  <h2 style="color: #0d1117;">Crypto Portfolio Summary</h2>
  <p>
    Total Value: <b>{_fmt_eur(portfolio.total_value)}</b> |
    Total P&amp;L: <b style="color: {pnl_color};">{_fmt_eur(portfolio.total_pnl_eur)} ({_fmt_pct(portfolio.total_pnl_pct)})</b>
  </p>
  <table style="width: 100%; border-collapse: collapse;">
    <tr>
      <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left;">Symbol</th>
      <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right;">Value</th>
      <th style="background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: right;">P&amp;L</th>
    </tr>
    {rows_html}
    <tr style="font-weight: bold;">
      <td style="padding: 6px 8px; border-top: 2px solid #0d1117;">Total</td>
      <td style="padding: 6px 8px; border-top: 2px solid #0d1117; text-align: right;">{_fmt_eur(portfolio.total_value)}</td>
      <td style="padding: 6px 8px; border-top: 2px solid #0d1117; text-align: right; color: {pnl_color};">{_fmt_eur(portfolio.total_pnl_eur)}</td>
    </tr>
  </table>
</body>
</html>"""
    return html
