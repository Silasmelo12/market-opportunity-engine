"""
Fixtures and synthetic OHLCV generators for testing refined double bottom and double top patterns.
"""

from typing import Tuple
import numpy as np
from src.strategies.base import OHLCVSeries


def make_series(
    open_p: np.ndarray,
    high_p: np.ndarray,
    low_p: np.ndarray,
    close_p: np.ndarray,
    volume: np.ndarray = None,
    dates: list = None,
) -> OHLCVSeries:
    n = len(close_p)
    if volume is None:
        volume = np.full(n, 1000.0, dtype=np.float64)
    if dates is None:
        dates = [f"2025-01-{(i % 28) + 1:02d}" for i in range(n)]
    return OHLCVSeries(
        open=open_p.astype(np.float64),
        high=high_p.astype(np.float64),
        low=low_p.astype(np.float64),
        close=close_p.astype(np.float64),
        volume=volume.astype(np.float64),
        dates=dates,
    )


def create_vertical_rally_double_bottom(n_bars: int = 120) -> OHLCVSeries:
    """
    Creates a synthetic series with a strong vertical rally where minor pauses
    in the high region trigger raw double bottoms, but should be REJECTED by refined rules:
    - Located at 60-bar highest highs
    - Occurring way above SMA50
    - No prior downward drop (prior drop < 5%)
    - RSI during pause stays high (> 50-60)
    """
    prices = np.linspace(50.0, 150.0, n_bars)
    # Add a fake mini-double bottom at the top (around bar 100)
    prices[95] = 142.0  # b1
    prices[96] = 145.0  # neckline
    prices[97] = 142.1  # b2
    prices[98] = 147.0  # breakout!
    prices[99:] = 150.0

    high = prices + 1.0
    low = prices - 1.0
    open_p = prices - 0.2
    close_p = prices.copy()
    close_p[98] = 147.0

    return make_series(open_p, high, low, close_p)


def create_valid_reversal_double_bottom(n_bars: int = 120) -> OHLCVSeries:
    """
    Creates a realistic double bottom after a significant downtrend (> 10% drop),
    well below SMA50, with oversold RSI (< 45), forming B1 and B2, followed by a neck breakout
    which is NOT a 60-bar high, and break RSI <= 60.
    """
    # 0 to 60: downtrend from 100 down to 70 (30% drop)
    part1 = np.linspace(100.0, 70.0, 65)
    # 65 to 90: consolidation forming bottom B1, neckline, bottom B2
    # B1 at 68, Neckline at 74, B2 at 68.2, breakout at 75
    part2 = np.array([
        70.0, 69.0, 68.0, 69.5, 71.0, 72.5, 74.0, 73.0, 70.5, 69.0, 68.2, 69.0, 70.5, 72.0, 73.5, 75.0, 76.0
    ])
    # remaining bars steady around 76
    rem = np.linspace(76.0, 77.0, n_bars - len(part1) - len(part2))
    prices = np.concatenate([part1, part2, rem])

    close_p = prices.copy()
    high = prices + 0.8
    low = prices - 0.8
    open_p = prices - 0.1

    # Ensure neckline high is well marked
    # Neckline is at index 65 + 6 = 71
    high[71] = 74.2
    low[67] = 67.5   # B1
    low[75] = 67.6   # B2
    close_p[79] = 74.8  # breakout bar (c[t-1] <= neckline, c[t] > neckline)
    close_p[80] = 75.5

    return make_series(open_p, high, low, close_p)


def create_valid_reversal_double_top(n_bars: int = 120) -> OHLCVSeries:
    """
    Creates a realistic double top after a significant uptrend (> 10% gain),
    well above SMA50, with overbought RSI (> 55), forming T1 and T2, followed by support breakdown
    which is NOT a 60-bar low, and break RSI >= 40.
    """
    # 0 to 65: uptrend from 50 up to 90
    part1 = np.linspace(50.0, 90.0, 65)
    # 65 to 85: consolidation forming T1, Neckline, T2, breakdown
    part2 = np.array([
        90.0, 92.0, 93.0, 91.5, 89.0, 87.0, 86.0, 87.5, 89.5, 91.5, 93.1, 91.0, 89.0, 87.0, 85.0, 83.5, 82.0
    ])
    rem = np.linspace(82.0, 81.0, n_bars - len(part1) - len(part2))
    prices = np.concatenate([part1, part2, rem])

    close_p = prices.copy()
    high = prices + 0.8
    low = prices - 0.8
    open_p = prices + 0.1

    # T1 at index 67, T2 at index 75, Neckline at index 71
    high[67] = 93.5
    high[75] = 93.6
    low[71] = 85.8
    close_p[79] = 85.5  # breakdown bar
    close_p[80] = 84.0

    return make_series(open_p, high, low, close_p)
