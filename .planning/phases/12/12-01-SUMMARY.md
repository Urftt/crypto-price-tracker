---
phase: 12
plan: 1
subsystem: export-reporting
tags: [pdf, report, notify, telegram, email, cli]
dependency_graph:
  requires: [portfolio, exchange, watchlist_db, alerts_db]
  provides: [report, notify, export-cli, summary-cli]
  affects: [cli.py, pyproject.toml]
tech_stack:
  added: [xhtml2pdf]
  patterns: [html-to-pdf, telegram-bot-api, smtp-starttls, multi-channel-notify]
key_files:
  created:
    - src/crypto_price_tracker/report.py
    - src/crypto_price_tracker/notify.py
    - tests/test_report.py
    - tests/test_notify.py
  modified:
    - src/crypto_price_tracker/cli.py
    - tests/test_cli.py
    - pyproject.toml
    - uv.lock
decisions:
  - xhtml2pdf chosen over weasyprint (pure Python, no system deps)
  - rlpycairo excluded via uv override (requires C compiler, only needed for SVG rendering)
  - Telegram uses httpx (existing dep), email uses stdlib smtplib
  - Report skips sections with empty data (no watchlist = no watchlist section)
  - Summary text stays under 4096 chars (Telegram limit) with top-5 holdings truncation
metrics:
  duration: 5 min
  completed: 2026-03-08
  tests_added: 37
  tests_total: 260
---

# Phase 12 Plan 01: Backend report/notify modules + CLI subcommands + unit tests Summary

xhtml2pdf HTML-to-PDF with inline CSS tables, multi-channel notifications (Telegram via httpx, email via smtplib STARTTLS), and two new CLI subcommands (export, summary send).

## What Was Built

### report.py
- `generate_report_html()` -- full HTML report with Portfolio Summary, Holdings, Top Prices, Watchlist, Active Alerts sections. Green (#3fb950) / red (#f85149) P&L coloring. Sections with empty data are omitted.
- `html_to_pdf()` -- xhtml2pdf conversion returning `bytes` via `buffer.getvalue()`.
- `build_summary_text()` -- Telegram-compatible HTML (pre/b/code tags) with top-5 holdings, under 4096 chars.
- `build_summary_html()` -- email HTML table with P&L coloring and total footer row.

### notify.py
- `send_telegram()` -- reads CRYPTO_TELEGRAM_TOKEN and CRYPTO_TELEGRAM_CHAT_ID from env, POST to Bot API via httpx. Returns False if not configured.
- `send_email()` -- reads CRYPTO_SMTP_* env vars, MIMEMultipart("alternative") with STARTTLS. Skips login if no user/password. Returns False if not configured.
- `send_summary()` -- tries all channels, catches errors per channel, returns list of succeeded channel names.

### CLI Subcommands
- `crypto export --format pdf [--output FILE]` -- fetches live prices, generates full report PDF. Auto-names as `crypto-report-YYYY-MM-DD.pdf` if no --output given.
- `crypto summary send` -- builds text + HTML summaries, sends to all configured channels. Prints which channels received the message.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] xhtml2pdf pycairo build failure**
- **Found during:** Step 1 (dependency installation)
- **Issue:** xhtml2pdf -> svglib -> rlpycairo -> pycairo requires a C compiler (gcc/clang) which is not available in this environment.
- **Fix:** Added `[tool.uv] override-dependencies = ["rlpycairo>=0; python_version < '0'"]` to pyproject.toml, effectively excluding rlpycairo/pycairo from the dependency tree. These packages are only needed for SVG rendering in PDFs, which is not used (we generate HTML tables only).
- **Files modified:** pyproject.toml
- **Commit:** 79dfca2

## Test Results

| Test File | Tests | Status |
|-----------|-------|--------|
| tests/test_report.py | 21 | All passing |
| tests/test_notify.py | 12 | All passing |
| tests/test_cli.py | 41 (4 new) | All passing |
| Full suite | 260 | All passing |

## Verification Checklist

- [x] `uv sync` completes without errors (xhtml2pdf installed)
- [x] `python -c "from crypto_price_tracker.report import ..."` succeeds
- [x] `python -c "from crypto_price_tracker.notify import ..."` succeeds
- [x] `python -m pytest tests/test_report.py -x -v` -- 21 passed
- [x] `python -m pytest tests/test_notify.py -x -v` -- 12 passed
- [x] `python -m pytest tests/test_cli.py -x -v` -- 41 passed
- [x] `python -m pytest tests/ -x` -- 260 passed, no regressions

## Commit

- `79dfca2`: feat(12-01): add report/notify modules, export CLI, and summary send command
