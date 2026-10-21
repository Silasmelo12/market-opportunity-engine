# Feature Specification: B3 Futures & Commodity Aliases, Mobile UX Optimization, and Simulator Strategy Pair Optimizer

**Feature Branch**: `005-futures-aliases-and-mobile-ux`
**Created**: 2026-10-21
**Status**: Backfilled
**Source**: Generated from existing implementation via `speckit.sync.backfill`

## Backfill Notice

> [!NOTE]
> This specification was generated from the existing codebase via `speckit.sync.backfill`.
> It documents the implemented behavior of the recent platform enhancements, including B3 mini-contract aliases, mobile viewport optimizations, category filtering, and portfolio simulation optimization.

---

## User Scenarios & Testing

### User Story 1 - Shorthand Ticker Aliases for Futures & Commodities (Priority: P1)

As a trader or investor, I want to type common market abbreviations such as `WIN`, `WDO`, `XAUUSD`, or `GOLD` directly into the asset selector
so that I can instantly analyze B3 futures and gold without needing to know internal Yahoo Finance ticker symbology (`^BVSP`, `USDBRL=X`, `GC=F`).

**Acceptance Scenarios**:
1. **Given** the user enters `WIN` in the asset input, **When** they submit or select the asset, **Then** the system resolves the ticker to `^BVSP` (Mini Índice / Ibovespa) and displays price in points (`pts`).
2. **Given** the user enters `WDO` in the asset input, **When** they submit or select the asset, **Then** the system resolves the ticker to `USDBRL=X` (Mini Dólar) and displays price formatted with 4 decimals.
3. **Given** the user enters `XAUUSD` or `GOLD`, **When** the analysis runs, **Then** the system loads Gold Futures `GC=F` seamlessly.

---

### User Story 2 - Smooth and Unconstrained Mobile Smartphone Scrolling (Priority: P1)

As a mobile user navigating the platform on a smartphone (e.g. Poco X7 Pro), I want to touch and swipe anywhere on the 48-strategy list without the screen freezing
so that I can easily scroll through the entire page naturally without inner scroll traps.

**Acceptance Scenarios**:
1. **Given** the user toggles open the 48-strategy filter on a mobile screen (< 1024px), **When** they swipe up or down touching directly on strategy checkboxes or headers, **Then** the entire page scrolls smoothly without getting trapped.
2. **Given** the mobile view, **When** the strategy accordion is closed, **Then** the mobile toggle button shows clear open/close state indicators.

---

### User Story 3 - Clean Default Terminal State with Selective Strategy Activation (Priority: P2)

As an analyst inspecting a chart, I want all strategy filters to start completely unchecked when the terminal opens
so that the candlestick chart starts clean and uncluttered, allowing me to selectively turn on only the strategies I want to observe.

**Acceptance Scenarios**:
1. **Given** the user opens the Terminal tab, **When** no strategy has been checked, **Then** 0 markers are displayed on the chart and the counter shows `Marcadores visíveis: 0`.
2. **Given** the user checks a specific strategy box (or clicks an opportunity from the Radar), **Then** only that strategy's buy or sell markers immediately render on the chart.

---

### User Story 4 - Multi-Category Exploration in Radar with Client Caching (Priority: P2)

As an active market scanner, I want to filter the Radar table by asset class (Destaques, Ações Brasil, FIIs, Ações EUA, Commodities, Forex, Cripto, Todos)
so that I can focus on specific sectors with fast, cached switching.

**Acceptance Scenarios**:
1. **Given** the Radar view, **When** the user clicks a category pill, **Then** the table updates instantly using client-side category caching when available.
2. **Given** an opportunity row in the Radar table, **When** the user clicks the asset name or action button, **Then** the application switches to the Terminal, sets the active timeframe, and automatically pre-activates the corresponding strategy.

---

### User Story 5 - Simulation Pair Optimization (Priority: P3)

As a quantitative backtester, I want the system to test multiple combinations of Buy and Sell strategies automatically
so that I can identify the top-performing strategy pairings for any given asset over historical periods.

**Acceptance Scenarios**:
1. **Given** an asset in the Simulator tab, **When** the user clicks "Otimizar Combinações", **Then** the backend evaluates buy/sell strategy combinations and ranks the Top 5 configurations by net profit and return.

