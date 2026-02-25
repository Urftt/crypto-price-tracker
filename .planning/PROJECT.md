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
- [ ] `crypto watch` subcommand with 10-second auto-refresh
- [ ] `crypto info <SYMBOL>` subcommand for single-coin detail view
- [ ] All prices displayed in EUR
- [ ] Hardcoded top 20 coin list (BTC, ETH, SOL, etc.)
- [ ] Public Bitvavo API (no auth required)
- [ ] uv-managed project with pyproject.toml

### Out of Scope

- Authentication / private Bitvavo endpoints — public data only
- Extended stats (ATH, supply, 24h high/low) — keep info view simple
- Dynamic coin list from API — hardcoded top 20 is sufficient
- Portfolio tracking / balance management — this is a viewer only
- USD or multi-currency support — EUR only
- Mobile or web interface — CLI only

## Context

- Bitvavo is a European crypto exchange with a public REST API for market data
- Public endpoints include ticker price, 24h stats, and market info — no API key needed
- The top 20 list will be maintained as a constant in the code (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, LINK, MATIC, SHIB, TRX, UNI, LTC, ATOM, XLM, BCH, NEAR, APT)
- EUR trading pairs are native to Bitvavo (e.g., BTC-EUR)

## Constraints

- **Runtime**: Python 3.12+
- **Project tooling**: uv with pyproject.toml (no setup.py, no requirements.txt)
- **API**: Bitvavo public REST API only, no websockets
- **Dependencies**: Minimal — CLI framework, HTTP client, table renderer, that's it
- **Design**: Clean and minimal terminal output, no unnecessary decoration

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bitvavo API over CoinGecko/CMC | User preference, EUR-native exchange | — Pending |
| Hardcoded top 20 list | Simpler than dynamic ranking, no extra API calls | — Pending |
| 10-second refresh for watch mode | User prefers near-real-time updates | — Pending |
| Public endpoints only | No auth complexity, market data is freely available | — Pending |
| uv for project management | Modern Python tooling, fast dependency resolution | — Pending |

---
*Last updated: 2026-02-25 after initialization*
