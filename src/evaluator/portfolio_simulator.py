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


def simulate_portfolio_multi_asset(*args, **kwargs) -> PortfolioSimulationResult:
    raise NotImplementedError
