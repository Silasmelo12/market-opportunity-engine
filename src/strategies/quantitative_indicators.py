"""
Quantitative Indicators Strategy Engine.
Implements 10 quantitative technical indicators across 4 families:
1. Mean Reversion: Bollinger Close-In, Keltner Squeeze, Z-Score Extremes.
2. Oscillators & Divergences: RSI Divergence, Stochastic Extremes, MACD Histogram Momentum.
3. Institutional Volume & Flow: VWAP Bands, Money Flow Index (MFI), Volume Climax / VSA Absorption.
4. Volatility & Trend: SuperTrend / ATR Trailing.

Strictly adheres to Zero Look-Ahead Bias:
- Calculations at bar t incorporate data up to Close[t].
- Fill/execution occurs at Open[t+1] on the subsequent bar.
- Fully vectorized via NumPy and Pandas.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

from .base import OHLCVSeries, SignalRecord, ReferenceLineSegment


# ==========================================
# Contiguous Vectorized Helpers (Anti-Lookahead)
# ==========================================

def compute_sma(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Simple Moving Average using rolling window."""
    s = pd.Series(arr)
    return s.rolling(window=period, min_periods=period).mean().to_numpy()


def compute_ema(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Exponential Moving Average."""
    s = pd.Series(arr)
    return s.ewm(span=period, adjust=False).mean().to_numpy()


def compute_rolling_std(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Rolling Standard Deviation."""
    s = pd.Series(arr)
    return s.rolling(window=period, min_periods=period).std().to_numpy()


def compute_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    """Calculates Average True Range (Wilder/EMA smoothed)."""
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]

    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    s_tr = pd.Series(tr)
    return s_tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()


def compute_rsi_series(close: np.ndarray, period: int = 14) -> np.ndarray:
    """Calculates Relative Strength Index (RSI)."""
    diff = np.diff(close, prepend=close[0])
    gain = np.where(diff > 0, diff, 0.0)
    loss = np.where(diff < 0, -diff, 0.0)

    s_gain = pd.Series(gain)
    s_loss = pd.Series(loss)

    avg_gain = s_gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()
    avg_loss = s_loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()

    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi[avg_loss == 0] = 100.0
    return rsi



class QuantitativeIndicatorsEngine:
    """
    Engine executing quantitative technical indicator strategies.
    """

    SUPPORTED_STRATEGIES = [
        "bollinger_close_in",
        "keltner_squeeze",
        "zscore_extreme",
        "rsi_divergence",
        "stochastic_extreme",
        "macd_momentum",
        "vwap_bands",
        "mfi_extreme",
        "volume_climax_vsa",
        "supertrend_trailing",
    ]

    def __init__(self) -> None:
        self.supported_strategies = list(self.SUPPORTED_STRATEGIES)
        self.pending_signals: List[Dict[str, Any]] = []

