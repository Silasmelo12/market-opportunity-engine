"""
Pydantic schemas and serialization helpers for FastAPI server.
Converts NumPy types (float64, int64, ndarray) into native Python types
to avoid JSON serialization errors.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import numpy as np


def sanitize_val(v: Any) -> Any:
    """Recursively converts NumPy scalars and arrays to native Python types."""
    if isinstance(v, (np.floating, float)):
        if np.isnan(v) or np.isinf(v):
            return None
        return float(v)
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.ndarray):
        return [sanitize_val(x) for x in v.tolist()]
    if isinstance(v, dict):
        return {k: sanitize_val(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [sanitize_val(x) for x in v]
    return v


# 1. Models for /api/analyze

class CandleBar(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class SignalItem(BaseModel):
    strategy_id: str
    strategy_sub_id: str
    strategy_label: str
    group_id: str
    direction: str = "BUY"  # "BUY" | "SELL"
    signal_date: str
    execution_date: str
    signal_bar_index: int
    execution_bar_index: int
    execution_price: float
    reference_line_price: Optional[float] = None
    is_open: bool = False
    forward_return_pct: Optional[float] = None
    mae_pct: Optional[float] = None


class ReferenceLineItem(BaseModel):
    start_date: str
    end_date: str
    start_bar_index: int
    end_bar_index: int
    price_level: float
    status: str
    variation_id: str
    line_type: str = "SUPPORT"  # "SUPPORT" | "RESISTANCE"
    direction: str = "BUY"      # "BUY" | "SELL"


class StrategySummaryItem(BaseModel):
    strategy_sub_id: str
    strategy_label: str
    group_id: str
    direction: str = "BUY"      # "BUY" | "SELL"
    win_rate: float
    mean_forward_return: float
    median_forward_return: float
    mean_mae: float
    max_mae: float
    efficiency_score: float
    total_signals: int
    executed_buys: int
    retest_fill_rate: Optional[float] = None
    open_signals_count: int = 0


class TimingStatusModel(BaseModel):
    status_category: str  # "IDEAL", "EXTENDED", "LATE"
    status_label: str
    distance_pct: float
    recommended_price: float
    current_price: float
    advice_text: str
    direction: str = "BUY"


class AnalyzeResponse(BaseModel):
    ticker: str
    interval: str
    period: str
    current_price: float
    candles: List[CandleBar]
    signals: List[SignalItem]
    reference_lines: List[ReferenceLineItem]
    summaries: List[StrategySummaryItem]
    current_state: Dict[str, Any]
    timing_status: Optional[TimingStatusModel] = None


# 2. Models for /api/radar

class RadarItem(BaseModel):
    ticker: str
    asset_name: Optional[str] = None
    category: str
    current_price: float
    strategy_sub_id: str
    strategy_label: str
    direction: str = "BUY"  # "BUY" | "SELL"
    status_signal: str
    timing_category: str
    timing_label: str
    distance_pct: float
    recommended_price: float
    historical_n: int
    historical_win_rate: float
    advice_text: str


class RadarPage(BaseModel):
    items: List[RadarItem]
    page: int
    page_size: int
    total_assets: int
    total_pages: int
    direction: str = "BUY"
    strategies: List[str] = []
    cached: bool = False


# 3. Models for /api/simulate

class SimulateRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    contribution_amount: float = 1000.0   # Serves as contribution in accumulation, or initial_capital in cycle_trade
    initial_capital: float = 1000.0
    buy_strategy: Optional[str] = None    # Specific buy strategy or "ALL"
    sell_strategy: Optional[str] = None   # Specific sell strategy or "ALL"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    selected_strategies: Optional[List[str]] = None
    lookback_n: int = 10
    retest_m: int = 5
    retest_tol: float = 0.0


class AccumulationPoint(BaseModel):
    date: str
    total_invested: float
    portfolio_value: float
    shares: float
    close_price: float
    cash_inflow: float


class SimulationMetricSummary(BaseModel):
    simulation_mode: str = "cycle_trade"
    total_invested: float
    final_portfolio_value: float
    total_profit_loss: float
    total_return_pct: float
    xirr_annualized_pct: Optional[float] = None
    max_drawdown_pct: float
    total_trades_count: int
    shares_accumulated: float
    average_cost_price: float
    current_market_price: float
    dca_regular_final_value: float
    alpha_vs_dca_pct: float
    # Extended metrics for Cycle Trade (Buy -> Sell)
    winning_trades_count: Optional[int] = None
    losing_trades_count: Optional[int] = None
    win_rate_pct: Optional[float] = None
    avg_trade_return_pct: Optional[float] = None
    avg_trade_bars: Optional[float] = None
    buy_and_hold_return_pct: Optional[float] = None


class SimulateResponse(BaseModel):
    ticker: str
    period: str
    metrics: SimulationMetricSummary
    curve: List[AccumulationPoint]
    trades: List[Dict[str, Any]]


# 4. Models for /api/simulate/optimize

class StrategyPairRankItemModel(BaseModel):
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


class OptimizeCombinationsRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    initial_capital: float = 1000.0
    min_trades: int = 2
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lookback_n: int = 10
    retest_m: int = 5
    retest_tol: float = 0.0


class OptimizeCombinationsResponse(BaseModel):
    ticker: str
    period: str
    initial_capital: float
    total_combinations_tested: int
    champion: Optional[StrategyPairRankItemModel] = None
    top_combinations: List[StrategyPairRankItemModel] = []
