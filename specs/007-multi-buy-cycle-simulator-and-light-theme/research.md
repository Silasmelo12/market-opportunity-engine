# Research: Multi-Buy Cycle Trade, Light Theme & Enhanced Professional Simulator

**Feature**: `007-multi-buy-cycle-simulator-and-light-theme`  
**Date**: 2026-10-21  
**Status**: Completed  

---

## 1. Technical Context & Clarifications

### 1.1 Accumulation Logic in Cycle Trade (`simulate_cycle_trade`)
- **Current Behavior**:
  - `simulate_cycle_trade` starts with `initial_capital` (e.g. R$ 1,000). When the first `BUY` signal occurs, it spends all available cash to buy shares: `shares = cash / p_buy`, `cash = 0`, `in_pos = True`.
  - While `in_pos == True`, any subsequent `BUY` signal is skipped/ignored because `cash == 0` and the code checks `if not in_pos and cash > 0:`.
  - When a `SELL` signal executes, all shares are sold: `exit_cap = shares * p_sell`, `cash = exit_cap`, `in_pos = False`.
- **Target User Behavior**:
  - In "Trade (Compra -> Venda)", the investor wants to buy on **every single buy signal** that triggers before a sell signal, accumulating shares across bottoms/pullbacks, and when a sell signal finally triggers, sell 100% of the accumulated position.
- **Capital Allocation Models**:
  - *Option A (Fixed Cash per Signal / DCA-into-cycle)*: Each buy signal allocates a fixed amount (e.g., `contribution_amount` or `initial_capital / max_entries`). If cash is available or additional capital is funded, add `entry_capital / p_buy` shares.
  - *Option B (Compounded / Multi-Aporte Capital Pool)*: Allow either fixed contribution per signal ($R\$ 100$ or user-specified) or full cycle reinvestment.
  - *Decision*: Support both:
    1. If `contribution_amount` is provided (or user sets fixed tranche per signal, e.g. default $R\$ 1,000$ per buy signal), each `BUY` signal injects `contribution_amount` into the trade:
       $$\text{shares}_k = \frac{\text{contribution}}{\text{p\_buy}_k}$$
       $$\text{total\_shares} = \sum \text{shares}_k$$
       $$\text{total\_invested} = \sum \text{contribution}$$
       $$\text{avg\_price} = \frac{\text{total\_invested}}{\text{total\_shares}}$$
    2. When `SELL` triggers at $p_{sell}$:
       $$\text{exit\_capital} = \text{total\_shares} \times p_{sell}$$
       $$\text{profit\_loss} = \text{exit\_capital} - \text{total\_invested}$$
       $$\text{return\_pct} = \frac{p_{sell} - \text{avg\_price}}{\text{avg\_price}} \times 100$$
    3. Trade record stores `buy_entries: List[BuyEntryRecord]` with individual timestamps, prices, and shares, allowing full auditability and expandable rows in the UI table.

### 1.2 Performance & Institutional Metrics
- **Metrics to calculate**:
  - **Profit Factor (Fator de Lucro)**:
    $$\text{Profit Factor} = \frac{\sum \text{Ganhos Brutos}}{\sum |\text{Perdas Brutas}|}$$
    (If gross loss == 0, return `999.0` or `float('inf')` represented safely as 999.0 in JSON).
  - **Max Drawdown (Rebaixamento Máximo %)**: Calculated over the timeline curve:
    $$\text{Peak}_t = \max_{s \le t} (\text{Equity}_s), \quad \text{DD}_t = \frac{\text{Peak}_t - \text{Equity}_t}{\text{Peak}_t} \times 100$$
    $$\text{Max Drawdown} = \max_t (\text{DD}_t)$$
  - **Win Rate (%)**: $\frac{\text{Trades com Lucro}}{\text{Trades Fechados}} \times 100$.
  - **Average Cycle Duration (Duração Média em Dias/Barras)**.
  - **Buy & Hold Comparison**:
    $$\text{B&H Return} = \frac{\text{Close}_{\text{end}} - \text{Close}_{\text{start}}}{\text{Close}_{\text{start}}} \times 100$$

### 1.3 Light Theme Architecture
- **CSS Strategy**:
  - Use `data-theme="light"` on `document.documentElement` (`<html>`).
  - Define semantic CSS variables in `src/web/index.html` (or utility classes):
    - Dark mode (default):
      - `--bg-primary`: `#090D16` / `#0b0f19`
      - `--card-bg`: `#111827`
      - `--card-border`: `#1F2937`
      - `--text-primary`: `#F9FAFB`
      - `--text-secondary`: `#9CA3AF`
    - Light mode:
      - `--bg-primary`: `#F8FAFC`
      - `--card-bg`: `#FFFFFF`
      - `--card-border`: `#E2E8F0`
      - `--text-primary`: `#0F172A`
      - `--text-secondary`: `#475569`
  - TradingView Lightweight Charts dynamically updates layout colors via `chart.applyOptions({ layout: { background: { color: ... }, textColor: ... }, grid: { vertLines: { color: ... }, horzLines: { color: ... } } })`.
  - Plotly charts update `paper_bgcolor`, `plot_bgcolor`, `font.color`, and grid lines via `Plotly.relayout`.
  - Theme preference persisted in `localStorage.getItem('terminal_theme')` with immediate inline script in `<head>` to prevent flash of dark theme on reload.

---

## 2. Alternatives Evaluated & Rationale

| Decision Area | Chosen Approach | Alternatives Considered | Rationale |
|---|---|---|---|
| Multi-Buy in Cycle Trade | List of `BuyEntry` in `TradeRecord` + weighted average price calculation | Keeping single `buy_price` and overriding it | Maintaining the exact sub-entries guarantees transparency, auditability, and allows rendering detailed breakdown in the UI. |
| Theme Management | CSS variables + `data-theme="light"` on `<html>` + dynamic canvas refresh | Separate CSS files for light and dark | Semantic CSS variables with `data-theme` allow instant zero-lag switching without fetching new files, and ensure full compatibility with Tailwind utility classes. |
| Institutional Metrics | Computed in Python backend (`accumulation_simulator.py`) and sent in `SimulationMetricSummary` | Calculated purely on client JS | Backend calculation ensures precision, unit test coverage in `pytest`, and consistent values between API consumers and UI. |

---

## 3. Risk Assessment & Mitigations

1. **Zero Look-Ahead Bias**:
   - *Risk*: A multi-buy loop could accidentally look at future bars or execute multiple buys in the same bar without causal sequence.
   - *Mitigation*: Ensure `execution_bar_index` strictly respects the signal's execution price and bar index. A sell can only execute on or after the bar of the last buy.
2. **Chart Theme Re-render lag**:
   - *Risk*: Switching themes while Lightweight Charts has candlestick data could cause flickering or reset zoom.
   - *Mitigation*: Use `chart.applyOptions()` which mutates colors in place without recreating the series or clearing data points.
