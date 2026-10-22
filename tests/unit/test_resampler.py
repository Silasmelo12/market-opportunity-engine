"""
Unit tests for OHLCV Resampling and Intraday Data Normalization.
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from src.data_loader import resample_ohlcv, clean_and_normalize_df
from src.data_loader.fetcher import DataLoader, MAX_PERIODS


def test_resample_ohlcv_hourly_to_4h():
    """
    Verifies resampling of 1h bars into 4h bars:
    Open='first', High='max', Low='min', Close='last', Volume='sum'
    """
    # 8 consecutive 1h bars starting aligned at midnight (00:00 to 07:00 -> two 4h bars: 00:00 and 04:00)
    dates = pd.date_range("2024-01-01 00:00", periods=8, freq="1h")
    df = pd.DataFrame(
        {
            "open": [10.0, 10.5, 11.0, 11.5, 12.0, 12.2, 11.8, 12.5],
            "high": [10.8, 11.2, 11.8, 12.0, 12.5, 12.8, 12.1, 13.0],
            "low":  [ 9.8, 10.2, 10.9, 11.0, 11.7, 11.5, 11.2, 12.0],
            "close":[10.5, 11.0, 11.5, 11.8, 12.2, 11.8, 12.0, 12.8],
            "volume":[100,  150,  200,  250,  300,  350,  400,  450],
        },
        index=dates,
    )

    resampled = resample_ohlcv(df, target_interval="4h")
    assert len(resampled) == 2

    bar1 = resampled.iloc[0]
    assert bar1["open"] == pytest.approx(10.0)      # Open of first 1h bar
    assert bar1["high"] == pytest.approx(12.0)      # Max high of first 4 bars
    assert bar1["low"] == pytest.approx(9.8)        # Min low of first 4 bars
    assert bar1["close"] == pytest.approx(11.8)     # Close of 4th 1h bar
    assert bar1["volume"] == pytest.approx(700)     # 100+150+200+250

    bar2 = resampled.iloc[1]
    assert bar2["open"] == pytest.approx(12.0)
    assert bar2["high"] == pytest.approx(13.0)
    assert bar2["low"] == pytest.approx(11.2)
    assert bar2["close"] == pytest.approx(12.8)
    assert bar2["volume"] == pytest.approx(1500)    # 300+350+400+450


def test_resample_ohlcv_drops_nan_gaps():
    """
    Ensures that empty periods (e.g., weekends, non-trading hours) do not produce NaN bars.
    """
    dates = pd.to_datetime(["2024-01-01 10:00", "2024-01-01 11:00", "2024-01-03 10:00", "2024-01-03 11:00"])
    df = pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0],
            "high": [11.5, 12.5, 13.5, 14.5],
            "low": [9.5, 10.5, 11.5, 12.5],
            "close": [11.0, 12.0, 13.0, 14.0],
            "volume": [100, 200, 300, 400],
        },
        index=dates,
    )

    res = resample_ohlcv(df, target_interval="2h")
    # Must only contain rows with actual trades, no NaN rows
    assert not res.isna().any().any()
    assert len(res) == 2


def test_clean_and_normalize_intraday_window():
    """
    Ensures clean_and_normalize_df adapts rolling window for short intraday data.
    """
    dates = pd.date_range("2024-01-01 09:30", periods=50, freq="5min")
    df = pd.DataFrame(
        {
            "Open": np.linspace(10, 15, 50),
            "High": np.linspace(11, 16, 50),
            "Low": np.linspace(9, 14, 50),
            "Close": np.linspace(10.5, 15.5, 50),
            "Volume": np.ones(50) * 1000,
        },
        index=dates,
    )

    series = clean_and_normalize_df(df, ticker="TEST_INTRA", interval="5m")
    assert series.length == 50
    assert series.interval == "5m"
    assert series.dy_rolling_12m is not None


def test_load_asset_data_hourly_60m_supported():
    """
    Verifies that DataLoader supports '60m' and '1h' intervals,
    mapping them to the 730d ceiling without raising ValueError.
    """
    assert "60m" in MAX_PERIODS
    assert MAX_PERIODS["60m"] == "730d"
    assert MAX_PERIODS["1h"] == "730d"

    dummy_df = pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [11.0, 12.0],
            "Low": [9.5, 10.5],
            "Close": [10.5, 11.5],
            "Volume": [1000, 2000],
        },
        index=pd.date_range("2024-01-01 10:00", periods=2, freq="1h")
    )

    with patch("yfinance.Ticker") as mock_ticker_cls:
        mock_instance = MagicMock()
        mock_instance.history.return_value = dummy_df
        mock_ticker_cls.return_value = mock_instance

        # Test with interval="60m" and period="2y"
        series_60m = DataLoader.load_asset_data(
            ticker="MOCK_TEST_60M",
            interval="60m",
            period="2y",
            use_cache=False
        )
        assert series_60m is not None
        assert series_60m.interval == "60m"
        call_kwargs = mock_instance.history.call_args.kwargs
        assert call_kwargs["period"] == "730d"

        # Test with interval="1h" and period="5y"
        series_1h = DataLoader.load_asset_data(
            ticker="MOCK_TEST_1H",
            interval="1h",
            period="5y",
            use_cache=False
        )
        assert series_1h is not None
        assert series_1h.interval == "1h"
        call_kwargs = mock_instance.history.call_args.kwargs
        assert call_kwargs["period"] == "730d"

