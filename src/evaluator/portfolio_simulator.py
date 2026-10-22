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


def advise_portfolio_rebalance(
    available_cash: float,
    holdings_input: List[Dict[str, Any]],
    opportunity_profiles: List[AssetOpportunityProfile],
    max_weight_pct: float = 25.0,
    rebalance_band_pct: float = 5.0,
    min_rotation_score_delta: float = 15.0,
) -> Dict[str, Any]:
    """
    Evaluates the user's current portfolio (available_cash + holdings) against the
    analyzed universe opportunity profiles and generates an actionable Today's Action Plan:
    - SELL_FULL: 100% exit when a holding triggers its champion SELL (top) signal.
    - SELL_PARTIAL_REBALANCE: partial trim when a holding's weight > max_weight_pct + rebalance_band_pct.
    - ROTATE_OUT / ROTATE_IN: tactical rotation when cash is constrained and an IDEAL buy candidate
      outscores a stagnant holding by >= min_rotation_score_delta.
    - BUY: score-weighted allocation of available cash into top BUY candidates, capped at max_weight_pct.
    - HOLD: healthy holdings maintained in portfolio.
    """
    cash = max(0.0, float(available_cash))
    max_w = max(5.0, min(100.0, float(max_weight_pct)))
    band_w = max(1.0, min(50.0, float(rebalance_band_pct)))
    rot_delta = max(5.0, float(min_rotation_score_delta))

    profiles_by_ticker: Dict[str, AssetOpportunityProfile] = {
        p.ticker.upper(): p for p in opportunity_profiles if p.current_price > 0
    }

    # 1. Consolidate and evaluate current holdings
    holdings_evaluated: List[PortfolioHolding] = []
    for h_raw in (holdings_input or []):
        t_code = str(h_raw.get("ticker", "")).strip().upper()
        sh = float(h_raw.get("shares", 0.0) or 0.0)
        avg_p = float(h_raw.get("average_buy_price", 0.0) or 0.0)
        if not t_code or sh <= 0.0:
            continue
        prof = profiles_by_ticker.get(t_code)
        cur_p = prof.current_price if prof and prof.current_price > 0 else avg_p
        a_name = prof.asset_name if prof else t_code
        if avg_p <= 0.0:
            avg_p = cur_p
        holdings_evaluated.append(
            PortfolioHolding(
                ticker=t_code,
                asset_name=a_name,
                shares=sh,
                average_buy_price=avg_p,
                current_price=cur_p,
            )
        )

    current_holdings_value = sum(h.shares * h.current_price for h in holdings_evaluated)
    total_equity = round(cash + current_holdings_value, 2)

    for h in holdings_evaluated:
        h.recalculate(total_portfolio_equity=total_equity)

    if total_equity <= 0.0:
        return {
            "current_cash": round(cash, 2),
            "current_holdings_value": 0.0,
            "total_portfolio_equity": 0.0,
            "projected_cash_after": round(cash, 2),
            "projected_invested_after": 0.0,
            "max_weight_pct": max_w,
            "holdings_evaluated": [],
            "recommendations": [],
            "opportunity_ranking": sorted(
                opportunity_profiles,
                key=lambda x: (-x.potential_score, -x.win_rate_pct, x.ticker),
            ),
        }

    recommendations: List[PortfolioActionRecommendation] = []
    projected_cash = cash
    projected_shares_map: Dict[str, float] = {h.ticker: h.shares for h in holdings_evaluated}
    handled_holdings: set = set()

    # 2. Rule 1 (SELL_FULL) & Rule 2 (SELL_PARTIAL_REBALANCE) on existing holdings
    for h in holdings_evaluated:
        prof = profiles_by_ticker.get(h.ticker)
        c_price = h.current_price
        if prof and prof.active_direction == "SELL":
            # Rule 1: Full exit on Champion Sell (Top) signal
            proceeds = round(h.shares * c_price, 2)
            projected_cash += proceeds
            projected_shares_map[h.ticker] = 0.0
            handled_holdings.add(h.ticker)
            recommendations.append(
                PortfolioActionRecommendation(
                    ticker=h.ticker,
                    asset_name=h.asset_name,
                    action_type="SELL_FULL",
                    action_label="VENDER TOTAL",
                    reason_text=f"Sinal de Venda (Topo) confirmado pela estratégia campeã ({prof.champion_sell_label}). Realizar 100% da posição.",
                    strategy_sub_id=prof.champion_sell_id,
                    strategy_label=prof.champion_sell_label,
                    potential_score=prof.potential_score,
                    timing_category=prof.timing_category,
                    current_price=round(c_price, 2),
                    reference_price=round(prof.recommended_price or c_price, 2),
                    current_shares=round(h.shares, 4),
                    recommended_shares_delta=round(-h.shares, 4),
                    target_shares=0.0,
                    order_value=proceeds,
                    current_weight_pct=h.current_weight_pct,
                    target_weight_pct=0.0,
                )
            )
        elif h.current_weight_pct > (max_w + band_w):
            # Rule 2: Partial rebalance trim back to max_weight_pct
            target_val = (max_w / 100.0) * total_equity
            excess_val = max(0.0, h.market_value - target_val)
            raw_trim_shares = excess_val / c_price if c_price > 0 else 0.0
            trim_shares = min(h.shares, round_shares_for_ticker(h.ticker, raw_trim_shares, mode="round"))
            if trim_shares > 0:
                proceeds = round(trim_shares * c_price, 2)
                rem_shares = max(0.0, h.shares - trim_shares)
                new_weight = ((rem_shares * c_price) / total_equity) * 100.0
                projected_cash += proceeds
                projected_shares_map[h.ticker] = rem_shares
                handled_holdings.add(h.ticker)
                s_id = prof.champion_sell_id if prof else "sell_rebal_rv_rf"
                s_lbl = prof.champion_sell_label if prof else "Rebalanceamento de Banda"
                p_score = prof.potential_score if prof else 50.0
                t_cat = prof.timing_category if prof else "EXTENDED"
                recommendations.append(
                    PortfolioActionRecommendation(
                        ticker=h.ticker,
                        asset_name=h.asset_name,
                        action_type="SELL_PARTIAL_REBALANCE",
                        action_label="VENDER PARCIAL / REBALANCEAR",
                        reason_text=f"Peso atual ({h.current_weight_pct:.1f}%) ultrapassou o teto de {max_w:.0f}% + banda ({band_w:.0f}%). Reduzir ao teto.",
                        strategy_sub_id=s_id,
                        strategy_label=s_lbl,
                        potential_score=p_score,
                        timing_category=t_cat,
                        current_price=round(c_price, 2),
                        reference_price=round(c_price, 2),
                        current_shares=round(h.shares, 4),
                        recommended_shares_delta=round(-trim_shares, 4),
                        target_shares=round(rem_shares, 4),
                        order_value=proceeds,
                        current_weight_pct=h.current_weight_pct,
                        target_weight_pct=round(new_weight, 2),
                    )
                )

    # 3. Rule 3: Tactical Opportunity-Cost Rotation (when cash is low and an IDEAL top candidate exists)
    unhandled_holdings = [h for h in holdings_evaluated if h.ticker not in handled_holdings and projected_shares_map.get(h.ticker, 0.0) > 0]
    ideal_buy_candidates = [
        p for p in opportunity_profiles
        if p.active_direction == "BUY"
        and p.timing_category == "IDEAL"
        and p.current_price > 0
        and projected_shares_map.get(p.ticker, 0.0) == 0.0
    ]
    ideal_buy_candidates.sort(key=lambda x: (-x.potential_score, -x.win_rate_pct, x.ticker))

    rotated_in_tickers: set = set()
    if projected_cash < (0.10 * total_equity) and unhandled_holdings and ideal_buy_candidates:
        # Find weakest stagnant holding (lowest potential score and unrealized_pnl_pct <= 5.0%)
        stagnant_candidates = []
        for h in unhandled_holdings:
            h_prof = profiles_by_ticker.get(h.ticker)
            h_score = h_prof.potential_score if h_prof else 40.0
            if h.unrealized_pnl_pct <= 5.0:
                stagnant_candidates.append((h_score, h, h_prof))
        stagnant_candidates.sort(key=lambda x: x[0])

        if stagnant_candidates:
            weak_score, weak_h, weak_prof = stagnant_candidates[0]
            best_cand = ideal_buy_candidates[0]
            score_diff = best_cand.potential_score - weak_score
            if score_diff >= rot_delta:
                # Execute ROTATE_OUT on weak_h
                proceeds = round(weak_h.shares * weak_h.current_price, 2)
                projected_cash += proceeds
                projected_shares_map[weak_h.ticker] = 0.0
                handled_holdings.add(weak_h.ticker)
                recommendations.append(
                    PortfolioActionRecommendation(
                        ticker=weak_h.ticker,
                        asset_name=weak_h.asset_name,
                        action_type="ROTATE_OUT",
                        action_label="ROTACIONAR (SAÍDA)",
                        reason_text=f"Posição estagnada (Score {weak_score:.1f}) substituída por {best_cand.ticker} em Timing IDEAL (Score {best_cand.potential_score:.1f}, +{score_diff:.1f} pts).",
                        strategy_sub_id=weak_prof.champion_sell_id if weak_prof else "sell_rebal_relative_strength",
                        strategy_label=weak_prof.champion_sell_label if weak_prof else "Rotação por Força Relativa",
                        potential_score=weak_score,
                        timing_category=weak_prof.timing_category if weak_prof else "LATE",
                        current_price=round(weak_h.current_price, 2),
                        reference_price=round(weak_h.current_price, 2),
                        current_shares=round(weak_h.shares, 4),
                        recommended_shares_delta=round(-weak_h.shares, 4),
                        target_shares=0.0,
                        order_value=proceeds,
                        current_weight_pct=weak_h.current_weight_pct,
                        target_weight_pct=0.0,
                    )
                )

                # Execute paired ROTATE_IN on best_cand capped at max_w
                max_cap_val = (max_w / 100.0) * total_equity
                alloc_val = min(projected_cash, proceeds, max_cap_val)
                buy_sh = round_shares_for_ticker(best_cand.ticker, alloc_val / best_cand.current_price, mode="floor")
                if buy_sh > 0:
                    cost = round(buy_sh * best_cand.current_price, 2)
                    projected_cash = max(0.0, projected_cash - cost)
                    projected_shares_map[best_cand.ticker] = buy_sh
                    rotated_in_tickers.add(best_cand.ticker)
                    new_w = (cost / total_equity) * 100.0
                    recommendations.append(
                        PortfolioActionRecommendation(
                            ticker=best_cand.ticker,
                            asset_name=best_cand.asset_name,
                            action_type="ROTATE_IN",
                            action_label="ROTACIONAR (ENTRADA)",
                            reason_text=f"Alocação tática via rotação de {weak_h.ticker}: sinal de compra em Timing IDEAL ({best_cand.champion_buy_label}, Score {best_cand.potential_score:.1f}).",
                            strategy_sub_id=best_cand.champion_buy_id,
                            strategy_label=best_cand.champion_buy_label,
                            potential_score=best_cand.potential_score,
                            timing_category=best_cand.timing_category,
                            current_price=round(best_cand.current_price, 2),
                            reference_price=round(best_cand.recommended_price or best_cand.current_price, 2),
                            current_shares=0.0,
                            recommended_shares_delta=round(buy_sh, 4),
                            target_shares=round(buy_sh, 4),
                            order_value=cost,
                            current_weight_pct=0.0,
                            target_weight_pct=round(new_w, 2),
                        )
                    )

    # 4. Score-Weighted BUY Allocation for Available Cash
    max_cap_per_asset = (max_w / 100.0) * total_equity
    eligible_buys: List[AssetOpportunityProfile] = []
    for p in opportunity_profiles:
        if p.ticker in rotated_in_tickers or p.ticker in handled_holdings:
            continue
        if p.current_price <= 0:
            continue
        cur_sh = projected_shares_map.get(p.ticker, 0.0)
        cur_val = cur_sh * p.current_price
        if (max_cap_per_asset - cur_val) < min(10.0, p.current_price):
            continue
        if p.active_direction == "BUY" and p.timing_category in ("IDEAL", "EXTENDED"):
            eligible_buys.append(p)

    # If no active IDEAL/EXTENDED BUY signals exist, fallback to top-scoring BUY profiles with score >= 50
    if not eligible_buys:
        for p in opportunity_profiles:
            if p.ticker in rotated_in_tickers or p.ticker in handled_holdings or p.current_price <= 0:
                continue
            cur_sh = projected_shares_map.get(p.ticker, 0.0)
            cur_val = cur_sh * p.current_price
            if (max_cap_per_asset - cur_val) >= min(10.0, p.current_price) and p.potential_score >= 45.0 and p.active_direction != "SELL":
                eligible_buys.append(p)

    eligible_buys.sort(
        key=lambda x: (
            1 if x.timing_category == "IDEAL" else (0 if x.timing_category == "EXTENDED" else -1),
            x.potential_score,
            x.win_rate_pct,
        ),
        reverse=True,
    )

    max_slots = max(1, int(math.ceil(100.0 / max_w)) + 1)
    selected_buys = eligible_buys[:max_slots]

    if projected_cash > 1.0 and selected_buys:
        total_score_sum = sum(max(1.0, p.potential_score) for p in selected_buys)
        cash_pool_for_sizing = projected_cash

        for p in selected_buys:
            if projected_cash <= 1.0:
                break
            cur_sh = projected_shares_map.get(p.ticker, 0.0)
            cur_val = cur_sh * p.current_price
            cur_w = (cur_val / total_equity) * 100.0
            room_val = max(0.0, max_cap_per_asset - cur_val)
            if room_val <= 0.0:
                continue

            score_weight = max(1.0, p.potential_score) / total_score_sum if total_score_sum > 0 else (1.0 / len(selected_buys))
            # Allow score-weighted share of cash pool or up to room_val so top candidates reach healthy allocation up to cap
            desired_val = max(cash_pool_for_sizing * score_weight, min(room_val, cash_pool_for_sizing / max(1, len(selected_buys))))
            alloc_val = min(projected_cash, room_val, desired_val)

            buy_sh = round_shares_for_ticker(p.ticker, alloc_val / p.current_price, mode="floor")
            if buy_sh <= 0.0 and projected_cash >= p.current_price and room_val >= p.current_price:
                # If integer rounding floored to 0 but 1 share fits within cap & cash
                if is_integer_lot_ticker(p.ticker):
                    buy_sh = 1.0

            if buy_sh > 0.0:
                cost = round(buy_sh * p.current_price, 2)
                if cost <= projected_cash + 1e-6 and (cur_val + cost) <= max_cap_per_asset + 1e-2:
                    projected_cash = max(0.0, round(projected_cash - cost, 2))
                    new_sh = cur_sh + buy_sh
                    projected_shares_map[p.ticker] = new_sh
                    handled_holdings.add(p.ticker)
                    new_w = ((new_sh * p.current_price) / total_equity) * 100.0
                    action_verb = "Reforçar posição" if cur_sh > 0 else "Nova compra recomendada"
                    recommendations.append(
                        PortfolioActionRecommendation(
                            ticker=p.ticker,
                            asset_name=p.asset_name,
                            action_type="BUY",
                            action_label="COMPRAR",
                            reason_text=f"{action_verb}: estratégia campeã ({p.champion_buy_label}) com Win Rate de {p.win_rate_pct:.1f}%, Timing {p.timing_category} e Score {p.potential_score:.1f}/100.",
                            strategy_sub_id=p.champion_buy_id,
                            strategy_label=p.champion_buy_label,
                            potential_score=p.potential_score,
                            timing_category=p.timing_category,
                            current_price=round(p.current_price, 2),
                            reference_price=round(p.recommended_price or p.current_price, 2),
                            current_shares=round(cur_sh, 4),
                            recommended_shares_delta=round(buy_sh, 4),
                            target_shares=round(new_sh, 4),
                            order_value=cost,
                            current_weight_pct=round(cur_w, 2),
                            target_weight_pct=round(new_w, 2),
                        )
                    )

    # 5. Any remaining existing holdings that were not modified receive HOLD ("MANTER")
    for h in holdings_evaluated:
        if h.ticker not in handled_holdings and projected_shares_map.get(h.ticker, 0.0) > 0:
            prof = profiles_by_ticker.get(h.ticker)
            recommendations.append(
                PortfolioActionRecommendation(
                    ticker=h.ticker,
                    asset_name=h.asset_name,
                    action_type="HOLD",
                    action_label="MANTER",
                    reason_text=f"Posição saudável dentro do limite de risco ({h.current_weight_pct:.1f}% <= {max_w:.0f}%) e sem gatilho de venda no topo.",
                    strategy_sub_id=prof.champion_buy_id if prof else "t1_open",
                    strategy_label=prof.champion_buy_label if prof else "Manutenção de Ciclo",
                    potential_score=prof.potential_score if prof else 60.0,
                    timing_category=prof.timing_category if prof else "EXTENDED",
                    current_price=round(h.current_price, 2),
                    reference_price=round(prof.recommended_price if prof else h.current_price, 2),
                    current_shares=round(h.shares, 4),
                    recommended_shares_delta=0.0,
                    target_shares=round(h.shares, 4),
                    order_value=0.0,
                    current_weight_pct=h.current_weight_pct,
                    target_weight_pct=h.current_weight_pct,
                )
            )

    order_priority = {
        "SELL_FULL": 1,
        "SELL_PARTIAL_REBALANCE": 2,
        "ROTATE_OUT": 3,
        "ROTATE_IN": 4,
        "BUY": 5,
        "HOLD": 6,
    }
    recommendations.sort(key=lambda r: (order_priority.get(r.action_type, 9), -r.potential_score, r.ticker))

    projected_invested = round(total_equity - projected_cash, 2)
    ranked_profiles = sorted(
        opportunity_profiles,
        key=lambda x: (-x.potential_score, -x.win_rate_pct, x.ticker),
    )

    return {
        "current_cash": round(cash, 2),
        "current_holdings_value": round(current_holdings_value, 2),
        "total_portfolio_equity": round(total_equity, 2),
        "projected_cash_after": round(projected_cash, 2),
        "projected_invested_after": max(0.0, projected_invested),
        "max_weight_pct": max_w,
        "holdings_evaluated": holdings_evaluated,
        "recommendations": recommendations,
        "opportunity_ranking": ranked_profiles,
    }


