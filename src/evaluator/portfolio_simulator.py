"""
Multi-Asset Portfolio Manager, Rebalancing Advisor & Historical Simulator Engine.
Provides deterministic Potential Score (0-100) evaluation per asset based on
its historical Champion Strategy Pair, actionable Today's Rebalancing Plan,
and Zero Look-Ahead Bias bar-by-bar multi-asset portfolio simulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import math
import numpy as np
import pandas as pd

from ..strategies.base import OHLCVSeries, SignalRecord
from .accumulation_simulator import optimize_strategy_pairs
from .statistical_engine import evaluate_all_strategies
from .timing_classifier import classify_timing_status


def is_integer_lot_ticker(ticker: str) -> bool:
    """
    Returns True for Brazilian B3 equities and FIIs (.SA) or indices (^BVSP)
    where standard/fractional shares are whole integers (>= 1 share).
    Cryptocurrencies (-USD) and international assets support up to 4 decimals.
    """
    t = (ticker or "").strip().upper()
    return t.endswith(".SA") or t.startswith("^")


def round_shares_for_ticker(ticker: str, raw_shares: float, mode: str = "floor") -> float:
    """
    Rounds share count according to market convention:
    - .SA tickers: integer shares (floor for BUY so we never exceed cash; floor/round for partial sell).
    - Fractional tickers (-USD, US equities, etc.): 4 decimal places.
    """
    if raw_shares <= 0.0:
        return 0.0
    if is_integer_lot_ticker(ticker):
        if mode == "round":
            return float(max(0, int(round(raw_shares))))
        return float(max(0, int(math.floor(raw_shares + 1e-9))))
    factor = 10000.0
    if mode == "round":
        return round(raw_shares, 4)
    return math.floor(raw_shares * factor + 1e-9) / factor


@dataclass
class PortfolioHolding:
    ticker: str
    asset_name: str
    shares: float
    average_buy_price: float
    current_price: float
    market_value: float = 0.0
    invested_value: float = 0.0
    unrealized_pnl_value: float = 0.0
    unrealized_pnl_pct: float = 0.0
    current_weight_pct: float = 0.0
    entry_bar_index: int = 0

    def __post_init__(self):
        self.ticker = (self.ticker or "").strip().upper()
        self.shares = max(0.0, float(self.shares))
        self.average_buy_price = max(0.0, float(self.average_buy_price))
        self.current_price = max(0.0, float(self.current_price))
        self.entry_bar_index = max(0, int(self.entry_bar_index))
        self.recalculate(total_portfolio_equity=0.0)

    def recalculate(self, total_portfolio_equity: float = 0.0) -> None:
        self.market_value = round(self.shares * self.current_price, 2)
        self.invested_value = round(self.shares * self.average_buy_price, 2)
        self.unrealized_pnl_value = round(self.market_value - self.invested_value, 2)
        if self.average_buy_price > 0:
            self.unrealized_pnl_pct = round(((self.current_price / self.average_buy_price) - 1.0) * 100.0, 2)
        else:
            self.unrealized_pnl_pct = 0.0
        if total_portfolio_equity > 0:
            w = (self.market_value / total_portfolio_equity) * 100.0
            self.current_weight_pct = round(max(0.0, min(100.0, w)), 2)


@dataclass
class AssetOpportunityProfile:
    ticker: str
    asset_name: str
    category: str
    current_price: float
    champion_buy_id: str
    champion_buy_label: str
    champion_sell_id: str
    champion_sell_label: str
    win_rate_pct: float = 0.0
    historical_return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    closed_trades: int = 0
    active_direction: str = "NEUTRAL"
    timing_category: str = "LATE"
    timing_label: str = "Atrasado"
    distance_pct: float = 0.0
    recommended_price: float = 0.0
    potential_score: float = 0.0

    def __post_init__(self):
        self.ticker = (self.ticker or "").strip().upper()
        self.potential_score = round(max(0.0, min(100.0, float(self.potential_score))), 1)
        if self.active_direction not in ("BUY", "SELL", "NEUTRAL"):
            self.active_direction = "NEUTRAL"
        if self.timing_category not in ("IDEAL", "EXTENDED", "LATE"):
            self.timing_category = "LATE"


@dataclass
class PortfolioActionRecommendation:
    ticker: str
    asset_name: str
    action_type: str
    action_label: str
    reason_text: str
    strategy_sub_id: str
    strategy_label: str
    potential_score: float
    timing_category: str
    current_price: float
    reference_price: float
    current_shares: float = 0.0
    recommended_shares_delta: float = 0.0
    target_shares: float = 0.0
    order_value: float = 0.0
    current_weight_pct: float = 0.0
    target_weight_pct: float = 0.0


@dataclass
class PortfolioLedgerEvent:
    event_id: int
    date: str
    ticker: str
    asset_name: str
    event_type: str
    event_label: str
    strategy_sub_id: str
    strategy_label: str
    potential_score: float
    execution_price: float
    shares_delta: float
    trade_value: float
    realized_pnl_value: Optional[float] = None
    realized_pnl_pct: Optional[float] = None
    weight_before_pct: float = 0.0
    weight_after_pct: float = 0.0
    cash_after: float = 0.0
    portfolio_equity_after: float = 0.0


@dataclass
class PortfolioCurvePoint:
    date: str
    portfolio_equity: float
    cash_balance: float
    invested_equity: float
    benchmark_equity: float
    drawdown_pct: float


@dataclass
class PortfolioSimulationResult:
    initial_capital: float
    final_equity: float
    final_cash: float
    final_invested_value: float
    net_profit: float
    total_return_pct: float
    benchmark_return_pct: float
    alpha_vs_benchmark_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_events_count: int
    closed_exits_count: int
    winning_exits_count: int
    losing_exits_count: int
    rebalance_rotations_count: int
    current_holdings: List[PortfolioHolding] = field(default_factory=list)
    opportunity_profiles: List[AssetOpportunityProfile] = field(default_factory=list)
    ledger_events: List[PortfolioLedgerEvent] = field(default_factory=list)
    curve: List[PortfolioCurvePoint] = field(default_factory=list)


def calculate_potential_score(
    win_rate_pct: float,
    historical_return_pct: float,
    max_drawdown_pct: float,
    timing_category: str,
    active_direction: str = "BUY",
) -> float:
    """
    Computes deterministic Potential Score in [0.0, 100.0]:
    Score = clip(0.35 * S_win + 0.30 * S_ret + 0.15 * S_dd + 0.20 * S_timing, 0, 100)
    """
    s_win = min(100.0, max(0.0, float(win_rate_pct)))
    s_ret = min(100.0, max(0.0, (float(historical_return_pct) / 150.0) * 100.0))
    s_dd = min(100.0, max(0.0, 100.0 - abs(float(max_drawdown_pct)) * 2.0))

    if active_direction == "BUY":
        if timing_category == "IDEAL":
            s_timing = 100.0
        elif timing_category == "EXTENDED":
            s_timing = 55.0
        else:
            s_timing = 15.0
    else:
        s_timing = 15.0

    raw = 0.35 * s_win + 0.30 * s_ret + 0.15 * s_dd + 0.20 * s_timing
    return round(max(0.0, min(100.0, raw)), 1)


def compute_asset_opportunity_profile(
    ticker: str,
    series: OHLCVSeries,
    signals: List[SignalRecord],
    prop_state: Optional[Dict[str, Any]] = None,
    pending_signals: Optional[List[Dict[str, Any]]] = None,
    asset_name: str = "",
    category: str = "Destaques",
    strategy_labels_map: Optional[Dict[str, str]] = None,
) -> AssetOpportunityProfile:
    """
    Identifies the historical Champion Strategy Pair (Buy + Sell) for a given asset
    and computes its current Timing Status and Potential Score (0-100).
    """
    t_norm = (ticker or "").strip().upper()
    a_name = asset_name or t_norm
    labels_map = strategy_labels_map or {}
    prop_state = prop_state or {}
    pending_signals = pending_signals or []

    if series.length == 0:
        return AssetOpportunityProfile(
            ticker=t_norm,
            asset_name=a_name,
            category=category,
            current_price=0.0,
            champion_buy_id="t1_open",
            champion_buy_label=labels_map.get("t1_open", "t1_open"),
            champion_sell_id="sell_t1_open",
            champion_sell_label=labels_map.get("sell_t1_open", "sell_t1_open"),
        )

    current_price = float(series.close[-1])
    last_bar_idx = series.length - 1

    champion, _ = optimize_strategy_pairs(
        series=series,
        signals=signals,
        initial_capital=1000.0,
        min_trades=1,
        strategy_labels_map=labels_map,
        top_n=5,
        cycle_entry_mode="single_buy",
    )

    if champion is not None:
        champ_buy_id = champion.buy_sub_id
        champ_buy_label = champion.buy_label
        champ_sell_id = champion.sell_sub_id or "sell_t1_open"
        champ_sell_label = champion.sell_label or labels_map.get(champ_sell_id, champ_sell_id)
        win_rate_pct = float(champion.win_rate_pct)
        hist_ret_pct = float(champion.total_return_pct)
        max_dd_pct = float(champion.max_drawdown_pct)
        closed_trades = int(champion.closed_trades)
    else:
        # Fallback if no closed pairs exist yet
        champ_buy_id = "t1_open"
        champ_sell_id = "sell_t1_open"
        buy_sigs_all = [s for s in signals if s.direction == "BUY"]
        sell_sigs_all = [s for s in signals if s.direction == "SELL"]
        if buy_sigs_all:
            champ_buy_id = buy_sigs_all[-1].strategy_sub_id
        if sell_sigs_all:
            champ_sell_id = sell_sigs_all[-1].strategy_sub_id
        champ_buy_label = labels_map.get(champ_buy_id, champ_buy_id)
        champ_sell_label = labels_map.get(champ_sell_id, champ_sell_id)
        win_rate_pct = 50.0
        hist_ret_pct = 10.0
        max_dd_pct = -10.0
        closed_trades = 0

    # Determine current active signal & timing for this asset
    active_direction = "NEUTRAL"
    recommended_price = current_price
    is_awaiting_retest = False
    active_sub_id = champ_buy_id

    # 1. Check if Champion Sell Strategy (or any pending sell on last bar) triggered recently
    sell_sigs_champ = [s for s in signals if s.direction == "SELL" and s.strategy_sub_id == champ_sell_id]
    buy_sigs_champ = [s for s in signals if s.direction == "BUY" and s.strategy_sub_id == champ_buy_id]

    last_sell_bar = sell_sigs_champ[-1].execution_bar_index if sell_sigs_champ else -1
    last_buy_bar = buy_sigs_champ[-1].execution_bar_index if buy_sigs_champ else -1

    pending_sells = [p for p in pending_signals if p.get("direction") == "SELL"]
    pending_buys = [p for p in pending_signals if p.get("direction") == "BUY"]

    # Check if a sell signal is active right now (formed on last 2 bars and after last buy)
    if (last_sell_bar >= max(0, last_bar_idx - 2) and last_sell_bar >= last_buy_bar) or any(
        p.get("strategy_sub_id") == champ_sell_id for p in pending_sells
    ):
        active_direction = "SELL"
        active_sub_id = champ_sell_id
        if sell_sigs_champ and last_sell_bar >= max(0, last_bar_idx - 2):
            recommended_price = float(sell_sigs_champ[-1].execution_price)
        elif pending_sells:
            recommended_price = float(pending_sells[-1].get("reference_line_price") or current_price)
    else:
        # Check BUY opportunities (prioritizing champion buy, then active pending/retest buys, then latest buy)
        champ_pending_buy = next((p for p in pending_buys if p.get("strategy_sub_id") == champ_buy_id), None)
        champ_retest = prop_state.get(champ_buy_id) if isinstance(prop_state, dict) else None

        if champ_pending_buy is not None:
            active_direction = "BUY"
            recommended_price = float(champ_pending_buy.get("reference_line_price") or current_price)
        elif champ_retest and champ_retest.get("status") == "AGUARDANDO_RETESTE":
            active_direction = "BUY"
            recommended_price = float(champ_retest.get("active_line_price") or current_price)
            is_awaiting_retest = True
        elif buy_sigs_champ and (last_bar_idx - buy_sigs_champ[-1].execution_bar_index) <= 8 and last_buy_bar > last_sell_bar:
            active_direction = "BUY"
            recommended_price = float(buy_sigs_champ[-1].execution_price)
        elif pending_buys:
            active_direction = "BUY"
            p0 = pending_buys[0]
            active_sub_id = p0.get("strategy_sub_id", champ_buy_id)
            recommended_price = float(p0.get("reference_line_price") or current_price)
        elif buy_sigs_champ:
            active_direction = "BUY"
            recommended_price = float(buy_sigs_champ[-1].execution_price)
        else:
            all_buys = [s for s in signals if s.direction == "BUY"]
            if all_buys:
                active_direction = "BUY"
                recommended_price = float(all_buys[-1].execution_price)

    timing = classify_timing_status(
        current_price=current_price,
        recommended_price=recommended_price,
        strategy_sub_id=active_sub_id,
        strategy_label=labels_map.get(active_sub_id, active_sub_id),
        mean_forward_return=max(5.0, hist_ret_pct / max(1, closed_trades)),
        is_awaiting_retest=is_awaiting_retest,
        direction="SELL" if active_direction == "SELL" else "BUY",
    )

    score = calculate_potential_score(
        win_rate_pct=win_rate_pct,
        historical_return_pct=hist_ret_pct,
        max_drawdown_pct=max_dd_pct,
        timing_category=timing.status_category,
        active_direction=active_direction,
    )

    return AssetOpportunityProfile(
        ticker=t_norm,
        asset_name=a_name,
        category=category,
        current_price=round(current_price, 4),
        champion_buy_id=champ_buy_id,
        champion_buy_label=champ_buy_label,
        champion_sell_id=champ_sell_id,
        champion_sell_label=champ_sell_label,
        win_rate_pct=round(win_rate_pct, 1),
        historical_return_pct=round(hist_ret_pct, 1),
        max_drawdown_pct=round(max_dd_pct, 1),
        closed_trades=closed_trades,
        active_direction=active_direction,
        timing_category=timing.status_category,
        timing_label=timing.status_label,
        distance_pct=round(float(timing.distance_pct), 2),
        recommended_price=round(float(timing.recommended_price), 4),
        potential_score=score,
    )


def advise_portfolio_rebalance(*args, **kwargs) -> Dict[str, Any]:
    raise NotImplementedError


def simulate_portfolio_multi_asset(*args, **kwargs) -> PortfolioSimulationResult:
    raise NotImplementedError
