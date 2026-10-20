import pytest
import numpy as np
import pandas as pd
from src.strategies.base import OHLCVSeries
from src.strategies.mql5_candles import MQL5CandleEngine
from src.ui.theme import STRATEGY_LABELS_PT


def test_mql5_engine_has_14_patterns():
    engine = MQL5CandleEngine()
    assert len(engine.BULLISH_PATTERNS) == 14
    assert len(engine.BEARISH_PATTERNS) == 14
    assert len(engine.PATTERNS) == 28
    expected_new = [
        "inverted_hammer",
        "tweezer_bottom",
        "dragonfly_doji",
        "abandoned_baby_bullish",
        "bullish_kicker",
        "climactic_pinbar",
    ]
    for p in expected_new:
        assert p in engine.PATTERNS
        assert p in STRATEGY_LABELS_PT


def test_inverted_hammer_detection():
    # Build a 25 bar downtrend where bar 22 is an inverted hammer
    n = 25
    dates = pd.date_range("2024-01-01", periods=n, freq="1D")
    # Base downtrend: prices falling from 100 to 50
    close = np.linspace(100, 50, n)
    open_p = close + 1.0
    high = open_p + 0.5
    low = close - 0.5
    volume = np.full(n, 1000.0)

    # Inverted hammer at bar 20: small body, upper shadow >= 2 * body, small lower shadow
    t = 20
    open_p[t] = 52.0
    close[t] = 52.2  # body = 0.2
    high[t] = 54.0   # upper shadow = 1.8 (>= 2 * 0.2)
    low[t] = 51.95   # lower shadow = 0.05 (<= 0.3 * 0.2)

    series = OHLCVSeries(
        ticker="TEST",
        interval="1d",
        timestamps=np.array(dates.astype("int64") // 10**9),
        open=open_p,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )

    engine = MQL5CandleEngine(body_ma_period=5, trend_ma_period=10)
    masks = engine.compute_pattern_masks(series)
    assert masks["inverted_hammer"][t] == True

    signals, _ = engine.generate_signals(series, pattern_filter=["inverted_hammer"])
    matching = [s for s in signals if s.signal_bar_index == t]
    assert len(matching) == 1
    assert matching[0].execution_bar_index == t + 1
    assert matching[0].execution_price == open_p[t + 1]


def test_zero_lookahead_on_final_bar():
    n = 25
    dates = pd.date_range("2024-01-01", periods=n, freq="1D")
    close = np.linspace(100, 50, n)
    open_p = close + 1.0
    high = open_p + 0.5
    low = close - 0.5
    volume = np.full(n, 1000.0)

    # Make the last bar (n-1) an inverted hammer
    t = n - 1
    open_p[t] = 50.0
    close[t] = 50.2
    high[t] = 53.0
    low[t] = 49.95

    series = OHLCVSeries(
        ticker="TEST",
        interval="1d",
        timestamps=np.array(dates.astype("int64") // 10**9),
        open=open_p,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )

    engine = MQL5CandleEngine(body_ma_period=5, trend_ma_period=10)
    signals, _ = engine.generate_signals(series, pattern_filter=["inverted_hammer"])

    # No signal executed past the array length
    for s in signals:
        assert s.execution_bar_index < n

    # Pending signal should be recorded for t = n - 1
    assert any(p["signal_bar_index"] == t for p in engine.pending_signals)
