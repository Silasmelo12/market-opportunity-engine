"""
FastAPI High-Performance Engine for Market Opportunity & Bottom Statistical Engine.
Serves JSON endpoints (/api/analyze, `/api/radar`, `/api/simulate`, `/api/strategies`)
and mounts the native zero-latency web terminal at root (`/`).
Fully supports BUY (Fundos), SELL (Topos), and BOTH operational directions.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..data_loader import DataLoader, strip_corporate_suffix, parse_b3_file
from ..strategies import StrategyCatalog, SignalRecord

from ..evaluator import (
    evaluate_all_strategies,
    classify_timing_status,
    simulate_accumulation,
    simulate_cycle_trade,
    optimize_strategy_pairs,
    optimize_dca_strategies,
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
from ..ui.theme import STRATEGY_LABELS_PT, get_friendly_label, get_asset_name, ASSET_NAMES_PT
from .cache import daily_cache
from .schemas import (
    sanitize_val,
    AnalyzeResponse,
    CandleBar,
    SignalItem,
    ReferenceLineItem,
    StrategySummaryItem,
    TimingStatusModel,
    RadarItem,
    RadarPage,
    SimulateRequest,
    SimulateResponse,
    AccumulationPoint,
    SimulationMetricSummary,
    StrategyPairRankItemModel,
    OptimizeCombinationsRequest,
    OptimizeCombinationsResponse,
    PortfolioHoldingInput,
    PortfolioHoldingEvaluatedModel,
    AssetOpportunityProfileModel,
    PortfolioActionRecommendationModel,
    PortfolioAdviseRequest,
    PortfolioAdviseResponse,
    PortfolioLedgerEventModel,
    PortfolioCurvePointModel,
    PortfolioSimulationMetricsModel,
    PortfolioSimulateRequest,
    PortfolioSimulateResponse,
    PortfolioQuotesRequest,
    PortfolioQuotesResponse,
    QuoteItem,
    B3ParseResult,
)


app = FastAPI(
    title="Market Opportunity & Bottom Statistical Engine",
    version="4.0.0",
    description="High-performance backend and 60fps trading terminal API for Top and Bottom opportunities.",
)

# Enable CORS for local dev / cross-origin if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _prewarm_featured_radar():
    """Background pre-warm for featured basket page 1 to ensure instant UI loading."""
    import threading
    def _worker():
        try:
            # Prewarm featured basket
            for ticker, cat in TICKERS_FEATURED[:20]:
                _scan_single_ticker(ticker, cat, interval="1d", horizon_x=60, refresh=False)
        except Exception:
            pass

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


# In-memory TTL Cache
_CACHE_DATA: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _get_cache(key: str) -> Optional[Any]:
    entry = _CACHE_DATA.get(key)
    if entry and (time.time() - entry["time"] < CACHE_TTL_SECONDS):
        return entry["data"]
    return None


def _set_cache(key: str, data: Any) -> None:
    _CACHE_DATA[key] = {"time": time.time(), "data": data}


# Persistent Radar Disk Cache (2 hours TTL)
RADAR_CACHE_DIR = Path(".cache") / "radar"
RADAR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
RADAR_DISK_CACHE_TTL_SECONDS = 7200  # 2 hours


def _get_radar_disk_cache(cache_key: str) -> Optional[List[RadarItem]]:
    safe_name = cache_key.replace(":", "_").replace("/", "_") + ".json"
    cache_file = RADAR_CACHE_DIR / safe_name
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        saved_time = data.get("timestamp", 0)
        if time.time() - saved_time < RADAR_DISK_CACHE_TTL_SECONDS:
            raw_items = data.get("items", [])
            return [RadarItem(**item) for item in raw_items]
    except Exception:
        pass
    return None


def _set_radar_disk_cache(cache_key: str, items: List[RadarItem]) -> None:
    safe_name = cache_key.replace(":", "_").replace("/", "_") + ".json"
    cache_file = RADAR_CACHE_DIR / safe_name
    try:
        payload = {
            "timestamp": time.time(),
            "items": [item.model_dump() for item in items]
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass


def _get_group_id(sub_id: str) -> str:
    if sub_id.startswith("t1_") or sub_id.startswith("t2_") or sub_id.startswith("sell_t1_") or sub_id.startswith("sell_t2_"):
        return "proprietary"
    if "double_bottom" in sub_id or "wyckoff_spring" in sub_id or "double_top" in sub_id or "wyckoff_upthrust" in sub_id:
        return "price_action"
    if sub_id in (
        "dca_dynamic", "value_proxy", "rebal_rf_rv", "rebal_relative_strength",
        "sell_overbought_stat", "sell_value_proxy", "sell_rebal_rv_rf", "sell_rebal_relative_strength"
    ):
        return "allocation"
    if sub_id in (
        "bollinger_close_in", "bb_reversal_buy", "bb_reversal_sell",
        "keltner_squeeze", "squeeze_breakout_buy", "squeeze_breakout_sell",
        "zscore_extreme", "zscore_bottom_buy", "zscore_top_sell",
        "rsi_divergence", "rsi_bullish_div", "rsi_bearish_div",
        "stochastic_extreme", "stoch_oversold_cross", "stoch_overbought_cross",
        "macd_momentum", "macd_bottom_turn", "macd_top_turn",
        "vwap_bands", "vwap_band_buy", "vwap_band_sell",
        "mfi_extreme", "mfi_bottom_buy", "mfi_top_sell",
        "volume_climax_vsa", "vsa_absorption_buy", "vsa_climax_sell",
        "supertrend_trailing", "supertrend_bull_flip", "supertrend_bear_flip"
    ):
        return "quant"
    return "mql5"


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": "4.0.0",
        "cache_backend": daily_cache.backend,
    }


@app.get("/api/strategies")
def get_strategy_catalog():
    """Returns the list of all registered strategies grouped by category and direction."""
    categories = {
        "proprietary": {
            "name": "Estratégia Proprietária - Compra (Negação 2x2)",
            "direction": "BUY",
            "strategies": [
                {"id": "t1_open", "label": STRATEGY_LABELS_PT["t1_open"], "direction": "BUY"},
                {"id": "t1_retest", "label": STRATEGY_LABELS_PT["t1_retest"], "direction": "BUY"},
                {"id": "t2_open", "label": STRATEGY_LABELS_PT["t2_open"], "direction": "BUY"},
                {"id": "t2_retest", "label": STRATEGY_LABELS_PT["t2_retest"], "direction": "BUY"},
            ],
        },
        "proprietary_sell": {
            "name": "Estratégia Proprietária - Venda (Negação de Topo 2x2)",
            "direction": "SELL",
            "strategies": [
                {"id": "sell_t1_open", "label": STRATEGY_LABELS_PT["sell_t1_open"], "direction": "SELL"},
                {"id": "sell_t1_retest", "label": STRATEGY_LABELS_PT["sell_t1_retest"], "direction": "SELL"},
                {"id": "sell_t2_open", "label": STRATEGY_LABELS_PT["sell_t2_open"], "direction": "SELL"},
                {"id": "sell_t2_retest", "label": STRATEGY_LABELS_PT["sell_t2_retest"], "direction": "SELL"},
            ],
        },
        "price_action": {
            "name": "Price Action Institucional - Compra",
            "direction": "BUY",
            "strategies": [
                {"id": "price_action_double_bottom_bos", "label": STRATEGY_LABELS_PT["price_action_double_bottom_bos"], "direction": "BUY"},
                {"id": "buy_double_top_inverted", "label": STRATEGY_LABELS_PT["buy_double_top_inverted"], "direction": "BUY"},
                {"id": "price_action_wyckoff_spring", "label": STRATEGY_LABELS_PT["price_action_wyckoff_spring"], "direction": "BUY"},
            ],
        },
        "price_action_sell": {
            "name": "Price Action Institucional - Venda",
            "direction": "SELL",
            "strategies": [
                {"id": "sell_double_top_bos", "label": STRATEGY_LABELS_PT["sell_double_top_bos"], "direction": "SELL"},
                {"id": "sell_double_bottom_inverted", "label": STRATEGY_LABELS_PT["sell_double_bottom_inverted"], "direction": "SELL"},
                {"id": "sell_wyckoff_upthrust", "label": STRATEGY_LABELS_PT["sell_wyckoff_upthrust"], "direction": "SELL"},
            ],
        },
        "allocation": {
            "name": "Alocação & Holder - Compra",
            "direction": "BUY",
            "strategies": [
                {"id": "dca_dynamic", "label": STRATEGY_LABELS_PT["dca_dynamic"], "direction": "BUY"},
                {"id": "value_proxy", "label": STRATEGY_LABELS_PT["value_proxy"], "direction": "BUY"},
                {"id": "rebal_rf_rv", "label": STRATEGY_LABELS_PT["rebal_rf_rv"], "direction": "BUY"},
                {"id": "rebal_relative_strength", "label": STRATEGY_LABELS_PT["rebal_relative_strength"], "direction": "BUY"},
            ],
        },
        "allocation_sell": {
            "name": "Alocação & Realização - Venda",
            "direction": "SELL",
            "strategies": [
                {"id": "sell_overbought_stat", "label": STRATEGY_LABELS_PT["sell_overbought_stat"], "direction": "SELL"},
                {"id": "sell_rebal_rv_rf", "label": STRATEGY_LABELS_PT["sell_rebal_rv_rf"], "direction": "SELL"},
                {"id": "sell_rebal_relative_strength", "label": STRATEGY_LABELS_PT["sell_rebal_relative_strength"], "direction": "SELL"},
                {"id": "sell_value_proxy", "label": STRATEGY_LABELS_PT["sell_value_proxy"], "direction": "SELL"},
            ],
        },
        "mql5": {
            "name": "Padrões de Velas de Fundo (14 MQL5 - Compra)",
            "direction": "BUY",
            "strategies": [
                {"id": "hammer", "label": STRATEGY_LABELS_PT["hammer"], "direction": "BUY"},
                {"id": "inverted_hammer", "label": STRATEGY_LABELS_PT["inverted_hammer"], "direction": "BUY"},
                {"id": "bullish_engulfing", "label": STRATEGY_LABELS_PT["bullish_engulfing"], "direction": "BUY"},
                {"id": "piercing_line", "label": STRATEGY_LABELS_PT["piercing_line"], "direction": "BUY"},
                {"id": "morning_star", "label": STRATEGY_LABELS_PT["morning_star"], "direction": "BUY"},
                {"id": "bullish_harami", "label": STRATEGY_LABELS_PT["bullish_harami"], "direction": "BUY"},
                {"id": "three_inside_up", "label": STRATEGY_LABELS_PT["three_inside_up"], "direction": "BUY"},
                {"id": "three_outside_up", "label": STRATEGY_LABELS_PT["three_outside_up"], "direction": "BUY"},
                {"id": "three_white_soldiers", "label": STRATEGY_LABELS_PT["three_white_soldiers"], "direction": "BUY"},
                {"id": "tweezer_bottom", "label": STRATEGY_LABELS_PT["tweezer_bottom"], "direction": "BUY"},
                {"id": "dragonfly_doji", "label": STRATEGY_LABELS_PT["dragonfly_doji"], "direction": "BUY"},
                {"id": "abandoned_baby_bullish", "label": STRATEGY_LABELS_PT["abandoned_baby_bullish"], "direction": "BUY"},
                {"id": "bullish_kicker", "label": STRATEGY_LABELS_PT["bullish_kicker"], "direction": "BUY"},
                {"id": "climactic_pinbar", "label": STRATEGY_LABELS_PT["climactic_pinbar"], "direction": "BUY"},
            ],
        },
        "quant_buy": {
            "name": "Indicadores Quantitativos - Compra (Fundos)",
            "direction": "BUY",
            "strategies": [
                {"id": "bollinger_close_in", "label": STRATEGY_LABELS_PT["bollinger_close_in"], "direction": "BUY"},
                {"id": "keltner_squeeze", "label": STRATEGY_LABELS_PT["keltner_squeeze"], "direction": "BUY"},
                {"id": "zscore_extreme", "label": STRATEGY_LABELS_PT["zscore_extreme"], "direction": "BUY"},
                {"id": "rsi_divergence", "label": STRATEGY_LABELS_PT["rsi_divergence"], "direction": "BUY"},
                {"id": "stochastic_extreme", "label": STRATEGY_LABELS_PT["stochastic_extreme"], "direction": "BUY"},
                {"id": "macd_momentum", "label": STRATEGY_LABELS_PT["macd_momentum"], "direction": "BUY"},
                {"id": "vwap_bands", "label": STRATEGY_LABELS_PT["vwap_bands"], "direction": "BUY"},
                {"id": "mfi_extreme", "label": STRATEGY_LABELS_PT["mfi_extreme"], "direction": "BUY"},
                {"id": "volume_climax_vsa", "label": STRATEGY_LABELS_PT["volume_climax_vsa"], "direction": "BUY"},
                {"id": "supertrend_trailing", "label": STRATEGY_LABELS_PT["supertrend_trailing"], "direction": "BUY"},
            ],
        },
        "quant_sell": {
            "name": "Indicadores Quantitativos - Venda (Topos)",
            "direction": "SELL",
            "strategies": [
                {"id": "bollinger_close_in", "label": STRATEGY_LABELS_PT["bollinger_close_in"], "direction": "SELL"},
                {"id": "keltner_squeeze", "label": STRATEGY_LABELS_PT["keltner_squeeze"], "direction": "SELL"},
                {"id": "zscore_extreme", "label": STRATEGY_LABELS_PT["zscore_extreme"], "direction": "SELL"},
                {"id": "rsi_divergence", "label": STRATEGY_LABELS_PT["rsi_divergence"], "direction": "SELL"},
                {"id": "stochastic_extreme", "label": STRATEGY_LABELS_PT["stochastic_extreme"], "direction": "SELL"},
                {"id": "macd_momentum", "label": STRATEGY_LABELS_PT["macd_momentum"], "direction": "SELL"},
                {"id": "vwap_bands", "label": STRATEGY_LABELS_PT["vwap_bands"], "direction": "SELL"},
                {"id": "mfi_extreme", "label": STRATEGY_LABELS_PT["mfi_extreme"], "direction": "SELL"},
                {"id": "volume_climax_vsa", "label": STRATEGY_LABELS_PT["volume_climax_vsa"], "direction": "SELL"},
                {"id": "supertrend_trailing", "label": STRATEGY_LABELS_PT["supertrend_trailing"], "direction": "SELL"},
            ],
        },
        "mql5_sell": {
            "name": "Padrões de Velas de Topo (14 MQL5 - Venda)",
            "direction": "SELL",
            "strategies": [
                {"id": "shooting_star", "label": STRATEGY_LABELS_PT["shooting_star"], "direction": "SELL"},
                {"id": "hanging_man", "label": STRATEGY_LABELS_PT["hanging_man"], "direction": "SELL"},
                {"id": "bearish_engulfing", "label": STRATEGY_LABELS_PT["bearish_engulfing"], "direction": "SELL"},
                {"id": "dark_cloud_cover", "label": STRATEGY_LABELS_PT["dark_cloud_cover"], "direction": "SELL"},
                {"id": "evening_star", "label": STRATEGY_LABELS_PT["evening_star"], "direction": "SELL"},
                {"id": "bearish_harami", "label": STRATEGY_LABELS_PT["bearish_harami"], "direction": "SELL"},
                {"id": "three_inside_down", "label": STRATEGY_LABELS_PT["three_inside_down"], "direction": "SELL"},
                {"id": "three_outside_down", "label": STRATEGY_LABELS_PT["three_outside_down"], "direction": "SELL"},
                {"id": "three_black_crows", "label": STRATEGY_LABELS_PT["three_black_crows"], "direction": "SELL"},
                {"id": "tweezer_top", "label": STRATEGY_LABELS_PT["tweezer_top"], "direction": "SELL"},
                {"id": "gravestone_doji", "label": STRATEGY_LABELS_PT["gravestone_doji"], "direction": "SELL"},
                {"id": "abandoned_baby_bearish", "label": STRATEGY_LABELS_PT["abandoned_baby_bearish"], "direction": "SELL"},
                {"id": "bearish_kicker", "label": STRATEGY_LABELS_PT["bearish_kicker"], "direction": "SELL"},
                {"id": "climactic_bearish_pinbar", "label": STRATEGY_LABELS_PT["climactic_bearish_pinbar"], "direction": "SELL"},
            ],
        },
    }
    return categories


@app.get("/api/analyze", response_model=AnalyzeResponse)
def analyze_asset(
    ticker: str = Query("PETR4.SA", description="Ticker symbol"),
    interval: str = Query("1d", description="Bar timeframe: 5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d, 1wk"),
    period: str = Query("2y", description="Data period"),
    lookback_n: int = Query(10, description="Lookback window N"),
    retest_m: int = Query(5, description="Retest window M"),
    retest_tol: float = Query(0.005, description="Retest tolerance"),
    horizon_x: int = Query(60, description="Forward evaluation horizon"),
    refresh: bool = Query(False, description="Bypass cache"),
):
    cache_key = f"analyze:{ticker}:{interval}:{period}:{lookback_n}:{retest_m}:{retest_tol}:{horizon_x}"
    if not refresh:
        cached = _get_cache(cache_key)
        if cached:
            return cached

    try:
        series = DataLoader.load_asset_data(ticker=ticker, interval=interval, period=period, use_cache=not refresh)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro ao carregar dados para {ticker}: {str(exc)}")

    if series.length < 15:
        raise HTTPException(status_code=400, detail=f"Histórico insuficiente para {ticker} ({series.length} barras).")

    catalog = StrategyCatalog(
        lookback_n=lookback_n,
        retest_window_m=retest_m,
        tolerance_pct=retest_tol,
    )
    results = catalog.run_all(series)
    signals = results["signals"]
    ref_lines = results["reference_lines"]
    prop_state = results["prop_current_state"]
    pending = results["pending_signals"]

    # Calculate summaries (including pending strategies so they appear in metrics/ranking)
    pending_sub_ids = [
        (p.get("strategy_id", "mql5_candles"), p.get("strategy_sub_id"), p.get("direction", "BUY"))
        for p in pending if p.get("strategy_sub_id")
    ]
    summaries_raw = evaluate_all_strategies(
        series=series,
        signals=signals,
        horizon_bars=horizon_x,
        total_signals_by_sub_id=results["total_signals_by_sub_id"],
        include_empty_sub_ids=pending_sub_ids,
    )

    # Format dates
    is_intraday = interval in ("5m", "15m", "30m", "60m", "1h", "2h", "4h", "12h")
    date_strs: List[str] = []
    ts_seconds: List[int] = []

    for ts in series.timestamps:
        dt = pd.to_datetime(ts)
        sec = int(dt.timestamp())
        ts_seconds.append(sec)
        if is_intraday:
            date_strs.append(dt.strftime("%Y-%m-%d %H:%M"))
        else:
            date_strs.append(dt.strftime("%Y-%m-%d"))

    # Build candles for Lightweight Charts
    candles: List[CandleBar] = []
    for i in range(series.length):
        time_val = str(ts_seconds[i]) if is_intraday else date_strs[i]
        candles.append(
            CandleBar(
                time=time_val,
                open=float(series.open[i]),
                high=float(series.high[i]),
                low=float(series.low[i]),
                close=float(series.close[i]),
                volume=float(series.volume[i]),
            )
        )

    # Re-evaluate signals to attach forward_return_pct & mae_pct in metadata
    evaluate_all_strategies(
        series=series,
        signals=signals,
        horizon_bars=horizon_x,
        total_signals_by_sub_id=results["total_signals_by_sub_id"],
    )

    signal_items: List[SignalItem] = []
    for sig in signals:
        meta = sig.metadata or {}
        sig_date = date_strs[sig.signal_bar_index] if sig.signal_bar_index < len(date_strs) else ""
        exec_date = date_strs[sig.execution_bar_index] if sig.execution_bar_index < len(date_strs) else ""
        signal_items.append(
            SignalItem(
                strategy_id=sig.strategy_id,
                strategy_sub_id=sig.strategy_sub_id,
                strategy_label=get_friendly_label(sig.strategy_sub_id),
                group_id=_get_group_id(sig.strategy_sub_id),
                direction=sig.direction,
                signal_date=sig_date,
                execution_date=exec_date,
                signal_bar_index=sig.signal_bar_index,
                execution_bar_index=sig.execution_bar_index,
                execution_price=float(sig.execution_price),
                reference_line_price=float(sig.reference_line_price) if sig.reference_line_price else None,
                is_open=bool(meta.get("is_open", False)),
                forward_return_pct=float(meta.get("forward_return_pct")) if meta.get("forward_return_pct") is not None else None,
                mae_pct=float(meta.get("mae_pct")) if meta.get("mae_pct") is not None else None,
            )
        )

    # Append pending signals formed on the final bar so they appear as active markers and in the signals list
    for p in pending:
        sub_id = p.get("strategy_sub_id", "")
        strat_id = p.get("strategy_id", "mql5_candles")
        d_dir = p.get("direction", "BUY")
        s_idx = p.get("signal_bar_index", series.length - 1)
        ref_p = p.get("reference_line_price")
        sig_date = date_strs[s_idx] if s_idx < len(date_strs) else ""
        exec_price = float(ref_p if ref_p is not None else series.close[-1])
        signal_items.append(
            SignalItem(
                strategy_id=strat_id,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                group_id=_get_group_id(sub_id),
                direction=d_dir,
                signal_date=sig_date,
                execution_date=f"{sig_date} (Pendente)",
                signal_bar_index=s_idx,
                execution_bar_index=s_idx,
                execution_price=exec_price,
                reference_line_price=float(ref_p) if ref_p is not None else None,
                is_open=True,
                forward_return_pct=None,
                mae_pct=None,
            )
        )

    ref_line_items: List[ReferenceLineItem] = []
    for rl in ref_lines:
        s_date = date_strs[rl.start_bar_index] if rl.start_bar_index < len(date_strs) else ""
        e_date = date_strs[rl.end_bar_index] if rl.end_bar_index < len(date_strs) else ""
        ref_line_items.append(
            ReferenceLineItem(
                start_date=s_date,
                end_date=e_date,
                start_bar_index=rl.start_bar_index,
                end_bar_index=rl.end_bar_index,
                price_level=float(rl.price_level),
                status=str(rl.status),
                variation_id=str(rl.variation_id),
                line_type=str(rl.line_type),
                direction=str(rl.direction),
            )
        )

    summary_items: List[StrategySummaryItem] = []
    for s in summaries_raw:
        summary_items.append(
            StrategySummaryItem(
                strategy_sub_id=s.strategy_sub_id,
                strategy_label=get_friendly_label(s.strategy_sub_id),
                group_id=_get_group_id(s.strategy_sub_id),
                direction=s.direction,
                win_rate=float(s.win_rate),
                mean_forward_return=float(s.mean_forward_return),
                median_forward_return=float(s.median_forward_return),
                mean_mae=float(s.mean_mae),
                max_mae=float(s.max_mae),
                efficiency_score=float(s.efficiency_score),
                total_signals=int(s.total_signals),
                executed_buys=int(s.executed_buys),
                retest_fill_rate=float(s.retest_fill_rate) if s.retest_fill_rate is not None else None,
                open_signals_count=int(s.open_signals_count),
            )
        )

    # Timing status classifier
    current_price = float(series.close[-1])
    timing_model: Optional[TimingStatusModel] = None

    # Check pending or last active retest
    best_candidate_price: Optional[float] = None
    best_candidate_sub: str = ""
    best_candidate_dir: str = "BUY"
    if pending:
        p0 = pending[-1]
        best_candidate_sub = p0.get("strategy_sub_id", "")
        best_candidate_dir = p0.get("direction", "BUY")
        best_candidate_price = p0.get("reference_line_price") or current_price
    else:
        for sub, info in prop_state.items():
            if info.get("status") == "AGUARDANDO_RETESTE":
                best_candidate_sub = sub
                best_candidate_dir = info.get("direction", "BUY")
                best_candidate_price = info.get("active_line_price")
                break

    if best_candidate_price is None and signals:
        last_sig = signals[-1]
        best_candidate_sub = last_sig.strategy_sub_id
        best_candidate_dir = last_sig.direction
        best_candidate_price = last_sig.execution_price

    if best_candidate_price is not None:
        s_sum = next((s for s in summaries_raw if s.strategy_sub_id == best_candidate_sub), None)
        mean_ret = s_sum.mean_forward_return if s_sum else None
        ts_obj = classify_timing_status(
            current_price=current_price,
            recommended_price=best_candidate_price,
            strategy_sub_id=best_candidate_sub,
            strategy_label=get_friendly_label(best_candidate_sub),
            mean_forward_return=mean_ret,
            direction=best_candidate_dir,
        )
        timing_model = TimingStatusModel(
            status_category=ts_obj.status_category,
            status_label=ts_obj.status_label,
            distance_pct=float(ts_obj.distance_pct),
            recommended_price=float(ts_obj.recommended_price),
            current_price=float(ts_obj.current_price),
            advice_text=ts_obj.advice_text,
            direction=ts_obj.direction,
        )

    resp_data = AnalyzeResponse(
        ticker=ticker,
        interval=interval,
        period=period,
        current_price=current_price,
        candles=candles,
        signals=signal_items,
        reference_lines=ref_line_items,
        summaries=summary_items,
        current_state=sanitize_val(prop_state),
        timing_status=timing_model,
    )
    _set_cache(cache_key, resp_data)
    return resp_data


# ==========================================
# UNIVERSO EXPANDIDO DE ATIVOS (151 TICKERS)
# ==========================================
TICKERS_BR_ACOES = [
    '^BVSP', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA',
    'ABEV3.SA', 'WEGE3.SA', 'RENT3.SA', 'EGIE3.SA', 'PRIO3.SA',
    'BRSR6.SA', 'KLBN4.SA', 'CXSE3.SA', 'BMGB4.SA', 'BRKM5.SA',
    'TASA4.SA', 'PMAM3.SA', 'CMIG4.SA', 'CPFE3.SA', 'POMO4.SA',
    'TAEE11.SA', 'BBSE3.SA', 'SUZB3.SA', 'GGBR4.SA', 'CSNA3.SA',
    'USIM5.SA', 'VIVT3.SA', 'TIMS3.SA', 'HAPV3.SA', 'LREN3.SA',
]

TICKERS_FIIS = [
    'HGLG11.SA', 'KNRI11.SA', 'MXRF11.SA', 'VISC11.SA',
    'BTLG11.SA', 'HGRE11.SA', 'KNIP11.SA', 'HSML11.SA',
    'GGRC11.SA', 'RBRR11.SA', 'RBVA11.SA', 'SNCI11.SA',
    'TRXF11.SA', 'XPLG11.SA', 'CPTS11.SA', 'VGIR11.SA', 'VRTA11.SA',
    'VINO11.SA', 'RECR11.SA', 'HFOF11.SA', 'BTAL11.SA',
    'TGAR11.SA', 'ALZR11.SA',
]

TICKERS_USA = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'ADBE',
    'NFLX', 'CRM', 'KO', 'AMD', 'INTC', 'CSCO', 'ABBV', 'CVX', 'XOM',
    'PFE', 'IBM', 'MMM', 'VZ', 'T', 'BA', 'CAT', 'GE', 'GM', 'F', 'UBER',
    'LYFT', 'TM', 'SNAP', 'PINS', 'PYPL', 'SHOP', 'ZM', 'DOCU', 'CRWD', 'NET',
    'O', 'SPG', 'PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'DLR', 'WELL',
    'AVB', 'EQR', 'BXP', 'VTR', 'ARE', 'MAA', 'UDR', 'KIM', 'REG',
    'HST', 'FRT', 'NNN', 'WPC', 'GLPI',
]

TICKERS_COMMODITIES = [
    'GC=F', 'SI=F', 'CL=F', 'BZ=F', 'HG=F', 'NG=F',
    'ZC=F', 'ZS=F', 'ZW=F', 'KC=F', 'CT=F', 'SB=F', 'LE=F', 'HE=F',
]

TICKERS_FX = [
    'USDBRL=X', 'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X',
    'USDCAD=X', 'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X', 'EURCHF=X',
]

TICKERS_CRYPTO = [
    'BTC-USD', 'ETH-USD', 'SOL-USD',
]

TICKERS_BDRS = [
    'NVDC34.SA', 'AAPL34.SA', 'MSFT34.SA', 'GOGL34.SA', 'AMZO34.SA',
    'M1TA34.SA', 'TSLA34.SA', 'AVGO34.SA', 'TSMC34.SA', 'A1MD34.SA',
    'TMCO34.SA', 'BERK34.SA', 'JPMC34.SA', 'VISA34.SA', 'MSCD34.SA',
    'BOAC34.SA', 'GSGI34.SA', 'WALM34.SA', 'COCA34.SA', 'PEPB34.SA',
    'MCDC34.SA', 'DISB34.SA', 'NFLX34.SA', 'NIKE34.SA', 'COWC34.SA',
    'LILY34.SA', 'N1VO34.SA', 'JNJB34.SA', 'UNHH34.SA', 'PFIZ34.SA',
    'EXXO34.SA', 'CHVX34.SA', 'CATP34.SA', 'BOEI34.SA', 'IVVB11.SA',
    'BIVB39.SA', 'NASD11.SA', 'BNDA39.SA', 'ACWI11.SA', 'BACW39.SA', 'SPCX34.SA',
]

TICKERS_FEATURED = [
    ('^BVSP', 'Ações Brasil'),
    ('USDBRL=X', 'Forex'),
    ('GC=F', 'Commodities'),
    ('PETR4.SA', 'Ações Brasil'),
    ('VALE3.SA', 'Ações Brasil'),
    ('ITUB4.SA', 'Ações Brasil'),
    ('BBAS3.SA', 'Ações Brasil'),
    ('HGLG11.SA', 'FIIs Brasil'),
    ('MXRF11.SA', 'FIIs Brasil'),
    ('AAPL', 'Ações EUA'),
    ('NVDA', 'Ações EUA'),
    ('MSFT', 'Ações EUA'),
    ('TSLA', 'Ações EUA'),
    ('CL=F', 'Commodities'),
    ('GC=F', 'Commodities'),
    ('EURUSD=X', 'Forex'),
    ('BTC-USD', 'Criptomoedas'),
]

DEFAULT_SCANNER_BASKET = (
    [(t, "Ações Brasil") for t in TICKERS_BR_ACOES] +
    [(t, "FIIs Brasil") for t in TICKERS_FIIS] +
    [(t, "BDRs") for t in TICKERS_BDRS] +
    [(t, "Ações EUA") for t in TICKERS_USA] +
    [(t, "Commodities") for t in TICKERS_COMMODITIES] +
    [(t, "Forex") for t in TICKERS_FX] +
    [(t, "Criptomoedas") for t in TICKERS_CRYPTO]
)


def _normalize_category(cat: Optional[str]) -> str:
    if not cat:
        return "featured"
    c = cat.lower().strip()
    if "destaque" in c or "featured" in c:
        return "featured"
    if "fii" in c:
        return "fiis"
    if "brasil" in c or "br" in c or "acoes" in c or "ações" in c:
        return "acoes_br"
    if "eua" in c or "usa" in c:
        return "usa"
    if "commodit" in c:
        return "commodities"
    if "forex" in c or "fx" in c:
        return "forex"
    if "bdr" in c:
        return "bdrs"
    if "cripto" in c or "crypto" in c:
        return "crypto"
    if "all" in c or "todo" in c:
        return "all"
    return c


def _scan_single_ticker(ticker: str, category: str, interval: str = "1d", horizon_x: int = 60, refresh: bool = False) -> List[RadarItem]:
    items: List[RadarItem] = []
    try:
        series = DataLoader.load_asset_data(ticker=ticker, interval=interval, period="2y", use_cache=True)
    except Exception:
        return items

    if series.length < 20:
        return items

    last_ts = int(series.timestamps[-1]) if len(series.timestamps) > 0 else 0
    cache_key = f"radar:v6:{interval}:{horizon_x}:{ticker}:{last_ts}"

    if not refresh:
        cached_items = daily_cache.get(cache_key)
        if cached_items is not None:
            return [RadarItem(**it) for it in cached_items]

    current_price = float(series.close[-1])
    catalog = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)
    results = catalog.run_all(series)
    signals = results["signals"]
    prop_state = results["prop_current_state"]
    pending = results["pending_signals"]

    summaries = evaluate_all_strategies(
        series=series,
        signals=signals,
        horizon_bars=horizon_x,
        total_signals_by_sub_id=results["total_signals_by_sub_id"],
    )
    summary_map = {s.strategy_sub_id: s for s in summaries}

    # Bidirectional extraction: separate processing for BUY and SELL so both directions
    # are always detected and available for filtering.
    buy_items: List[RadarItem] = []
    sell_items: List[RadarItem] = []

    # 1. Pending signals formed on the final bar
    if pending:
        for p in pending:
            sub_id = p.get("strategy_sub_id", "")
            d_dir = p.get("direction", "BUY")
            p_exec = p.get("reference_line_price") or current_price
            s_stat = summary_map.get(sub_id)
            mean_ret = s_stat.mean_forward_return if s_stat else None
            timing = classify_timing_status(
                current_price=current_price,
                recommended_price=p_exec,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                mean_forward_return=mean_ret,
                direction=d_dir,
            )
            item = RadarItem(
                ticker=ticker,
                asset_name=strip_corporate_suffix(get_asset_name(ticker)),
                category=category,
                current_price=current_price,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                direction=d_dir,
                status_signal="Formado na Barra",
                timing_category=timing.status_category,
                timing_label=timing.status_label,
                distance_pct=float(timing.distance_pct),
                recommended_price=float(timing.recommended_price),
                historical_n=int(s_stat.executed_buys if s_stat else 0),
                historical_win_rate=float(s_stat.win_rate if s_stat else 0.0),
                advice_text=timing.advice_text,
            )
            if d_dir == "BUY":
                buy_items.append(item)
            else:
                sell_items.append(item)

    # 2. Retest active state
    for sub_id, st_info in prop_state.items():
        if st_info.get("status") == "AGUARDANDO_RETESTE":
            ref_line = st_info.get("active_line_price") or current_price
            d_dir = st_info.get("direction", "BUY")
            s_stat = summary_map.get(sub_id)
            mean_ret = s_stat.mean_forward_return if s_stat else None
            timing = classify_timing_status(
                current_price=current_price,
                recommended_price=ref_line,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                mean_forward_return=mean_ret,
                is_awaiting_retest=True,
                direction=d_dir,
            )
            item = RadarItem(
                ticker=ticker,
                asset_name=strip_corporate_suffix(get_asset_name(ticker)),
                category=category,
                current_price=current_price,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                direction=d_dir,
                status_signal=f"Reteste ({st_info.get('retest_bars_remaining')}b rest.)",
                timing_category=timing.status_category,
                timing_label=timing.status_label,
                distance_pct=float(timing.distance_pct),
                recommended_price=float(timing.recommended_price),
                historical_n=int(s_stat.executed_buys if s_stat else 0),
                historical_win_rate=float(s_stat.win_rate if s_stat else 0.0),
                advice_text=timing.advice_text,
            )
            if d_dir == "BUY":
                buy_items.append(item)
            else:
                sell_items.append(item)

    # 3. Fallback: if no active pending/retest for BUY, retrieve the most recent BUY signal
    if not buy_items and signals:
        buy_sigs = [s for s in signals if s.direction == "BUY"]
        if buy_sigs:
            sorted_buys = sorted(buy_sigs, key=lambda s: s.execution_bar_index)
            latest_buy = sorted_buys[-1]
            bars_ago = (series.length - 1) - latest_buy.execution_bar_index
            sub_id = latest_buy.strategy_sub_id
            s_stat = summary_map.get(sub_id)
            mean_ret = s_stat.mean_forward_return if s_stat else None
            timing = classify_timing_status(
                current_price=current_price,
                recommended_price=latest_buy.execution_price,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                mean_forward_return=mean_ret,
                direction="BUY",
            )
            status_text = "Executado Hoje" if bars_ago == 0 else f"Último Sinal ({bars_ago}b atrás)"
            buy_items.append(
                RadarItem(
                    ticker=ticker,
                    asset_name=strip_corporate_suffix(get_asset_name(ticker)),
                    category=category,
                    current_price=current_price,
                    strategy_sub_id=sub_id,
                    strategy_label=get_friendly_label(sub_id),
                    direction="BUY",
                    status_signal=status_text,
                    timing_category=timing.status_category,
                    timing_label=timing.status_label,
                    distance_pct=float(timing.distance_pct),
                    recommended_price=float(timing.recommended_price),
                    historical_n=int(s_stat.executed_buys if s_stat else 0),
                    historical_win_rate=float(s_stat.win_rate if s_stat else 0.0),
                    advice_text=timing.advice_text,
                )
            )

    # 4. Fallback: if no active pending/retest for SELL, retrieve the most recent SELL signal
    if not sell_items and signals:
        sell_sigs = [s for s in signals if s.direction == "SELL"]
        if sell_sigs:
            sorted_sells = sorted(sell_sigs, key=lambda s: s.execution_bar_index)
            latest_sell = sorted_sells[-1]
            bars_ago = (series.length - 1) - latest_sell.execution_bar_index
            sub_id = latest_sell.strategy_sub_id
            s_stat = summary_map.get(sub_id)
            mean_ret = s_stat.mean_forward_return if s_stat else None
            timing = classify_timing_status(
                current_price=current_price,
                recommended_price=latest_sell.execution_price,
                strategy_sub_id=sub_id,
                strategy_label=get_friendly_label(sub_id),
                mean_forward_return=mean_ret,
                direction="SELL",
            )
            status_text = "Executado Hoje" if bars_ago == 0 else f"Último Sinal ({bars_ago}b atrás)"
            sell_items.append(
                RadarItem(
                    ticker=ticker,
                    asset_name=strip_corporate_suffix(get_asset_name(ticker)),
                    category=category,
                    current_price=current_price,
                    strategy_sub_id=sub_id,
                    strategy_label=get_friendly_label(sub_id),
                    direction="SELL",
                    status_signal=status_text,
                    timing_category=timing.status_category,
                    timing_label=timing.status_label,
                    distance_pct=float(timing.distance_pct),
                    recommended_price=float(timing.recommended_price),
                    historical_n=int(s_stat.executed_buys if s_stat else 0),
                    historical_win_rate=float(s_stat.win_rate if s_stat else 0.0),
                    advice_text=timing.advice_text,
                )
            )

    items = buy_items + sell_items
    # Store ticker scan in daily cache
    try:
        daily_cache.set(cache_key, [item.model_dump() for item in items])
    except Exception:
        pass
    return items


@app.get("/api/radar", response_model=RadarPage)
def scan_radar(
    interval: str = Query("1d", description="Timeframe"),
    horizon_x: int = Query(60, description="Evaluation horizon"),
    category: Optional[str] = Query("featured", description="Category filter (featured, acoes_br, fiis, usa, commodities, fx, crypto, all)"),
    refresh: bool = Query(False, description="Force fresh download"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    direction: str = Query("BUY", description="Direction filter: BUY | SELL | BOTH"),
    strategies: str = Query("", description="CSV of strategy_sub_id filters. Empty means all."),
):
    norm_cat = _normalize_category(category)

    if norm_cat == "featured":
        basket = TICKERS_FEATURED
    elif norm_cat == "acoes_br":
        basket = [(t, "Ações Brasil") for t in TICKERS_BR_ACOES]
    elif norm_cat == "fiis":
        basket = [(t, "FIIs Brasil") for t in TICKERS_FIIS]
    elif norm_cat == "usa":
        basket = [(t, "Ações EUA") for t in TICKERS_USA]
    elif norm_cat == "commodities":
        basket = [(t, "Commodities") for t in TICKERS_COMMODITIES]
    elif norm_cat == "forex":
        basket = [(t, "Forex") for t in TICKERS_FX]
    elif norm_cat == "bdrs":
        basket = [(t, "BDRs") for t in TICKERS_BDRS]
    elif norm_cat == "crypto":
        basket = [(t, "Criptomoedas") for t in TICKERS_CRYPTO]
    else:
        basket = DEFAULT_SCANNER_BASKET

    total_assets = len(basket)
    total_pages = max(1, (total_assets + page_size - 1) // page_size)

    # If requested page is beyond total_pages, return empty page immediately
    if page > total_pages:
        return RadarPage(
            items=[],
            page=page,
            page_size=page_size,
            total_assets=total_assets,
            total_pages=total_pages,
            direction=direction,
            strategies=[s.strip() for s in strategies.split(",") if s.strip()],
            cached=False,
        )

    # Slice only the tickers belonging to this page (prevents computing entire universe!)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_assets)
    page_basket = basket[start_idx:end_idx]

    # Parse strategy filters
    strat_filter_list = [s.strip() for s in strategies.split(",") if s.strip()]
    strat_filter_set = set(strat_filter_list) if strat_filter_list else None

    # Scan the sliced basket in parallel
    page_opportunities: List[RadarItem] = []
    max_workers = min(12, max(1, len(page_basket)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_scan_single_ticker, ticker, cat, interval, horizon_x, refresh)
            for ticker, cat in page_basket
        ]
        for f in futures:
            page_opportunities.extend(f.result())

    # Direction and Strategy filtering
    filtered_items: List[RadarItem] = []
    for item in page_opportunities:
        if direction.upper() != "BOTH" and item.direction.upper() != direction.upper():
            continue
        if strat_filter_set and item.strategy_sub_id not in strat_filter_set:
            continue
        filtered_items.append(item)

    priority_order = {"IDEAL": 0, "EXTENDED": 1, "LATE": 2}
    filtered_items.sort(key=lambda x: (priority_order.get(x.timing_category, 3), x.distance_pct))

    return RadarPage(
        items=filtered_items,
        page=page,
        page_size=page_size,
        total_assets=total_assets,
        total_pages=total_pages,
        direction=direction,
        strategies=strat_filter_list,
        cached=(daily_cache.backend != "none"),
    )
    return all_opportunities


@app.get("/api/tickers")
def get_all_tickers():
    return {
        "featured": [t[0] for t in TICKERS_FEATURED],
        "acoes_br": TICKERS_BR_ACOES,
        "fiis": TICKERS_FIIS,
        "usa": TICKERS_USA,
        "commodities": TICKERS_COMMODITIES,
        "forex": TICKERS_FX,
        "crypto": TICKERS_CRYPTO,
        "bdrs": TICKERS_BDRS,
        "total": len(DEFAULT_SCANNER_BASKET),
        "all": [t[0] for t in DEFAULT_SCANNER_BASKET],
    }


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate_accumulation_endpoint(req: SimulateRequest):
    period_to_use = req.period
    if req.interval in ("5m", "15m", "30m") and req.period not in ("1d", "5d", "7d", "30d", "60d"):
        period_to_use = "60d"
    elif req.interval in ("60m", "1h", "2h", "4h", "12h") and req.period in ("5y", "max"):
        period_to_use = "730d"

    try:
        series = DataLoader.load_asset_data(ticker=req.ticker, interval=req.interval, period=period_to_use, use_cache=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro ao carregar dados para {req.ticker}: {str(exc)}")

    catalog = StrategyCatalog(
        lookback_n=req.lookback_n,
        retest_window_m=req.retest_m,
        tolerance_pct=req.retest_tol,
    )
    results = catalog.run_all(series)
    all_signals = results["signals"]

    def _matches_strat(sig: SignalRecord, target: str) -> bool:
        if not target or target == "ALL":
            return True
        c_target = target.replace("price_action_", "")
        c_sub = sig.strategy_sub_id.replace("price_action_", "")
        c_id = sig.strategy_id.replace("price_action_", "")
        return (
            sig.strategy_sub_id == target
            or sig.strategy_id == target
            or c_sub == c_target
            or c_id == c_target
        )

    has_specific_buy = bool(req.buy_strategy and req.buy_strategy != "ALL")
    has_specific_sell = bool(req.sell_strategy and req.sell_strategy != "ALL")

    if has_specific_buy or has_specific_sell:
        # If user explicitly chose specific strategy in the simulator, prioritize it over sidebar checkboxes
        signals = all_signals
        if has_specific_buy:
            signals = [s for s in signals if s.direction != "BUY" or _matches_strat(s, req.buy_strategy)]
        if has_specific_sell:
            signals = [s for s in signals if s.direction != "SELL" or _matches_strat(s, req.sell_strategy)]
    elif req.selected_strategies:
        selected_set = set(req.selected_strategies)
        signals = [
            s for s in all_signals
            if s.strategy_sub_id in selected_set or s.strategy_id in selected_set or any(_matches_strat(s, x) for x in selected_set)
        ]
    else:
        signals = all_signals

    # Mode 1: Cycle Trade (Compra em Fundo -> Vende no Próximo Topo)
    if req.simulation_mode == "cycle_trade":
        # If user only selected BUY strategies, auto-pair with corresponding SELL counterparts if available
        if req.selected_strategies:
            selected_set = set(req.selected_strategies)
            has_buys = any(s.direction == "BUY" for s in signals)
            has_sells = any(s.direction == "SELL" for s in signals)
            if has_buys and not has_sells:
                auto_sell_ids = set()
                for b_id in selected_set:
                    cand = f"sell_{b_id}"
                    if cand in STRATEGY_LABELS_PT:
                        auto_sell_ids.add(cand)
                    elif b_id.startswith("candle_"):
                        auto_sell_ids.add(b_id.replace("candle_", "sell_candle_"))
                if auto_sell_ids:
                    signals = [s for s in all_signals if s.strategy_sub_id in (selected_set | auto_sell_ids)]

        init_cap = req.initial_capital if req.initial_capital > 0 else req.contribution_amount
        contrib_amount = req.contribution_amount if req.contribution_amount is not None else init_cap
        cycle_res = simulate_cycle_trade(
            series=series,
            signals=signals,
            initial_capital=init_cap,
            contribution_amount=contrib_amount,
            start_date=req.start_date,
            end_date=req.end_date,
            strategy_labels_map=STRATEGY_LABELS_PT,
            cycle_entry_mode=req.cycle_entry_mode,
        )

        curve_points: List[AccumulationPoint] = []
        for i, ts in enumerate(cycle_res.timeline_timestamps):
            d_str = pd.to_datetime(ts).strftime("%Y-%m-%d")
            c_price = float(series.close[min(i, series.length - 1)])
            curve_points.append(
                AccumulationPoint(
                    date=d_str,
                    total_invested=float(cycle_res.timeline_invested[i]),
                    portfolio_value=float(cycle_res.timeline_equity[i]),
                    shares=0.0,
                    close_price=c_price,
                    cash_inflow=0.0,
                )
            )

        trades_list = []
        for t in cycle_res.trades:
            sub_entries_list = []
            if t.buy_entries:
                for be in t.buy_entries:
                    sub_entries_list.append({
                        "entry_id": be.entry_id,
                        "date": be.date,
                        "bar_index": be.bar_index,
                        "price": be.price,
                        "shares": be.shares,
                        "capital": be.capital,
                        "strategy_sub_id": be.strategy_sub_id,
                        "strategy_label": be.strategy_label,
                    })

            trades_list.append({
                "trade_id": t.trade_id,
                "buy_strategy": t.buy_strategy_label,
                "buy_sub_id": t.buy_strategy_sub_id,
                "buy_date": t.buy_date,
                "buy_price": t.buy_price,
                "sell_strategy": t.sell_strategy_label or "-",
                "sell_sub_id": t.sell_strategy_sub_id or "-",
                "sell_date": t.sell_date or "Em Aberto",
                "sell_price": t.sell_price if t.sell_price is not None else 0.0,
                "return_pct": t.return_pct,
                "profit_loss": t.profit_loss,
                "duration_bars": t.duration_bars,
                "shares": t.shares,
                "entry_capital": t.entry_capital,
                "exit_capital": t.exit_capital,
                "status": t.status,
                "num_entries": t.num_entries,
                "average_buy_price": t.average_buy_price,
                "total_invested": t.total_invested,
                "total_shares": t.total_shares,
                "buy_entries": sub_entries_list,
            })

        alpha_vs_bnh = cycle_res.return_on_capital_pct - cycle_res.buy_and_hold_return_pct
        metrics_obj = {
            "simulation_mode": "cycle_trade",
            "total_invested": cycle_res.total_invested,
            "final_portfolio_value": cycle_res.final_equity,
            "total_profit_loss": cycle_res.net_profit,
            "total_return_pct": cycle_res.return_on_capital_pct,
            "xirr_annualized_pct": None,
            "max_drawdown_pct": cycle_res.max_drawdown_pct,
            "total_trades_count": cycle_res.total_trades_count,
            "shares_accumulated": 0.0,
            "average_cost_price": 0.0,
            "current_market_price": cycle_res.current_market_price,
            "dca_regular_final_value": 0.0,
            "alpha_vs_dca_pct": round(alpha_vs_bnh, 2),
            "winning_trades_count": cycle_res.winning_trades_count,
            "losing_trades_count": cycle_res.losing_trades_count,
            "win_rate_pct": cycle_res.win_rate_pct,
            "avg_trade_return_pct": cycle_res.avg_trade_return_pct,
            "avg_trade_bars": cycle_res.avg_trade_bars,
            "buy_and_hold_return_pct": cycle_res.buy_and_hold_return_pct,
            "profit_factor": cycle_res.profit_factor,
            "avg_entries_per_cycle": cycle_res.avg_entries_per_cycle,
        }

        return SimulateResponse(
            ticker=req.ticker,
            period=period_to_use,
            metrics=metrics_obj,
            curve=curve_points,
            trades=trades_list,
        )

    # Mode 2: Acumulação Contínua de Cotas (DCA nos Fundos)
    sim_dict = simulate_accumulation(
        series=series,
        signals=signals,
        contribution_amount=req.contribution_amount,
        start_date=req.start_date,
        end_date=req.end_date,
    )

    # Aggregate simulation across all selected strategies (or sum them)
    # Build curve and trades
    total_invested = sum(res.total_invested for res in sim_dict.values())
    final_equity = sum(res.current_equity for res in sim_dict.values())
    total_shares = sum(res.total_shares for res in sim_dict.values())
    total_contributions = sum(res.num_contributions for res in sim_dict.values())
    net_profit = final_equity - total_invested
    ret_pct = ((final_equity / total_invested) - 1.0) * 100.0 if total_invested > 0 else 0.0
    avg_price = (total_invested / total_shares) if total_shares > 0 else 0.0

    # Build timeline curve
    curve_points = []
    if sim_dict:
        # Use timeline of first strategy or combined
        first_res = next(iter(sim_dict.values()))
        # Combine timeline invested and equity across all
        comb_invested = np.zeros(len(first_res.timeline_timestamps), dtype=np.float64)
        comb_equity = np.zeros(len(first_res.timeline_timestamps), dtype=np.float64)
        for s_res in sim_dict.values():
            comb_invested += s_res.timeline_invested
            comb_equity += s_res.timeline_equity

        for i, ts in enumerate(first_res.timeline_timestamps):
            d_str = pd.to_datetime(ts).strftime("%Y-%m-%d")
            c_price = float(series.close[min(i, series.length - 1)])
            curve_points.append(
                AccumulationPoint(
                    date=d_str,
                    total_invested=float(comb_invested[i]),
                    portfolio_value=float(comb_equity[i]),
                    shares=float(comb_equity[i] / c_price) if c_price > 0 else 0.0,
                    close_price=c_price,
                    cash_inflow=req.contribution_amount if i > 0 and comb_invested[i] > comb_invested[i - 1] else 0.0,
                )
            )

    trades_list = []
    for sig in signals:
        trades_list.append({
            "date": pd.to_datetime(series.timestamps[sig.execution_bar_index]).strftime("%Y-%m-%d") if sig.execution_bar_index < series.length else "",
            "strategy": sig.strategy_sub_id,
            "direction": sig.direction,
            "execution_price": float(sig.execution_price),
            "amount_invested": req.contribution_amount,
            "shares": float(req.contribution_amount / sig.execution_price) if sig.execution_price > 0 else 0.0,
        })

    metrics_obj = {
        "simulation_mode": "accumulation",
        "total_invested": round(total_invested, 2),
        "final_portfolio_value": round(final_equity, 2),
        "total_profit_loss": round(net_profit, 2),
        "total_return_pct": round(ret_pct, 2),
        "xirr_annualized_pct": None,
        "max_drawdown_pct": 0.0,
        "total_trades_count": total_contributions,
        "shares_accumulated": round(total_shares, 4),
        "average_cost_price": round(avg_price, 2),
        "current_market_price": round(float(series.close[-1]), 2),
        "dca_regular_final_value": round(final_equity, 2),
        "alpha_vs_dca_pct": 0.0,
    }

    return SimulateResponse(
        ticker=req.ticker,
        period=period_to_use,
        metrics=metrics_obj,
        curve=curve_points,
        trades=trades_list,
    )


@app.post("/api/simulate/optimize", response_model=OptimizeCombinationsResponse)
def optimize_combinations_endpoint(req: OptimizeCombinationsRequest):
    period_to_use = req.period
    if req.interval in ("5m", "15m", "30m") and req.period not in ("1d", "5d", "7d", "30d", "60d"):
        period_to_use = "60d"
    elif req.interval in ("60m", "1h", "2h", "4h", "12h") and req.period in ("5y", "max"):
        period_to_use = "730d"

    try:
        series = DataLoader.load_asset_data(ticker=req.ticker, interval=req.interval, period=period_to_use, use_cache=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro ao carregar dados para {req.ticker}: {str(exc)}")

    catalog = StrategyCatalog(
        lookback_n=req.lookback_n,
        retest_window_m=req.retest_m,
        tolerance_pct=req.retest_tol,
    )
    results = catalog.run_all(series)
    all_signals = results["signals"]

    is_dca = (req.simulation_mode == "accumulation")

    if is_dca:
        contrib = req.contribution_amount if req.contribution_amount > 0 else req.initial_capital
        champion, top_combos = optimize_dca_strategies(
            series=series,
            signals=all_signals,
            contribution_amount=contrib,
            start_date=req.start_date,
            end_date=req.end_date,
            strategy_labels_map=STRATEGY_LABELS_PT,
            top_n=15,
        )
    else:
        champion, top_combos = optimize_strategy_pairs(
            series=series,
            signals=all_signals,
            initial_capital=req.initial_capital,
            min_trades=req.min_trades,
            start_date=req.start_date,
            end_date=req.end_date,
            strategy_labels_map=STRATEGY_LABELS_PT,
            top_n=15,
            cycle_entry_mode=req.cycle_entry_mode,
        )

    champ_model = None
    if champion:
        champ_model = StrategyPairRankItemModel(
            rank=champion.rank,
            buy_sub_id=champion.buy_sub_id,
            buy_label=champion.buy_label,
            sell_sub_id=champion.sell_sub_id,
            sell_label=champion.sell_label,
            simulation_mode=champion.simulation_mode,
            closed_trades=champion.closed_trades,
            winning_trades=champion.winning_trades,
            win_rate_pct=champion.win_rate_pct,
            total_return_pct=champion.total_return_pct,
            net_profit=champion.net_profit,
            max_drawdown_pct=champion.max_drawdown_pct,
            has_open_trade=champion.has_open_trade,
            final_equity=champion.final_equity,
            cycle_entry_mode=champion.cycle_entry_mode,
            total_invested=champion.total_invested,
            average_buy_price=champion.average_buy_price,
            total_shares=champion.total_shares,
            total_contributions=champion.total_contributions,
        )

    top_models = [
        StrategyPairRankItemModel(
            rank=c.rank,
            buy_sub_id=c.buy_sub_id,
            buy_label=c.buy_label,
            sell_sub_id=c.sell_sub_id,
            sell_label=c.sell_label,
            simulation_mode=c.simulation_mode,
            closed_trades=c.closed_trades,
            winning_trades=c.winning_trades,
            win_rate_pct=c.win_rate_pct,
            total_return_pct=c.total_return_pct,
            net_profit=c.net_profit,
            max_drawdown_pct=c.max_drawdown_pct,
            has_open_trade=c.has_open_trade,
            final_equity=c.final_equity,
            cycle_entry_mode=c.cycle_entry_mode,
            total_invested=c.total_invested,
            average_buy_price=c.average_buy_price,
            total_shares=c.total_shares,
            total_contributions=c.total_contributions,
        )
        for c in top_combos
    ]

    return OptimizeCombinationsResponse(
        ticker=req.ticker,
        period=period_to_use,
        simulation_mode=req.simulation_mode,
        initial_capital=req.initial_capital,
        total_combinations_tested=len(top_combos),
        champion=champ_model,
        top_combinations=top_models,
    )


def _resolve_portfolio_universe_tickers(
    universe_category: str = "featured",
    custom_tickers: Optional[List[str]] = None,
    holdings_tickers: Optional[List[str]] = None,
    max_assets: int = 24,
) -> List[Tuple[str, str]]:
    """
    Resolves a deduplicated list of (ticker, category) pairs for portfolio analysis/simulation.
    Always includes any tickers currently held by the user so they are evaluated for SELL/REBALANCE/ROTATE.
    """
    norm_cat = _normalize_category(universe_category)
    if norm_cat == "custom" and custom_tickers:
        raw_basket = [(t.strip().upper(), "Personalizado") for t in custom_tickers if t and t.strip()]
    elif norm_cat == "featured":
        raw_basket = list(TICKERS_FEATURED)
    elif norm_cat == "acoes_br":
        raw_basket = [(t, "Ações Brasil") for t in TICKERS_BR_ACOES if t != "^BVSP"]
    elif norm_cat == "fiis":
        raw_basket = [(t, "FIIs Brasil") for t in TICKERS_FIIS]
    elif norm_cat == "usa":
        raw_basket = [(t, "Ações EUA") for t in TICKERS_USA[:max_assets]]
    elif norm_cat == "commodities":
        raw_basket = [(t, "Commodities") for t in TICKERS_COMMODITIES]
    elif norm_cat == "forex":
        raw_basket = [(t, "Forex") for t in TICKERS_FX]
    elif norm_cat == "bdrs":
        raw_basket = [(t, "BDRs") for t in TICKERS_BDRS[:max_assets]]
    elif norm_cat == "crypto":
        raw_basket = [(t, "Criptomoedas") for t in TICKERS_CRYPTO]
    elif custom_tickers:
        raw_basket = [(t.strip().upper(), "Personalizado") for t in custom_tickers if t and t.strip()]
    else:
        raw_basket = list(TICKERS_FEATURED)

    seen = set()
    final_basket: List[Tuple[str, str]] = []

    for ht in (holdings_tickers or []):
        t_clean = (ht or "").strip().upper()
        if t_clean and t_clean not in seen:
            seen.add(t_clean)
            cat_label = "Carteira Atual"
            for bt, bcat in DEFAULT_SCANNER_BASKET:
                if bt.upper() == t_clean:
                    cat_label = bcat
                    break
            final_basket.append((t_clean, cat_label))

    for t_cand, c_label in raw_basket:
        t_clean = (t_cand or "").strip().upper()
        if not t_clean or t_clean == "^BVSP" or t_clean in seen:
            continue
        seen.add(t_clean)
        final_basket.append((t_clean, c_label))
        if len(final_basket) >= max_assets + len(holdings_tickers or []):
            break

    return final_basket


def _load_and_profile_single_asset(
    ticker: str,
    category: str,
    interval: str = "1d",
    period: str = "2y",
) -> Optional[Dict[str, Any]]:
    """
    Loads OHLCVSeries, runs StrategyCatalog, and computes AssetOpportunityProfile for one ticker.
    Uses in-memory cache to accelerate repeated portfolio advisories and simulations.
    """
    period_to_use = period
    if interval in ("5m", "15m", "30m") and period not in ("1d", "5d", "7d", "30d", "60d"):
        period_to_use = "60d"
    elif interval in ("60m", "1h", "2h", "4h", "12h") and period in ("5y", "max"):
        period_to_use = "730d"

    cache_key = f"portfolio_asset:{ticker}:{interval}:{period_to_use}"
    cached = _get_cache(cache_key)
    if cached is not None:
        return cached

    try:
        series = DataLoader.load_asset_data(ticker=ticker, interval=interval, period=period_to_use, use_cache=True)
    except Exception:
        return None

    if series is None or series.length < 15:
        return None

    catalog = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)
    res = catalog.run_all(series)
    signals = res["signals"]
    prop_state = res["prop_current_state"]
    pending = res["pending_signals"]

    asset_name = strip_corporate_suffix(get_asset_name(ticker))
    profile = compute_asset_opportunity_profile(
        ticker=ticker,
        series=series,
        signals=signals,
        prop_state=prop_state,
        pending_signals=pending,
        asset_name=asset_name,
        category=category,
        strategy_labels_map=STRATEGY_LABELS_PT,
    )

    bundle = {
        "ticker": ticker.upper(),
        "asset_name": asset_name,
        "category": category,
        "series": series,
        "signals": signals,
        "prop_state": prop_state,
        "pending_signals": pending,
        "profile": profile,
    }
    _set_cache(cache_key, bundle)
    return bundle


@app.post("/api/portfolio/advise", response_model=PortfolioAdviseResponse)
def advise_portfolio_endpoint(req: PortfolioAdviseRequest):
    holdings_tickers = [h.ticker for h in req.holdings if h.ticker]
    basket = _resolve_portfolio_universe_tickers(
        universe_category=req.universe_category,
        custom_tickers=req.custom_tickers,
        holdings_tickers=holdings_tickers,
        max_assets=24,
    )

    bundles: List[Dict[str, Any]] = []
    max_workers = min(10, max(1, len(basket)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_load_and_profile_single_asset, t, cat, req.interval, req.period)
            for t, cat in basket
        ]
        for f in futures:
            res = f.result()
            if res is not None:
                bundles.append(res)

    profiles = [b["profile"] for b in bundles]
    holdings_dicts = [
        {"ticker": h.ticker, "shares": h.shares, "average_buy_price": h.average_buy_price}
        for h in req.holdings
    ]

    advise_res = advise_portfolio_rebalance(
        available_cash=req.available_cash,
        holdings_input=holdings_dicts,
        opportunity_profiles=profiles,
        max_weight_pct=req.max_weight_pct,
        rebalance_band_pct=req.rebalance_band_pct,
        min_rotation_score_delta=req.min_rotation_score_delta,
    )

    holdings_models = [
        PortfolioHoldingEvaluatedModel(
            ticker=h.ticker,
            asset_name=h.asset_name,
            shares=h.shares,
            average_buy_price=h.average_buy_price,
            current_price=h.current_price,
            market_value=h.market_value,
            invested_value=h.invested_value,
            unrealized_pnl_value=h.unrealized_pnl_value,
            unrealized_pnl_pct=h.unrealized_pnl_pct,
            current_weight_pct=h.current_weight_pct,
            entry_bar_index=h.entry_bar_index,
        )
        for h in advise_res["holdings_evaluated"]
    ]

    rec_models = [
        PortfolioActionRecommendationModel(
            ticker=r.ticker,
            asset_name=r.asset_name,
            action_type=r.action_type,
            action_label=r.action_label,
            reason_text=r.reason_text,
            strategy_sub_id=r.strategy_sub_id,
            strategy_label=r.strategy_label,
            potential_score=r.potential_score,
            timing_category=r.timing_category,
            current_price=r.current_price,
            reference_price=r.reference_price,
            current_shares=r.current_shares,
            recommended_shares_delta=r.recommended_shares_delta,
            target_shares=r.target_shares,
            order_value=r.order_value,
            current_weight_pct=r.current_weight_pct,
            target_weight_pct=r.target_weight_pct,
        )
        for r in advise_res["recommendations"]
    ]

    ranking_models = [
        AssetOpportunityProfileModel(
            ticker=p.ticker,
            asset_name=p.asset_name,
            category=p.category,
            current_price=p.current_price,
            champion_buy_id=p.champion_buy_id,
            champion_buy_label=p.champion_buy_label,
            champion_sell_id=p.champion_sell_id,
            champion_sell_label=p.champion_sell_label,
            win_rate_pct=p.win_rate_pct,
            historical_return_pct=p.historical_return_pct,
            max_drawdown_pct=p.max_drawdown_pct,
            closed_trades=p.closed_trades,
            active_direction=p.active_direction,
            timing_category=p.timing_category,
            timing_label=p.timing_label,
            distance_pct=p.distance_pct,
            recommended_price=p.recommended_price,
            potential_score=p.potential_score,
        )
        for p in advise_res["opportunity_ranking"]
    ]

    return PortfolioAdviseResponse(
        universe_category=req.universe_category,
        interval=req.interval,
        period=req.period,
        current_cash=advise_res["current_cash"],
        current_holdings_value=advise_res["current_holdings_value"],
        total_portfolio_equity=advise_res["total_portfolio_equity"],
        projected_cash_after=advise_res["projected_cash_after"],
        projected_invested_after=advise_res["projected_invested_after"],
        max_weight_pct=advise_res["max_weight_pct"],
        holdings_evaluated=holdings_models,
        recommendations=rec_models,
        opportunity_ranking=ranking_models,
    )


@app.post("/api/portfolio/simulate", response_model=PortfolioSimulateResponse)
def simulate_portfolio_endpoint(req: PortfolioSimulateRequest):
    basket = _resolve_portfolio_universe_tickers(
        universe_category=req.universe_category,
        custom_tickers=req.custom_tickers,
        holdings_tickers=[],
        max_assets=24,
    )

    bundles: List[Dict[str, Any]] = []
    max_workers = min(10, max(1, len(basket)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_load_and_profile_single_asset, t, cat, req.interval, req.period)
            for t, cat in basket
        ]
        for f in futures:
            res = f.result()
            if res is not None:
                bundles.append(res)

    sim_res = simulate_portfolio_multi_asset(
        asset_bundles=bundles,
        initial_capital=req.initial_capital,
        max_weight_pct=req.max_weight_pct,
        rebalance_band_pct=req.rebalance_band_pct,
        min_rotation_score_delta=req.min_rotation_score_delta,
        start_date=req.start_date,
        end_date=req.end_date,
        strategy_labels_map=STRATEGY_LABELS_PT,
    )

    metrics_model = PortfolioSimulationMetricsModel(
        initial_capital=sim_res.initial_capital,
        final_equity=sim_res.final_equity,
        final_cash=sim_res.final_cash,
        final_invested_value=sim_res.final_invested_value,
        net_profit=sim_res.net_profit,
        total_return_pct=sim_res.total_return_pct,
        benchmark_return_pct=sim_res.benchmark_return_pct,
        alpha_vs_benchmark_pct=sim_res.alpha_vs_benchmark_pct,
        max_drawdown_pct=sim_res.max_drawdown_pct,
        win_rate_pct=sim_res.win_rate_pct,
        profit_factor=sim_res.profit_factor,
        total_events_count=sim_res.total_events_count,
        closed_exits_count=sim_res.closed_exits_count,
        winning_exits_count=sim_res.winning_exits_count,
        losing_exits_count=sim_res.losing_exits_count,
        rebalance_rotations_count=sim_res.rebalance_rotations_count,
    )

    final_holdings_models = [
        PortfolioHoldingEvaluatedModel(
            ticker=h.ticker,
            asset_name=h.asset_name,
            shares=h.shares,
            average_buy_price=h.average_buy_price,
            current_price=h.current_price,
            market_value=h.market_value,
            invested_value=h.invested_value,
            unrealized_pnl_value=h.unrealized_pnl_value,
            unrealized_pnl_pct=h.unrealized_pnl_pct,
            current_weight_pct=h.current_weight_pct,
            entry_bar_index=h.entry_bar_index,
        )
        for h in sim_res.current_holdings
    ]

    curve_models = [
        PortfolioCurvePointModel(
            date=c.date,
            portfolio_equity=c.portfolio_equity,
            cash_balance=c.cash_balance,
            invested_equity=c.invested_equity,
            benchmark_equity=c.benchmark_equity,
            drawdown_pct=c.drawdown_pct,
        )
        for c in sim_res.curve
    ]

    ledger_models = [
        PortfolioLedgerEventModel(
            event_id=ev.event_id,
            date=ev.date,
            ticker=ev.ticker,
            asset_name=ev.asset_name,
            event_type=ev.event_type,
            event_label=ev.event_label,
            strategy_sub_id=ev.strategy_sub_id,
            strategy_label=ev.strategy_label,
            potential_score=ev.potential_score,
            execution_price=ev.execution_price,
            shares_delta=ev.shares_delta,
            trade_value=ev.trade_value,
            realized_pnl_value=ev.realized_pnl_value,
            realized_pnl_pct=ev.realized_pnl_pct,
            weight_before_pct=ev.weight_before_pct,
            weight_after_pct=ev.weight_after_pct,
            cash_after=ev.cash_after,
            portfolio_equity_after=ev.portfolio_equity_after,
        )
        for ev in sim_res.ledger_events
    ]

    ranking_models = [
        AssetOpportunityProfileModel(
            ticker=p.ticker,
            asset_name=p.asset_name,
            category=p.category,
            current_price=p.current_price,
            champion_buy_id=p.champion_buy_id,
            champion_buy_label=p.champion_buy_label,
            champion_sell_id=p.champion_sell_id,
            champion_sell_label=p.champion_sell_label,
            win_rate_pct=p.win_rate_pct,
            historical_return_pct=p.historical_return_pct,
            max_drawdown_pct=p.max_drawdown_pct,
            closed_trades=p.closed_trades,
            active_direction=p.active_direction,
            timing_category=p.timing_category,
            timing_label=p.timing_label,
            distance_pct=p.distance_pct,
            recommended_price=p.recommended_price,
            potential_score=p.potential_score,
        )
        for p in sim_res.opportunity_profiles
    ]

    return PortfolioSimulateResponse(
        universe_category=req.universe_category,
        interval=req.interval,
        period=req.period,
        metrics=metrics_model,
        final_holdings=final_holdings_models,
        curve=curve_models,
        ledger_events=ledger_models,
        opportunity_ranking=ranking_models,
    )


# Mount Web Terminal Static Assets at Root
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
@app.post("/api/portfolio/quotes", response_model=PortfolioQuotesResponse)
def get_portfolio_quotes_endpoint(req: PortfolioQuotesRequest):
    results: Dict[str, QuoteItem] = {}
    if not req.tickers:
        return PortfolioQuotesResponse(quotes=results)

    # Normalize tickers
    resolved_tickers = []
    for t in req.tickers:
        clean = t.strip().upper()
        if not clean:
            continue
        # If Brazilian equity, FII, or BDR without suffix, append .SA
        has_sa = clean.endswith('.SA')
        is_b3 = any(clean.endswith(sfx) for sfx in ('3', '4', '5', '6', '11', '34', '33', '35', '39'))
        if is_b3 and not has_sa:
            resolved = f"{clean}.SA"
        else:
            resolved = clean
        resolved_tickers.append((t, resolved))

    def _fetch_single_quote(original_ticker: str, yf_ticker: str) -> Optional[QuoteItem]:
        cache_key = f"quote_{yf_ticker}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            series = DataLoader.load_asset_data(ticker=yf_ticker, period="5d", interval="1d", use_cache=True)
            if series is not None and series.close is not None and len(series.close) >= 1:
                close_price = float(series.close[-1])
                prev_price = float(series.close[-2]) if len(series.close) >= 2 else close_price
                chg = ((close_price - prev_price) / prev_price * 100.0) if prev_price > 0 else 0.0
                time_str = str(series.timestamps[-1]) if (series.timestamps is not None and len(series.timestamps) > 0) else None
                item = QuoteItem(
                    ticker=original_ticker,
                    price=round(close_price, 4),
                    change_pct=round(chg, 2),
                    time=time_str,
                )
                _set_cache(cache_key, item)
                return item
        except Exception as err:
            logger.warning(f"Error fetching quote for {yf_ticker}: {err}")
        return None

    with ThreadPoolExecutor(max_workers=min(10, max(1, len(resolved_tickers)))) as executor:
        futures = {executor.submit(_fetch_single_quote, orig, yf): orig for orig, yf in resolved_tickers}
        for f in futures:
            res = f.result()
            if res:
                results[res.ticker.upper()] = res

    return PortfolioQuotesResponse(quotes=results)


# 10. Endpoints for B3 Official Spreadsheet Integration

@app.get("/api/b3/sync-local", response_model=B3ParseResult)
def b3_sync_local():
    """
    Scans the local B3/ directory for the most recent official movement spreadsheet (.xlsx or .csv)
    and returns parsed holdings, Preço Médio contábil and passive income.
    """
    b3_dir = Path("B3")
    if not b3_dir.exists():
        # Also check relative to workspace
        b3_dir = Path(__file__).resolve().parent.parent.parent / "B3"
    
    if not b3_dir.exists():
        raise HTTPException(status_code=404, detail="Diretório B3/ não encontrado.")

    # Find .xlsx or .csv files in B3/
    files = list(b3_dir.glob("*.xlsx")) + list(b3_dir.glob("*.csv"))
    if not files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo de movimentação (.xlsx ou .csv) encontrado na pasta B3/.")

    # Select the most recent file by modification time
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    try:
        result = parse_b3_file(latest_file, filename=latest_file.name)
        return result
    except Exception as err:
        logger.error(f"Erro ao processar planilha B3 {latest_file}: {err}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar planilha B3: {str(err)}")


@app.post("/api/b3/parse", response_model=B3ParseResult)
async def b3_parse_uploaded_file(file: UploadFile = File(...)):
    """
    Parses an uploaded B3 spreadsheet (.xlsx or .csv) and computes custody holdings and income.
    """
    try:
        content = await file.read()
        filename = file.filename or "movimentacao.xlsx"
        result = parse_b3_file(content, filename=filename)
        return result
    except Exception as err:
        logger.error(f"Erro ao processar arquivo B3 enviado {file.filename}: {err}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar planilha B3: {str(err)}")


if os.path.exists(static_dir):

    app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")



