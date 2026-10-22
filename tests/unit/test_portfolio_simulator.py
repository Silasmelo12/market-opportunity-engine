"""
Unit tests for Multi-Asset Portfolio Manager, Rebalancing Advisor & Simulator Engine (016).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategies.base import OHLCVSeries, SignalRecord
from src.evaluator.portfolio_simulator import (
    PortfolioHolding,
    AssetOpportunityProfile,
    calculate_potential_score,
    compute_asset_opportunity_profile,
    advise_portfolio_rebalance,
    is_integer_lot_ticker,
    round_shares_for_ticker,
)


def _make_mock_series(ticker: str = "PETR4.SA", n_bars: int = 80, base_price: float = 30.0) -> OHLCVSeries:
    dates = pd.date_range("2025-01-01", periods=n_bars, freq="D")
    ts = dates.values.astype("datetime64[ns]")
    t = np.arange(n_bars, dtype=np.float64)
    close = base_price + 4.0 * np.sin(t / 4.0) + 0.08 * t
    open_p = close - 0.2
    high = close + 0.8
    low = close - 0.8
    vol = np.full(n_bars, 100000.0, dtype=np.float64)
    return OHLCVSeries(
        ticker=ticker,
        interval="1d",
        timestamps=ts,
        open=open_p,
        high=high,
        low=low,
        close=close,
        volume=vol,
    )


def test_integer_vs_fractional_lot_rounding():
    assert is_integer_lot_ticker("PETR4.SA") is True
    assert is_integer_lot_ticker("HGLG11.SA") is True
    assert is_integer_lot_ticker("BTC-USD") is False
    assert is_integer_lot_ticker("AAPL") is False

    # .SA rounds down to whole integer in floor mode so cash is never exceeded
    assert round_shares_for_ticker("PETR4.SA", 41.89, mode="floor") == 41.0
    # Crypto keeps up to 4 decimals
    assert round_shares_for_ticker("BTC-USD", 0.12349, mode="floor") == 0.1234


def test_calculate_potential_score_bounds_and_monotonicity():
    score_ideal = calculate_potential_score(
        win_rate_pct=80.0,
        historical_return_pct=90.0,
        max_drawdown_pct=-6.0,
        timing_category="IDEAL",
        active_direction="BUY",
    )
    score_extended = calculate_potential_score(
        win_rate_pct=80.0,
        historical_return_pct=90.0,
        max_drawdown_pct=-6.0,
        timing_category="EXTENDED",
        active_direction="BUY",
    )
    score_late = calculate_potential_score(
        win_rate_pct=80.0,
        historical_return_pct=90.0,
        max_drawdown_pct=-6.0,
        timing_category="LATE",
        active_direction="BUY",
    )
    assert 0.0 <= score_late < score_extended < score_ideal <= 100.0


def test_compute_asset_opportunity_profile_identifies_champion():
    series = _make_mock_series("VALE3.SA", n_bars=60, base_price=50.0)
    signals = [
        SignalRecord("prop", "t1_open", 5, 6, 48.0, 47.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 18, 19, 56.0, 56.5, direction="SELL"),
        SignalRecord("prop", "t1_open", 30, 31, 50.0, 49.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 45, 46, 58.0, 58.5, direction="SELL"),
        SignalRecord("prop", "t1_open", 57, 58, float(series.close[-1]) - 0.5, float(series.low[57]), direction="BUY"),
    ]
    prof = compute_asset_opportunity_profile(
        ticker="VALE3.SA",
        series=series,
        signals=signals,
        asset_name="Vale",
        category="Ações Brasil",
    )
    assert prof.ticker == "VALE3.SA"
    assert prof.champion_buy_id == "t1_open"
    assert prof.champion_sell_id == "sell_t1_open"
    assert prof.closed_trades >= 2
    assert prof.win_rate_pct == 100.0
    assert 0.0 <= prof.potential_score <= 100.0


def test_advise_portfolio_10k_cash_respects_max_weight_cap_and_cash_conservation():
    profiles = [
        AssetOpportunityProfile("PETR4.SA", "Petrobras", "Ações Brasil", 38.0, "t1_open", "Negação", "sell_t1_open", "Topo", 82.0, 75.0, -7.0, 5, "BUY", "IDEAL", "Ideal", 0.5, 37.8, 86.0),
        AssetOpportunityProfile("VALE3.SA", "Vale", "Ações Brasil", 60.0, "t1_open", "Negação", "sell_t1_open", "Topo", 78.0, 62.0, -9.0, 4, "BUY", "IDEAL", "Ideal", 0.8, 59.5, 81.0),
        AssetOpportunityProfile("ITUB4.SA", "Itaú", "Ações Brasil", 34.0, "t1_open", "Negação", "sell_t1_open", "Topo", 75.0, 50.0, -6.0, 5, "BUY", "IDEAL", "Ideal", 0.4, 33.8, 78.0),
        AssetOpportunityProfile("WEGE3.SA", "WEG", "Ações Brasil", 42.0, "t1_open", "Negação", "sell_t1_open", "Topo", 70.0, 48.0, -8.0, 4, "BUY", "EXTENDED", "Estendido", 3.1, 40.7, 68.0),
        AssetOpportunityProfile("BBAS3.SA", "Banco do Brasil", "Ações Brasil", 28.0, "t1_open", "Negação", "sell_t1_open", "Topo", 68.0, 44.0, -7.5, 4, "BUY", "EXTENDED", "Estendido", 3.4, 27.1, 65.0),
    ]

    res = advise_portfolio_rebalance(
        available_cash=10000.0,
        holdings_input=[],
        opportunity_profiles=profiles,
        max_weight_pct=25.0,
        rebalance_band_pct=5.0,
    )

    assert res["total_portfolio_equity"] == 10000.0
    assert res["projected_cash_after"] >= 0.0
    buy_recs = [r for r in res["recommendations"] if r.action_type == "BUY"]
    assert len(buy_recs) >= 3
    total_spent = sum(r.order_value for r in buy_recs)
    assert total_spent <= 10000.0 + 1e-6
    for r in buy_recs:
        # Must respect 25% max weight cap and integer lot for .SA
        assert r.target_weight_pct <= 25.0 + 1e-2
        assert r.recommended_shares_delta == int(r.recommended_shares_delta)


def test_advise_portfolio_triggers_sell_full_and_partial_rebalance_and_rotation():
    profiles = [
        # Held asset 1: Active SELL signal on champion -> should trigger SELL_FULL
        AssetOpportunityProfile("PETR4.SA", "Petrobras", "Ações Brasil", 40.0, "t1_open", "Compra", "sell_double_top_bos", "Topo Duplo", 75.0, 50.0, -8.0, 4, "SELL", "IDEAL", "Topo", 0.0, 40.0, 48.0),
        # Held asset 2: Excessive weight (> 25% + 5% = 30%) -> should trigger SELL_PARTIAL_REBALANCE
        AssetOpportunityProfile("VALE3.SA", "Vale", "Ações Brasil", 60.0, "t1_open", "Compra", "sell_t1_open", "Topo", 75.0, 50.0, -8.0, 4, "BUY", "EXTENDED", "Estendido", 4.0, 57.5, 70.0),
        # Held asset 3: Stagnant low-score holding -> candidate for ROTATE_OUT when cash is low
        AssetOpportunityProfile("ABEV3.SA", "Ambev", "Ações Brasil", 12.0, "t1_open", "Compra", "sell_t1_open", "Topo", 45.0, 8.0, -18.0, 2, "NEUTRAL", "LATE", "Atrasado", 9.0, 11.0, 35.0),
        # New top candidate in IDEAL timing with score 88.0 (>= 35.0 + 15)
        AssetOpportunityProfile("ITUB4.SA", "Itaú", "Ações Brasil", 35.0, "t1_retest", "Reteste", "sell_t1_open", "Topo", 85.0, 90.0, -5.0, 6, "BUY", "IDEAL", "Ideal", 0.5, 34.8, 88.0),
    ]

    # Case A: SELL_FULL + SELL_PARTIAL_REBALANCE
    # PETR4: 50 * 40 = 2000 (20%)
    # VALE3: 80 * 60 = 4800 (48% > 30% band)
    # Cash: 3200 -> Total Equity = 10000
    res_a = advise_portfolio_rebalance(
        available_cash=3200.0,
        holdings_input=[
            {"ticker": "PETR4.SA", "shares": 50.0, "average_buy_price": 36.0},
            {"ticker": "VALE3.SA", "shares": 80.0, "average_buy_price": 50.0},
        ],
        opportunity_profiles=profiles,
        max_weight_pct=25.0,
        rebalance_band_pct=5.0,
    )
    actions_a = {r.ticker: r.action_type for r in res_a["recommendations"]}
    assert actions_a["PETR4.SA"] == "SELL_FULL"
    assert actions_a["VALE3.SA"] == "SELL_PARTIAL_REBALANCE"

    # Case B: Tactical Rotation when cash is low and ABEV3 is stagnant (score 35 vs ITUB4 score 88)
    res_b = advise_portfolio_rebalance(
        available_cash=100.0,
        holdings_input=[
            {"ticker": "ABEV3.SA", "shares": 200.0, "average_buy_price": 12.0},
        ],
        opportunity_profiles=[profiles[2], profiles[3]],
        max_weight_pct=100.0,
        rebalance_band_pct=5.0,
        min_rotation_score_delta=15.0,
    )
    actions_b = {r.ticker: r.action_type for r in res_b["recommendations"]}
    assert actions_b.get("ABEV3.SA") == "ROTATE_OUT"
    assert actions_b.get("ITUB4.SA") == "ROTATE_IN"



def test_simulate_portfolio_multi_asset_zero_lookahead_and_cash_conservation():
    from src.evaluator.portfolio_simulator import simulate_portfolio_multi_asset

    s_a = _make_mock_series("PETR4.SA", n_bars=60, base_price=30.0)
    s_b = _make_mock_series("VALE3.SA", n_bars=60, base_price=50.0)
    s_c = _make_mock_series("ITUB4.SA", n_bars=60, base_price=25.0)

    sigs_a = [
        SignalRecord("prop", "t1_open", 4, 5, 30.0, 29.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 20, 21, 36.0, 36.5, direction="SELL"),
        SignalRecord("prop", "t1_open", 35, 36, 31.0, 30.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 50, 51, 38.0, 38.5, direction="SELL"),
    ]
    sigs_b = [
        SignalRecord("prop", "t1_open", 8, 9, 50.0, 49.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 28, 29, 58.0, 58.5, direction="SELL"),
    ]
    sigs_c = [
        SignalRecord("prop", "t1_open", 12, 13, 25.0, 24.5, direction="BUY"),
        SignalRecord("prop", "sell_t1_open", 42, 43, 29.0, 29.5, direction="SELL"),
    ]

    bundles_full = [
        {"ticker": "PETR4.SA", "asset_name": "Petrobras", "series": s_a, "signals": sigs_a},
        {"ticker": "VALE3.SA", "asset_name": "Vale", "series": s_b, "signals": sigs_b},
        {"ticker": "ITUB4.SA", "asset_name": "Itaú", "series": s_c, "signals": sigs_c},
    ]

    res_full = simulate_portfolio_multi_asset(
        asset_bundles=bundles_full,
        initial_capital=10000.0,
        max_weight_pct=35.0,
        rebalance_band_pct=5.0,
    )

    assert res_full.initial_capital == 10000.0
    assert res_full.final_equity > 10000.0
    assert res_full.total_events_count >= 4
    assert len(res_full.curve) == 60
    for ev in res_full.ledger_events:
        assert ev.cash_after >= 0.0
        assert ev.portfolio_equity_after > 0.0

    # Strict Zero Look-Ahead Bias Truncation Test at bar cutoff = 30
    cutoff = 30

    def _slice_series(s: OHLCVSeries, k: int) -> OHLCVSeries:
        return OHLCVSeries(
            ticker=s.ticker,
            interval=s.interval,
            timestamps=s.timestamps[:k],
            open=s.open[:k],
            high=s.high[:k],
            low=s.low[:k],
            close=s.close[:k],
            volume=s.volume[:k],
        )

    bundles_trunc = [
        {
            "ticker": "PETR4.SA",
            "asset_name": "Petrobras",
            "series": _slice_series(s_a, cutoff),
            "signals": [sig for sig in sigs_a if sig.execution_bar_index < cutoff],
        },
        {
            "ticker": "VALE3.SA",
            "asset_name": "Vale",
            "series": _slice_series(s_b, cutoff),
            "signals": [sig for sig in sigs_b if sig.execution_bar_index < cutoff],
        },
        {
            "ticker": "ITUB4.SA",
            "asset_name": "Itaú",
            "series": _slice_series(s_c, cutoff),
            "signals": [sig for sig in sigs_c if sig.execution_bar_index < cutoff],
        },
    ]

    res_trunc = simulate_portfolio_multi_asset(
        asset_bundles=bundles_trunc,
        initial_capital=10000.0,
        max_weight_pct=35.0,
        rebalance_band_pct=5.0,
    )

    # Every curve point up to cutoff must match bit-for-bit!
    for i in range(cutoff):
        assert res_trunc.curve[i].date == res_full.curve[i].date
        assert res_trunc.curve[i].portfolio_equity == res_full.curve[i].portfolio_equity
        assert res_trunc.curve[i].cash_balance == res_full.curve[i].cash_balance

    # Every ledger event up to cutoff date must match bit-for-bit!
    cutoff_date = res_trunc.curve[-1].date
    full_events_up_to_cutoff = [e for e in res_full.ledger_events if e.date <= cutoff_date]
    assert len(res_trunc.ledger_events) == len(full_events_up_to_cutoff)
    for e_tr, e_fl in zip(res_trunc.ledger_events, full_events_up_to_cutoff):
        assert e_tr.ticker == e_fl.ticker
        assert e_tr.event_type == e_fl.event_type
        assert e_tr.shares_delta == e_fl.shares_delta
        assert e_tr.execution_price == e_fl.execution_price
        assert e_tr.cash_after == e_fl.cash_after
