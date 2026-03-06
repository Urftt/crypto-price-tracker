"""CLI integration tests for the crypto price tracker.

Tests invoke main() with patched sys.argv and mocked API layer so no real
HTTP calls are made.  Each test verifies a distinct CLI behaviour.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from crypto_price_tracker.cli import main
from crypto_price_tracker.models import CoinData, Holding, PriceAlert


@pytest.fixture
def mock_coins() -> list[CoinData]:
    return [
        CoinData(
            symbol="BTC",
            name="Bitcoin",
            price=56754.0,
            change_24h=1.67,
            volume=2186.73,
            volume_eur=120339407.0,
        ),
        CoinData(
            symbol="ETH",
            name="Ethereum",
            price=2345.50,
            change_24h=-3.21,
            volume=45000.0,
            volume_eur=95000000.0,
        ),
    ]


def test_prices_command_calls_api_and_renders(mock_coins):
    """prices command should call get_top_coins(top_n=20) and render the table."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins) as mock_api,
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.check_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.render_price_table") as mock_render,
    ):
        sys.argv = ["crypto", "prices"]
        main()

    mock_api.assert_called_once_with(top_n=20)
    mock_render.assert_called_once_with(mock_coins, triggered_symbols=set())


def test_prices_command_respects_top_n_flag(mock_coins):
    """prices -n 10 should call get_top_coins(top_n=10)."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins) as mock_api,
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.check_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.render_price_table"),
    ):
        sys.argv = ["crypto", "prices", "-n", "10"]
        main()

    mock_api.assert_called_once_with(top_n=10)


def test_info_command_renders_matching_coin(mock_coins):
    """info BTC should call render_coin_detail with the BTC CoinData object."""
    btc = mock_coins[0]
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.render_coin_detail") as mock_detail,
    ):
        sys.argv = ["crypto", "info", "BTC"]
        main()

    mock_detail.assert_called_once_with(btc)


def test_info_command_case_insensitive(mock_coins):
    """info btc (lowercase) should normalise the symbol and find BTC."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.render_coin_detail") as mock_detail,
    ):
        sys.argv = ["crypto", "info", "btc"]
        main()

    mock_detail.assert_called_once()


def test_info_command_not_found_exits_with_error(mock_coins):
    """info DOESNOTEXIST should exit with code 1 when symbol not in results."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        pytest.raises(SystemExit) as exc_info,
    ):
        sys.argv = ["crypto", "info", "DOESNOTEXIST"]
        main()

    assert exc_info.value.code == 1


def test_no_command_shows_help(capsys):
    """Running crypto with no subcommand should print usage/help text."""
    sys.argv = ["crypto"]
    main()
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "usage" in output.lower() or "crypto" in output.lower()


def test_watch_command_parses_interval(mock_coins):
    """watch --interval 10 should call get_top_coins and render, then exit on KeyboardInterrupt."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins) as mock_api,
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.check_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.render_price_table") as mock_render,
        patch("time.sleep", side_effect=KeyboardInterrupt),
    ):
        sys.argv = ["crypto", "watch", "--interval", "10"]
        main()

    mock_api.assert_called()
    mock_render.assert_called()


# ---- Portfolio subcommand tests ----


def test_portfolio_add_command():
    """portfolio add should call add_holding with correct arguments."""
    with patch("crypto_price_tracker.cli.add_holding", return_value=1) as mock_add:
        sys.argv = ["crypto", "portfolio", "add", "BTC", "0.5", "45000"]
        main()

    mock_add.assert_called_once_with("BTC", 0.5, 45000.0, None)


def test_portfolio_remove_command():
    """portfolio remove should call remove_holding with the lot ID."""
    with patch("crypto_price_tracker.cli.remove_holding", return_value=True) as mock_rm:
        sys.argv = ["crypto", "portfolio", "remove", "1"]
        main()

    mock_rm.assert_called_once_with(1)


def test_portfolio_list_command(mock_coins):
    """portfolio list should aggregate holdings and render the portfolio table."""
    holdings = [Holding(1, "BTC", 0.5, 45000.0, "2026-01-15")]
    with (
        patch("crypto_price_tracker.cli.get_all_holdings", return_value=holdings),
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.render_portfolio_table") as mock_render,
    ):
        sys.argv = ["crypto", "portfolio", "list"]
        main()

    mock_render.assert_called_once()