def _compute_causal_score_at_bar(
    signals: List[SignalRecord],
    up_to_bar: int,
    strategy_sub_id: str,
) -> float:
    """
    Computes a strictly causal Potential Score (0-100) for an asset/strategy at `up_to_bar`,
    using ONLY signals with `execution_bar_index <= up_to_bar`.
    Guarantees 100% Zero Look-Ahead Bias under series truncation tests.
    """
    past_sigs = [s for s in signals if 0 <= s.execution_bar_index <= up_to_bar]
    if not past_sigs:
        return 68.0

    buys = [s for s in past_sigs if s.direction == "BUY" and (strategy_sub_id in ("ALL", s.strategy_sub_id))]
    if not buys:
        buys = [s for s in past_sigs if s.direction == "BUY"]
    sells = [s for s in past_sigs if s.direction == "SELL"]

    merged = sorted(buys + sells, key=lambda x: (x.execution_bar_index, 0 if x.direction == "BUY" else 1))
    in_pos = False
    entry_p = 0.0
    entry_bar = -1
    closed = 0
    wins = 0
    cum_ret = 0.0
    worst_loss = 0.0

    for s in merged:
        p = float(s.execution_price)
        if p <= 0:
            continue
        if not in_pos and s.direction == "BUY":
            in_pos = True
            entry_p = p
            entry_bar = s.execution_bar_index
        elif in_pos and s.direction == "SELL" and s.execution_bar_index > entry_bar:
            ret_pct = ((p - entry_p) / entry_p) * 100.0
            closed += 1
            if ret_pct > 0:
                wins += 1
            else:
                worst_loss = min(worst_loss, ret_pct)
            cum_ret += ret_pct
            in_pos = False

    if closed == 0:
        # Prior score for confirmed bottom signal with no prior closed cycles yet
        return 72.0

    win_rate = (wins / closed) * 100.0
    return calculate_potential_score(
        win_rate_pct=win_rate,
        historical_return_pct=max(0.0, cum_ret),
        max_drawdown_pct=worst_loss,
        timing_category="IDEAL",
        active_direction="BUY",
    )


