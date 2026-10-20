"""
Mathematical proof and unit tests for Zero Look-Ahead Bias (Constitution Principle II)
and Evaluator isolation of open vs. closed signals across all 8 strategy families.
"""

import numpy as np
import pandas as pd
import pytest
from src.strategies.base import OHLCVSeries, SignalRecord
from src.strategies import (
    ProprietaryReversalEngine,
    MQL5CandleEngine,
    ClassicStrategiesEngine,
    StrategyCatalog,
)
from src.evaluator import (
    evaluate_strategy_performance,
    split_closed_and_open_signals,
)


def generate_synthetic_market_series(n: int = 350, seed: int = 42) -> OHLCVSeries:
    """
    Creates a realistic multi-regime synthetic OHLCV series with dividends
    that triggers proprietary, classic, and candlestick setups.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=np.float64)
    # Wave + noise to create trends, pullbacks, breakouts, and reversals
    base = 100.0 + 15.0 * np.sin(t / 12.0) - 8.0 * np.cos(t / 5.0) + rng.normal(0, 1.2, size=n)
    close = np.maximum(10.0, base)
    open_arr = np.maximum(10.0, close + rng.normal(0, 1.5, size=n))
    high = np.maximum(open_arr, close) + np.abs(rng.normal(0.5, 0.8, size=n))
    low = np.minimum(open_arr, close) - np.abs(rng.normal(0.5, 1.2, size=n))
    volume = rng.uniform(1000, 5000, size=n)
    dividends = np.where(np.arange(n) % 30 == 0, 0.8, 0.0)
    dy_rolling = pd.Series(dividends).rolling(252, min_periods=1).sum().to_numpy() / close

    timestamps = pd.date_range("2022-01-01", periods=n, freq="D").to_numpy(dtype="datetime64[ns]")
    return OHLCVSeries(
        ticker="SYNTH.SA",
        interval="1d",
        timestamps=timestamps,
        open=open_arr,
        high=high,
        low=low,
        close=close,
        volume=volume,
        dividends=dividends,
        dy_rolling_12m=dy_rolling,
    )


def slice_series(series: OHLCVSeries, end_len: int) -> OHLCVSeries:
    return OHLCVSeries(
        ticker=series.ticker,
        interval=series.interval,
        timestamps=series.timestamps[:end_len],
        open=series.open[:end_len],
        high=series.high[:end_len],
        low=series.low[:end_len],
        close=series.close[:end_len],
        volume=series.volume[:end_len],
        dividends=series.dividends[:end_len] if series.dividends is not None else None,
        dy_rolling_12m=series.dy_rolling_12m[:end_len] if series.dy_rolling_12m is not None else None,
    )


def _sig_key(s: SignalRecord):
    return (
        s.strategy_id,
        s.strategy_sub_id,
        s.signal_bar_index,
        s.execution_bar_index,
        round(s.execution_price, 6),
        round(s.reference_line_price, 6) if s.reference_line_price is not None else None,
    )


@pytest.mark.parametrize("cutoff", [120, 200, 280, 320])
def test_zero_lookahead_invariance_under_truncation(cutoff: int):
    """
    Proves that truncating future data at bar `cutoff` does NOT alter any signal
    whose execution occurred prior to `cutoff` across all 8 strategy families.
    """
    full_series = generate_synthetic_market_series(n=350, seed=42)
    truncated_series = slice_series(full_series, cutoff)

    full_cat = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)
    trunc_cat = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)

    full_res = full_cat.run_all(full_series)
    trunc_res = trunc_cat.run_all(truncated_series)

    # All signals in full_res that executed before `cutoff` must match trunc_res identically
    full_before_cutoff = [
        _sig_key(s) for s in full_res["signals"] if s.execution_bar_index < cutoff
    ]
    trunc_all = [_sig_key(s) for s in trunc_res["signals"]]

    assert full_before_cutoff == trunc_all

    # Furthermore, every signal must strictly satisfy execution_bar_index > signal_bar_index
    # and execution_bar_index < truncated_series.length
    for s in trunc_res["signals"]:
        assert s.execution_bar_index > s.signal_bar_index
        assert s.execution_bar_index < cutoff


def test_last_bar_pattern_registers_as_pending_without_out_of_bounds_exec():
    """
    Verifies that a pattern confirmed on the very last bar (t = len - 1) does NOT emit
    a SignalRecord with t_exec >= len, and instead populates pending_signals.
    """
    # Construct a 25-bar series where the final bar (t=24) forms a Hammer in a downtrend (Close < SMA20)
    n = 25
    opens = np.full(n, 100.0)
    highs = np.full(n, 101.0)
    lows = np.full(n, 99.0)
    closes = np.full(n, 100.0)

    # Bar 24 (last bar): drops below SMA20 (~100), forms a Hammer with long lower shadow
    opens[24] = 94.0
    closes[24] = 94.5   # body = 0.5, Close < SMA20
    highs[24] = 94.55   # upper shadow = 0.05 <= 0.3 * 0.5
    lows[24] = 91.0     # lower shadow = 3.0 >= 2.0 * 0.5

    timestamps = pd.date_range("2024-01-01", periods=n, freq="D").to_numpy(dtype="datetime64[ns]")
    series = OHLCVSeries(
        ticker="TEST",
        interval="1d",
        timestamps=timestamps,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        volume=np.ones(n) * 1000.0,
    )

    mql5 = MQL5CandleEngine()
    signals, _ = mql5.generate_signals(series, pattern_filter=["hammer"])

    # No executed signal with t_exec == 25 may exist
    assert all(s.execution_bar_index < n for s in signals)
    assert len(signals) == 0
    assert len(mql5.pending_signals) == 1
    assert mql5.pending_signals[0]["strategy_sub_id"] == "hammer"
    assert mql5.pending_signals[0]["signal_bar_index"] == 24


def test_evaluator_excludes_open_signals_from_closed_metrics():
    """
    Verifies that signals with `t_exec + X >= len(close)` are marked `is_open=True`,
    counted in `open_signals_count`, and excluded from `Win Rate %`, `Avg Forward Return`, and `MAE %`.
    """
    n = 50
    # Flat 100 price except controlled moves
    opens = np.full(n, 100.0)
    highs = np.full(n, 105.0)
    lows = np.full(n, 95.0)
    closes = np.full(n, 100.0)

    # Signal 1 (Closed): executed at t_exec = 10 at P_exec = 100.0, horizon X = 20 -> t_exec + X = 30 < 50
    # At bar 30, Close[30] = 120.0 (+20% win). Lowest low in [10..30] is 90.0 (-10% MAE).
    closes[30] = 120.0
    lows[15] = 90.0

    # Signal 2 (Closed): executed at t_exec = 12 at P_exec = 100.0, horizon X = 20 -> t_exec + X = 32 < 50
    # At bar 32, Close[32] = 90.0 (-10% loss). Lowest low in [12..32] is 90.0 (-10% MAE).
    closes[32] = 90.0

    # Signal 3 (Open!): executed at t_exec = 35 at P_exec = 100.0, horizon X = 20 -> 35 + 20 = 55 >= 50
    # Even if price drops to 50 at bar 49, this open signal MUST NOT distort closed stats!
    lows[49] = 50.0
    closes[49] = 50.0

    timestamps = pd.date_range("2024-01-01", periods=n, freq="D").to_numpy(dtype="datetime64[ns]")
    series = OHLCVSeries(
        ticker="EVAL_TEST",
        interval="1d",
        timestamps=timestamps,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        volume=np.ones(n) * 1000.0,
    )

    signals = [
        SignalRecord("prop_reversal", "t1_open", 9, 10, 100.0, 99.0, metadata={}),
        SignalRecord("prop_reversal", "t1_open", 11, 12, 100.0, 99.0, metadata={}),
        SignalRecord("prop_reversal", "t1_open", 34, 35, 100.0, 99.0, metadata={}),
    ]

    closed_sigs, open_sigs = split_closed_and_open_signals(series, signals, horizon_bars=20)
    assert len(closed_sigs) == 2
    assert len(open_sigs) == 1
    assert open_sigs[0].execution_bar_index == 35

    summary = evaluate_strategy_performance(series, signals, horizon_bars=20)

    assert summary.executed_buys == 3
    assert summary.open_signals_count == 1
    assert signals[0].metadata["is_open"] is False
    assert signals[1].metadata["is_open"] is False
    assert signals[2].metadata["is_open"] is True

    # Closed Win Rate must be 1 win out of 2 closed trades = 50.0%
    assert summary.win_rate == pytest.approx(50.0)
    # Closed Mean Forward Return must be (+20% + -10%) / 2 = +5.0%
    assert summary.mean_forward_return == pytest.approx(5.0)
    # Closed Mean MAE must be (-10% + -10%) / 2 = -10.0% (unaffected by -50% on open trade 3!)
    assert summary.mean_mae == pytest.approx(-10.0)