def test_portfolio_lots_command():
    """portfolio lots BTC should render individual lots for BTC."""
    lots = [Holding(1, "BTC", 0.5, 45000.0, "2026-01-15")]
    with (
        patch("crypto_price_tracker.cli.get_holdings_by_symbol", return_value=lots),
        patch("crypto_price_tracker.cli.render_portfolio_lots") as mock_render,
    ):
        sys.argv = ["crypto", "portfolio", "lots", "BTC"]
        main()

    mock_render.assert_called_once()


def test_portfolio_export_csv(capsys):
    """portfolio export --format csv should print CSV output to stdout."""
    holdings = [Holding(1, "BTC", 0.5, 45000.0, "2026-01-15")]
    csv_output = "id,symbol,amount,buy_price,buy_date\r\n1,BTC,0.5,45000.0,2026-01-15\r\n"
    with (
        patch("crypto_price_tracker.cli.get_all_holdings", return_value=holdings),
        patch("crypto_price_tracker.cli.export_csv", return_value=csv_output),
    ):
        sys.argv = ["crypto", "portfolio", "export", "--format", "csv"]
        main()

    captured = capsys.readouterr()
    assert "BTC" in captured.out
    assert "symbol" in captured.out


def test_portfolio_no_subcommand(capsys):
    """portfolio with no subcommand should print help text."""
    sys.argv = ["crypto", "portfolio"]
    main()

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "portfolio" in output.lower() or "usage" in output.lower()


# ---- Alert subcommand tests ----


def test_alert_add_command():
    """alert add should call add_alert with default direction."""
    with patch("crypto_price_tracker.cli.add_alert", return_value=1) as mock_add:
        sys.argv = ["crypto", "alert", "add", "BTC", "100000"]
        main()

    mock_add.assert_called_once_with("BTC", 100000.0, "above")


def test_alert_add_below_command():
    """alert add --below should call add_alert with direction='below'."""
    with patch("crypto_price_tracker.cli.add_alert", return_value=2) as mock_add:
        sys.argv = ["crypto", "alert", "add", "ETH", "1500", "--below"]
        main()

    mock_add.assert_called_once_with("ETH", 1500.0, "below")


def test_alert_remove_command():
    """alert remove should call remove_alert_db with the ID."""
    with patch("crypto_price_tracker.cli.remove_alert_db", return_value=True) as mock_rm:
        sys.argv = ["crypto", "alert", "remove", "1"]
        main()

    mock_rm.assert_called_once_with(1)


def test_alert_list_command():
    """alert list should call get_all_alerts and render_alert_list."""
    alerts = [PriceAlert(1, "BTC", 100000.0, "above", "active", "2026-03-01T10:00:00", None)]
    with (
        patch("crypto_price_tracker.cli.get_all_alerts", return_value=alerts),
        patch("crypto_price_tracker.cli.render_alert_list") as mock_render,
    ):
        sys.argv = ["crypto", "alert", "list"]
        main()

    mock_render.assert_called_once()


def test_alert_check_no_triggers(mock_coins):
    """alert check with no triggers should exit 0."""
    alert = PriceAlert(1, "BTC", 200000.0, "above", "active", "2026-03-01T10:00:00", None)
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[alert]),
        pytest.raises(SystemExit) as exc_info,
    ):
        sys.argv = ["crypto", "alert", "check"]
        main()

    assert exc_info.value.code == 0


def test_alert_check_with_triggers(mock_coins):
    """alert check with triggers should mark triggered and exit 1."""
    alert = PriceAlert(1, "BTC", 50000.0, "above", "active", "2026-03-01T10:00:00", None)
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[alert]),
        patch("crypto_price_tracker.cli.mark_triggered") as mock_mark,
        patch("crypto_price_tracker.cli.render_alert_banner") as mock_banner,
        pytest.raises(SystemExit) as exc_info,
    ):
        sys.argv = ["crypto", "alert", "check"]
        main()

    assert exc_info.value.code == 1
    mock_mark.assert_called_once_with(1)
    mock_banner.assert_called_once()


def test_alert_no_subcommand(capsys):
    """alert with no subcommand should print help text."""
    sys.argv = ["crypto", "alert"]
    main()

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "alert" in output.lower() or "add" in output.lower()


def test_prices_command_with_alert_checking(mock_coins):
    """prices command should check alerts and pass triggered_symbols."""
    with (
        patch("crypto_price_tracker.cli.get_top_coins", return_value=mock_coins),
        patch("crypto_price_tracker.cli.get_active_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.check_alerts", return_value=[]),
        patch("crypto_price_tracker.cli.render_price_table") as mock_render,
    ):
        sys.argv = ["crypto", "prices"]
        main()

    mock_render.assert_called_once_with(mock_coins, triggered_symbols=set())
