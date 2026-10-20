"""
Unit tests for Accumulation Simulator and Timing Status Classifier.
"""

import numpy as np
import pandas as pd
import pytest
from src.strategies.base import OHLCVSeries, SignalRecord
from src.evaluator import (
    simulate_accumulation,
    simulate_cycle_trade,
    optimize_strategy_pairs,
    classify_timing_status,
)


def make_test_series(closes: list) -> OHLCVSeries:
    n = len(closes)
    timestamps = pd.date_range("2024-01-01", periods=n, freq="D").to_numpy(dtype="datetime64[ns]")
    c_arr = np.array(closes, dtype=np.float64)
    return OHLCVSeries(
        ticker="SIM_TEST",
        interval="1d",
        timestamps=timestamps,
        open=c_arr.copy(),
        high=c_arr * 1.02,
        low=c_arr * 0.98,
        close=c_arr,
        volume=np.ones(n) * 1000,
    )


def test_simulate_accumulation_fixed_contributions():
    """
    Verifies fixed contribution simulation:
    - 2 buys of R$ 100 each
    - Buy 1 at bar 1, P_exec = 10.0 -> 10 shares
    - Buy 2 at bar 3, P_exec = 20.0 -> 5 shares
    - Total shares = 15
    - Total invested = 200.0
    - If Close[-1] = 25.0 -> Equity = 15 * 25 = 375.0, Profit = 175.0, Return = +87.5%
    - Average price = 200 / 15 = 13.33
    """
    series = make_test_series([10.0, 10.0, 15.0, 20.0, 25.0])
    signals = [
        SignalRecord("prop_reversal", "t1_open", 0, 1, 10.0, None, {}),
        SignalRecord("prop_reversal", "t1_open", 2, 3, 20.0, None, {}),
    ]

    res = simulate_accumulation(series, signals, contribution_amount=100.0)
    assert "t1_open" in res
    sim = res["t1_open"]

    assert sim.num_contributions == 2
    assert sim.total_invested == 200.0
    assert sim.total_shares == pytest.approx(15.0)
    assert sim.current_equity == pytest.approx(375.0)
    assert sim.net_profit == pytest.approx(175.0)
    assert sim.return_on_capital_pct == pytest.approx(87.5)
    assert sim.average_buy_price == pytest.approx(13.33, abs=0.01)
    assert len(sim.timeline_equity) == 5
    assert sim.timeline_invested[-1] == 200.0


def test_simulate_accumulation_date_range_filter():
    """
    Ensures start_date and end_date correctly filter out signals outside the window.
    """
    series = make_test_series([10.0, 10.0, 15.0, 20.0, 25.0])
    # timestamps are 2024-01-01, 2024-01-02, 2024-01-03, 2024-01-04, 2024-01-05
    signals = [
        SignalRecord("dca_dynamic", "dca_dynamic", 0, 1, 10.0, None, {}),  # 2024-01-02
        SignalRecord("dca_dynamic", "dca_dynamic", 2, 3, 20.0, None, {}),  # 2024-01-04
    ]

    # Filter to only include 2024-01-03 onwards
    res = simulate_accumulation(
        series,
        signals,
        contribution_amount=100.0,
        start_date="2024-01-03",
    )
    sim = res["dca_dynamic"]
    assert sim.num_contributions == 1
    assert sim.total_invested == 100.0
    assert sim.total_shares == pytest.approx(5.0)


def test_timing_status_classifier_bands():
    """
    Verifies the 3 timing status categories:
    - Current <= +1.5%: IDEAL
    - +1.5% < Current <= +4.0%: EXTENDED
    - Current > +4.0%: LATE
    - Retest waiting: IDEAL
    """
    # 1. Recommended = 100.0, Current = 101.0 (+1.0%) -> IDEAL
    st1 = classify_timing_status(current_price=101.0, recommended_price=100.0, strategy_sub_id="t1_open")
    assert st1.status_category == "IDEAL"
    assert "ZONA IDEAL" in st1.status_label

    # 2. Recommended = 100.0, Current = 103.0 (+3.0%) -> EXTENDED
    st2 = classify_timing_status(current_price=103.0, recommended_price=100.0, strategy_sub_id="t1_open")
    assert st2.status_category == "EXTENDED"
    assert "ESTENDIDO" in st2.status_label

    # 3. Recommended = 100.0, Current = 105.0 (+5.0%) -> LATE
    st3 = classify_timing_status(current_price=105.0, recommended_price=100.0, strategy_sub_id="t1_open")
    assert st3.status_category == "LATE"
    assert "ATRASADO" in st3.status_label

    # 4. Recommended = 100.0, Current = 103.0 (+3.0%), but mean_forward_return is 6.0% (3.0% is 50% > 30% threshold) -> LATE
    st4 = classify_timing_status(
        current_price=103.0,
        recommended_price=100.0,
        strategy_sub_id="t1_open",
        mean_forward_return=6.0,
    )
    assert st4.status_category == "LATE"

    # 5. Awaiting retest touch flag -> always IDEAL
    st5 = classify_timing_status(
        current_price=103.0,
        recommended_price=100.0,
        strategy_sub_id="t1_retest",
        is_awaiting_retest=True,
    )
    assert st5.status_category == "IDEAL"


