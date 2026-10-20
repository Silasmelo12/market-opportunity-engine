"""
Base contracts and dataclasses for Market Opportunity & Bottom Statistical Engine.
Enforces strict anti-lookahead compliance and standardized output formats.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import numpy as np


@dataclass(frozen=True)
class OHLCVSeries:
    """
    Higienized historical price series backed by contiguous 1D NumPy arrays.
    """
    ticker: str
    interval: str  # "1d" | "1wk"
    timestamps: np.ndarray  # int64 timestamps (or datetime64[ns])
    open: np.ndarray        # float64
    high: np.ndarray        # float64
    low: np.ndarray         # float64
    close: np.ndarray       # float64
    volume: np.ndarray      # float64
    dividends: Optional[np.ndarray] = None  # float64
    dy_rolling_12m: Optional[np.ndarray] = None  # float64 (percentage or decimal)

    @property
    def length(self) -> int:
        return len(self.close)


@dataclass(frozen=True)
class SignalRecord:
    """
    Standardized contract for an executed buy or sell signal.
    Guarantees execution_bar_index >= signal_bar_index (Zero Look-Ahead Bias).
    """
    strategy_id: str             # e.g., "prop_reversal", "mql5_hammer", "dca_dynamic"
    strategy_sub_id: str         # e.g., "t1_open", "t1_retest", "t2_open", "t2_retest"
    signal_bar_index: int        # Index where the setup condition was confirmed
    execution_bar_index: int     # Index where fill occurred (t_exec >= signal_bar_index)
    execution_price: float       # Real execution price (Open or line/gap touch)
    reference_line_price: Optional[float] = None  # Reference support or resistance level
    direction: str = "BUY"       # "BUY" (Fundo) | "SELL" (Topo)
    metadata: Optional[Dict[str, Any]] = None     # Optional metadata for diagnostics/plot


@dataclass(frozen=True)
class ReferenceLineSegment:
    """
    Visual reference line segment for charting and state tracking.
    """
    start_bar_index: int         # Breakout bar index
    end_bar_index: int           # Negation or expiration bar index
    price_level: float           # Reference low/high price level
    status: str                  # "ACTIVE_PENDING" | "NEGATED_EXECUTED" | "EXPIRED" | "CANCELLED"
    variation_id: str            # Technical sub_id or label
    line_type: str = "SUPPORT"   # "SUPPORT" (Fundo) | "RESISTANCE" (Topo)
    direction: str = "BUY"       # "BUY" | "SELL"


@dataclass
class StrategyStatsSummary:
    """
    Aggregated performance metrics computed prospectively over X bars.
    """
    strategy_id: str
    strategy_sub_id: str
    horizon_bars: int            # Window X (e.g., 20, 60, 120, 252)
    total_signals: int           # Total generated setups
    executed_buys: int           # Total filled trades (buys or sells)
    retest_fill_rate: float      # Retest fill rate (1.0 for market-on-open)
    win_rate: float              # Percentage of wins
    mean_forward_return: float   # Mean forward return percentage
    median_forward_return: float # Median forward return percentage
    mean_mae: float              # Mean Maximum Adverse Excursion
    max_mae: float               # Worst observed MAE
    efficiency_score: float      # Composite score
    direction: str = "BUY"       # "BUY" | "SELL"
    open_signals_count: int = 0  # Signals with less than X bars remaining to date
