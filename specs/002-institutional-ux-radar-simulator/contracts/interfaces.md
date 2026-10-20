# Contract Specification: Feature 002

## 1. `src/evaluator/accumulation_simulator.py`

```python
def simulate_accumulation(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    contribution_amount: float = 100.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, SimulationResult]:
    """
    Simula aportes periódicos em cada compra sinalizada pela estratégia.
    Retorna dicionário mapeando strategy_sub_id para SimulationResult.
    """
```

## 2. `src/evaluator/timing_classifier.py`

```python
def classify_timing_status(
    current_price: float,
    recommended_price: float,
    strategy_sub_id: str,
    mean_forward_return: Optional[float] = None,
    atr_14: Optional[float] = None
) -> TimingStatus:
    """
    Avalia a distância percentual e classifica o Semáforo de Timing:
    - IDEAL: <= +1.5% acima do preço recomendado (ou em reteste)
    - EXTENDED: +1.5% a +4.0%
    - LATE: > +4.0% ou > 30% do retorno médio consumido
    """
```

## 3. `src/data_loader/resampler.py`

```python
def resample_ohlcv(df: pd.DataFrame, target_interval: str) -> pd.DataFrame:
    """
    Agrega barras horárias para intervalos de 2h, 4h e 12h:
    Open='first', High='max', Low='min', Close='last', Volume='sum'
    Removendo períodos fora de pregão sem negociação.
    """
```
