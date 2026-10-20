"""
Unified interface and strategy catalog manager for all 8 strategy families.
"""

from typing import Dict, Any, List, Tuple, Optional
from .base import (
    OHLCVSeries,
    SignalRecord,
    ReferenceLineSegment,
    StrategyStatsSummary,
)
from .proprietary_reversal import ProprietaryReversalEngine
from .mql5_candles import MQL5CandleEngine
from .classic_engines import ClassicStrategiesEngine, compute_rsi


class StrategyCatalog:
    """
    Orchestrates all strategy families (4 Proprietary variants, 6 Classic engines,
    and 14 MQL5 candlestick patterns = 24 distinct sub-strategies) while maintaining
    state isolation and collecting pending alerts on the latest bar.
    """

    def __init__(
        self,
        lookback_n: int = 10,
        retest_window_m: int = 5,
        tolerance_pct: float = 0.0,
    ) -> None:
        self.prop_engine = ProprietaryReversalEngine(
            lookback_n=lookback_n,
            retest_window_m=retest_window_m,
            tolerance_pct=tolerance_pct,
        )
        self.classic_engine = ClassicStrategiesEngine()
        self.mql5_engine = MQL5CandleEngine()

    def run_all(
        self,
        series: OHLCVSeries,
        benchmark_close: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executes all strategy engines on the given OHLCVSeries and returns:
          - signals: List[SignalRecord]
          - reference_lines: List[ReferenceLineSegment]
          - prop_current_state: Dict[str, Dict[str, Any]]
          - pending_signals: List[Dict[str, Any]]
          - total_signals_by_sub_id: Dict[str, int]
        """
        prop_sigs, prop_lines = self.prop_engine.generate_signals(series)
        classic_sigs, _ = self.classic_engine.generate_signals(series, benchmark_close=benchmark_close)
        mql5_sigs, _ = self.mql5_engine.generate_signals(series)

        all_signals = prop_sigs + classic_sigs + mql5_sigs
        pending = (
            self.prop_engine.pending_signals
            + self.classic_engine.pending_signals
            + self.mql5_engine.pending_signals
        )

        total_signals_map: Dict[str, int] = dict(self.prop_engine.total_signals_by_variant)
        for sig in classic_sigs + mql5_sigs:
            if sig.metadata and "total_variant_signals" in sig.metadata:
                total_signals_map[sig.strategy_sub_id] = int(sig.metadata["total_variant_signals"])

        return {
            "signals": all_signals,
            "reference_lines": prop_lines,
            "prop_current_state": self.prop_engine.get_current_state(),
            "pending_signals": pending,
            "total_signals_by_sub_id": total_signals_map,
        }


__all__ = [
    "OHLCVSeries",
    "SignalRecord",
    "ReferenceLineSegment",
    "StrategyStatsSummary",
    "ProprietaryReversalEngine",
    "MQL5CandleEngine",
    "ClassicStrategiesEngine",
    "StrategyCatalog",
    "compute_rsi",
]
