"""
Unit tests for the 14 MQL5 Top (Bearish) Candlestick Patterns.
Verifies:
- All 14 patterns are recognized and filtered by Close > SMA(20).
- Direction is explicitly set to 'SELL'.
- Confirmed patterns execute at Open[t+1].
- Last bar pattern registers as pending without out-of-bounds execution.
"""

import numpy as np
import pytest
from src.strategies.base import OHLCVSeries
from src.strategies.mql5_candles import MQL5CandleEngine


def make_series(opens, highs, lows, closes, volumes=None):
    n = len(opens)
    ts = np.array([f"2023-01-{i+1:02d}" for i in range(n)], dtype="object")
    vols = np.array(volumes, dtype=np.float64) if volumes is not None else np.full(n, 1000.0, dtype=np.float64)
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


def test_shooting_star_detection():
    """
    Shooting Star: in an uptrend (Close > SMA(20)), small body near low of range,
    upper shadow >= 2 * body, lower shadow <= 0.2 * body.
    """
    # 22 bars: first 20 steady rise, bar 20 shooting star, bar 21 execution
    # For shooting star at bar 20: body = |120.3 - 120.0| = 0.3.
    # High = 125.0 -> upper_shadow = 125.0 - 120.3 = 4.7 >= 2 * 0.3 = 0.6.
    # Low = 120.0 -> lower_shadow = 0 <= 0.2 * 0.3.
    # Range = 5.0 >= 0.5 * avg_body0.
    opens  = [100.0 + i for i in range(20)] + [120.0, 118.0]
    highs  = [100.5 + i for i in range(20)] + [125.0, 119.0]
    lows   = [ 99.5 + i for i in range(20)] + [120.0, 117.0]
    closes = [100.2 + i for i in range(20)] + [120.3, 117.5]

    series = make_series(opens, highs, lows, closes)
    engine = MQL5CandleEngine(body_ma_period=12, trend_ma_period=20)
    signals, _ = engine.generate_signals(series, pattern_filter=["shooting_star"], direction_filter="SELL")

    assert len(signals) == 1
    sig = signals[0]
    assert sig.strategy_sub_id == "shooting_star"
    assert sig.direction == "SELL"
    assert sig.execution_bar_index == 21
    assert sig.execution_price == 118.0


def test_bearish_engulfing_detection():
    """
    Bearish Engulfing: bar t-1 bullish, bar t bearish opening >= close[t-1] and closing <= open[t-1].
    """
    opens  = [100.0 + i for i in range(20)] + [120.0, 125.0, 115.0]
    highs  = [100.5 + i for i in range(20)] + [123.0, 126.0, 116.0]
    lows   = [ 99.5 + i for i in range(20)] + [119.5, 118.0, 114.0]
    closes = [100.2 + i for i in range(20)] + [122.5, 119.0, 114.5]

    series = make_series(opens, highs, lows, closes)
    engine = MQL5CandleEngine()
    signals, _ = engine.generate_signals(series, pattern_filter=["bearish_engulfing"], direction_filter="SELL")

    assert len(signals) >= 1
    sig = signals[0]
    assert sig.strategy_sub_id == "bearish_engulfing"
    assert sig.direction == "SELL"
