---
description: "Task list for Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira"
---

# Tasks: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Input**: Design documents from `/specs/016-portfolio-manager-simulator/`

**Prerequisites**: [plan.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/plan.md), [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/spec.md), [research.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/research.md), [data-model.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/data-model.md), [contracts/portfolio-api.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/contracts/portfolio-api.md)

**Tests**: Unit, anti-look-ahead, cash conservation, and API contract tests included per specification (SC-002, SC-003, SC-005) and Constitution Quality Gates.

**Organization**: Tasks are grouped by user story (`[US1]`, `[US2]`, `[US3]`) to enable independent implementation, testing, and atomic commits per task.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths and verbatim validation constraints from `data-model.md` are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new portfolio evaluator module skeleton and export bindings.

- [X] T001 Create module skeleton and imports for multi-asset portfolio evaluation in `src/evaluator/portfolio_simulator.py`
- [X] T002 Export portfolio simulator dataclasses and public functions in `src/evaluator/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain entities, Potential Score (0–100) calculator, and Pydantic API schemas that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Define core dataclasses `PortfolioHolding` (`ticker` required uppercase, `shares > 0.0`, `average_buy_price > 0.0`, `current_price > 0.0`, `market_value >= 0.0`, `invested_value >= 0.0`, `unrealized_pnl_pct = ((current_price / average_buy_price) - 1) * 100`, `current_weight_pct` `0.0` a `100.0`, `entry_bar_index >= 0`), `AssetOpportunityProfile` (`potential_score` `0.0` a `100.0` arredondado 1 casa decimal, `active_direction` in `BUY | SELL | NEUTRAL`, `timing_category` in `IDEAL | EXTENDED | LATE`), `PortfolioActionRecommendation` (`action_type` in `BUY | SELL_FULL | SELL_PARTIAL_REBALANCE | ROTATE_OUT | ROTATE_IN | HOLD`, `recommended_shares_delta` inteiro para `.SA` e até 4 dec. para outros, `target_weight_pct` `0.0` a `max_weight_pct`), `PortfolioLedgerEvent` (`event_id >= 1`, `event_type` in `BUY | SELL_FULL | SELL_PARTIAL_REBALANCE | ROTATE_OUT | ROTATE_IN`, `shares_delta != 0.0`, `cash_after >= 0.0`, `portfolio_equity_after > 0.0`), `PortfolioCurvePoint`, and `PortfolioSimulationResult` in `src/evaluator/portfolio_simulator.py`
- [X] T004 Implement `compute_asset_opportunity_profile` and deterministic `potential_score` (`clip(0.35 * S_win + 0.30 * S_ret + 0.15 * S_dd + 0.20 * S_timing, 0.0, 100.0)`) using `optimize_strategy_pairs` and `classify_timing_status` in `src/evaluator/portfolio_simulator.py`
- [X] T005 [P] Add Pydantic request and response schemas (`PortfolioHoldingInput`, `PortfolioHoldingEvaluatedModel`, `AssetOpportunityProfileModel`, `PortfolioActionRecommendationModel`, `PortfolioAdviseRequest`, `PortfolioAdviseResponse`, `PortfolioLedgerEventModel`, `PortfolioCurvePointModel`, `PortfolioSimulationMetricsModel`, `PortfolioSimulateRequest`, `PortfolioSimulateResponse`) in `src/api/schemas.py`
- [X] T006 Implement universe basket resolution helper `_resolve_portfolio_universe_tickers(universe_category, custom_tickers, holdings_tickers)` with parallel profile evaluation via `ThreadPoolExecutor` in `src/api/server.py`

**Checkpoint**: Foundation ready — User Story 1, User Story 2, and User Story 3 can now be implemented.

---

## Phase 3: User Story 1 - Consultor de Rebalanceamento Hoje & Plano de Ação Acionável (Priority: P1) 🎯 MVP

**Goal**: Allow the user to input available cash (e.g., R$ 10,000.00) and current holdings, select a target universe, and receive an actionable Today's Rebalancing Action Plan (`COMPRAR`, `VENDER TOTAL`, `VENDER PARCIAL / REBALANCEAR`, `ROTACIONAR`, `MANTER`) with exact share quantities, R$ amounts, and current vs. target weights persisted in `localStorage`.

**Independent Test**: Open the "Carteira" tab, set `Caixa Disponível = 10000` (or add existing holdings + cash), select universe `"Destaques"`, click "Gerar Plano de Hoje & Simular Carteira", and verify that actionable recommendations are rendered respecting `max_weight_pct` (e.g. 25%) and strict cash conservation (`projected_cash_after >= 0`).

### Implementation & Tests for User Story 1

- [X] T007 [US1] Implement `advise_portfolio_rebalance` in `src/evaluator/portfolio_simulator.py` enforcing the 3 rebalancing rules (`SELL_FULL` on active champion sell signal, `SELL_PARTIAL_REBALANCE` when `current_weight_pct > max_weight_pct + rebalance_band_pct`, `ROTATE_OUT`/`ROTATE_IN` when a candidate in `IDEAL` timing exceeds a stagnant holding's score by `>= min_rotation_score_delta`), score-weighted buy sizing capped at `max_weight_pct`, and integer share rounding for `.SA` tickers
- [X] T008 [US1] Implement `POST /api/portfolio/advise` endpoint in `src/api/server.py` orchestrating `DataLoader`, parallel `compute_asset_opportunity_profile`, and `advise_portfolio_rebalance`
- [ ] T009 [US1] Add the 5th main navigation tab button (`data-tab="tab-portfolio"` "Carteira") and the `#tab-portfolio` HTML section (Left sidebar with `#portfolio-cash-input`, `#portfolio-holdings-list`, holding add/clear controls, `#portfolio-universe-select`, `#portfolio-custom-tickers-input`, `#portfolio-interval-select`, `#portfolio-period-select`, `#portfolio-max-weight-input`, `#btn-run-portfolio`, and Main section for Today's Action Plan summary cards + `#portfolio-recommendations-tbody`) in `src/web/index.html`
- [ ] T010 [US1] Implement client-side portfolio state management with `localStorage` persistence (`market_engine_portfolio_v1`), contextual hiding of `#global-direction-selector` on `tab-portfolio`, holding list CRUD, `POST /api/portfolio/advise` integration, and rendering of `#portfolio-recommendations-tbody` and `#btn-apply-portfolio-orders` in `src/web/app.js`
- [ ] T011 [P] [US1] Write unit tests for `compute_asset_opportunity_profile` and `advise_portfolio_rebalance` (verifying 100% cash allocation with 25% cap, `.SA` integer lot rounding, `SELL_FULL`, `SELL_PARTIAL_REBALANCE`, `ROTATE_OUT`/`ROTATE_IN`, and strict cash conservation) in `tests/unit/test_portfolio_simulator.py`
- [ ] T012 [P] [US1] Write FastAPI contract tests for `POST /api/portfolio/advise` in `tests/unit/test_api_endpoints.py`

