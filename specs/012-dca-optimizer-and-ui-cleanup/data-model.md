# Data Model: Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA

## Entidades & Esquemas de Dados

### 1. OptimizeCombinationsRequest (Entrada da API)
```python
class OptimizeCombinationsRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    cycle_entry_mode: str = "multi_buy"   # "multi_buy" | "single_buy" (utilizado apenas em cycle_trade)
    contribution_amount: float = 1000.0   # Valor do aporte periódico em DCA
    initial_capital: float = 1000.0
    min_trades: int = 2
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lookback_n: int = 10
    retest_m: int = 5
    retest_tol: float = 0.0
```

### 2. StrategyPairRankItemModel (Saída do Ranking / Campeã)
```python
class StrategyPairRankItemModel(BaseModel):
    rank: int
    buy_sub_id: str
    buy_label: str
    sell_sub_id: Optional[str] = None
    sell_label: Optional[str] = None
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    closed_trades: int = 0                # Em DCA: mapeia para total de aportes realizados
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate_pct: float = 0.0
    total_return_pct: float
    net_profit: float
    max_drawdown_pct: float = 0.0
    cycle_entry_mode: Optional[str] = None
    # Atributos específicos enriquecidos para DCA:
    total_invested: Optional[float] = None
    final_equity: Optional[float] = None
    average_buy_price: Optional[float] = None
    total_shares: Optional[float] = None
```

### 3. OptimizeCombinationsResponse (Resposta Unificada)
```python
class OptimizeCombinationsResponse(BaseModel):
    ticker: str
    period: str
    simulation_mode: str = "cycle_trade"
    initial_capital: float
    total_combinations_tested: int
    champion: Optional[StrategyPairRankItemModel] = None
    top_combinations: List[StrategyPairRankItemModel] = []
```
