"""
End-to-End Integration and Pipeline Serialization Validation Test.
Simulates loading, strategy execution, statistical evaluation, and UI payload generation
for multiple assets across all 5 supported market classes.
"""

import numpy as np
import pytest
from src.data_loader import DataLoader
from src.strategies import StrategyCatalog
from src.evaluator import evaluate_all_strategies
from src.ui.price_chart import _format_date


TEST_TICKERS = [
    "AAPL",        # US Stock
    "PETR4.SA",    # B3 Stock
    "HGLG11.SA",   # B3 FII
    "BTC-USD",     # Crypto
    "CL=F",        # Commodity
]


@pytest.mark.parametrize("ticker", TEST_TICKERS)
def test_full_pipeline_multi_market(ticker: str):
    """
    Validates end-to-end data fetching, 18-strategy execution, prospective evaluation,
    and JSON/Plotly UI data conversion for each asset class.
    """
    try:
        series = DataLoader.load_asset_data(ticker=ticker, interval="1d", period="1y", use_cache=True)
    except Exception as e:
        pytest.skip(f"Network/yfinance unavailable for {ticker}: {e}")

    assert series.length > 50
    assert series.close.dtype == np.float64
    assert series.open.dtype == np.float64

    # Run all 18 strategies
    catalog = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)
    res = catalog.run_all(series)

    signals = res["signals"]
    lines = res["reference_lines"]
    prop_state = res["prop_current_state"]
    pending = res["pending_signals"]

    # Verify state snapshot keys
    assert {"t1_open", "t1_retest", "t2_open", "t2_retest"}.issubset(set(prop_state.keys()))

    # Evaluate performance over X=60
    summaries = evaluate_all_strategies(
        series=series,
        signals=signals,
        horizon_bars=60,
        total_signals_by_sub_id=res["total_signals_by_sub_id"],
    )

    # Validate UI payload formats and JSON serialization safety
    dates = [_format_date(ts) for ts in series.timestamps]
    assert len(dates) == series.length
    assert all(isinstance(d, str) and len(d) == 10 for d in dates)

    # Verify every signal can serialize float prices safely
    for sig in signals:
        assert isinstance(float(sig.execution_price), float)
        assert isinstance(int(sig.execution_bar_index), int)
        if sig.reference_line_price is not None:
            assert isinstance(float(sig.reference_line_price), float)

    # Verify reference lines
    for line in lines:
        assert isinstance(float(line.price_level), float)
        assert isinstance(int(line.start_bar_index), int)
        assert isinstance(int(line.end_bar_index), int)

    # Verify summaries
    for s in summaries:
        assert 0.0 <= s.win_rate <= 100.0
        assert isinstance(s.mean_forward_return, float)
        assert isinstance(s.mean_mae, float)
        assert isinstance(s.efficiency_score, float)