def simulate_portfolio_multi_asset(
    asset_bundles: List[Dict[str, Any]],
    initial_capital: float = 10000.0,
    max_weight_pct: float = 25.0,
    rebalance_band_pct: float = 5.0,
    min_rotation_score_delta: float = 15.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy_labels_map: Optional[Dict[str, str]] = None,
) -> PortfolioSimulationResult:
    """
    Executes a strictly causal (Zero Look-Ahead Bias) bar-by-bar multi-asset portfolio simulation:
    - Unifies timestamps across all assets in `asset_bundles`.
    - Applies 4-step bar precedence:
      1. SELL_FULL on confirmed SELL signals for held assets.
      2. SELL_PARTIAL_REBALANCE when a held asset's weight exceeds max_weight_pct + rebalance_band_pct.
      3. ROTATE_OUT / ROTATE_IN when cash < 10% of equity and an IDEAL BUY signal at bar t
         outscores a stagnant holding (held >= 3 bars, unrealized_pnl_pct <= 3.0%) by >= min_rotation_score_delta.
      4. Score-weighted BUY allocation of available cash into confirmed BUY signals at bar t, capped at max_weight_pct.
    - Computes Equal-Weight Buy & Hold basket benchmark and institutional KPIs.
    """
    init_cap = max(100.0, float(initial_capital))
    max_w = max(5.0, min(100.0, float(max_weight_pct)))
    band_w = max(1.0, min(50.0, float(rebalance_band_pct)))
    rot_delta = max(5.0, float(min_rotation_score_delta))
    labels_map = strategy_labels_map or {}

    valid_bundles = [
        b for b in (asset_bundles or [])
        if b and b.get("series") is not None and b["series"].length > 0
    ]

    if not valid_bundles:
        return PortfolioSimulationResult(
            initial_capital=round(init_cap, 2),
            final_equity=round(init_cap, 2),
            final_cash=round(init_cap, 2),
            final_invested_value=0.0,
            net_profit=0.0,
            total_return_pct=0.0,
            benchmark_return_pct=0.0,
            alpha_vs_benchmark_pct=0.0,
            max_drawdown_pct=0.0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            total_events_count=0,
            closed_exits_count=0,
            winning_exits_count=0,
            losing_exits_count=0,
            rebalance_rotations_count=0,
        )

    # 1. Build unified chronological date/timestamp index across all assets
    all_ts_list = []
    asset_data_map: Dict[str, Dict[str, Any]] = {}

    start_dt = pd.to_datetime(start_date) if start_date else None
    end_dt = pd.to_datetime(end_date) if end_date else None

    for b in valid_bundles:
        series: OHLCVSeries = b["series"]
        t_code = str(b.get("ticker") or series.ticker).strip().upper()
        a_name = str(b.get("asset_name") or t_code)
        sigs: List[SignalRecord] = b.get("signals") or []
        prof: Optional[AssetOpportunityProfile] = b.get("profile")

        ts_pd = pd.to_datetime(series.timestamps)
        mask = np.ones(series.length, dtype=bool)
        if start_dt is not None:
            mask &= (ts_pd >= start_dt)
        if end_dt is not None:
            mask &= (ts_pd <= end_dt)

        valid_idx = np.flatnonzero(mask)
        if len(valid_idx) == 0:
            continue

        norm_dates = [pd.to_datetime(series.timestamps[idx]).strftime("%Y-%m-%d %H:%M") if series.interval in ("5m", "15m", "30m", "60m", "1h", "2h", "4h", "12h") else pd.to_datetime(series.timestamps[idx]).strftime("%Y-%m-%d") for idx in valid_idx]
        date_to_orig_bar = {d_str: int(orig_i) for d_str, orig_i in zip(norm_dates, valid_idx)}
        all_ts_list.extend(norm_dates)

        sigs_by_bar: Dict[int, List[SignalRecord]] = {}
        for s in sigs:
            if 0 <= s.execution_bar_index < series.length and mask[s.execution_bar_index]:
                sigs_by_bar.setdefault(int(s.execution_bar_index), []).append(s)

        asset_data_map[t_code] = {
            "ticker": t_code,
            "asset_name": a_name,
            "series": series,
            "signals": sigs,
            "signals_by_bar": sigs_by_bar,
            "date_to_bar": date_to_orig_bar,
            "first_close": float(series.close[valid_idx[0]]),
            "last_known_close": float(series.close[valid_idx[0]]),
            "last_known_bar": int(valid_idx[0]),
            "profile": prof,
        }

    master_dates = sorted(set(all_ts_list))
    if not master_dates or not asset_data_map:
        return PortfolioSimulationResult(
            initial_capital=round(init_cap, 2),
            final_equity=round(init_cap, 2),
            final_cash=round(init_cap, 2),
            final_invested_value=0.0,
            net_profit=0.0,
            total_return_pct=0.0,
            benchmark_return_pct=0.0,
            alpha_vs_benchmark_pct=0.0,
            max_drawdown_pct=0.0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            total_events_count=0,
            closed_exits_count=0,
            winning_exits_count=0,
            losing_exits_count=0,
            rebalance_rotations_count=0,
        )

    # 2. Equal-Weight Buy & Hold Benchmark initialization at t=0
    n_bench = len(asset_data_map)
    bench_alloc_per_asset = init_cap / n_bench
    bench_shares: Dict[str, float] = {}
    for t_code, info in asset_data_map.items():
        p0 = info["first_close"]
        bench_shares[t_code] = (bench_alloc_per_asset / p0) if p0 > 0 else 0.0

    # 3. Portfolio State Machine variables
    cash = float(init_cap)
    holdings_map: Dict[str, PortfolioHolding] = {}
    holding_scores_map: Dict[str, float] = {}
    ledger_events: List[PortfolioLedgerEvent] = []
    curve_points: List[PortfolioCurvePoint] = []

    event_counter = 0
    closed_exits = 0
    winning_exits = 0
    losing_exits = 0
    rebalance_rotations = 0
    gross_profit_sum = 0.0
    gross_loss_sum = 0.0

    peak_equity = float(init_cap)
    max_drawdown_pct = 0.0

    def _calc_total_equity() -> float:
        inv = sum(h.shares * h.current_price for h in holdings_map.values() if h.shares > 0)
        return cash + inv

    # 4. Chronological Bar-by-Bar Simulation Loop (Zero Look-Ahead Bias)
    for t_idx, d_str in enumerate(master_dates):
        # Update causal prices for assets trading on this bar
        for t_code, info in asset_data_map.items():
            orig_bar = info["date_to_bar"].get(d_str)
            if orig_bar is not None:
                c_p = float(info["series"].close[orig_bar])
                if c_p > 0:
                    info["last_known_close"] = c_p
                    info["last_known_bar"] = orig_bar
            if t_code in holdings_map:
                holdings_map[t_code].current_price = info["last_known_close"]

        total_eq_start = _calc_total_equity()
        for h in holdings_map.values():
            h.recalculate(total_portfolio_equity=total_eq_start)

        sold_today: set = set()

        # STEP 1: SELL_FULL on confirmed SELL signals at this bar
        for t_code in list(holdings_map.keys()):
            h = holdings_map.get(t_code)
            if not h or h.shares <= 0:
                continue
            info = asset_data_map[t_code]
            orig_bar = info["date_to_bar"].get(d_str)
            if orig_bar is None or t_idx <= h.entry_bar_index:
                continue
            bar_sigs = info["signals_by_bar"].get(orig_bar, [])
            sell_sigs = [s for s in bar_sigs if s.direction == "SELL" and float(s.execution_price) > 0]
            if sell_sigs:
                s_sig = sell_sigs[0]
                p_sell = float(s_sig.execution_price)
                proceeds = round(h.shares * p_sell, 2)
                cost_basis = h.shares * h.average_buy_price
                pnl_val = round(proceeds - cost_basis, 2)
                pnl_pct = round(((p_sell - h.average_buy_price) / h.average_buy_price) * 100.0, 2) if h.average_buy_price > 0 else 0.0

                w_before = h.current_weight_pct
                cash = round(cash + proceeds, 2)
                del holdings_map[t_code]
                holding_scores_map.pop(t_code, None)
                sold_today.add(t_code)

                closed_exits += 1
                if pnl_val > 0:
                    winning_exits += 1
                    gross_profit_sum += pnl_val
                else:
                    losing_exits += 1
                    gross_loss_sum += abs(pnl_val)

                eq_after = _calc_total_equity()
                event_counter += 1
                ledger_events.append(
                    PortfolioLedgerEvent(
                        event_id=event_counter,
                        date=d_str,
                        ticker=t_code,
                        asset_name=h.asset_name,
                        event_type="SELL_FULL",
                        event_label="VENDA TOTAL (TOPO)",
                        strategy_sub_id=s_sig.strategy_sub_id,
                        strategy_label=labels_map.get(s_sig.strategy_sub_id, s_sig.strategy_sub_id),
                        potential_score=holding_scores_map.get(t_code, 65.0),
                        execution_price=round(p_sell, 2),
                        shares_delta=round(-h.shares, 4),
                        trade_value=proceeds,
                        realized_pnl_value=pnl_val,
                        realized_pnl_pct=pnl_pct,
                        weight_before_pct=round(w_before, 2),
                        weight_after_pct=0.0,
                        cash_after=round(cash, 2),
                        portfolio_equity_after=round(eq_after, 2),
                    )
                )

        # STEP 2: SELL_PARTIAL_REBALANCE when weight > max_weight_pct + rebalance_band_pct
        total_eq_mid = _calc_total_equity()
        for t_code in list(holdings_map.keys()):
            h = holdings_map[t_code]
            h.recalculate(total_portfolio_equity=total_eq_mid)
            if t_idx > h.entry_bar_index and h.current_weight_pct > (max_w + band_w) and h.current_price > 0:
                target_val = (max_w / 100.0) * total_eq_mid
                excess_val = max(0.0, h.market_value - target_val)
                trim_sh = min(h.shares, round_shares_for_ticker(t_code, excess_val / h.current_price, mode="round"))
                if trim_sh > 0 and trim_sh < h.shares:
                    p_exec = h.current_price
                    proceeds = round(trim_sh * p_exec, 2)
                    cost_part = trim_sh * h.average_buy_price
                    pnl_val = round(proceeds - cost_part, 2)
                    pnl_pct = round(((p_exec - h.average_buy_price) / h.average_buy_price) * 100.0, 2) if h.average_buy_price > 0 else 0.0
                    w_before = h.current_weight_pct

                    h.shares = round(h.shares - trim_sh, 4)
                    cash = round(cash + proceeds, 2)
                    eq_after = _calc_total_equity()
                    h.recalculate(total_portfolio_equity=eq_after)
                    sold_today.add(t_code)

                    closed_exits += 1
                    rebalance_rotations += 1
                    if pnl_val > 0:
                        winning_exits += 1
                        gross_profit_sum += pnl_val
                    else:
                        losing_exits += 1
                        gross_loss_sum += abs(pnl_val)

                    event_counter += 1
                    ledger_events.append(
                        PortfolioLedgerEvent(
                            event_id=event_counter,
                            date=d_str,
                            ticker=t_code,
                            asset_name=h.asset_name,
                            event_type="SELL_PARTIAL_REBALANCE",
                            event_label="REBALANCEAMENTO PARCIAL",
                            strategy_sub_id="sell_rebal_rv_rf",
                            strategy_label=labels_map.get("sell_rebal_rv_rf", "Rebalanceamento de Banda"),
                            potential_score=holding_scores_map.get(t_code, 65.0),
                            execution_price=round(p_exec, 2),
                            shares_delta=round(-trim_sh, 4),
                            trade_value=proceeds,
                            realized_pnl_value=pnl_val,
                            realized_pnl_pct=pnl_pct,
                            weight_before_pct=round(w_before, 2),
                            weight_after_pct=round(h.current_weight_pct, 2),
                            cash_after=round(cash, 2),
                            portfolio_equity_after=round(eq_after, 2),
                        )
                    )

        # Gather confirmed BUY signals executing at this bar across all assets
        buy_candidates_today: List[Tuple[float, str, SignalRecord]] = []
        for t_code, info in asset_data_map.items():
            if t_code in sold_today:
                continue
            orig_bar = info["date_to_bar"].get(d_str)
            if orig_bar is None:
                continue
            bar_sigs = info["signals_by_bar"].get(orig_bar, [])
            b_sigs = [s for s in bar_sigs if s.direction == "BUY" and float(s.execution_price) > 0]
            if b_sigs:
                best_sig = b_sigs[0]
                c_score = _compute_causal_score_at_bar(info["signals"], orig_bar, best_sig.strategy_sub_id)
                buy_candidates_today.append((c_score, t_code, best_sig))

        buy_candidates_today.sort(key=lambda x: (-x[0], x[1]))

        # STEP 3: Tactical Opportunity-Cost Rotation (ROTATE_OUT -> ROTATE_IN) when cash is low
        total_eq_rot = _calc_total_equity()
        unheld_buy_cands = [c for c in buy_candidates_today if c[1] not in holdings_map]
        if cash < (0.10 * total_eq_rot) and unheld_buy_cands and holdings_map:
            best_cand_score, best_cand_ticker, best_cand_sig = unheld_buy_cands[0]
            stagnant_list = []
            for t_code, h in holdings_map.items():
                bars_held = t_idx - h.entry_bar_index
                h_score = holding_scores_map.get(t_code, 55.0)
                if bars_held >= 3 and h.unrealized_pnl_pct <= 3.0:
                    stagnant_list.append((h_score, t_code, h))
            stagnant_list.sort(key=lambda x: (x[0], x[2].unrealized_pnl_pct))

            if stagnant_list:
                weak_score, weak_ticker, weak_h = stagnant_list[0]
                if (best_cand_score - weak_score) >= rot_delta and weak_h.current_price > 0:
                    # Execute ROTATE_OUT
                    p_out = weak_h.current_price
                    proceeds = round(weak_h.shares * p_out, 2)
                    cost_basis = weak_h.shares * weak_h.average_buy_price
                    pnl_val = round(proceeds - cost_basis, 2)
                    pnl_pct = round(((p_out - weak_h.average_buy_price) / weak_h.average_buy_price) * 100.0, 2) if weak_h.average_buy_price > 0 else 0.0
                    w_before = weak_h.current_weight_pct
                    sh_out = weak_h.shares

                    cash = round(cash + proceeds, 2)
                    del holdings_map[weak_ticker]
                    holding_scores_map.pop(weak_ticker, None)
                    sold_today.add(weak_ticker)

                    closed_exits += 1
                    rebalance_rotations += 1
                    if pnl_val > 0:
                        winning_exits += 1
                        gross_profit_sum += pnl_val
                    else:
                        losing_exits += 1
                        gross_loss_sum += abs(pnl_val)

                    eq_after_out = _calc_total_equity()
                    event_counter += 1
                    ledger_events.append(
                        PortfolioLedgerEvent(
                            event_id=event_counter,
                            date=d_str,
                            ticker=weak_ticker,
                            asset_name=weak_h.asset_name,
                            event_type="ROTATE_OUT",
                            event_label="ROTAÇÃO (SAÍDA)",
                            strategy_sub_id="sell_rebal_relative_strength",
                            strategy_label=labels_map.get("sell_rebal_relative_strength", "Rotação por Custo de Oportunidade"),
                            potential_score=weak_score,
                            execution_price=round(p_out, 2),
                            shares_delta=round(-sh_out, 4),
                            trade_value=proceeds,
                            realized_pnl_value=pnl_val,
                            realized_pnl_pct=pnl_pct,
                            weight_before_pct=round(w_before, 2),
                            weight_after_pct=0.0,
                            cash_after=round(cash, 2),
                            portfolio_equity_after=round(eq_after_out, 2),
                        )
                    )

                    # Execute paired ROTATE_IN on best_cand_ticker
                    p_in = float(best_cand_sig.execution_price)
                    max_cap_val = (max_w / 100.0) * eq_after_out
                    alloc_val = min(cash, proceeds, max_cap_val)
                    buy_sh = round_shares_for_ticker(best_cand_ticker, alloc_val / p_in, mode="floor")
                    if buy_sh > 0:
                        cost_in = round(buy_sh * p_in, 2)
                        cash = max(0.0, round(cash - cost_in, 2))
                        c_info = asset_data_map[best_cand_ticker]
                        new_h = PortfolioHolding(
                            ticker=best_cand_ticker,
                            asset_name=c_info["asset_name"],
                            shares=buy_sh,
                            average_buy_price=p_in,
                            current_price=c_info["last_known_close"],
                            entry_bar_index=t_idx,
                        )
                        holdings_map[best_cand_ticker] = new_h
                        holding_scores_map[best_cand_ticker] = best_cand_score
                        eq_after_in = _calc_total_equity()
                        new_h.recalculate(total_portfolio_equity=eq_after_in)

                        event_counter += 1
                        ledger_events.append(
                            PortfolioLedgerEvent(
                                event_id=event_counter,
                                date=d_str,
                                ticker=best_cand_ticker,
                                asset_name=c_info["asset_name"],
                                event_type="ROTATE_IN",
                                event_label="ROTAÇÃO (ENTRADA)",
                                strategy_sub_id=best_cand_sig.strategy_sub_id,
                                strategy_label=labels_map.get(best_cand_sig.strategy_sub_id, best_cand_sig.strategy_sub_id),
                                potential_score=best_cand_score,
                                execution_price=round(p_in, 2),
                                shares_delta=round(buy_sh, 4),
                                trade_value=cost_in,
                                realized_pnl_value=None,
                                realized_pnl_pct=None,
                                weight_before_pct=0.0,
                                weight_after_pct=round(new_h.current_weight_pct, 2),
                                cash_after=round(cash, 2),
                                portfolio_equity_after=round(eq_after_in, 2),
                            )
                        )
                        buy_candidates_today = [c for c in buy_candidates_today if c[1] != best_cand_ticker]

        # STEP 4: Score-Weighted BUY Allocation of Available Cash
        if cash > 1.0 and buy_candidates_today:
            total_eq_buy = _calc_total_equity()
            max_cap_val = (max_w / 100.0) * total_eq_buy
            score_sum = sum(max(1.0, c[0]) for c in buy_candidates_today)
            cash_pool = cash

            for c_score, t_code, b_sig in buy_candidates_today:
                if cash <= 1.0:
                    break
                p_buy = float(b_sig.execution_price)
                if p_buy <= 0:
                    continue
                c_info = asset_data_map[t_code]
                existing_h = holdings_map.get(t_code)
                cur_val = (existing_h.shares * p_buy) if existing_h else 0.0
                w_before = ((existing_h.shares * existing_h.current_price) / total_eq_buy * 100.0) if existing_h and total_eq_buy > 0 else 0.0
                room_val = max(0.0, max_cap_val - cur_val)
                if room_val < min(10.0, p_buy):
                    continue

                w_prop = max(1.0, c_score) / score_sum if score_sum > 0 else (1.0 / len(buy_candidates_today))
                desired_val = max(cash_pool * w_prop, room_val)
                alloc_val = min(cash, room_val, desired_val)
                buy_sh = round_shares_for_ticker(t_code, alloc_val / p_buy, mode="floor")
                if buy_sh <= 0.0:
                    continue

                cost = round(buy_sh * p_buy, 2)
                if cost > cash + 1e-6 or (cur_val + cost) > max_cap_val + 1e-2:
                    continue

                cash = max(0.0, round(cash - cost, 2))
                if existing_h is None:
                    new_h = PortfolioHolding(
                        ticker=t_code,
                        asset_name=c_info["asset_name"],
                        shares=buy_sh,
                        average_buy_price=p_buy,
                        current_price=c_info["last_known_close"],
                        entry_bar_index=t_idx,
                    )
                    holdings_map[t_code] = new_h
                    holding_scores_map[t_code] = c_score
                else:
                    tot_sh = existing_h.shares + buy_sh
                    avg_p = ((existing_h.shares * existing_h.average_buy_price) + cost) / tot_sh
                    existing_h.shares = round(tot_sh, 4)
                    existing_h.average_buy_price = round(avg_p, 4)
                    existing_h.current_price = c_info["last_known_close"]
                    holding_scores_map[t_code] = max(holding_scores_map.get(t_code, 0.0), c_score)

                eq_after_b = _calc_total_equity()
                holdings_map[t_code].recalculate(total_portfolio_equity=eq_after_b)

                event_counter += 1
                ledger_events.append(
                    PortfolioLedgerEvent(
                        event_id=event_counter,
                        date=d_str,
                        ticker=t_code,
                        asset_name=c_info["asset_name"],
                        event_type="BUY",
                        event_label="COMPRA",
                        strategy_sub_id=b_sig.strategy_sub_id,
                        strategy_label=labels_map.get(b_sig.strategy_sub_id, b_sig.strategy_sub_id),
                        potential_score=c_score,
                        execution_price=round(p_buy, 2),
                        shares_delta=round(buy_sh, 4),
                        trade_value=cost,
                        realized_pnl_value=None,
                        realized_pnl_pct=None,
                        weight_before_pct=round(w_before, 2),
                        weight_after_pct=round(holdings_map[t_code].current_weight_pct, 2),
                        cash_after=round(cash, 2),
                        portfolio_equity_after=round(eq_after_b, 2),
                    )
                )

        # End-of-Bar Mark-to-Market Equity & Benchmark Calculation
        invested_eq = sum(h.shares * asset_data_map[t_code]["last_known_close"] for t_code, h in holdings_map.items() if h.shares > 0)
        port_eq = cash + invested_eq
        if port_eq > peak_equity:
            peak_equity = port_eq
        dd_pct = ((port_eq - peak_equity) / peak_equity) * 100.0 if peak_equity > 0 else 0.0
        if dd_pct < max_drawdown_pct:
            max_drawdown_pct = dd_pct

        bench_eq = sum(bench_shares[t_code] * info["last_known_close"] for t_code, info in asset_data_map.items())

        curve_points.append(
            PortfolioCurvePoint(
                date=d_str,
                portfolio_equity=round(port_eq, 2),
                cash_balance=round(cash, 2),
                invested_equity=round(invested_eq, 2),
                benchmark_equity=round(bench_eq, 2),
                drawdown_pct=round(dd_pct, 2),
            )
        )

    final_eq = curve_points[-1].portfolio_equity if curve_points else init_cap
    final_bench = curve_points[-1].benchmark_equity if curve_points else init_cap
    final_inv = curve_points[-1].invested_equity if curve_points else 0.0

    for h in holdings_map.values():
        h.recalculate(total_portfolio_equity=final_eq)

    net_profit = round(final_eq - init_cap, 2)
    tot_ret_pct = round(((final_eq / init_cap) - 1.0) * 100.0, 2) if init_cap > 0 else 0.0
    bench_ret_pct = round(((final_bench / init_cap) - 1.0) * 100.0, 2) if init_cap > 0 else 0.0
    alpha_pct = round(tot_ret_pct - bench_ret_pct, 2)
    win_rate = round((winning_exits / closed_exits) * 100.0, 2) if closed_exits > 0 else 0.0
    if gross_loss_sum > 0:
        pf = round(gross_profit_sum / gross_loss_sum, 2)
    elif gross_profit_sum > 0:
        pf = 99.99
    else:
        pf = 0.0

    final_holdings_list = sorted(
        [h for h in holdings_map.values() if h.shares > 0],
        key=lambda x: -x.market_value,
    )
    opp_profiles = [
        info["profile"] for info in asset_data_map.values() if info.get("profile") is not None
    ]
    opp_profiles.sort(key=lambda x: (-x.potential_score, -x.win_rate_pct, x.ticker))

    return PortfolioSimulationResult(
        initial_capital=round(init_cap, 2),
        final_equity=round(final_eq, 2),
        final_cash=round(cash, 2),
        final_invested_value=round(final_inv, 2),
        net_profit=net_profit,
        total_return_pct=tot_ret_pct,
        benchmark_return_pct=bench_ret_pct,
        alpha_vs_benchmark_pct=alpha_pct,
        max_drawdown_pct=round(max_drawdown_pct, 2),
        win_rate_pct=win_rate,
        profit_factor=pf,
        total_events_count=len(ledger_events),
        closed_exits_count=closed_exits,
        winning_exits_count=winning_exits,
        losing_exits_count=losing_exits,
        rebalance_rotations_count=rebalance_rotations,
        current_holdings=final_holdings_list,
        opportunity_profiles=opp_profiles,
        ledger_events=ledger_events,
        curve=curve_points,
    )
