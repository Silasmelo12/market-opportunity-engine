# Implementation Plan: Multi-Buy Cycle Trade, Light Theme & Enhanced Professional Simulator

**Branch**: `007-multi-buy-cycle-simulator-and-light-theme` | **Date**: 2026-10-21 | **Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/spec.md)

**Input**: Feature specification from `specs/007-multi-buy-cycle-simulator-and-light-theme/spec.md`

## Summary

This feature extends the quantitative engine and web dashboard with three major enhancements:
1. **Multi-Buy Cycle Accumulation**: In cycle trading mode (`simulate_cycle_trade`), the simulator executes on every confirmed buy signal before a sell signal, accumulating shares, calculating weighted average entry price, and liquidating 100% of accumulated shares upon a confirmed sell signal.
2. **Light Theme (Tema Claro)**: Adds a light mode toggle with an executive fintech palette (clean slate/white, crisp slate text, soft borders), dynamic color updates for TradingView Canvas and Plotly charts, and persistence in `localStorage`.
3. **Institutional Simulator Enhancements**: Upgrades the simulator dashboard with executive KPI cards (Strategy Return vs. Buy & Hold, Win Rate, Profit Factor, Max Drawdown %, Average Entries per Cycle) and an expandable/detailed cycle trades table displaying individual buy entries and exit details.

---

## Technical Context

**Language/Version**: Python 3.11+, Vanilla JavaScript (ES6+), HTML5, CSS3 / Tailwind CSS  
**Primary Dependencies**: FastAPI, Pydantic, NumPy, Pandas, Uvicorn, TradingView Lightweight Charts, Plotly.js  
**Storage**: In-memory cache + Disk cache (`.cache/`) + optional Redis (`redis-py`)  
**Testing**: pytest (`tests/unit/test_accumulation.py`, `tests/api/test_simulate_endpoint.py`)  
**Target Platform**: Web (Modern desktop and mobile browsers, modern Windows/Linux host)  
**Project Type**: Quantitative Trading Analytics Engine & Web Dashboard  
**Performance Goals**: < 100ms simulation execution, seamless zero-lag theme toggling without chart recreation  
**Constraints**: Zero look-ahead bias (strict causal signal execution), atomic git commit per task implemented  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Python FastAPI + Web SPA)**: All simulation logic lives in Python (`src/evaluator/accumulation_simulator.py`), contracts defined in `src/api/schemas.py`, and UI is an HTML/JS SPA in `src/web/`.
- [x] **Principle II (Zero Look-Ahead Bias)**: Multi-buy purchases only execute at known prices (`execution_price` causal to signal bar), and sell signals only liquidate if strictly occurring on or after the buy executions.
- [x] **Principle III (Multi-Market Robustness)**: Applicable to all asset classes (US Equities, B3 Equities, FIIs, Crypto, Commodities).
- [x] **Principle IV (Modular Domain Separation)**: `accumulation_simulator` operates within `evaluator`, `api` orchestrates endpoints, `web` renders interface.
- [x] **Quality Gates (Commit por Tarefa OBRIGATÓRIO)**: Each task in `tasks.md` will receive an atomic git commit upon completion.

---

## Project Structure

### Documentation (this feature)

```text
specs/007-multi-buy-cycle-simulator-and-light-theme/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── simulate-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── evaluator/
│   └── accumulation_simulator.py  # simulate_cycle_trade multi-buy logic & metrics
├── api/
│   ├── app.py                     # /api/simulate endpoint integration
│   └── schemas.py                 # Pydantic models for multi-buy trades & metrics
└── web/
    ├── index.html                 # Theme toggle button, light theme styles, simulator KPI cards
    └── app.js                     # Theme switching logic, chart options updater, simulator render
tests/
└── unit/
    └── test_accumulation.py       # Unit tests for multi-buy cycle simulation
```

---

## Design Artifacts

- **Research**: [research.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/research.md)
- **Data Model**: [data-model.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/data-model.md)
- **API Contracts**: [simulate-contract.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/contracts/simulate-contract.md)
- **Quickstart**: [quickstart.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/quickstart.md)
