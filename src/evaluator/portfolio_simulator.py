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


def compute_asset_opportunity_profile(*args, **kwargs) -> AssetOpportunityProfile:
    raise NotImplementedError


def advise_portfolio_rebalance(*args, **kwargs) -> Dict[str, Any]:
    raise NotImplementedError


def simulate_portfolio_multi_asset(*args, **kwargs) -> PortfolioSimulationResult:
    raise NotImplementedError
