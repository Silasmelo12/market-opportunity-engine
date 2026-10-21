# Data Model: Feature 006

## DoublePatternParams (config da estratégia)
| Campo | Default compra | Default venda | Regra |
|---|---|---|---|
| trend_sma_period | 50 | 50 | > 0 |
| prior_move_pct | 0.06 | 0.06 | 0.05–0.08 |
| relative_window | 60 | 60 | ≥ 20 |
| depth_window | 40 | 40 | janela antes de B1/T1 |
| rsi_period | 14 | 14 | |
| rsi_pivot_threshold | < 45 | > 55 | |
| rsi_break_limit | ≤ 60 | ≥ 40 | |

Histórico insuficiente (< relative_window ou < trend_sma_period barras, RSI NaN) → sinal descartado.

## Estratégias (catálogo)
| strategy_sub_id | Label | Direção | Grupo |
|---|---|---|---|
| double_bottom_bos | Fundo Duplo + BOS | BUY | price_action |
| sell_double_top_bos | Topo Duplo + BOS | SELL | price_action |
| sell_double_bottom_inverted | Fundo Duplo Invertido (Venda) | SELL | price_action |
| buy_double_top_inverted | Topo Duplo Invertido (Compra) | BUY | price_action |

## RadarItem
Inalterado (`src/api/schemas.py`). `asset_name` passa a vir sem sufixo "S.A.".

## RadarPage (novo)
| Campo | Tipo |
|---|---|
| items | List[RadarItem] |
| page | int (≥1) |
| page_size | int (1–100) |
| total_assets | int |
| total_pages | int |
| direction | "BUY" \| "SELL" \| "BOTH" |
| strategies | List[str] (vazio = todas) |
| cached | bool (página inteira veio do cache) |

## DailyCacheEntry
- Chave: `radar:v6:{interval}:{horizon_x}:{ticker}:{last_bar_date}`
- Valor: JSON `List[RadarItem]` (todas as direções/estratégias do ticker; filtros aplicados após leitura)
- TTL: 26h. Transição: ausente → calculado → expirado (nova data de pregão gera nova chave).
