# API Contracts: Multi-Buy Cycle Trade & Light Theme

**Feature**: `007-multi-buy-cycle-simulator-and-light-theme`  
**Endpoint**: `POST /api/simulate`  

---

## 1. Request Contract

`POST /api/simulate`

```json
{
  "ticker": "PETR4.SA",
  "interval": "1d",
  "period": "2y",
  "strategy_sub_ids": ["buy_double_bottom_inverted", "prop_retest_standard"],
  "simulation_mode": "cycle_trade",
  "initial_capital": 1000.0,
  "contribution_amount": 500.0,
  "start_date": "2024-01-01",
  "end_date": "2026-10-20"
}
```

### Request Fields
- `ticker` (str, required): Target asset ticker.
- `interval` (str, default `"1d"`): Timeframe.
- `period` (str, default `"2y"`): Historical window.
- `strategy_sub_ids` (List[str], optional): Strategies to include.
- `simulation_mode` (str, default `"cycle_trade"`): `"cycle_trade"` (Compra -> Venda) or `"continuous_dca"` (Acúmulo Contínuo).
- `initial_capital` (float, default `1000.0`): Capital allocated for the first buy entry or base portfolio.
- `contribution_amount` (float, default `500.0`): Capital added on each subsequent buy signal within an open cycle.

---

## 2. Response Contract

`200 OK`

```json
{
  "ticker": "PETR4.SA",
  "period": "2y",
  "metrics": {
    "simulation_mode": "cycle_trade",
    "total_invested": 3000.0,
    "final_portfolio_value": 3650.0,
    "total_profit_loss": 650.0,
    "total_return_pct": 21.67,
    "profit_factor": 2.45,
    "max_drawdown_pct": 6.82,
    "total_trades_count": 2,
    "winning_trades_count": 2,
    "losing_trades_count": 0,
    "win_rate_pct": 100.0,
    "avg_trade_return_pct": 10.83,
    "avg_entries_per_cycle": 2.5,
    "avg_trade_bars": 18.0,
    "buy_and_hold_return_pct": 14.20,
    "shares_accumulated": 0.0,
    "average_cost_price": 0.0,
    "current_market_price": 38.50,
    "dca_regular_final_value": 3200.0,
    "alpha_vs_dca_pct": 14.06
  },
  "curve": [
    {
      "date": "2024-01-05",
      "invested": 1000.0,
      "equity": 1020.0
    }
  ],
  "trades": [
    {
      "trade_id": 1,
      "status": "FECHADO",
      "num_entries": 3,
      "total_invested": 2000.0,
      "total_shares": 65.42,
      "average_buy_price": 30.57,
      "first_buy_date": "2024-02-10",
      "last_buy_date": "2024-03-01",
      "sell_strategy_sub_id": "sell_double_bottom_inverted",
      "sell_strategy_label": "Topo Falso + BOS (Venda)",
      "sell_date": "2024-03-25",
      "sell_price": 35.10,
      "sell_bar_index": 55,
      "exit_capital": 2296.24,
      "profit_loss": 296.24,
      "return_pct": 14.81,
      "duration_bars": 30,
      "buy_entries": [
        {
          "entry_id": 1,
          "date": "2024-02-10",
          "bar_index": 25,
          "price": 30.00,
          "shares": 33.33,
          "capital": 1000.0,
          "strategy_sub_id": "prop_retest_standard",
          "strategy_label": "Negação + Reteste"
        },
        {
          "entry_id": 2,
          "date": "2024-02-22",
          "bar_index": 35,
          "price": 30.80,
          "shares": 16.23,
          "capital": 500.0,
          "strategy_sub_id": "buy_double_bottom_classic",
          "strategy_label": "Fundo Duplo Clássico"
        },
        {
          "entry_id": 3,
          "date": "2024-03-01",
          "bar_index": 41,
          "price": 31.50,
          "shares": 15.87,
          "capital": 500.0,
          "strategy_sub_id": "prop_retest_standard",
          "strategy_label": "Negação + Reteste"
        }
      ]
    }
  ]
}
```

---

## 3. Frontend Theme Contract (Client DOM State)

- **Attribute**: `document.documentElement.setAttribute('data-theme', 'light' | 'dark')`
- **LocalStorage Key**: `'terminal_theme' -> 'light' | 'dark'`
- **Default Value**: `'dark'` (if not set in `localStorage`)
- **Theme Event**: Dispatches custom event `themeChanged` with `{ detail: { theme: 'light' | 'dark' } }` to synchronize Lightweight Charts and Plotly instances without reloading the document.
