# Quickstart: Multi-Buy Cycle Trade & Light Theme Validation

**Feature**: `007-multi-buy-cycle-simulator-and-light-theme`  
**Date**: 2026-10-21  

---

## 1. Setup & Environment Verification

Execute from repository root:

```powershell
# Activate virtual environment if present, or run with standard python
python -m pytest tests/unit/test_accumulation.py -v
```

---

## 2. Validation Scenario 1: Multi-Buy Cycle Accumulation Unit Test

Verifies that when multiple consecutive buy signals occur before a sell signal:
1. Every buy signal executes and adds shares.
2. The average buy price is correctly calculated as total invested / total shares.
3. The sell signal liquidates all shares and calculates PnL correctly based on the weighted average price.

```powershell
python -m pytest tests/unit/test_accumulation.py -k "test_simulate_cycle_trade_multi_buy" -v
```

---

## 3. Validation Scenario 2: API Contract & Extended Metrics

Starts the server and requests a simulation with multi-buy enabled:

```powershell
# Run the FastAPI server in background or test via TestClient
python -c "from fastapi.testclient import TestClient; from src.api.app import app; c = TestClient(app); r = c.post('/api/simulate', json={'ticker':'PETR4.SA','simulation_mode':'cycle_trade'}); print(r.status_code, r.json()['metrics'])"
```

Expected output:
- Status `200`
- JSON metrics including `profit_factor`, `max_drawdown_pct`, `win_rate_pct`, `buy_and_hold_return_pct`.

---

## 4. Validation Scenario 3: Light Theme UI Verification

1. Start the API server:
   ```powershell
   python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
   ```
2. Open `http://localhost:8000` in the browser.
3. Click the Theme toggle button (Sun/Moon icon) in the top-right header:
   - Interface switches from dark slate background to crisp fintech light background (`#F8FAFC`).
   - Cards and tables change to white background with subtle gray borders (`#E2E8F0`).
   - TradingView Candlestick Chart background switches to white with dark gray text and soft grid lines.
   - Plotly equity chart updates background and font colors.
4. Refresh the page: the light theme remains active without dark flash (`localStorage` persistence).
5. Switch to the "Simulador" tab:
   - High-level KPI cards show Strategy Return, Buy & Hold comparison, Win Rate, and Profit Factor.
   - Cycle trades table clearly shows the number of entries per cycle, average entry price, and exit price.
