# Data Model & Contracts: Feature 002

**Feature**: `002-institutional-ux-radar-simulator`
**Date**: 2026-10-20

## Core Data Structures

### 1. `SimulationResult`
Armazena a evolução financeira simulada para uma estratégia.

```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class SimulationResult:
    strategy_sub_id: str
    strategy_label: str
    total_invested: float           # Total aportado em dinheiro (N_compras * contribution_amount)
    total_shares: float             # Total de cotas/frações acumuladas
    current_equity: float           # Valor de mercado atual (total_shares * Close[-1])
    net_profit: float               # Lucro líquido (current_equity - total_invested)
    return_on_capital_pct: float    # Rentabilidade ((current_equity / total_invested) - 1.0) * 100
    average_buy_price: float        # Preço médio ponderado (total_invested / total_shares)
    current_price: float            # Preço atual do ativo
    num_contributions: int          # Quantidade de aportes realizados
    timeline_timestamps: np.ndarray # Datas da evolução temporal
    timeline_invested: np.ndarray   # Série temporal de capital desembolsado acumulado
    timeline_equity: np.ndarray     # Série temporal de patrimônio a mercado
```

### 2. `TimingStatus`
Classificação do timing de entrada para exibição no Radar e no Header do Ativo.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TimingStatus:
    status_category: str            # "IDEAL" | "EXTENDED" | "LATE"
    status_label: str               # "🟢 ZONA IDEAL / DESCONTO" | "🟡 ESTENDIDO (CAUTELA)" | "🔴 ATRASADO (BONDE ANDOU)"
    distance_pct: float             # Distância percentual do preço atual em relação ao preço sugerido
    recommended_price: float        # Preço sugerido de entrada (P_exec ou Linha de Referência)
    current_price: float            # Preço de fechamento da última barra
    strategy_sub_id: str
    strategy_label: str
    advice_text: str                # Texto explicativo da recomendação
```

### 3. `RadarOpportunityItem`
Item consolidado da tabela do Radar Scanner.

```python
@dataclass
class RadarOpportunityItem:
    ticker: str
    asset_class: str
    strategy_sub_id: str
    strategy_label: str
    historical_n: int
    historical_win_rate: float
    recommended_price: float
    current_price: float
    distance_pct: float
    timing_status: TimingStatus
```
