"""
Pydantic schemas and serialization helpers for FastAPI server.
Converts NumPy types (float64, int64, ndarray) into native Python types
to avoid JSON serialization errors.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import numpy as np


def sanitize_val(v: Any) -> Any:
    """Recursively converts NumPy scalars and arrays to native Python types."""
    if isinstance(v, (np.floating, float)):
        if np.isnan(v) or np.isinf(v):
            return None
        return float(v)
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.ndarray):
        return [sanitize_val(x) for x in v.tolist()]
    if isinstance(v, dict):
        return {k: sanitize_val(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [sanitize_val(x) for x in v]
    return v


# 1. Models for /api/analyze

class CandleBar(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class SignalItem(BaseModel):
    strategy_id: str
    strategy_sub_id: str
    strategy_label: str
    group_id: str
    direction: str = "BUY"  # "BUY" | "SELL"
    signal_date: str
    execution_date: str
    signal_bar_index: int
    execution_bar_index: int
    execution_price: float
    reference_line_price: Optional[float] = None
    is_open: bool = False
    forward_return_pct: Optional[float] = None
    mae_pct: Optional[float] = None


class ReferenceLineItem(BaseModel):
    start_date: str
    end_date: str
    start_bar_index: int
    end_bar_index: int
    price_level: float
    status: str
    variation_id: str
    line_type: str = "SUPPORT"  # "SUPPORT" | "RESISTANCE"
    direction: str = "BUY"      # "BUY" | "SELL"


class StrategySummaryItem(BaseModel):
    strategy_sub_id: str
    strategy_label: str
    group_id: str
    direction: str = "BUY"      # "BUY" | "SELL"
    win_rate: float
    mean_forward_return: float
    median_forward_return: float
    mean_mae: float
    max_mae: float
    efficiency_score: float
    total_signals: int
    executed_buys: int
    retest_fill_rate: Optional[float] = None
    open_signals_count: int = 0


class TimingStatusModel(BaseModel):
    status_category: str  # "IDEAL", "EXTENDED", "LATE"
    status_label: str
    distance_pct: float
    recommended_price: float
    current_price: float
    advice_text: str
    direction: str = "BUY"


class AnalyzeResponse(BaseModel):
    ticker: str
    interval: str
    period: str
    current_price: float
    candles: List[CandleBar]
    signals: List[SignalItem]
    reference_lines: List[ReferenceLineItem]
    summaries: List[StrategySummaryItem]
    current_state: Dict[str, Any]
    timing_status: Optional[TimingStatusModel] = None


# 2. Models for /api/radar

class RadarItem(BaseModel):
    ticker: str
    asset_name: Optional[str] = None
    category: str
    current_price: float
    strategy_sub_id: str
    strategy_label: str
    direction: str = "BUY"  # "BUY" | "SELL"
    status_signal: str
    timing_category: str
    timing_label: str
    distance_pct: float
    recommended_price: float
    historical_n: int
    historical_win_rate: float
    advice_text: str


class RadarPage(BaseModel):
    items: List[RadarItem]
    page: int
    page_size: int
    total_assets: int
    total_pages: int
    direction: str = "BUY"
    strategies: List[str] = []
    cached: bool = False


# 3. Models for /api/simulate

class SimulateRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    cycle_entry_mode: str = "multi_buy"   # "multi_buy" | "single_buy"
    contribution_amount: float = 1000.0   # Serves as contribution in accumulation, or per-signal contribution in multi-buy cycle_trade
    initial_capital: float = 1000.0
    buy_strategy: Optional[str] = None    # Specific buy strategy or "ALL"
    sell_strategy: Optional[str] = None   # Specific sell strategy or "ALL"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    selected_strategies: Optional[List[str]] = None
    lookback_n: int = 10
    retest_m: int = 5
    retest_tol: float = 0.0


class AccumulationPoint(BaseModel):
    date: str
    total_invested: float
    portfolio_value: float
    shares: float
    close_price: float
    cash_inflow: float


class BuyEntrySchema(BaseModel):
    entry_id: int
    date: str
    bar_index: int
    price: float
    shares: float
    capital: float
    strategy_sub_id: str
    strategy_label: str


class TradeRecordSchema(BaseModel):
    trade_id: int
    buy_strategy_sub_id: str
    buy_strategy_label: str
    buy_date: str
    buy_price: float
    buy_bar_index: int
    sell_strategy_sub_id: Optional[str] = None
    sell_strategy_label: Optional[str] = None
    sell_date: Optional[str] = None
    sell_price: Optional[float] = None
    sell_bar_index: Optional[int] = None
    return_pct: float = 0.0
    profit_loss: float = 0.0
    duration_bars: int = 0
    shares: float = 0.0
    entry_capital: float = 0.0
    exit_capital: float = 0.0
    status: str = "FECHADO"
    num_entries: int = 1
    average_buy_price: float = 0.0
    total_invested: float = 0.0
    total_shares: float = 0.0
    buy_entries: Optional[List[BuyEntrySchema]] = None


class SimulationMetricSummary(BaseModel):
    simulation_mode: str = "cycle_trade"
    total_invested: float
    final_portfolio_value: float
    total_profit_loss: float
    total_return_pct: float
    xirr_annualized_pct: Optional[float] = None
    max_drawdown_pct: float
    total_trades_count: int
    shares_accumulated: float
    average_cost_price: float
    current_market_price: float
    dca_regular_final_value: float
    alpha_vs_dca_pct: float
    # Extended metrics for Cycle Trade (Buy -> Sell)
    winning_trades_count: Optional[int] = None
    losing_trades_count: Optional[int] = None
    win_rate_pct: Optional[float] = None
    avg_trade_return_pct: Optional[float] = None
    avg_trade_bars: Optional[float] = None
    buy_and_hold_return_pct: Optional[float] = None
    profit_factor: Optional[float] = None
    avg_entries_per_cycle: Optional[float] = None


class SimulateResponse(BaseModel):
    ticker: str
    period: str
    metrics: SimulationMetricSummary
    curve: List[AccumulationPoint]
    trades: List[Dict[str, Any]]


# 4. Models for /api/simulate/optimize

class StrategyPairRankItemModel(BaseModel):
    rank: int
    buy_sub_id: str
    buy_label: str
    sell_sub_id: Optional[str] = None
    sell_label: Optional[str] = None
    simulation_mode: str = "cycle_trade"
    closed_trades: int = 0
    winning_trades: int = 0
    win_rate_pct: float = 0.0
    total_return_pct: float
    net_profit: float
    max_drawdown_pct: float = 0.0
    has_open_trade: bool = False
    final_equity: float
    cycle_entry_mode: Optional[str] = "multi_buy"
    total_invested: Optional[float] = None
    average_buy_price: Optional[float] = None
    total_shares: Optional[float] = None
    total_contributions: Optional[int] = None


class OptimizeCombinationsRequest(BaseModel):
    ticker: str
    interval: str = "1d"
    period: str = "2y"
    simulation_mode: str = "cycle_trade"  # "cycle_trade" | "accumulation"
    cycle_entry_mode: str = "multi_buy"   # "multi_buy" | "single_buy"
    contribution_amount: float = 1000.0   # Aporte periódico para modo accumulation
    initial_capital: float = 1000.0
    min_trades: int = 2
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lookback_n: int = 10
    retest_m: int = 5
    retest_tol: float = 0.0


class OptimizeCombinationsResponse(BaseModel):
    ticker: str
    period: str
    simulation_mode: str = "cycle_trade"
    initial_capital: float
    total_combinations_tested: int
    champion: Optional[StrategyPairRankItemModel] = None
    top_combinations: List[StrategyPairRankItemModel] = []


# 5. Models for /api/portfolio/advise and /api/portfolio/simulate

class PortfolioHoldingInput(BaseModel):
    ticker: str
    shares: float = Field(..., gt=0.0)
    average_buy_price: float = Field(..., gt=0.0)


class PortfolioHoldingEvaluatedModel(BaseModel):
    ticker: str
    asset_name: str
    shares: float
    average_buy_price: float
    current_price: float
    market_value: float
    invested_value: float
    unrealized_pnl_value: float
    unrealized_pnl_pct: float
    current_weight_pct: float
    entry_bar_index: int = 0


class AssetOpportunityProfileModel(BaseModel):
    ticker: str
    asset_name: str
    category: str
    current_price: float
    champion_buy_id: str
    champion_buy_label: str
    champion_sell_id: str
    champion_sell_label: str
    win_rate_pct: float
    historical_return_pct: float
    max_drawdown_pct: float
    closed_trades: int
    active_direction: str
    timing_category: str
    timing_label: str
    distance_pct: float
    recommended_price: float
    potential_score: float


class PortfolioActionRecommendationModel(BaseModel):
    ticker: str
    asset_name: str
    action_type: str  # "BUY" | "SELL_FULL" | "SELL_PARTIAL_REBALANCE" | "ROTATE_OUT" | "ROTATE_IN" | "HOLD"
    action_label: str
    reason_text: str
    strategy_sub_id: str
    strategy_label: str
    potential_score: float
    timing_category: str
    current_price: float
    reference_price: float
    current_shares: float
    recommended_shares_delta: float
    target_shares: float
    order_value: float
    current_weight_pct: float
    target_weight_pct: float


class PortfolioAdviseRequest(BaseModel):
    available_cash: float = Field(10000.0, ge=0.0)
    holdings: List[PortfolioHoldingInput] = []
    universe_category: str = "featured"
    custom_tickers: List[str] = []
    interval: str = "1d"
    period: str = "2y"
    max_weight_pct: float = Field(25.0, ge=5.0, le=100.0)
    rebalance_band_pct: float = Field(5.0, ge=1.0, le=50.0)
    min_rotation_score_delta: float = Field(15.0, ge=5.0, le=80.0)


class PortfolioAdviseResponse(BaseModel):
    universe_category: str
    interval: str
    period: str
    current_cash: float
    current_holdings_value: float
    total_portfolio_equity: float
    projected_cash_after: float
    projected_invested_after: float
    max_weight_pct: float
    holdings_evaluated: List[PortfolioHoldingEvaluatedModel] = []
    recommendations: List[PortfolioActionRecommendationModel] = []
    opportunity_ranking: List[AssetOpportunityProfileModel] = []


class PortfolioLedgerEventModel(BaseModel):
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
    weight_before_pct: float
    weight_after_pct: float
    cash_after: float
    portfolio_equity_after: float


class PortfolioCurvePointModel(BaseModel):
    date: str
    portfolio_equity: float
    cash_balance: float
    invested_equity: float
    benchmark_equity: float
    drawdown_pct: float


class PortfolioSimulationMetricsModel(BaseModel):
    initial_capital: float
    final_equity: float
    final_cash: float
    final_invested_value: float
    net_profit: float
    total_return_pct: float
    benchmark_return_pct: float
    alpha_vs_benchmark_pct: float = Field(
        ...,
        description="Arithmetic excess return over benchmark percentage (total_return_pct - benchmark_return_pct)"
    )
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_events_count: int
    closed_exits_count: int
    winning_exits_count: int
    losing_exits_count: int
    rebalance_rotations_count: int


class PortfolioSimulateRequest(BaseModel):
    initial_capital: float = Field(10000.0, gt=0.0)
    universe_category: str = "featured"
    custom_tickers: List[str] = []
    interval: str = "1d"
    period: str = "2y"
    max_weight_pct: float = Field(25.0, ge=5.0, le=100.0)
    rebalance_band_pct: float = Field(5.0, ge=1.0, le=50.0)
    min_rotation_score_delta: float = Field(15.0, ge=5.0, le=80.0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class PortfolioSimulateResponse(BaseModel):
    universe_category: str
    interval: str
    period: str
    metrics: PortfolioSimulationMetricsModel
    final_holdings: List[PortfolioHoldingEvaluatedModel] = []
    curve: List[PortfolioCurvePointModel] = []
    ledger_events: List[PortfolioLedgerEventModel] = []
    opportunity_ranking: List[AssetOpportunityProfileModel] = []


class PortfolioQuotesRequest(BaseModel):
    tickers: List[str]


class QuoteItem(BaseModel):
    ticker: str
    price: float
    change_pct: float
    time: Optional[str] = None


class PortfolioQuotesResponse(BaseModel):
    quotes: Dict[str, QuoteItem]


# 9. Models for B3 Spreadsheet Integration

class B3MovementRecord(BaseModel):
    data: str
    entrada_saida: str  # "Credito" | "Debito"
    tipo: str           # "Compra", "Venda", "Rendimento", etc.
    ticker_raw: str
    ticker_clean: str   # Ex: "PETR4"
    ticker_sa: str      # Ex: "PETR4.SA"
    quantidade: float
    preco_unitario: float
    valor_operacao: float
    instituicao: Optional[str] = None


class B3Holding(BaseModel):
    ticker: str              # "PETR4.SA"
    ticker_clean: str        # "PETR4"
    shares: float            # Cotas em custódia líquida
    average_buy_price: float # Preço Médio ponderado contábil (R$)
    total_invested: float    # shares * average_buy_price
    asset_class: str         # "Ações Brasil", "FIIs", "BDRs", "Outros"


class B3MonthlyIncome(BaseModel):
    month_year: str          # "YYYY-MM"
    dividendos: float
    jcp: float
    rendimentos: float
    total: float


class B3ParseResult(BaseModel):
    filename: str
    total_movements: int
    holdings: List[B3Holding]
    total_invested: float
    total_income: float
    monthly_income: List[B3MonthlyIncome]

