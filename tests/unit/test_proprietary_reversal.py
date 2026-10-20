"""
Unit tests for ProprietaryReversalEngine (2x2 State Machine) - FR-004 edge cases:
1. Successive bearish breakouts without negation (dynamic overwrite of active_ref_line).
2. Sequential evaluation in window M: execution on the first touch t+k and cycle termination.
3. Gap down on retest open (Open[t+k] < Linha * (1 + tol)) filling at Open[t+k].
4. Touch on retest with close below the line (Low[t+k] <= Linha, Close[t+k] < Linha) filling at Linha.
5. Retest expiration after M bars without touch.
6. Complete state independence among the 4 variants and last-bar current state tracking.
"""

import numpy as np
import pandas as pd
import pytest
from src.strategies.base import OHLCVSeries
from src.strategies.proprietary_reversal import ProprietaryReversalEngine


def make_series(opens, highs, lows, closes, ticker="TEST") -> OHLCVSeries:
    n = len(closes)
    timestamps = pd.date_range("2024-01-01", periods=n, freq="D").to_numpy(dtype="datetime64[ns]")
    return OHLCVSeries(
        ticker=ticker,
        interval="1d",
        timestamps=timestamps,
        open=np.array(opens, dtype=np.float64),
        high=np.array(highs, dtype=np.float64),
        low=np.array(lows, dtype=np.float64),
        close=np.array(closes, dtype=np.float64),
        volume=np.ones(n, dtype=np.float64) * 1000.0,
        dividends=np.zeros(n, dtype=np.float64),
        dy_rolling_12m=np.zeros(n, dtype=np.float64),
    )


def test_successive_breakouts_overwrite_reference_line():
    """
    Verifies that successive bearish breakouts before negation overwrite the Active Reference Line
    so that only the latest broken low triggers negation.
    """
    # Bar 0: Low = 100, Close = 102
    # Bar 1: Close = 98 < Low[0](100) -> 1st Breakout! Active Line = 100.0, Low[1] = 95.0
    # Bar 2: Close = 93 < Low[1](95)  -> 2nd Breakout before negation! Overwrites Active Line = 95.0
    # Bar 3: Close = 97 > 95.0 (Note: 97 is < 100.0! It negates 95.0 because 100.0 was overwritten!)
    # Bar 4: Open = 97.5 (Execution for t1_open)
    opens  = [103.0, 100.0, 95.0, 94.0, 97.5]
    highs  = [104.0, 101.0, 96.0, 98.0, 99.0]
    lows   = [100.0,  95.0, 92.0, 93.0, 96.0]
    closes = [102.0,  98.0, 93.0, 97.0, 98.5]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series, variant_filter=["t1_open"])

    assert len(signals) == 1
    sig = signals[0]
    assert sig.strategy_sub_id == "t1_open"
    assert sig.signal_bar_index == 3
    assert sig.execution_bar_index == 4
    assert sig.execution_price == pytest.approx(97.5)
    assert sig.reference_line_price == pytest.approx(95.0)

    # First segment (100.0) must be marked CANCELLED, second (95.0) NEGATED_EXECUTED
    t1_segs = [s for s in segments if s.variation_id == "t1_open"]
    assert len(t1_segs) == 2
    assert t1_segs[0].price_level == pytest.approx(100.0)
    assert t1_segs[0].status == "CANCELLED"
    assert t1_segs[1].price_level == pytest.approx(95.0)
    assert t1_segs[1].status == "NEGATED_EXECUTED"


