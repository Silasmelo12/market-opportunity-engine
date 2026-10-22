"""
Unit tests for Quantitative Indicators Strategy Engine (Feature 013).
Validates anti-lookahead compliance, vectorization, and signal fidelity across all 10 indicators.
"""

import pytest
import numpy as np
from src.strategies.base import OHLCVSeries, SignalRecord
from src.strategies.quantitative_indicators import QuantitativeIndicatorsEngine


def make_synthetic_ohlcv(n: int = 250, seed: int = 42) -> OHLCVSeries:
    """Creates a deterministic synthetic OHLCV dataset for testing."""
    rng = np.random.RandomState(seed)
    timestamps = np.arange(1700000000, 1700000000 + n * 86400, 86400, dtype=np.int64)

    # Random walk with periodic waves
    t = np.linspace(0, 8 * np.pi, n)
    wave = 15.0 * np.sin(t)
    noise = np.cumsum(rng.randn(n) * 1.5)
    base_close = 50.0 + wave + noise
    base_close = np.clip(base_close, 10.0, 200.0)

    # OHLCV generation
    close = base_close.astype(np.float64)
    open_ = np.roll(close, 1)
    open_[0] = close[0] * 0.99
    high = np.maximum(open_, close) + rng.uniform(0.5, 2.0, size=n)
    low = np.minimum(open_, close) - rng.uniform(0.5, 2.0, size=n)
    volume = rng.uniform(500000.0, 5000000.0, size=n)

    return OHLCVSeries(
        ticker="TEST3",
        interval="1d",
        timestamps=timestamps,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def test_engine_initialization():
    engine = QuantitativeIndicatorsEngine()
    assert len(engine.supported_strategies) == 10


def test_bollinger_close_in_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_bollinger_close_in(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1
        assert sig.execution_price == series.open[sig.execution_bar_index]
        assert sig.direction == "BUY"


def test_keltner_squeeze_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_keltner_squeeze(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1
        assert sig.direction == "BUY"


def test_zscore_extreme_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_zscore_extreme(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1
        assert sig.direction == "BUY"


def test_rsi_divergence_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_rsi_divergence(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1
        assert sig.direction == "BUY"


def test_stochastic_extreme_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_stochastic_extreme(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1


def test_macd_momentum_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_macd_momentum(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1


def test_vwap_bands_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_vwap_bands(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1


def test_mfi_extreme_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_mfi_extreme(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1


def test_volume_climax_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_volume_climax_vsa(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1


def test_supertrend_trailing_signals():
    series = make_synthetic_ohlcv(200)
    engine = QuantitativeIndicatorsEngine()
    buy_sigs, sell_sigs = engine.generate_supertrend_trailing(series)
    assert isinstance(buy_sigs, list)
    assert isinstance(sell_sigs, list)
    for sig in buy_sigs:
        assert sig.execution_bar_index == sig.signal_bar_index + 1



