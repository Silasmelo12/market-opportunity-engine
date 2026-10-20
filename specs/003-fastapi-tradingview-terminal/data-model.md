# Data Model: Feature 003

**Feature**: `003-fastapi-tradingview-terminal`
**Date**: 2026-10-20

## Core API Schemas

### 1. `AnalyzeResponse` (JSON Payload de `/api/analyze`)
```json
{
  "ticker": "PETR4.SA",
  "interval": "1d",
  "period": "2y",
  "current_price": 38.50,
  "candles": [
    {
      "time": "2024-01-02",
      "open": 37.20,
      "high": 38.10,
      "low": 37.00,
      "close": 37.90,
      "volume": 25400000
    }
  ],
  "signals": [
    {
      "strategy_id": "prop_reversal",
      "strategy_sub_id": "t1_retest",
      "strategy_label": "Negação Barra Anterior - Entrada Reteste",
      "group_id": "proprietary",
      "signal_date": "2024-01-15",
      "execution_date": "2024-01-18",
      "signal_bar_index": 10,
      "execution_bar_index": 13,
      "execution_price": 36.80,
      "reference_line_price": 36.80,
      "is_open": false,
      "forward_return_pct": 12.5,
      "mae_pct": -2.1
    }
  ],
  "reference_lines": [
    {
      "start_date": "2024-01-10",
      "end_date": "2024-01-18",
      "start_bar_index": 8,
      "end_bar_index": 13,
      "price_level": 36.80,
      "status": "NEGATED_EXECUTED",
      "variation_id": "t1_retest"
    }
  ],
  "summaries": [
    {
      "strategy_sub_id": "t1_retest",
      "strategy_label": "Negação Barra Anterior - Entrada Reteste",
      "group_id": "proprietary",
      "win_rate": 85.7,
      "mean_forward_return": 14.2,
      "median_forward_return": 12.0,
      "mean_mae": -3.8,
      "max_mae": -9.2,
      "efficiency_score": 2.45,
      "total_signals": 14,
      "executed_buys": 12,
      "retest_fill_rate": 85.7,
      "open_signals_count": 1
    }
  ],
  "current_state": {
    "t1_retest": {
      "status": "AGUARDANDO_RETESTE",
      "active_line_price": 37.10,
      "distance_to_line_pct": 1.2,
      "retest_bars_remaining": 3
    }
  },
  "timing_status": {
    "status_category": "IDEAL",
    "status_label": "🟢 ZONA IDEAL / DESCONTO",
    "distance_pct": 1.1,
    "recommended_price": 38.08,
    "current_price": 38.50,
    "advice_text": "Dentro da janela ideal de execução (+1.1%)."
  }
}
```

### 2. `RadarItem` (JSON Payload de `/api/radar`)
```json
{
  "ticker": "PETR4.SA",
  "category": "Ações Brasil",
  "current_price": 38.50,
  "strategy_sub_id": "t1_retest",
  "strategy_label": "Negação Barra Anterior - Entrada Reteste",
  "status_signal": "Aguardando Reteste (3b rest.)",
  "timing_category": "IDEAL",
  "timing_label": "🟢 ZONA IDEAL / DESCONTO",
  "distance_pct": 1.1,
  "recommended_price": 38.08,
  "historical_n": 14,
  "historical_win_rate": 85.7,
  "advice_text": "Dentro da janela ideal de execução."
}
```

### 3. As 24 Estratégias Registradas (4 Grupos)
- **Grupo 1: Negação Proprietária (4)**: `t1_open`, `t1_retest`, `t2_open`, `t2_retest`
- **Grupo 2: Price Action Institucional (2)**: `price_action_double_bottom_bos`, `price_action_wyckoff_spring`
- **Grupo 3: Alocação & Holder (4)**: `dca_dynamic`, `value_proxy`, `rebal_rf_rv`, `rebal_relative_strength`
- **Grupo 4: Padrões de Velas de Fundo (14)**:
  `hammer`, `inverted_hammer`, `bullish_engulfing`, `piercing_line`, `morning_star`, `bullish_harami`, `three_inside_up`, `three_outside_up`, `three_white_soldiers`, `tweezer_bottom`, `dragonfly_doji`, `abandoned_baby_bullish`, `bullish_kicker`, `climactic_pinbar`.
