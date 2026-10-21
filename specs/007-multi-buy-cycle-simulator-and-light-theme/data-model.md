# Data Model: Multi-Buy Cycle Trade & Simulation Entities

**Feature**: `007-multi-buy-cycle-simulator-and-light-theme`  
**Date**: 2026-10-21  

---

## 1. Entities & Data Structures

### 1.1 `BuyEntryRecord` (New Domain Dataclass / Model)
Represents an individual buy execution within an ongoing multi-buy accumulation cycle.

| Field | Type | Description |
|---|---|---|
| `entry_id` | `int` | Sequential entry index within the cycle (1, 2, ...) |
| `date` | `str` | ISO date of execution (`YYYY-MM-DD`) |
| `bar_index` | `int` | Bar index in OHLCV series |
| `price` | `float` | Executed buy price ($P_k$) |
| `shares` | `float` | Shares purchased in this entry ($Q_k$) |
| `capital` | `float` | Monetary capital allocated to this entry ($C_k = Q_k \times P_k$) |
| `strategy_sub_id` | `str` | Strategy ID that triggered this entry |
| `strategy_label` | `str` | Human-readable label of the strategy |

### 1.2 `TradeRecord` (Updated Domain Dataclass)
Represents a complete cycle trade (or currently active cycle).

| Field | Type | Description |
|---|---|---|
| `trade_id` | `int` | Sequential trade/cycle index |
| `buy_entries` | `List[BuyEntryRecord]` | List of individual buy executions in this cycle |
| `num_entries` | `int` | Total number of buy executions in this cycle |
| `total_shares` | `float` | $\sum Q_k$ accumulated across all buy entries |
| `total_invested` | `float` | $\sum C_k$ total capital committed to the cycle |
| `average_buy_price` | `float` | $\frac{\text{total\_invested}}{\text{total\_shares}}$ |
| `first_buy_date` | `str` | Date of the initial buy entry |
| `last_buy_date` | `str` | Date of the most recent buy entry |
| `sell_strategy_sub_id`| `Optional[str]` | Strategy ID that triggered the liquidation |
| `sell_strategy_label` | `Optional[str]` | Human-readable strategy label for exit |
| `sell_date` | `Optional[str]` | Date of liquidation |
| `sell_price` | `Optional[float]` | Executed exit price ($P_{\text{sell}}$) |
| `sell_bar_index` | `Optional[int]` | Bar index of liquidation |
| `exit_capital` | `Optional[float]` | Gross capital returned ($\text{total\_shares} \times P_{\text{sell}}$) |
| `profit_loss` | `float` | Net PnL ($\text{exit\_capital} - \text{total\_invested}$) |
| `return_pct` | `float` | $\frac{P_{\text{sell}} - \text{average\_buy\_price}}{\text{average\_buy\_price}} \times 100$ |
| `duration_bars` | `int` | Total bar duration from first buy to sell |
| `status` | `str` | `"FECHADO"` or `"ABERTO"` |

### 1.3 `SimulationMetricSummary` (Updated API Schema)
Institutional metrics returned by the `/api/simulate` endpoint.

| Field | Type | Description |
|---|---|---|
| `simulation_mode` | `str` | `"cycle_trade"` or `"continuous_dca"` |
| `total_invested` | `float` | Total monetary capital deployed |
| `final_portfolio_value`| `float` | Current cash + mark-to-market equity |
| `total_profit_loss` | `float` | Absolute net profit/loss ($R\$$) |
| `total_return_pct` | `float` | Return over total invested capital (%) |
| `max_drawdown_pct` | `float` | Maximum peak-to-trough drop (%) |
| `profit_factor` | `Optional[float]` | Gross Profit / Gross Loss |
| `total_trades_count`| `int` | Number of cycles executed |
| `winning_trades_count` | `int` | Cycles closed with profit > 0 |
| `losing_trades_count` | `int` | Cycles closed with profit <= 0 |
| `win_rate_pct` | `float` | $\frac{\text{winning\_trades}}{\text{closed\_trades}} \times 100$ |
| `avg_trade_return_pct` | `float` | Mean return across closed cycles |
| `avg_entries_per_cycle`| `float` | Average number of buys per cycle |
| `avg_trade_bars` | `float` | Average holding time in bars |
| `buy_and_hold_return_pct` | `float` | Benchmark asset return over identical time range |
| `current_market_price` | `float` | Last closing price of asset |

---

## 2. State Machine & Transitions

```text
[IDLE / CASH]
      │
      │ Signal: BUY (Entry 1)
      ▼
[IN_CYCLE_POSITION] ◄─────────────────────────┐
      │                                       │
      ├───────► Signal: BUY (Entry k) ────────┘
      │         (Accumulate shares, add capital,
      │          recalculate average_buy_price)
      │
      │ Signal: SELL (Exit)
      ▼
[LIQUIDATED / CASH]
      │
      └───────► (Returns to IDLE or awaits next BUY)
```

1. **Cycle Start**: When `in_pos == False` and a `BUY` signal occurs at $t$, initiate `open_trade` with `BuyEntryRecord(entry_id=1, ...)`.
2. **Cycle Accumulation**: When `in_pos == True` and subsequent `BUY` signals occur at $t' > t$, append `BuyEntryRecord(entry_id=k, ...)`, add shares, and recalculate `average_buy_price`.
3. **Cycle Liquidation**: When `in_pos == True` and a `SELL` signal occurs at $t'' > t_{\text{last\_buy}}$, sell $100\%$ of `total_shares`. Record trade summary, compute PnL against `average_buy_price`, append to closed trades list, and reset position to `False`.
4. **End of Data**: If data ends with `in_pos == True`, mark as `"ABERTO"`, compute mark-to-market against `Close[-1]`, and include in trade history as open.
