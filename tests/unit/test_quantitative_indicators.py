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
