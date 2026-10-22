"""
Data fetching layer with local Parquet cache, intraday ceiling rules, and yfinance integration.
"""

import os
from pathlib import Path
from typing import Optional
import pandas as pd
import yfinance as yf
from ..strategies.base import OHLCVSeries
from .normalizer import clean_and_normalize_df

CACHE_DIR = Path(".cache/data")

# Maximum allowed history windows by yfinance API for sub-daily timeframes
MAX_PERIODS = {
    "5m": "60d",
    "15m": "60d",
    "30m": "60d",
    "60m": "730d",
    "1h": "730d",
    "2h": "730d",
    "4h": "730d",
    "12h": "730d",
}


def _parse_period_days(period_str: str) -> Optional[int]:
    """Converts standard period strings like '60d', '1y', '2y', '5y' to approximate calendar days."""
    p = period_str.strip().lower()
    if p.endswith("d"):
        try:
            return int(p[:-1])
        except ValueError:
            return None
    elif p.endswith("y"):
        try:
            return int(p[:-1]) * 365
        except ValueError:
            return None
    elif p.endswith("mo") or p.endswith("m"):
        num = p.replace("mo", "").replace("m", "")
        try:
            return int(num) * 30
        except ValueError:
            return None
    return None


TICKER_ALIASES = {
    "WIN": "^BVSP",
    "WIN=F": "^BVSP",
    "WINFUT": "^BVSP",
    "MINIINDICE": "^BVSP",
    "IBOV": "^BVSP",
    "WDO": "USDBRL=X",
    "WDO=F": "USDBRL=X",
    "WDOFUT": "USDBRL=X",
    "MINIDOLAR": "USDBRL=X",
    "DOLAR": "USDBRL=X",
    "USDBRL": "USDBRL=X",
    "XAUUSD": "GC=F",
    "XAUUSD=X": "GC=F",
    "GOLD": "GC=F",
    "OURO": "GC=F",
}


class DataLoader:
    """
    Manages loading, caching, and multi-timeframe fetching of financial asset series.
    Downloads the maximum historical dataset once, caches in Parquet, and slices
    locally according to the requested period. Only reaches out to yfinance if the
    local cache doesn't exist or doesn't have sufficient historical depth.
    """

    @staticmethod
    def _get_cache_path(ticker: str, interval: str) -> Path:
        sanitized_ticker = ticker.replace("^", "").replace("=", "_").replace("/", "_")
        return CACHE_DIR / f"{sanitized_ticker}_{interval}.parquet"

    @classmethod
    def load_asset_data(
        cls,
        ticker: str,
        interval: str = "1d",
        period: str = "5y",
        use_cache: bool = True
    ) -> OHLCVSeries:
        """
        Fetches historical data from yfinance only when necessary.
        Caches locally in Parquet, slices dynamically by the requested period,
        and returns an immutable OHLCVSeries.
        """
        clean_key = ticker.strip().upper().replace(" ", "").replace("/", "")
        ticker = TICKER_ALIASES.get(clean_key, ticker.strip().upper())
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        inter_lower = interval.lower()
        cache_path = cls._get_cache_path(ticker, interval)

        # For 2h, 4h, and 12h, download base 1h data and resample
        download_interval = "1h" if inter_lower in ("2h", "4h", "12h") else interval

        # Determine download ceiling: download maximum allowed so subsequent period changes are 0ms local slices
        if inter_lower in MAX_PERIODS:
            download_period = MAX_PERIODS[inter_lower]
        else:
            download_period = "5y" if period in ("60d", "1y", "2y", "5y") else period

        req_days = _parse_period_days(period)
        max_allowed_days = _parse_period_days(download_period)
        effective_req_days = req_days
        if effective_req_days is not None and max_allowed_days is not None:
            effective_req_days = min(effective_req_days, max_allowed_days)

        df: pd.DataFrame = pd.DataFrame()

        # 1. Try reading from existing local parquet cache
        if use_cache and cache_path.exists():
            try:
                df = pd.read_parquet(cache_path)
            except Exception:
                df = pd.DataFrame()

        # 2. Check if cache satisfies requested period depth
        need_download = df.empty
        if not df.empty and effective_req_days is not None and len(df) > 0:
            cached_days = (df.index[-1] - df.index[0]).days
            # If user wants a longer period than what's currently in cache, fetch fresh data
            max_ceiling = max_allowed_days if max_allowed_days is not None else 1825
            if effective_req_days > cached_days + 15 and cached_days < max_ceiling - 30:
                need_download = True

        # 3. Only reach out to yfinance if not in cache or cache is insufficient
        if need_download:
            yf_ticker = yf.Ticker(ticker)
            try:
                df = yf_ticker.history(period=download_period, interval=download_interval, auto_adjust=True)
            except Exception:
                df = pd.DataFrame()

            if df.empty:
                df = yf.download(ticker, period=download_period, interval=download_interval, progress=False, auto_adjust=True)

            if df.empty:
                raise ValueError(f"Could not retrieve data for ticker '{ticker}' with interval '{interval}'.")

            # Persist downloaded data to local parquet cache
            try:
                df.to_parquet(cache_path)
            except Exception:
                pass

        # 4. Slice locally by requested period window (instant in-memory slice, zero network call)
        if not df.empty and req_days is not None and period not in ("max", "5y"):
            cutoff = df.index[-1] - pd.Timedelta(days=req_days)
            df = df[df.index >= cutoff]

        return clean_and_normalize_df(df, ticker=ticker, interval=interval)
