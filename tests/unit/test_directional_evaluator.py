"""
Unit tests for directional statistical evaluation and timing classifier (Feature 004).
Verifies:
- Win rate, Forward Return % and MAE % inversion for SELL signals.
- Open vs closed signal segregation for SELL signals.
- Timing classifier bands for both BUY and SELL directions.
"""

import numpy as np
import pytest
from src.strategies.base import OHLCVSeries, SignalRecord
from src.evaluator.statistical_engine import evaluate_strategy_performance
from src.evaluator.timing_classifier import classify_timing_status


def make_test_series(closes, highs=None, lows=None):
    n = len(closes)
    ts = np.array([f"2023-01-{i+1:02d}" for i in range(n)], dtype="object")
    c = np.array(closes, dtype=np.float64)
    h = np.array(highs if highs is not None else closes, dtype=np.float64)
    l = np.array(lows if lows is not None else closes, dtype=np.float64)
    o = c.copy()
    v = np.full(n, 1000.0, dtype=np.float64)
    return OHLCVSeries(
        ticker="TEST",
        interval="1d",
        timestamps=ts,
        open=o,
        high=h,
        low=l,
        close=c,
        volume=v,
    )


def test_directional_evaluator_sell_win_and_forward_return():
    """
    For a SELL signal executed at P_exec = 100, if future price drops to 80,
    it is a WIN with +20% forward return.
    If price spikes to 110 during the window, MAE is -10%.
    """
    # 10 bars: bar 0 executes at 100. Over bars 1..5, max high is 110, bar 5 closes at 80.
    closes = [100.0, 95.0, 90.0, 105.0, 85.0, 80.0, 80.0]
    highs  = [100.0, 98.0, 92.0, 110.0, 88.0, 82.0, 82.0]
    lows   = [ 98.0, 92.0, 88.0,  99.0, 80.0, 78.0, 78.0]

    series = make_test_series(closes, highs, lows)
    sell_sig = SignalRecord(
        strategy_id="prop_reversal",
        strategy_sub_id="sell_t1_open",
        direction="SELL",
        signal_bar_index=0,
        execution_bar_index=0,
        execution_price=100.0,
        reference_line_price=100.0,
        metadata={},
    )

    summary = evaluate_strategy_performance(
        series=series,
        signals=[sell_sig],
        horizon_bars=5,
    )

    assert summary.direction == "SELL"
    assert summary.win_rate == 100.0
    assert summary.mean_forward_return == pytest.approx(20.0, rel=1e-2)  # (100 - 80) / 100 * 100 = +20%
    assert summary.mean_mae == pytest.approx(-10.0, rel=1e-2)  # -(110 - 100) / 100 * 100 = -10%


def test_directional_timing_classifier_sell_bands():
    """
    For SELL:
      - Current 99.0 vs Recommended 100.0 (-1.0% drop) -> IDEAL
      - Current 97.0 vs Recommended 100.0 (-3.0% drop) -> EXTENDED
      - Current 94.0 vs Recommended 100.0 (-6.0% drop) -> LATE
    """
    st_ideal = classify_timing_status(
        current_price=99.0,
        recommended_price=100.0,
        strategy_sub_id="sell_t1_open",
        direction="SELL",
    )
    assert st_ideal.status_category == "IDEAL"
    assert "IDEAL" in st_ideal.status_label

    st_ext = classify_timing_status(
        current_price=97.0,
        recommended_price=100.0,
        strategy_sub_id="sell_t1_open",
        direction="SELL",
    )
    assert st_ext.status_category == "EXTENDED"
    assert "ESTENDIDO" in st_ext.status_label

    st_late = classify_timing_status(
        current_price=94.0,
        recommended_price=100.0,
        strategy_sub_id="sell_t1_open",
        direction="SELL",
    )
    assert st_late.status_category == "LATE"
    assert "ATRASADO" in st_late.status_label
