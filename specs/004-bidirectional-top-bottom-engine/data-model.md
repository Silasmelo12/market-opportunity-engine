# Data Model & Contracts: Feature 004

**Feature**: `004-bidirectional-top-bottom-engine`  
**Date**: 2026-10-20  

## Data Contracts & Schemas

### 1. `SignalRecord` (Atualização em `src/strategies/base.py`)
```python
@dataclass(frozen=True)
class SignalRecord:
    strategy_id: str             # e.g., "prop_reversal", "prop_top_reversal", "mql5_candles", "mql5_top_candles"
    strategy_sub_id: str         # e.g., "t1_open", "sell_t1_open", "shooting_star", "hammer"
    signal_bar_index: int        # Índice da barra de confirmação
    execution_bar_index: int     # Índice da barra de preenchimento (>= signal_bar_index)
    execution_price: float       # Preço real de execução
    reference_line_price: Optional[float] = None
    direction: str = "BUY"       # "BUY" | "SELL"
    metadata: Optional[Dict[str, Any]] = None
```

### 2. `ReferenceLineSegment` (Direção e Níveis de Suporte / Resistência)
```python
@dataclass(frozen=True)
class ReferenceLineSegment:
    start_bar_index: int
    end_bar_index: int
    price_level: float
    status: str                 # "ACTIVE_PENDING" | "NEGATED_EXECUTED" | "EXPIRED" | "CANCELLED"
    variation_id: str
    line_type: str = "SUPPORT"  # "SUPPORT" (Fundo) | "RESISTANCE" (Topo)
```

### 3. `SignalItem` (Payload JSON em `src/api/schemas.py`)
```json
{
  "strategy_id": "prop_top_reversal",
  "strategy_sub_id": "sell_t1_open",
  "strategy_label": "Negação Topo Anterior (Venda Abertura)",
  "group_id": "proprietary_top",
  "direction": "SELL",
  "signal_date": "2024-05-10",
  "execution_date": "2024-05-13",
  "signal_bar_index": 45,
  "execution_bar_index": 46,
  "execution_price": 42.50,
  "reference_line_price": 42.10,
  "is_open": false,
  "forward_return_pct": 8.5,
  "mae_pct": -1.8
}
```

### 4. Dicionário de Nomes Comerciais das 24 Estratégias de Venda (`STRATEGY_LABELS_PT`)
- **Grupo 1: Negação Proprietária de Topo (4)**:
  - `sell_t1_open`: `"Negação Topo Barra Anterior (Venda Abertura)"`
  - `sell_t1_retest`: `"Negação Topo Barra Anterior (Venda Reteste)"`
  - `sell_t2_open`: `"Negação de Topo N Barras (Venda Abertura)"`
  - `sell_t2_retest`: `"Negação de Topo N Barras (Venda Reteste)"`
- **Grupo 2: Price Action de Topo (2)**:
  - `sell_double_top_bos`: `"Topo Duplo + Quebra de Estrutura Bearish (BOS)"`
  - `sell_wyckoff_upthrust`: `"Varredura de Topo / Wyckoff Upthrust (UTAD)"`
- **Grupo 3: Alocação & Realização (4)**:
  - `sell_overbought_stat`: `"Excesso Estatístico (Realização Parcial)"`
  - `sell_value_proxy`: `"Estiramento de Valuation (Value Proxy Venda)"`
  - `sell_rebal_rv_rf`: `"Rebalanceamento Renda Variável -> Renda Fixa"`
  - `sell_rebal_relative_strength`: `"Exaustão de Força Relativa (Z-Score)"`
- **Grupo 4: Velas Clássicas de Topo (14)**:
  - `shooting_star`: `"Vela Topo: Estrela Cadente (Shooting Star)"`
  - `hanging_man`: `"Vela Topo: Enforcado (Hanging Man)"`
  - `bearish_engulfing`: `"Vela Topo: Engolfo de Baixa"`
  - `dark_cloud_cover`: `"Vela Topo: Nuvem Negra (Dark Cloud Cover)"`
  - `evening_star`: `"Vela Topo: Estrela da Tarde (Evening Star)"`
  - `bearish_harami`: `"Vela Topo: Harami de Baixa"`
  - `three_inside_down`: `"Vela Topo: Três Por Dentro de Baixa"`
  - `three_outside_down`: `"Vela Topo: Três Por Fora de Baixa"`
  - `three_black_crows`: `"Vela Topo: Três Corvos Negros"`
  - `tweezer_top`: `"Vela Topo: Pinça de Topo (Tweezer Top)"`
  - `gravestone_doji`: `"Vela Topo: Doji Lápide (Gravestone)"`
  - `abandoned_baby_bearish`: `"Vela Topo: Bebê Abandonado de Baixa"`
  - `bearish_kicker`: `"Vela Topo: Kicker de Baixa"`
  - `climactic_bearish_pinbar`: `"Vela Topo: Pinbar Clímax de Topo"`
