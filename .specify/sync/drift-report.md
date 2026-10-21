# Spec Drift Report

Generated: 2026-10-21T12:30:51.884289+00:00
Project: Market Opportunity & Bottom Statistical Engine

## Summary

| Category | Count |
|---|---|
| Specs Analyzed | 4 |
| Requirements Checked | 57 |
| Aligned | 53 (93.0%) |
| Drifted | 4 (7.0%) |
| Not Implemented | 0 (0.0%) |
| Unspecced Code Features | 5 |

## Detailed Findings

### Spec: 001-market-opportunity-engine - Market Opportunity & Bottom Statistical Engine

#### Aligned
- FR-001 (Multi-asset selection: US, BR, FIIs, Crypto, Commodities)
- FR-002 (Timeframes: 1d, 1wk)
- FR-003 (Local caching disk/memory)
- FR-004 (Proprietary Reversal 4 variants Buy machine, gap & retest)
- FR-005 (Configurable N, M, tol parameters)
- FR-006 (DCA Dynamic SMA200 / RSI14)
- FR-007 (Rebalancing Fixed Income vs Equities)
- FR-008 (Rebalancing Relative Strength Z-Score 60)
- FR-009 (Value Proxy / Fundamentalist Mayer Multiple)
- FR-010 (Double Bottom BOS / CHoCH)
- FR-011 (Wyckoff Spring / Liquidity Sweep)
- FR-012 (8 classic MQL5 candlestick reversal patterns)
- FR-013 (Holder evaluation on window X: N, Win Rate %, Forward Return %, MAE %, Efficiency Score)
- FR-014 (Zero Look-Ahead Bias)
- FR-015 (Interactive candlestick chart with trade markers and reference lines)
- FR-016 (Efficiency ranking and Risk x Return scatter plot)
- FR-017 (Current state monitor / active reference line)
- SC-001 (Processing speed < 2.5s)
- SC-002 (State machine execution < 100ms)
- SC-003 (100% auditable anti-lookahead bias)
- SC-004 (Timeframe switching < 1.5s via cache)
- SC-005 (100% of tested assets calculated without unhandled failures)

### Spec: 002-institutional-ux-radar-simulator - Institutional UX/UI Design, Multi-Timeframe Intraday, Radar Scanner, Simulador de Acumulacao e Guia de Estrategias

