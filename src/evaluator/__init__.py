"""
Statistical Evaluator package interface.
"""

from .statistical_engine import (
    evaluate_strategy_performance,
    evaluate_all_strategies,
    split_closed_and_open_signals,
)
from .accumulation_simulator import (
    SimulationResult,
    simulate_accumulation,
    TradeRecord,
    CycleSimulationResult,
    simulate_cycle_trade,
    StrategyPairRankItem,
    optimize_strategy_pairs,
    optimize_dca_strategies,
)
from .timing_classifier import (
    TimingStatus,
    classify_timing_status,
)
from .portfolio_simulator import (
    PortfolioHolding,
    AssetOpportunityProfile,
    PortfolioActionRecommendation,
    PortfolioLedgerEvent,
    PortfolioCurvePoint,
    PortfolioSimulationResult,
    compute_asset_opportunity_profile,
    advise_portfolio_rebalance,
    simulate_portfolio_multi_asset,
)

__all__ = [
    "evaluate_strategy_performance",
    "evaluate_all_strategies",
    "split_closed_and_open_signals",
    "SimulationResult",
    "simulate_accumulation",
    "TradeRecord",
    "CycleSimulationResult",
    "simulate_cycle_trade",
    "StrategyPairRankItem",
    "optimize_strategy_pairs",
    "optimize_dca_strategies",
    "TimingStatus",
    "classify_timing_status",
    "PortfolioHolding",
    "AssetOpportunityProfile",
    "PortfolioActionRecommendation",
    "PortfolioLedgerEvent",
    "PortfolioCurvePoint",
    "PortfolioSimulationResult",
    "compute_asset_opportunity_profile",
    "advise_portfolio_rebalance",
    "simulate_portfolio_multi_asset",
]