---

## Requirements

### Functional Requirements

- **FR-001 (Ticker Aliases Engine)**:
  - The backend (`src/data_loader/fetcher.py`) and frontend (`src/web/app.js`) MUST implement a unified `TICKER_ALIASES` mapping:
    - `WIN` -> `^BVSP`
    - `WDO` -> `USDBRL=X`
    - `XAUUSD` -> `GC=F`
    - `GOLD` -> `GC=F`
  - Any user input matching an alias MUST be automatically resolved before querying data or executing simulation.

- **FR-002 (B3 Mini Contracts & Points/Forex Formatting)**:
  - The catalog of monitored assets MUST include `^BVSP` (Mini Índice / WIN) in Ações Brasil and `USDBRL=X` (Mini Dólar / WDO) in Forex, bringing the total catalog to 153 assets.
  - Price formatting (`formatPrice`) MUST display `^BVSP` prices as integer points with suffix `pts` (e.g. `208.500 pts`) and `USDBRL=X` / Forex with 4 decimal places.

- **FR-003 (Dual International Commodity Naming)**:
  - Commodities in `theme.py` and `app.js` MUST be labeled with dual international and localized names (e.g., `Gold (Ouro / XAUUSD)`, `Silver (Prata)`, `Crude Oil WTI (Petróleo)`).

- **FR-004 (Mobile Scroll Architecture)**:
  - On viewport widths below 1024px (`@media (max-width: 1023px)`), the strategy filter wrapper `#strategies-wrapper-collapsible.mobile-open` and `#strategy-accordions-container` MUST NOT use fixed `max-height` or `overflow-y: auto` with `overscroll-behavior: contain`.
  - The elements MUST expand into the natural document flow (`overflow: visible !important; height: auto !important; touch-action: pan-y !important;`) so that touch drag gestures scroll the parent screen without entrapment.

- **FR-005 (Default Unselected Filters)**:
  - All 48 strategy checkboxes in `index.html` MUST start unchecked (`checked = false`).
  - The global state `activeStrategies` in `app.js` MUST initialize as `new Set([])`.
  - When `activeStrategies.size === 0`, the canvas series MUST clear all markers and render empty summary graphs.

- **FR-006 (Radar Category Pills & Deep Linking)**:
  - Radar tab MUST provide category filter buttons (`featured`, `Ações Brasil`, `FIIs Brasil`, `Ações EUA`, `Commodities`, `Forex`, `Criptomoedas`, `all`).
  - Clicking any ticker row MUST route to the Terminal, synchronize timeframe, and activate the clicked strategy.

- **FR-007 (Simulator Strategy Pair Optimizer)**:
  - The API MUST provide `/api/simulate/optimize` running a grid search across viable buy and sell strategy pairs to produce top combination rankings.

---

## Key Entities

- **Ticker Alias Record**: Mapping between user-friendly colloquial shorthand strings and canonical Yahoo Finance symbols.
- **Category Filter State**: Client-side state tracking active radar category and storing categorized scan results in memory.
- **Optimized Strategy Pair**: Data transfer object containing Buy Strategy ID, Sell Strategy ID, Total Invested, Final Capital, Net Profit, and ROI %.

---

## Dependencies

- **Spec 001**: Mathematical base strategies and anti-lookahead execution rules.
- **Spec 003**: FastAPI backend and 60fps TradingView canvas architecture.
- **Spec 004**: Bidirectional BUY/SELL strategies and 48-strategy catalog.

---

## Success Criteria

- **SC-001**: Ticker alias resolution occurs in < 1ms with 100% case-insensitivity.
- **SC-002**: Mobile swipe gestures anywhere inside the strategy accordion scroll smoothly without lag or lockup.
- **SC-003**: 100% of existing unit and integration tests (46 tests) pass without regression.
- **SC-004**: Zero emojis across all interface text, labels, and code.

---

## Implementation Notes

- Yahoo Finance does not support `WIN=F` or `WDO=F` directly; therefore, `^BVSP` (Ibovespa index) and `USDBRL=X` (USD/BRL currency spot) serve as accurate proxies.
- Mobile scroll trap was eliminated by avoiding nested scroll boxes on viewports under 1024px.
