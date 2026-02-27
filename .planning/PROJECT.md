# Crypto Price Tracker

## What This Is

A lightweight Python CLI tool that displays current cryptocurrency prices from the Bitvavo API. It shows the top 20 crypto assets in a clean terminal table with color-coded price direction (green/red), and supports subcommands for one-shot viewing, live watching, and individual coin info. All prices in EUR.

## Core Value

Instant, glanceable crypto prices in the terminal — one command, no browser needed.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Display top 20 crypto prices in a formatted terminal table
- [ ] Show price, 24h change %, market cap, and volume per coin
- [ ] Green/red coloring for positive/negative 24h change
- [ ] `crypto prices` subcommand for one-shot price table
- [ ] `crypto watch` subcommand with auto-refresh (default 30s, configurable via `--interval` flag)
- [ ] `crypto info <SYMBOL>` subcommand for single-coin detail view
- [ ] All prices displayed in EUR
- [ ] Dynamic top N coins from Bitvavo API, sorted by market cap (default top 20)
- [ ] Public Bitvavo API (no auth required)
- [ ] uv-managed project with pyproject.toml

### Out of Scope

- Authentication / private Bitvavo endpoints — public data only
- Extended stats (ATH, supply, 24h high/low) — keep info view simple
- Custom coin lists / watchlists — dynamic ranking is sufficient
- Portfolio tracking / balance management — this is a viewer only
- USD or multi-currency support — EUR only
- Mobile or web interface — CLI only

## Context

- Bitvavo is a European crypto exchange with a public REST API for market data
- Public endpoints include ticker price, 24h stats, and market info — no API key needed
- The top N coins are fetched dynamically from Bitvavo and sorted by market cap
- EUR trading pairs are native to Bitvavo (e.g., BTC-EUR)

## Constraints

- **Runtime**: Python 3.12+
- **Project tooling**: uv with pyproject.toml (no setup.py, no requirements.txt)
- **API**: Bitvavo public REST API only, no websockets
- **Dependencies**: Minimal — CLI framework, HTTP client, table renderer, that's it
- **Design**: Clean and minimal terminal output, no unnecessary decoration

## Current Milestone: v1.0 Core CLI

**Goal:** Build the core CLI tool that fetches and displays crypto prices from the Bitvavo API in the terminal.

**Target features:**
- Top 20 crypto price table with color-coded 24h changes
- `crypto prices` one-shot subcommand
- `crypto watch` with configurable auto-refresh
- `crypto info <SYMBOL>` single-coin detail view
- EUR prices via public Bitvavo API
- uv-managed Python project

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bitvavo API over CoinGecko/CMC | User preference, EUR-native exchange | — Pending |
| Dynamic top N from API | More accurate ranking, stays current as market shifts | — Pending |
| Configurable refresh interval | Default 30s, --interval flag for override, balances freshness and API politeness | — Pending |
| Public endpoints only | No auth complexity, market data is freely available | — Pending |
| uv for project management | Modern Python tooling, fast dependency resolution | — Pending |

---
*Last updated: 2026-02-28 after milestone v1.0 started*