#### Aligned
- FR-001 (FinTech Dark design system: #0B0E14, #151924, #262B38, #00E676, #FF5252)
- FR-002 (4 Navigation tabs: Radar, Terminal, Simulador, Playbook)
- FR-003 (Friendly Portuguese names dictionary)
- FR-004 (Radar scanner with timing traffic light: Ideal, Extended, Late)
- FR-005 (Interactive asset selection in Radar to load into Terminal)
- FR-006 (Ranking & Scatter chart improvements)
- FR-007 (Accumulation simulator with capital, net profit, profitability, average price)
- FR-008 (Playbook educational guide with strategy formulas and psychology)
- FR-009 (Intraday timeframes & resampling: 5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d, 1wk)
- FR-010 (Preserve math contracts & unit tests)
- SC-001 (Radar initial rendering)
- SC-003 (100% technical identifiers replaced by friendly names)
- SC-004 (100% tests passing)
- SC-005 (Bar charts percentage labels never clipped)

#### Drifted
- **FR-002 / FR-007 / SC-002**: Spec says "UI implemented in Streamlit using @st.fragment, st.session_state and st.column_config" but code does "Migrated to high-performance decoupled FastAPI + Native HTML5/JS Canvas SPA in Feature 003"
  - Location: `src/api/server.py and src/web/`
  - Severity: `moderate`

### Spec: 003-fastapi-tradingview-terminal - FastAPI High-Performance Engine + 60fps TradingView Web Terminal & Granular Strategy Controls

#### Aligned
- FR-001 (Decoupled FastAPI backend serving static SPA on /)
- FR-002 (REST JSON endpoints: /api/strategies, /api/analyze, /api/radar, /api/simulate, /api/tickers)
- FR-003 (TradingView Lightweight Charts 60fps Canvas + Plotly.js)
- FR-004 (100% Client-side 0ms strategy filtering without network requests)
- FR-005 (Granular checkboxes & accordion groups with Select All / Deselect All)
- FR-006 (Timeframe selection bar: 5m to 1wk)
- FR-007 (4 Instant tabs layout)
- FR-008 (Strict preservation of mathematical engines and anti-lookahead tests)
- SC-001 (Client-side interactive filtering < 16ms / 60fps)
- SC-002 (GET /api/analyze response speed)
- SC-003 (48 strategies catalog completeness)
- SC-004 (Unit tests passing)
- SC-005 (Zero dependency on Node.js / npm for execution)

#### Drifted
- **FR-004 / FR-005**: Spec says "All 24/48 strategies start checked by default upon loading" but code does "All 48 strategies start completely UNCHECKED by default per user request; markers activate on user check or Radar opportunity click"
  - Location: `src/web/app.js:20 and src/web/index.html`
  - Severity: `minor`
- **FR-002 (/api/tickers)**: Spec says "Total monitored basket consists of 151 tickers across 7 categories" but code does "Expanded to 153 tickers with inclusion of B3 Mini Contracts (^BVSP Mini Indice, USDBRL=X Mini Dolar)"
  - Location: `src/api/server.py:61-75 and tests/unit/test_api_endpoints.py:70`
  - Severity: `minor`

### Spec: 004-bidirectional-top-bottom-engine - Bidirectional Market Opportunity & Top/Bottom Statistical Engine (Modos Compra, Venda e Ambos)

#### Aligned
- FR-001 (SignalRecord.direction contract: explicit BUY or SELL)
- FR-002 (Proprietary Reversal Sell Machine with 4 variants, gap fills & resistance state machine)
- FR-003 (Classic & MQL5 Sell Engines: 6 quantitative + 14 candlestick patterns = 24 top strategies)
- FR-004 (Directional Evaluator: inverse return formula & inverse MAE calculation for SELL)
- FR-005 (Directional Timing Classifier for tops with Ideal, Extended, Late)
- FR-006 (UI 3-Way Direction Segmented Control: Compra | Venda | Ambos)
- FR-007 (Lightweight Charts Multi-Direction Markers & resistance reference lines)
- Invariant 1 (Zero Look-Ahead Bias on SELL orders)
- Invariant 2 (Backward Compatibility with existing tests and API endpoints)
- Invariant 3 (60fps performance on direction switching)

#### Drifted
- **FR-005 (Commodity Naming)**: Spec says "Commodities identified by generic labels (e.g. Ouro Futuro, GC=F)" but code does "Updated to international dual naming: Gold (Ouro / XAUUSD), Silver (Prata), Crude Oil WTI (Petroleo)"
  - Location: `src/ui/theme.py:27-46 and src/web/app.js:77-98`
  - Severity: `minor`

### Unspecced Code Features

| Feature | Location | Approx Lines | Suggested Spec |
|---|---|---|---|
| B3 Futures & Commodity Ticker Aliases | `src/data_loader/fetcher.py:32 and src/web/app.js:34` | 35 | `spec-005-futures-aliases-and-mobile-ux` |
| Mobile Touch-Scroll Optimization & Unconstrained Flow | `src/web/styles.css:260-280 and src/web/index.html:417` | 40 | `spec-005-futures-aliases-and-mobile-ux` |
| Radar Category Filter Pills with Client Caching | `src/web/index.html:136-145 and src/web/app.js:650-680` | 65 | `spec-005-futures-aliases-and-mobile-ux` |
| Radar to Terminal Interactive Auto-Configuring Deep Link | `src/web/app.js:774-818` | 45 | `spec-005-futures-aliases-and-mobile-ux` |
| Strategy Pair Optimization Grid Search in Portfolio Simulator | `src/evaluator/portfolio_simulator.py:165-240 and src/api/server.py:800-840` | 115 | `spec-005-futures-aliases-and-mobile-ux` |

## Inter-Spec Conflicts

- Spec 002 (Streamlit Architecture) vs Spec 003 (FastAPI SPA Architecture): Spec 003 explicitly superseded Spec 002 UI layer while preserving 100% of the mathematical algorithms.

## Recommendations

1. **Backfill Spec 005**: Create `specs/005-futures-aliases-and-mobile-ux/spec.md` to formalize the newly added features (WIN/WDO/XAUUSD aliases, mobile touch-scroll unconstrained flow, radar category pills, and strategy pair optimizer).
2. **Synchronize Spec 003 with UI Defaults**: Update `specs/003-fastapi-tradingview-terminal/spec.md` to document that strategy filters now default to unchecked, improving user control upon asset analysis.
3. **Archive Streamlit Legacy Spec 002 Artifacts**: Add a formal deprecation note in Spec 002 clarifying that Streamlit UI components were superseded by Spec 003 FastAPI SPA.
4. **Use speckit-sync-propose / speckit-sync-apply**: Use the Spec Sync workflow to automatically apply these documentation synchronizations across the `specs/` directory.