"""
Statistical Evaluator Engine (Zero Look-Ahead Bias leak to Strategy Engines).
This module is the ONLY component authorized to inspect future bars [t_exec, t_exec + X]
exclusively to compute Holder/Seller Win Rate, Forward Returns, Maximum Adverse Excursion (MAE),
Retest Fill Rate, and Composite Efficiency Score for both BUY and SELL directions.

- For direction="BUY":
  * is_win = future_close > p_exec
  * forward_return = ((future_close / p_exec) - 1.0) * 100
  * mae = min(0.0, ((min_low / p_exec) - 1.0) * 100)

- For direction="SELL":
  * is_win = future_close < p_exec
  * forward_return = ((p_exec - future_close) / p_exec) * 100
  * mae = -max(0.0, ((max_high - p_exec) / p_exec) * 100)  (represented as negative to reflect drawdown/calor)

Signals where t_exec + X >= len(close) are rigorously flagged as `is_open=True`
and excluded from closed historical performance metrics to prevent survivorship/truncation distortion.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from ..strategies.base import OHLCVSeries, SignalRecord, StrategyStatsSummary


def evaluate_strategy_performance(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    horizon_bars: int = 60,
    total_signals_override: Optional[int] = None,
    strategy_id: Optional[str] = None,
    strategy_sub_id: Optional[str] = None,
    direction: Optional[str] = None,
) -> StrategyStatsSummary:
    """
    Evaluates prospective performance over `horizon_bars` (X) for a list of SignalRecords
    belonging to a strategy or sub-variation, respecting BUY and SELL semantics.
    """
    if horizon_bars < 1:
        raise ValueError("horizon_bars (X) must be >= 1")

    n_bars = series.length
    inferred_strat_id = strategy_id or (signals[0].strategy_id if signals else "unknown")
    inferred_sub_id = strategy_sub_id or (signals[0].strategy_sub_id if signals else "unknown")
    inferred_direction = direction or (signals[0].direction if signals else "BUY")

    executed_signals = len(signals)

    if total_signals_override is not None:
        total_signals = max(int(total_signals_override), executed_signals)
    elif signals and signals[0].metadata and "total_variant_signals" in signals[0].metadata:
        total_signals = max(int(signals[0].metadata["total_variant_signals"]), executed_signals)
    else:
        total_signals = executed_signals

    if total_signals > 0:
        retest_fill_rate = (executed_signals / float(total_signals)) * 100.0
    else:
        retest_fill_rate = 0.0

    closed_returns: List[float] = []
    closed_maes: List[float] = []
    closed_wins: List[bool] = []
    open_signals_count = 0

    close_arr = series.close
    low_arr = series.low
    high_arr = series.high

    for sig in signals:
        t_exec = int(sig.execution_bar_index)
        p_exec = float(sig.execution_price)
        sig_dir = sig.direction if hasattr(sig, "direction") and sig.direction else inferred_direction
        is_buy = (sig_dir == "BUY")

        if t_exec < 0 or t_exec >= n_bars or p_exec <= 0.0:
            continue

        # Check if X future bars are available in the historical series
        if t_exec + horizon_bars >= n_bars:
            open_signals_count += 1
            if sig.metadata is not None:
                sig.metadata["is_open"] = True
                sig.metadata["is_win"] = None
                sig.metadata["forward_return_pct"] = None
                if is_buy:
                    curr_ret = ((float(close_arr[-1]) / p_exec) - 1.0) * 100.0
                    min_low_open = float(np.min(low_arr[t_exec:n_bars]))
                    mae_open = min(0.0, ((min_low_open / p_exec) - 1.0) * 100.0)
                else:
                    curr_ret = ((p_exec - float(close_arr[-1])) / p_exec) * 100.0
                    max_high_open = float(np.max(high_arr[t_exec:n_bars]))
                    mae_open = -max(0.0, ((max_high_open - p_exec) / p_exec) * 100.0)

                sig.metadata["unrealized_return_pct"] = curr_ret
                sig.metadata["mae_pct"] = mae_open
            continue

        # Closed signal: full X-bar horizon is available
        future_close = float(close_arr[t_exec + horizon_bars])
        if is_buy:
            fwd_ret_pct = ((future_close / p_exec) - 1.0) * 100.0
            is_win = bool(future_close > p_exec)
            low_window = low_arr[t_exec : t_exec + horizon_bars + 1]
            min_low = float(np.min(low_window))
            mae_pct = min(0.0, ((min_low / p_exec) - 1.0) * 100.0)
        else:
            fwd_ret_pct = ((p_exec - future_close) / p_exec) * 100.0
            is_win = bool(future_close < p_exec)
            high_window = high_arr[t_exec : t_exec + horizon_bars + 1]
            max_high = float(np.max(high_window))
            mae_pct = -max(0.0, ((max_high - p_exec) / p_exec) * 100.0)

        if sig.metadata is not None:
            sig.metadata["is_open"] = False
            sig.metadata["is_win"] = is_win
            sig.metadata["forward_return_pct"] = fwd_ret_pct
            sig.metadata["mae_pct"] = mae_pct

        closed_returns.append(fwd_ret_pct)
        closed_maes.append(mae_pct)
        closed_wins.append(is_win)

    n_closed = len(closed_returns)
    if n_closed == 0:
        return StrategyStatsSummary(
            strategy_id=inferred_strat_id,
            strategy_sub_id=inferred_sub_id,
            direction=inferred_direction,
            horizon_bars=horizon_bars,
            total_signals=total_signals,
            executed_buys=executed_signals,
            retest_fill_rate=round(retest_fill_rate, 2),
            win_rate=0.0,
            mean_forward_return=0.0,
            median_forward_return=0.0,
            mean_mae=0.0,
            max_mae=0.0,
            efficiency_score=0.0,
            open_signals_count=open_signals_count,
        )

    ret_arr = np.array(closed_returns, dtype=np.float64)
    mae_arr = np.array(closed_maes, dtype=np.float64)
    win_arr = np.array(closed_wins, dtype=bool)

    win_rate = float(np.mean(win_arr)) * 100.0
    mean_ret = float(np.mean(ret_arr))
    median_ret = float(np.median(ret_arr))
    mean_mae = float(np.mean(mae_arr))
    max_mae = float(np.min(mae_arr))

    # Composite Efficiency Score: rewards high win rate and positive return while penalizing MAE
    efficiency_score = ((win_rate / 100.0) * mean_ret) / (abs(mean_mae) + 1.0)

    return StrategyStatsSummary(
        strategy_id=inferred_strat_id,
        strategy_sub_id=inferred_sub_id,
        direction=inferred_direction,
        horizon_bars=horizon_bars,
        total_signals=total_signals,
        executed_buys=executed_signals,
        retest_fill_rate=round(retest_fill_rate, 2),
        win_rate=round(win_rate, 2),
        mean_forward_return=round(mean_ret, 2),
        median_forward_return=round(median_ret, 2),
        mean_mae=round(mean_mae, 2),
        max_mae=round(max_mae, 2),
        efficiency_score=round(efficiency_score, 4),
        open_signals_count=open_signals_count,
    )


def split_closed_and_open_signals(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    horizon_bars: int = 60,
) -> Tuple[List[SignalRecord], List[SignalRecord]]:
    closed_sigs: List[SignalRecord] = []
    open_sigs: List[SignalRecord] = []
    n_bars = series.length

    for sig in signals:
        if sig.execution_bar_index + horizon_bars >= n_bars:
            if sig.metadata is not None:
                sig.metadata["is_open"] = True
            open_sigs.append(sig)
        else:
            if sig.metadata is not None:
                sig.metadata["is_open"] = False
            closed_sigs.append(sig)

    return closed_sigs, open_sigs


def evaluate_all_strategies(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    horizon_bars: int = 60,
    total_signals_by_sub_id: Optional[Dict[str, int]] = None,
    include_empty_sub_ids: Optional[List[Tuple[str, str]]] = None,
) -> List[StrategyStatsSummary]:
    """
    Groups signals by (strategy_id, strategy_sub_id, direction) and evaluates performance for each.
    """
    grouped: Dict[Tuple[str, str, str], List[SignalRecord]] = {}
    for sig in signals:
        key = (sig.strategy_id, sig.strategy_sub_id, sig.direction)
        grouped.setdefault(key, []).append(sig)

    if include_empty_sub_ids:
        for item in include_empty_sub_ids:
            if len(item) == 2:
                grouped.setdefault((item[0], item[1], "BUY"), [])
            else:
                grouped.setdefault((item[0], item[1], item[2]), [])

    summaries: List[StrategyStatsSummary] = []
    for (strat_id, sub_id, d_dir), group_sigs in grouped.items():
        tot_override = None
        if total_signals_by_sub_id and sub_id in total_signals_by_sub_id:
            tot_override = total_signals_by_sub_id[sub_id]

        summary = evaluate_strategy_performance(
            series=series,
            signals=group_sigs,
            horizon_bars=horizon_bars,
            total_signals_override=tot_override,
            strategy_id=strat_id,
            strategy_sub_id=sub_id,
            direction=d_dir,
        )
        summaries.append(summary)

    # Sort descending by win_rate, then efficiency_score
    summaries.sort(key=lambda s: (s.win_rate, s.efficiency_score), reverse=True)
    return summaries
