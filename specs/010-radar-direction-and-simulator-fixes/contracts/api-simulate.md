# Contract: /api/simulate & /api/simulate/optimize

**Feature**: `010-radar-direction-and-simulator-fixes`  
**Endpoint 1**: `POST /api/simulate`  
**Endpoint 2**: `POST /api/simulate/optimize`  

---

## 1. `POST /api/simulate`

### Request Body
```json
{
  "ticker": "PETR4.SA",
  "interval": "5m",
  "period": "60d",
  "simulation_mode": "cycle_trade",
  "cycle_entry_mode": "single_buy",
  "contribution_amount": 100.0,
  "initial_capital": 100.0,
  "buy_strategy": "t1_open",
  "sell_strategy": "sell_t1_open",
  "start_date": "2026-10-01",
  "end_date": null,
  "lookback_n": 20,
  "retest_m": 5,
  "retest_tol": 0.005
}
```

### Regras de Negócio:
* Quando `cycle_entry_mode == "single_buy"`:
  * O simulador ignora sinais de compra adicionais enquanto uma posição já estiver aberta.
  * O `total_invested` permanece fixo no capital desembolsado para a posição simples.
  * A tabela de trades exibe compras com contagem `1x`.
* Quando `cycle_entry_mode == "multi_buy"`:
  * Compras adicionais acumulam cotas e recalculam o preço médio.
  * Compras com déficit de caixa adicionam capital investido externo.

---

## 2. `POST /api/simulate/optimize`

### Request Body
```json
{
  "ticker": "PETR4.SA",
  "interval": "5m",
  "period": "60d",
  "initial_capital": 100.0,
  "min_trades": 2,
  "cycle_entry_mode": "single_buy",
  "start_date": "2026-10-01",
  "end_date": null,
  "lookback_n": 20,
  "retest_m": 5,
  "retest_tol": 0.005
}
```

### Response
```json
{
  "ticker": "PETR4.SA",
  "period": "60d",
  "initial_capital": 100.0,
  "total_combinations_tested": 15,
  "champion": {
    "rank": 1,
    "buy_sub_id": "candle_bullish_engulfing",
    "buy_label": "Vela: Engolfo de Alta",
    "sell_sub_id": "sell_candle_bearish_harami",
    "sell_label": "Vela Topo: Harami de Baixa",
    "closed_trades": 58,
    "winning_trades": 43,
    "win_rate_pct": 74.1,
    "total_return_pct": 22.5,
    "net_profit": 22.51,
    "max_drawdown_pct": -3.1,
    "has_open_trade": false,
    "final_equity": 122.51,
    "cycle_entry_mode": "single_buy"
  },
  "top_combinations": [ ... ]
}
```
As métricas retornadas para o campeão devem ser **matematicamente idênticas** às retornadas por `/api/simulate` para a mesma combinação.
