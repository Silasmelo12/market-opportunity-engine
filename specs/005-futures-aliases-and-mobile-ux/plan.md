# Implementation Plan: B3 Futures & Commodity Aliases, Mobile UX Optimization, and Simulator Strategy Pair Optimizer

**Branch**: `005-futures-aliases-and-mobile-ux` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)
**Context**: Backfilled from existing implementation. Documents current architecture and design decisions.

## Summary

This feature set formalizes four key areas of enhancement:
1. Shorthand alias resolution for Brazilian futures and precious metals (`WIN`, `WDO`, `XAUUSD`, `GOLD`).
2. Mobile viewport optimizations ensuring unconstrained vertical page scrolling on smartphones.
3. Clean default state for strategy filters on terminal initialization (all 48 unchecked).
4. Portfolio simulator strategy pair grid search optimization (`/api/simulate/optimize`).

---

## Technical Context

**Language/Version**: Python 3.11+ / Vanilla ECMAScript 2022+ / HTML5 Canvas
**Primary Dependencies**:
- `yfinance` — Market data provider
- `FastAPI` / `Uvicorn` — High-performance asynchronous backend
- `TradingView Lightweight Charts` — 60fps canvas charting engine
- `Plotly.js` — Statistical distribution and ranking charts

**Performance Goals**:
- Alias resolution: < 1ms
- Mobile touch drag bubbling: 60fps native browser compositor
- 0ms client-side filter reactivity on checkbox toggling

---

## Architecture

### Component Hierarchy

```text
Frontend SPA (Vanilla JS + Lightweight Charts)
├── Ticker Resolver (resolveTicker: WIN -> ^BVSP, WDO -> USDBRL=X)
├── Strategy Filter Controller (state.activeStrategies = empty Set by default)
├── Responsive Mobile Container (overflow: visible; touch-action: pan-y)
└── Simulator Pair Optimization Controller
    └── POST /api/simulate/optimize
        └── FastAPI Backend (server.py)
            └── portfolio_simulator.py (optimize_strategy_pairs)
```

### Key Design Decisions

1. **Client & Server Symmetric Alias Resolution**:
   - `TICKER_ALIASES` is implemented identically in `src/data_loader/fetcher.py` and `src/web/app.js`.
   - Ensures that whether a ticker is sent via API query or entered in the UI input, the canonical symbol is resolved before caching or fetching.

2. **Elimination of Nested Scroll Containers on Mobile**:
   - Rather than having a fixed `max-height: 65vh` box with `overscroll-behavior: contain` inside a scrollable tab, the mobile view lets the strategy accordion expand naturally into the parent tab's scroll height.
   - This eliminates touch gesture hijacking on iOS Safari and Android Chrome.

3. **Opt-in Strategy Activation**:
   - Starting with an empty set (`new Set([])`) avoids overwhelming the user with 48 potential overlays at once, letting the user inspect raw price action or selectively activate setups.

---

## Project Structure

```text
src/
├── data_loader/
│   └── fetcher.py               # TICKER_ALIASES and canonical ticker normalization
├── ui/
│   └── theme.py                 # ASSET_NAMES_PT dual commodity and B3 futures naming
├── api/
│   ├── server.py                # Endpoints (/api/tickers, /api/simulate/optimize)
│   └── schemas.py               # Data models
├── evaluator/
│   └── portfolio_simulator.py   # optimize_strategy_pairs grid search logic
└── web/
    ├── index.html               # Unchecked checkboxes, category pills, mobile toggle
    ├── styles.css               # Responsive mobile-open layout & touch-action rules
    └── app.js                   # Client-side state, formatPrice, resolveTicker
tests/
└── unit/
    └── test_api_endpoints.py    # Total catalog count and asset name tests
```

---

## Testing

- Unit tests in `tests/unit/test_api_endpoints.py` validating 153 total assets and canonical name resolution.
- Anti-lookahead and simulation regression suites in `tests/unit/`.
