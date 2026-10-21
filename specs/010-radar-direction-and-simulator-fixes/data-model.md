# Data Model: Correção do Radar, Seletor de Modelo de Ciclo (1x vs Multi-Buy) e Alinhamento do Simulador

**Feature**: `010-radar-direction-and-simulator-fixes`  
**Date**: 2026-10-21  

---

## Entidades e Tipos de Dados

### 1. `CycleEntryMode` (Enumeração)
Define a modalidade de abertura e acumulação de entradas dentro de um ciclo de trade:

| Valor | Nome Amigável | Descrição |
|---|---|---|
| `single_buy` | Compra Única (1x por Ciclo) | Executa apenas o 1º sinal de compra após uma venda anterior. Ignora todas as compras subsequentes enquanto a posição estiver aberta. O capital investido é fixado no aporte inicial. |
| `multi_buy` | Acumulação Multi-Buy (Nx por Ciclo) | Executa compras em todos os sinais de compra confirmados no ciclo. Acumula cotas, recalcula o preço médio ponderado e liquida 100% no sinal de venda. |

---

### 2. Modificações em Modelos Existentes

#### `SimulateRequest` (em `src/api/schemas.py`)
```python
class SimulateRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    cycle_entry_mode: str = "multi_buy"    # NOVO: "single_buy" | "multi_buy"
    contribution_amount: Optional[float] = 1000.0
    initial_capital: float = 1000.0
    buy_strategy: str = "ALL"
    sell_strategy: str = "ALL"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    selected_strategies: Optional[List[str]] = None
    lookback_n: int = 20
    retest_m: int = 5
    retest_tol: float = 0.005
```

#### `OptimizeCombinationsRequest` (em `src/api/schemas.py`)
```python
class OptimizeCombinationsRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    initial_capital: float = 1000.0
    min_trades: int = 2
    cycle_entry_mode: str = "multi_buy"    # NOVO: "single_buy" | "multi_buy"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lookback_n: int = 20
    retest_m: int = 5
    retest_tol: float = 0.005
```

#### `StrategyPairRankItem` (em `src/evaluator/accumulation_simulator.py`)
Acrescido do metadado de modo de ciclo:
```python
@dataclass
class StrategyPairRankItem:
    rank: int
    buy_sub_id: str
    buy_label: str
    sell_sub_id: str
    sell_label: str
    closed_trades: int
    winning_trades: int
    win_rate_pct: float
    total_return_pct: float
    net_profit: float
    max_drawdown_pct: float
    has_open_trade: bool
    final_equity: float
    cycle_entry_mode: str = "multi_buy"  # NOVO
```

---

### 3. Estados no Frontend (`state` em `src/web/app.js`)

| Propriedade de Estado | Tipo | Descrição |
|---|:---:|---|
| `state.cycleEntryMode` | `string` | `'multi_buy'` (default) ou `'single_buy'` |
| `state.activeDirection` | `string` | `'BUY'`, `'SELL'` ou `'BOTH'` |
| `state.lastRadarPage` | `object` | Objeto contendo os dados paginados retornados pela API `/api/radar` |