**Checkpoint**: User Story 1 (Consultor de Rebalanceamento Hoje) is fully functional and independently testable.

---

## Phase 4: User Story 2 - Simulador Histórico Multiativos de Carteira com Rebalanceamento Dinâmico (Priority: P2)

**Goal**: Simulate bar-by-bar historical multi-asset portfolio management starting with initial capital (e.g., R$ 10,000.00), dynamically allocating to top-scoring assets on their champion buy signals, executing full exits on top signals, partial rebalancing above cap + band, and tactical rotations, with strict Zero Look-Ahead Bias and comparison against an Equal-Weight Buy & Hold basket benchmark.

**Independent Test**: Run `POST /api/portfolio/simulate` (or click "Gerar Plano de Hoje & Simular Carteira" in the UI) with `initial_capital = 10000`, universe `"featured"`, period `"2y"`, and verify the 6 institutional KPI cards and the chronological ledger table (`#portfolio-ledger-tbody`).

### Implementation & Tests for User Story 2

- [ ] T013 [US2] Implement `simulate_portfolio_multi_asset` in `src/evaluator/portfolio_simulator.py` with unified chronological `master_timeline`, causal forward-fill mark-to-market pricing, Equal-Weight Buy & Hold benchmark curve, bar-by-bar precedence (`SELL_FULL` -> `SELL_PARTIAL_REBALANCE` -> `ROTATE_OUT`/`ROTATE_IN` -> `BUY`), and consolidated KPIs (`final_equity`, `net_profit`, `total_return_pct`, `benchmark_return_pct`, `alpha_vs_benchmark_pct`, `max_drawdown_pct`, `win_rate_pct`, `profit_factor`, `rebalance_rotations_count`)
- [ ] T014 [US2] Implement `POST /api/portfolio/simulate` endpoint in `src/api/server.py`
- [ ] T015 [US2] Add the 6 Portfolio Simulator KPI cards, Current/Final Holdings summary table, and Chronological Ledger table (`#portfolio-ledger-tbody`) markup inside `#tab-portfolio` in `src/web/index.html`
- [ ] T016 [US2] Integrate `POST /api/portfolio/simulate` in `src/web/app.js` to populate the 6 KPI cards and render the chronological operations & rebalancing ledger table (`#portfolio-ledger-tbody`)
- [ ] T017 [P] [US2] Write unit tests for `simulate_portfolio_multi_asset` (including strict Zero Look-Ahead Bias truncation test verifying decisions up to bar $t$ are identical when $t+1 \dots N$ are truncated, cash conservation, and API contract test for `POST /api/portfolio/simulate`) in `tests/unit/test_portfolio_simulator.py` and `tests/unit/test_api_endpoints.py`

