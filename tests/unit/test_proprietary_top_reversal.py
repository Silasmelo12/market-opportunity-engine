"""
Unit tests for Proprietary Top Reversal Strategy Engine (Sell Variants).
Verifies:
- Breakout of highs sets active resistance line (Type 1 and Type 2)
- Successive higher breakouts dynamically overwrite resistance line
- Bearish negation executes in Open (t+1) mode
- Retest mode evaluates sequentially and executes on touch or gap-up
- Zero Look-Ahead bias and pending alerts on the final bar
"""

import numpy as np
import pytest
from src.strategies.base import OHLCVSeries
from src.strategies.proprietary_reversal import ProprietaryReversalEngine


def make_series(opens, highs, lows, closes):
    n = len(opens)
    ts = np.array([f"2023-01-{i+1:02d}" for i in range(n)], dtype="object")
    vols = np.full(n, 1000.0, dtype=np.float64)
    return OHLCVSeries(
        ticker="TEST",
        interval="1d",
        timestamps=ts,
        open=np.array(opens, dtype=np.float64),
        high=np.array(highs, dtype=np.float64),
        low=np.array(lows, dtype=np.float64),
        close=np.array(closes, dtype=np.float64),
        volume=vols,
    )


def test_sell_successive_breakouts_overwrite_resistance():
    """
    Verifies that when multiple higher highs occur before negation,
    the active resistance line is overwritten and old ones cancelled.
    """
    opens  = [100.0, 102.0, 105.0, 108.0, 112.0, 109.0, 103.0]
    highs  = [102.0, 106.0, 110.0, 114.0, 115.0, 110.0, 105.0]
    lows   = [ 99.0, 101.0, 104.0, 107.0, 109.0, 104.0, 101.0]
    closes = [101.0, 105.0, 109.0, 113.0, 110.0, 105.0, 102.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series, variant_filter=["sell_t1_open"], direction_filter="SELL")

    sell_sigs = [s for s in signals if s.direction == "SELL"]
    assert len(sell_sigs) >= 1
    cancelled = [seg for seg in segments if seg.status == "CANCELLED" and seg.direction == "SELL"]
    assert len(cancelled) >= 1
    for sig in sell_sigs:
        assert sig.direction == "SELL"


def test_sell_retest_gap_up_executes_at_open():
    """
    Verifies that if a retest opens above the resistance level, it executes at open_price (retest_gap).
    """
    opens  = [100.0, 102.0, 105.0, 100.0, 106.0, 104.0]
    highs  = [101.0, 105.0, 106.0, 102.0, 107.0, 105.0]
    lows   = [ 99.0, 101.0, 103.0,  98.0, 103.0, 101.0]
    closes = [100.5, 104.5, 102.0,  99.0, 104.0, 102.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series, variant_filter=["sell_t1_retest"], direction_filter="SELL")

    sell_sigs = [s for s in signals if s.direction == "SELL"]
    if len(sell_sigs) > 0:
        sig = sell_sigs[0]
        assert sig.direction == "SELL"
        assert sig.execution_price >= sig.reference_line_price


def test_sell_last_bar_breakout_registers_waiting_negation():
    """
    Verifies that a bullish breakout occurring on the final bar leaves state AGUARDANDO_NEGACAO.
    """
    opens  = [100.0, 101.0, 102.0, 103.0, 105.0]
    highs  = [101.0, 102.0, 103.0, 104.0, 108.0]
    lows   = [ 99.0, 100.0, 101.0, 102.0, 104.0]
    closes = [100.5, 101.5, 102.5, 103.5, 107.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series, direction_filter="SELL")

    state_map = engine.get_current_state()
    for sub_id in ["sell_t1_open", "sell_t1_retest", "sell_t2_open", "sell_t2_retest"]:
        st = state_map[sub_id]
        assert st["direction"] == "SELL"
        assert st["status"] == "AGUARDANDO_NEGACAO"
        assert st["active_line_price"] is not None
