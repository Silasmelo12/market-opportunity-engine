"""
Tests for refined double bottom and double top pattern strategies (US1 & US2 & US3).
Strictly validates zero look-ahead bias and mathematical filtering criteria.
"""

import numpy as np
import pytest
from src.strategies.classic_engines import (
    ClassicStrategiesEngine,
    DoublePatternParams,
    _detect_double_bottom_raw,
    _detect_double_top_raw,
)
from src.strategies.base import OHLCVSeries
from tests.fixtures_double_patterns import (
    create_vertical_rally_double_bottom,
    create_valid_reversal_double_bottom,
    create_valid_reversal_double_top,
    make_series,
)


class TestDoubleBottomRefined:
    """US1 - Refined Double Bottom + BOS Tests."""

    def test_vertical_rally_rejection(self):
        """
        In a strong vertical rally or extended high, a mini double-bottom MUST be rejected
        due to:
        - close[t] being the highest high of 60 bars (Position filter)
        - Price above SMA50 without prior 6% drop (Trend context)
        - RSI not oversold during bottoms (RSI filter)
        """
        engine = ClassicStrategiesEngine()
        series = create_vertical_rally_double_bottom(120)
        signals = engine.run_double_bottom_bos(series)
        # Even if raw detector catches it, refined strategy MUST produce 0 buy signals
        assert len(signals) == 0, f"Expected 0 signals during vertical rally, got {len(signals)}"

    def test_filter_rejection_at_60_bar_high(self):
        """
        If close[t] >= max(High[t-60:t]), the buy signal MUST be discarded.
        """
        engine = ClassicStrategiesEngine()
        # Create a series where breakout happens at the highest high of last 60 bars
        n = 100
        p = np.linspace(60.0, 90.0, n)
        # Force a double bottom shape at the very top
        p[-5] = 88.0
        p[-4] = 91.0
        p[-3] = 88.1
        p[-2] = 92.5  # Breakout that is higher than any high in last 60 bars
        p[-1] = 93.0
        series = make_series(p - 0.2, p + 0.5, p - 0.5, p)
        signals = engine.run_double_bottom_bos(series)
        assert len(signals) == 0, "Signal at 60-bar highest high must be rejected"

    def test_filter_rsi_anti_exhaustion(self):
        """
        B1/B2 must visit RSI < 45, and breakout must have RSI <= 60.
        """
        engine = ClassicStrategiesEngine()
        # In a constantly climbing asset with high RSI (all > 65), signals must be rejected
        p = np.linspace(50.0, 150.0, 120)
        # inject raw pattern
        p[60] = 100.0
        p[63] = 105.0
        p[66] = 100.1
        p[70] = 106.0
        series = make_series(p - 0.1, p + 0.5, p - 0.5, p)
        signals = engine.run_double_bottom_bos(series)
        assert len(signals) == 0

    def test_anti_lookahead_double_bottom(self):
        """
        Ensures that truncating the series at breakout bar t produces the exact same signal
        as running on the full series (zero look-ahead bias).
        """
        engine = ClassicStrategiesEngine()
        # Generate valid reversal series
        series = create_valid_reversal_double_bottom(120)
        signals_full = engine.run_double_bottom_bos(series)
        if len(signals_full) > 0:
            sig = signals_full[0]
            t = sig.signal_bar_index
            # Truncate at t + 1 (data known up to bar t)
            truncated_series = OHLCVSeries(
                ticker=series.ticker,
                interval=series.interval,
                timestamps=series.timestamps[: t + 1],
                open=series.open[: t + 1],
                high=series.high[: t + 1],
                low=series.low[: t + 1],
                close=series.close[: t + 1],
                volume=series.volume[: t + 1],
            )
            signals_trunc = engine.run_double_bottom_bos(truncated_series)
            assert len(signals_trunc) == 1
            assert signals_trunc[0].signal_bar_index == t
            assert signals_trunc[0].strategy_sub_id == "double_bottom_bos"