def test_simulate_cycle_trade_buy_sell_pairing():
    """
    Verifies that a BUY signal triggers entry and subsequent SELL signal triggers exit.
    - Buy at bar 1, p_exec = 10.0 with capital = 1000.0 -> 100 shares.
    - Sell at bar 3, p_exec = 12.0 -> Exit cash = 100 * 12 = 1200.0 (+20%).
    - Capital carries forward.
    - Buy at bar 4, p_exec = 12.0 -> 100 shares.
    - Sell at bar 5, p_exec = 15.0 -> Exit cash = 100 * 15 = 1500.0 (+25%).
    - Final capital = 1500.0 (+50% total return), 2 closed trades, 100% win rate.
    """
    series = make_test_series([10.0, 10.0, 11.0, 12.0, 12.0, 15.0])
    signals = [
        SignalRecord("prop_reversal", "t1_open", 0, 1, 10.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t1_open", 2, 3, 12.0, None, "SELL"),
        SignalRecord("prop_reversal", "t1_open", 3, 4, 12.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t1_open", 4, 5, 15.0, None, "SELL"),
    ]

    res = simulate_cycle_trade(series, signals, initial_capital=1000.0)

    assert res.total_trades_count == 2
    assert res.closed_trades_count == 2
    assert res.winning_trades_count == 2
    assert res.losing_trades_count == 0
    assert res.win_rate_pct == 100.0
    assert res.final_equity == pytest.approx(1500.0)
    assert res.return_on_capital_pct == pytest.approx(50.0)
    assert res.net_profit == pytest.approx(500.0)
    assert len(res.trades) == 2
    assert res.trades[0].status == "FECHADO"
    assert res.trades[0].return_pct == pytest.approx(20.0)
    assert res.trades[1].status == "FECHADO"
    assert res.trades[1].return_pct == pytest.approx(25.0)


def test_simulate_cycle_trade_unclosed_position():
    """
    Verifies that if a BUY is opened and no SELL occurs before the end of the series,
    the position is marked as 'ABERTO' with unrealized return evaluated at Close[-1].
    - Buy at bar 1, p_exec = 10.0 with capital = 1000.0 -> 100 shares.
    - Series ends at bar 2 with Close = 11.0.
    - Mark-to-market equity = 1100.0 (+10.0%).
    """
    series = make_test_series([10.0, 10.0, 11.0])
    signals = [
        SignalRecord("prop_reversal", "t1_open", 0, 1, 10.0, None, "BUY"),
    ]

    res = simulate_cycle_trade(series, signals, initial_capital=1000.0)

    assert res.total_trades_count == 1
    assert res.closed_trades_count == 0
    assert res.final_equity == pytest.approx(1100.0)
    assert res.net_profit == pytest.approx(100.0)
    assert res.return_on_capital_pct == pytest.approx(10.0)
    assert len(res.trades) == 1
    assert res.trades[0].status == "ABERTO"
    assert res.trades[0].return_pct == pytest.approx(10.0)


def test_optimize_strategy_pairs_finds_champion():
    """
    Verifies that optimize_strategy_pairs tests multiple combinations of Buy and Sell
    strategies and correctly identifies the champion pair with highest total return.
    - Pair A: (t1_open -> sell_t1_open): buy at 10, sell at 12 (+20%), buy at 12, sell at 15 (+25%) -> +50%
    - Pair B: (t2_open -> sell_t2_open): buy at 10, sell at 11 (+10%), buy at 12, sell at 13 (+8.33%) -> +19.16%
    - Champion must be Pair A (t1_open -> sell_t1_open).
    """
    series = make_test_series([10.0, 10.0, 11.0, 12.0, 12.0, 15.0])
    signals = [
        # Pair A signals
        SignalRecord("prop_reversal", "t1_open", 0, 1, 10.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t1_open", 2, 3, 12.0, None, "SELL"),
        SignalRecord("prop_reversal", "t1_open", 3, 4, 12.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t1_open", 4, 5, 15.0, None, "SELL"),
        # Pair B signals
        SignalRecord("prop_reversal", "t2_open", 0, 1, 10.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t2_open", 1, 2, 11.0, None, "SELL"),
        SignalRecord("prop_reversal", "t2_open", 3, 4, 12.0, None, "BUY"),
        SignalRecord("prop_reversal", "sell_t2_open", 4, 5, 13.0, None, "SELL"),
    ]

    champ, top_list = optimize_strategy_pairs(series, signals, initial_capital=1000.0, min_trades=2)

    assert champ is not None
    assert champ.buy_sub_id == "t1_open"
    assert champ.sell_sub_id == "sell_t1_open"
    assert champ.rank == 1
    assert champ.total_return_pct == pytest.approx(50.0)
    assert champ.closed_trades == 2
    assert len(top_list) >= 2
