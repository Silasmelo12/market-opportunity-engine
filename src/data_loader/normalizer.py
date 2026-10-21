"""
Data normalization, rolling metric computation, and OHLCV resampling.
"""

from typing import Tuple, Optional
import numpy as np
import pandas as pd
from ..strategies.base import OHLCVSeries


RESAMPLE_RULES = {
    "2h": "2h",
    "4h": "4h",
    "12h": "12h",
}


def resample_ohlcv(df: pd.DataFrame, target_interval: str) -> pd.DataFrame:
    """
    Resamples a 1h (or higher-frequency) OHLCV DataFrame to 2h, 4h, or 12h intervals:
    Open='first', High='max', Low='min', Close='last', Volume='sum'
    Removes NaN windows (non-trading periods, weekends, pre/post-market gaps).
    """
    rule = RESAMPLE_RULES.get(target_interval.lower())
    if not rule:
        return df

    # Standardize column names to lower case
    df_copy = df.copy()
    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = [col[0] for col in df_copy.columns]
    df_copy.columns = [str(c).strip().lower() for c in df_copy.columns]

    agg_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
    }
    if "volume" in df_copy.columns:
        agg_dict["volume"] = "sum"
    if "dividends" in df_copy.columns:
        agg_dict["dividends"] = "sum"

    resampled = df_copy.resample(rule).agg(agg_dict)
    # Immediately drop rows with no trade executions
    resampled = resampled.dropna(subset=["close", "open"]).sort_index()
    return resampled


def clean_and_normalize_df(df: pd.DataFrame, ticker: str, interval: str) -> OHLCVSeries:
    """
    Cleans raw yfinance dataframe, handles multi-index columns, fills missing data,
    computes Dividend Yield Rolling 12m (if dividends present), and converts to OHLCVSeries.
    Adapts rolling windows for intraday data where 252 days are not present.
    """
    df = df.copy()

    # Handle multi-index columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # Standardize column names to lower case
    df.columns = [str(c).strip().lower() for c in df.columns]

    # If interval is 2h, 4h, or 12h, apply resampling from base 1h data
    if interval.lower() in RESAMPLE_RULES:
        df = resample_ohlcv(df, target_interval=interval)

    # Ensure required columns exist
    required = ["open", "high", "low", "close", "volume"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' for ticker {ticker}")

    # Drop bars with missing close or open
    df = df.dropna(subset=["open", "high", "low", "close"]).sort_index()

    # Normalize index to timezone-naive timestamps
    if isinstance(df.index, pd.DatetimeIndex):
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        timestamps = df.index.to_numpy(dtype="datetime64[ns]")
    else:
        timestamps = pd.to_datetime(df.index).to_numpy(dtype="datetime64[ns]")

    # Extract OHLCV arrays
    open_arr = df["open"].to_numpy(dtype=np.float64)
    high_arr = df["high"].to_numpy(dtype=np.float64)
    low_arr = df["low"].to_numpy(dtype=np.float64)
    close_arr = df["close"].to_numpy(dtype=np.float64)
    volume_arr = df["volume"].to_numpy(dtype=np.float64)

    # Normalize Forex daily/weekly candles:
    # Yahoo Finance records open ~= close (zero/tiny body) for daily Forex pairs (e.g. EURUSD=X),
    # producing artificial dash candles. In continuous 24h forex markets, the daily open is the previous close.
    is_fx = ticker.endswith("=X") or "=X" in ticker.upper() or "/USD" in ticker.upper()
    if is_fx and interval.lower() in ("1d", "1wk") and len(close_arr) > 1:
        body_diff = np.abs(close_arr - open_arr)
        rng = np.maximum(high_arr - low_arr, 1e-9)
        if np.nanmedian(body_diff / rng) < 0.08:
            new_open = open_arr.copy()
            new_open[1:] = close_arr[:-1]
            open_arr = new_open
            high_arr = np.maximum(high_arr, open_arr)
            low_arr = np.minimum(low_arr, open_arr)

    # Dividends handling
    if "dividends" in df.columns:
        div_arr = df["dividends"].fillna(0.0).to_numpy(dtype=np.float64)
    else:
        div_arr = np.zeros(len(close_arr), dtype=np.float64)

    # Calculate Rolling 12M Dividend Yield
    # In daily: approx 252 bars. In weekly: approx 52 bars.
    # In intraday: adapt window to avoid requiring 252 days when max yfinance history is 60d.
    inter_lower = interval.lower()
    if inter_lower == "1wk":
        rolling_window = 52
    elif inter_lower == "1d":
        rolling_window = 252
    elif inter_lower in ("1h", "2h", "4h", "12h"):
        # For hourly data, use approx 1 month to 3 months of bars or minimum
        rolling_window = min(len(close_arr), 120)
    else:
        # For minutes (5m, 15m, 30m)
        rolling_window = min(len(close_arr), 78)

    div_series = pd.Series(div_arr, index=df.index)
    close_series = pd.Series(close_arr, index=df.index)

    rolling_div_sum = div_series.rolling(window=max(1, rolling_window), min_periods=1).sum()
    dy_rolling = (rolling_div_sum / np.where(close_series > 0, close_series, np.nan)).fillna(0.0).to_numpy(dtype=np.float64)

    return OHLCVSeries(
        ticker=ticker,
        interval=interval,
        timestamps=timestamps,
        open=open_arr,
        high=high_arr,
        low=low_arr,
        close=close_arr,
        volume=volume_arr,
        dividends=div_arr,
        dy_rolling_12m=dy_rolling
    )