def test_retest_single_cycle_first_touch_only():
    """
    Verifies that in Retest mode, the first bar t+k (1 <= k <= M) touching the line
    executes the buy and consumes the line immediately, ignoring subsequent touches in M.
    """
    # Bar 0: Low = 100
    # Bar 1: Close = 98 < 100 -> Breakout! Line = 100.0
    # Bar 2: Close = 105 > 100 -> Negation at t=2! Wait window M=3 covers bars 3, 4, 5.
    # Bar 3 (k=1): Open=104, Low=101, Close=103 -> No touch (Low=101 > 100)
    # Bar 4 (k=2): Open=103, Low=99.5, Close=102 -> TOUCH! Executes at 100.0 on bar 4.
    # Bar 5 (k=3): Open=102, Low=99.0, Close=103 -> Also touches 100, but line is already consumed!
    opens  = [102.0, 100.0,  99.0, 104.0, 103.0, 102.0]
    highs  = [103.0, 101.0, 106.0, 105.0, 104.0, 104.0]
    lows   = [100.0,  97.0,  98.0, 101.0,  99.5,  99.0]
    closes = [101.0,  98.0, 105.0, 103.0, 102.0, 103.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, _ = engine.generate_signals(series, variant_filter=["t1_retest"])

    assert len(signals) == 1
    sig = signals[0]
    assert sig.signal_bar_index == 2
    assert sig.execution_bar_index == 4
    assert sig.execution_price == pytest.approx(100.0)
    assert sig.metadata["fill_type"] == "retest_touch"
    assert sig.metadata["retest_bar_offset"] == 2


def test_retest_gap_down_executes_at_open():
    """
    Verifies FR-004 Gap Rule: if bar t+k opens with a gap below Linha * (1 + tol),
    P_exec is registered at the actual Open[t+k] price.
    """
    # Bar 0: Low = 100
    # Bar 1: Close = 98 < 100 -> Breakout! Line = 100.0
    # Bar 2: Close = 103 > 100 -> Negation at t=2!
    # Bar 3 (k=1): Opens in gap down at Open = 96.5 (< 100.0), Low = 95.0, Close = 99.0
    opens  = [102.0, 100.0,  98.5,  96.5, 99.0]
    highs  = [103.0, 101.0, 104.0, 100.0, 101.0]
    lows   = [100.0,  97.0,  98.0,  95.0, 98.0]
    closes = [101.0,  98.0, 103.0,  99.0, 100.5]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, _ = engine.generate_signals(series, variant_filter=["t1_retest"])

    assert len(signals) == 1
    sig = signals[0]
    assert sig.signal_bar_index == 2
    assert sig.execution_bar_index == 3
    assert sig.execution_price == pytest.approx(96.5)
    assert sig.metadata["fill_type"] == "retest_gap"


def test_retest_touch_and_close_below_still_executes_at_line():
    """
    Verifies FR-004 Simultaneity Rule: if bar t+k opens above the line, touches the line
    (Low[t+k] <= Linha * (1 + tol)), and closes below the line (Close[t+k] < Linha),
    the limit order was already filled at Linha.
    """
    # Bar 0: Low = 100
    # Bar 1: Close = 98 < 100 -> Breakout! Line = 100.0
    # Bar 2: Close = 104 > 100 -> Negation at t=2!
    # Bar 3 (k=1): Open = 102.0 (>= 100), Low = 97.0 (<= 100), Close = 98.0 (< 100)
    opens  = [102.0, 100.0,  98.5, 102.0]
    highs  = [103.0, 101.0, 105.0, 102.5]
    lows   = [100.0,  97.0,  98.0,  97.0]
    closes = [101.0,  98.0, 104.0,  98.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=3, tolerance_pct=0.0)
    signals, _ = engine.generate_signals(series, variant_filter=["t1_retest"])

    assert len(signals) == 1
    sig = signals[0]
    assert sig.signal_bar_index == 2
    assert sig.execution_bar_index == 3
    assert sig.execution_price == pytest.approx(100.0)
    assert sig.metadata["fill_type"] == "retest_touch"


def test_retest_expiration_after_m_bars_without_touch():
    """
    Verifies that if M bars pass after negation without Low[t+k] touching Linha * (1 + tol),
    the setup expires with 0 executed buys and status 'EXPIRED'.
    """
    # Bar 0: Low = 100
    # Bar 1: Close = 98 < 100 -> Breakout! Line = 100.0
    # Bar 2: Close = 105 > 100 -> Negation at t=2! M = 2 (bars 3 and 4)
    # Bar 3 (k=1): Low = 103 > 100
    # Bar 4 (k=2): Low = 104 > 100 -> Expires at end of bar 4!
    # Bar 5 (k=3): Low = 99 <= 100, Close = 105.0 -> Wick touches 100 on k=3, but window M=2 already expired!
    opens  = [102.0, 100.0,  99.0, 105.0, 106.0, 104.5]
    highs  = [103.0, 101.0, 106.0, 107.0, 108.0, 106.0]
    lows   = [100.0,  97.0,  98.0, 103.0, 104.0,  99.0]
    closes = [101.0,  98.0, 105.0, 106.0, 107.0, 105.0]

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=2, retest_window_m=2, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series, variant_filter=["t1_retest"])

    assert len(signals) == 0
    assert len(segments) == 1
    assert segments[0].status == "EXPIRED"
    assert segments[0].start_bar_index == 1
    assert segments[0].end_bar_index == 4
    assert engine.total_signals_by_variant["t1_retest"] == 1


def test_four_variants_independence_and_current_state():
    """
    Verifies that all 4 variants run simultaneously without state contamination
    and accurately report the current state on the final bar (t = len - 1).
    """
    # 6 bars where a breakout remains active on the final bar
    opens  = [105.0, 104.0, 103.0, 102.0, 101.0, 99.0]
    highs  = [106.0, 105.0, 104.0, 103.0, 102.0, 99.5]
    lows   = [103.0, 102.0, 101.0, 100.0,  99.0, 96.0]
    closes = [104.0, 103.0, 102.0, 101.0, 100.0, 97.0]  # Bar 5 closes at 97 < Low[4](99) and < min(Low[2:5])(99)

    series = make_series(opens, highs, lows, closes)
    engine = ProprietaryReversalEngine(lookback_n=3, retest_window_m=3, tolerance_pct=0.0)
    signals, segments = engine.generate_signals(series)

    assert len(signals) == 0
    state_map = engine.get_current_state()
    assert {"t1_open", "t1_retest", "t2_open", "t2_retest"}.issubset(set(state_map.keys()))

    for sub_id in ["t1_open", "t1_retest", "t2_open", "t2_retest"]:
        st = state_map[sub_id]
        assert st["status"] == "AGUARDANDO_NEGACAO"
        assert st["active_line_price"] == pytest.approx(99.0)
        assert st["breakout_bar_index"] == 5