**Checkpoint**: User Stories 1 and 2 are both functional and independently verified.

---

## Phase 5: User Story 3 - Visualização Gráfica de Evolução Patrimonial, Alocação de Ativos e Ergonomia Temática (Priority: P3)

**Goal**: Provide interactive Plotly.js charts for Portfolio Equity Evolution (Managed Portfolio vs. Equal-Weight Buy & Hold vs. Cash) and Asset Allocation Breakdown, Opportunity Score Ranking table, and full Light/Dark theme reactivity.

**Independent Test**: Run a portfolio analysis & simulation in `#tab-portfolio`, inspect the Equity Curve chart, Allocation chart, and Opportunity Ranking table, and toggle Light/Dark mode (`#btn-theme-toggle`) verifying instant theme adaptation.

### Implementation for User Story 3

- [ ] T018 [US3] Add containers for the Portfolio Equity Evolution chart (`#portfolio-equity-chart`), Portfolio Allocation Breakdown chart (`#portfolio-allocation-chart`), and Universe Opportunity Score Ranking table (`#portfolio-ranking-tbody`) inside `#tab-portfolio` in `src/web/index.html`
- [ ] T019 [US3] Implement `renderPortfolioEquityChart`, `renderPortfolioAllocationChart`, and `renderPortfolioOpportunityRanking` using Plotly.js with automatic re-rendering on Light/Dark theme toggle in `src/web/app.js`
- [ ] T020 [P] [US3] Add semantic badge styles (`COMPRAR`, `VENDER TOTAL`, `VENDER PARCIAL / REBALANCEAR`, `ROTACIONAR`, `MANTER`), Potential Score progress bar styles, and Light Mode (`body.light-theme`) overrides for `#tab-portfolio` in `src/web/styles.css`
- [ ] T021 [US3] Add UI/DOM structural verification tests for `#tab-portfolio`, navigation tab presence, and direction selector hiding in `tests/unit/test_api_endpoints.py`

**Checkpoint**: All 3 user stories are complete, styled for Dark & Light themes, and covered by automated tests.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all stories and quickstart verification.

- [ ] T022 Run full `pytest` test suite to verify 100% pass rate with zero regressions across existing and new tests
- [ ] T023 Validate all end-to-end scenarios defined in `specs/016-portfolio-manager-simulator/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1: T001–T002)**: No dependencies — starts immediately.
- **Foundational (Phase 2: T003–T006)**: Depends on Phase 1 — BLOCKS all user stories.
- **User Story 1 (Phase 3: T007–T012)**: Depends on Phase 2 — Delivers the MVP Today's Rebalancing Advisor (`POST /api/portfolio/advise` + UI Action Plan).
- **User Story 2 (Phase 4: T013–T017)**: Depends on Phase 2 (and shares UI tab from US1) — Delivers the Historical Multi-Asset Portfolio Simulator (`POST /api/portfolio/simulate` + KPIs + Ledger).
- **User Story 3 (Phase 5: T018–T021)**: Depends on US1 & US2 data payloads — Delivers interactive Plotly charts, Opportunity Ranking table, and Light/Dark theme polish.
- **Polish (Phase 6: T022–T023)**: Depends on Phases 3–5 completion.

### Parallel Opportunities

- `T004` (`src/evaluator/portfolio_simulator.py`) and `T005` (`src/api/schemas.py`) can be developed in parallel.
- `T011` (`tests/unit/test_portfolio_simulator.py`) and `T012` (`tests/unit/test_api_endpoints.py`) can run in parallel.
- `T019` (`src/web/app.js`) and `T020` (`src/web/styles.css`) can be developed in parallel.

---

## Parallel Example: User Story 1

```bash
# Run unit and API contract tests for User Story 1 in parallel:
Task: "T011 [P] [US1] Write unit tests for compute_asset_opportunity_profile and advise_portfolio_rebalance in tests/unit/test_portfolio_simulator.py"
Task: "T012 [P] [US1] Write FastAPI contract tests for POST /api/portfolio/advise in tests/unit/test_api_endpoints.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1: Consultor de Rebalanceamento Hoje).
3. Validate `POST /api/portfolio/advise` and the interactive Action Plan in `#tab-portfolio`.

### Incremental Delivery

1. **Increment 1 (P1)**: Today's Actionable Rebalancing Advisor + Portfolio Editor (`localStorage`).
2. **Increment 2 (P2)**: Causal Multi-Asset Historical Backtester + Institutional KPIs + Operations Ledger.
3. **Increment 3 (P3)**: Plotly Equity & Allocation Charts + Opportunity Score Ranking + Light/Dark Theme support.
4. **Governance Note**: Per Constitution v2.0.0, each completed task (`T001` through `T023`) MUST generate an individual git commit immediately after being marked `[X]` during `/speckit-implement`.
