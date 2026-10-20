# Contract Specification: Market Opportunity & Bottom Statistical Engine

## 1. Módulo `data_loader`

### `DataLoader.load_asset_data`
```python
def load_asset_data(
    ticker: str,
    interval: str = "1d",
    period: str = "5y",
    use_cache: bool = True
) -> OHLCVSeries:
    """
    Carrega dados do Yahoo Finance com normalização e cache local em Parquet.
    
    Inputs:
        ticker: str (ex: 'AAPL', 'PETR4.SA', 'HGLG11.SA', 'BTC-USD', 'CL=F')
        interval: str ('1d' ou '1wk')
        period: str (ex: '2y', '5y', 'max')
        use_cache: bool (default True)
        
    Outputs:
        OHLCVSeries: Estrutura higienizada com arrays NumPy (timestamps, open, high, low, close, volume)
    """
```

## 2. Módulo `strategy_engines`

Todos os motores de estratégia devem assinar a seguinte interface padronizada:

```python
from typing import List, Tuple
from .base import SignalRecord, ReferenceLineSegment
from ..data_loader import OHLCVSeries

class BaseStrategyEngine:
    def generate_signals(
        self,
        series: OHLCVSeries,
        **kwargs
    ) -> Tuple[List[SignalRecord], List[ReferenceLineSegment]]:
        """
        Gera os sinais de compra respeitando Zero Look-Ahead Bias.
        
        Returns:
            Tuple[List[SignalRecord], List[ReferenceLineSegment]]
        """
```

### Sub-IDs Registrados no Sistema:
1. `prop_reversal`:
   - `t1_open`: Rompimento Barra Anterior (`t-1`), Execução na Abertura (`Open t+1`).
   - `t1_retest`: Rompimento Barra Anterior (`t-1`), Execução em Reteste ($M$ barras).
   - `t2_open`: Rompimento Fundo de $N$ barras, Execução na Abertura (`Open t+1`).
   - `t2_retest`: Rompimento Fundo de $N$ barras, Execução em Reteste ($M$ barras).
2. `dca_dynamic`: Compra em desconto estatístico (`Close < SMA200 - k*StdDev` ou `RSI < 30`).
3. `rebal_rf_rv`: Rebalanceamento Renda Fixa vs. Variável (Drawdown de banda).
4. `rebal_relative_strength`: Força Relativa vs. Benchmark (Z-score 60 $\le -2.0$).
5. `value_proxy`: DY Percentil $\ge 80\%$ + Desconto SMA200 ou Mayer Multiple $\le 15\%$.
6. `price_action_double_bottom_bos`: Fundo Duplo com falha de continuação + BOS.
7. `price_action_wyckoff_spring`: Spring / Liquidity Sweep com rejeição e volume.
8. `mql5_candles`:
   - `hammer`, `bullish_engulfing`, `piercing_line`, `morning_star`, `bullish_harami`, `three_inside_up`, `three_outside_up`, `three_white_soldiers`.

## 3. Módulo `statistical_evaluator`

```python
def evaluate_strategy_performance(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    horizon_bars: int = 60
) -> StrategyStatsSummary:
    """
    Calcula as métricas prospectivas em X barras sem vazamento para as estratégias.
    
    Inputs:
        series: OHLCVSeries
        signals: List[SignalRecord]
        horizon_bars: int (janela X, ex: 20, 60, 120, 252)
        
    Outputs:
        StrategyStatsSummary com Win Rate, Retornos, MAE e Score.
    """
```

## 4. Módulo `ui_dashboard`

```python
def render_main_chart(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    reference_lines: List[ReferenceLineSegment]
) -> None:
    """Renderiza o gráfico OHLCV com Lightweight Charts / Plotly WebGL."""

def render_stats_panel(
    summaries: List[StrategyStatsSummary]
) -> None:
    """Renderiza os gráficos comparativos de Ranking e Risco x Retorno."""

def render_status_card(
    series: OHLCVSeries,
    active_line: Optional[ReferenceLineSegment]
) -> None:
    """Renderiza o monitor de confluência e estado atual da última barra."""
```
