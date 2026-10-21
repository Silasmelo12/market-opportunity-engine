"""
Accumulation Simulator Engine.
Simulates periodic fixed contributions (e.g. R$ 100 / US$ 100) executed at each buy signal
within a specified date range [start_date, end_date].
Computes shares accumulated, average buy price, net profit, return on capital,
and daily market value curve vs. invested capital.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import pandas as pd
from ..strategies.base import OHLCVSeries, SignalRecord


@dataclass
class SimulationResult:
    strategy_sub_id: str
    strategy_label: str
    total_invested: float           # Capital desembolsado do bolso (N_compras * contribution_amount)
    total_shares: float             # Total de cotas acumuladas
    current_equity: float           # Valor de mercado atual (total_shares * Close[-1])
    net_profit: float               # Lucro líquido em moeda (current_equity - total_invested)
    return_on_capital_pct: float    # Rentabilidade sobre o capital investido (%)
    average_buy_price: float        # Preço médio ponderado das compras
    current_price: float            # Preço da última barra da série
    num_contributions: int          # Quantidade de aportes realizados
    timeline_timestamps: np.ndarray # Array de timestamps (datetime64[ns])
    timeline_invested: np.ndarray   # Série temporal do capital aportado acumulado
    timeline_equity: np.ndarray     # Série temporal do valor de mercado das cotas


@dataclass
class BuyEntryRecord:
    entry_id: int
    date: str
    bar_index: int
    price: float
    shares: float
    capital: float
    strategy_sub_id: str
    strategy_label: str


@dataclass
class TradeRecord:
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
    status: str = "FECHADO"  # "FECHADO" | "ABERTO"
    buy_entries: Optional[List[BuyEntryRecord]] = None
    num_entries: int = 1
    average_buy_price: float = 0.0
    total_invested: float = 0.0
    total_shares: float = 0.0


@dataclass
class CycleSimulationResult:
    total_invested: float             # Capital inicial
    final_equity: float               # Capital final
    net_profit: float                 # Lucro líquido total
    return_on_capital_pct: float      # Rentabilidade total (%)
    total_trades_count: int           # Total de trades
    closed_trades_count: int          # Trades concluídos
    winning_trades_count: int         # Trades com retorno > 0
    losing_trades_count: int          # Trades com retorno <= 0
    win_rate_pct: float               # Taxa de acerto (%)
    avg_trade_return_pct: float       # Retorno médio por trade (%)
    avg_trade_bars: float             # Duração média em barras
    max_drawdown_pct: float           # Drawdown máximo da curva (%)
    current_market_price: float       # Preço da última barra
    buy_and_hold_return_pct: float    # Retorno Buy & Hold no mesmo período (%)
    profit_factor: float = 0.0        # Ganhos brutos / Perdas brutas
    avg_entries_per_cycle: float = 1.0 # Média de compras realizadas por ciclo
    trades: List[TradeRecord] = None  # Histórico de trades
    timeline_timestamps: np.ndarray = None # Array de timestamps
    timeline_invested: np.ndarray = None   # Linha de capital investido
    timeline_equity: np.ndarray = None     # Curva de evolução patrimonial


@dataclass
class StrategyPairRankItem:
    rank: int
    buy_sub_id: str
    buy_label: str
    sell_sub_id: str
    sell_label: str
    closed_trades: int
    winning_trades: int
    win_rate_pct: float
    total_return_pct: float
    net_profit: float
    max_drawdown_pct: float
    has_open_trade: bool
    final_equity: float


def simulate_cycle_trade(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    initial_capital: float = 1000.0,
    contribution_amount: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy_labels_map: Optional[Dict[str, str]] = None,
) -> CycleSimulationResult:
    """
    Executes a complete Cycle/Swing Trade simulation with Multi-Buy support:
    - Enters LONG on a BUY signal.
    - If already in position, any subsequent confirmed BUY signal accumulates shares
      (adding contribution_amount or initial_capital to total invested and recalculating weighted average price).
    - Exits LONG completely on the next chronological SELL signal, liquidating 100% of accumulated shares.
    - Marks any trailing open trade as ABERTO evaluated at Close[-1].
    - Constructs continuous bar-by-bar mark-to-market equity curve and calculates drawdown.
    """
    if initial_capital <= 0:
        raise ValueError("initial_capital must be > 0")

    n_bars = series.length
    if n_bars == 0:
        return CycleSimulationResult(
            total_invested=initial_capital,
            final_equity=initial_capital,
            net_profit=0.0,
            return_on_capital_pct=0.0,
            total_trades_count=0,
            closed_trades_count=0,
            winning_trades_count=0,
            losing_trades_count=0,
            win_rate_pct=0.0,
            avg_trade_return_pct=0.0,
            avg_trade_bars=0.0,
            max_drawdown_pct=0.0,
            current_market_price=0.0,
            buy_and_hold_return_pct=0.0,
            trades=[],
            timeline_timestamps=np.array([], dtype="datetime64[ns]"),
            timeline_invested=np.array([], dtype=np.float64),
            timeline_equity=np.array([], dtype=np.float64),
        )

    labels_map = strategy_labels_map or {}
    ts_series = pd.to_datetime(series.timestamps)

    mask_date = np.ones(n_bars, dtype=bool)
    if start_date:
        mask_date &= (ts_series >= pd.to_datetime(start_date))
    if end_date:
        mask_date &= (ts_series <= pd.to_datetime(end_date))

    timeline_idx = np.flatnonzero(mask_date)
    if len(timeline_idx) == 0:
        timeline_idx = np.arange(n_bars)

    t_stamps = series.timestamps[timeline_idx]
    close_sliced = series.close[timeline_idx]

    # Filter signals within mask_date
    valid_signals = [
        s for s in signals
        if 0 <= s.execution_bar_index < n_bars and mask_date[s.execution_bar_index]
    ]

    # Map signals by bar index
    signals_by_bar: Dict[int, List[SignalRecord]] = {}
    for s in valid_signals:
        signals_by_bar.setdefault(s.execution_bar_index, []).append(s)

    cash = float(initial_capital)
    shares = 0.0
    in_pos = False
    open_trade: Optional[TradeRecord] = None
    trades: List[TradeRecord] = []
    trade_counter = 0

    cumulative_invested = float(initial_capital)
    subsequent_contribution = float(contribution_amount) if contribution_amount is not None and contribution_amount > 0 else float(initial_capital)

    n_timeline = len(timeline_idx)
    timeline_equity = np.zeros(n_timeline, dtype=np.float64)
    timeline_invested = np.zeros(n_timeline, dtype=np.float64)

    for i, orig_bar in enumerate(timeline_idx):
        sigs = signals_by_bar.get(orig_bar, [])
        bar_date_str = str(pd.to_datetime(series.timestamps[orig_bar]).strftime("%Y-%m-%d"))

        # 1. If currently in position, check for SELL signals executing at this bar
        if in_pos and open_trade is not None:
            # Must strictly execute after the last buy entry bar
            last_buy_bar = open_trade.buy_entries[-1].bar_index if open_trade.buy_entries else open_trade.buy_bar_index
            sells = [s for s in sigs if s.direction == "SELL" and orig_bar > last_buy_bar]
            if sells:
                sell_sig = sells[0]
                p_sell = float(sell_sig.execution_price)
                if p_sell > 0:
                    exit_cap = shares * p_sell
                    avg_p = open_trade.average_buy_price if open_trade.average_buy_price > 0 else open_trade.buy_price
                    ret_pct = ((p_sell - avg_p) / avg_p) * 100.0
                    pnl = exit_cap - open_trade.total_invested
                    cash += exit_cap

                    open_trade.sell_strategy_sub_id = sell_sig.strategy_sub_id
                    open_trade.sell_strategy_label = labels_map.get(sell_sig.strategy_sub_id, sell_sig.strategy_sub_id)
                    open_trade.sell_date = bar_date_str
                    open_trade.sell_price = round(p_sell, 2)
                    open_trade.sell_bar_index = int(orig_bar)
                    open_trade.return_pct = round(ret_pct, 2)
                    open_trade.profit_loss = round(pnl, 2)
                    open_trade.duration_bars = int(orig_bar - open_trade.buy_bar_index)
                    open_trade.exit_capital = round(exit_cap, 2)
                    open_trade.status = "FECHADO"

                    trades.append(open_trade)
                    open_trade = None
                    shares = 0.0
                    in_pos = False

        # 2. Check for BUY signals executing at this bar
        buys = [s for s in sigs if s.direction == "BUY"]
        if buys:
            for buy_sig in buys:
                p_buy = float(buy_sig.execution_price)
                if p_buy <= 0:
                    continue

                if not in_pos:
                    # Initial buy starting a new cycle: use current compounded cash if available, else initial_capital
                    trade_counter += 1
                    entry_cap = cash if cash > 0 else float(initial_capital)
                    new_shares = entry_cap / p_buy
                    shares = new_shares
                    cash = 0.0
                    in_pos = True

                    first_entry = BuyEntryRecord(
                        entry_id=1,
                        date=bar_date_str,
                        bar_index=int(orig_bar),
                        price=round(p_buy, 2),
                        shares=round(new_shares, 4),
                        capital=round(entry_cap, 2),
                        strategy_sub_id=buy_sig.strategy_sub_id,
                        strategy_label=labels_map.get(buy_sig.strategy_sub_id, buy_sig.strategy_sub_id),
                    )

                    open_trade = TradeRecord(
                        trade_id=int(trade_counter),
                        buy_strategy_sub_id=buy_sig.strategy_sub_id,
                        buy_strategy_label=labels_map.get(buy_sig.strategy_sub_id, buy_sig.strategy_sub_id),
                        buy_date=bar_date_str,
                        buy_price=round(p_buy, 2),
                        buy_bar_index=int(orig_bar),
                        shares=round(shares, 4),
                        entry_capital=round(entry_cap, 2),
                        status="ABERTO",
                        buy_entries=[first_entry],
                        num_entries=1,
                        average_buy_price=round(p_buy, 4),
                        total_invested=round(entry_cap, 2),
                        total_shares=round(shares, 4),
                    )
                else:
                    # Subsequent buy accumulating into active cycle
                    add_cap = subsequent_contribution
                    new_shares = add_cap / p_buy
                    shares += new_shares
                    cumulative_invested += add_cap
                    cash = max(0.0, cash - add_cap)

                    sub_entry = BuyEntryRecord(
                        entry_id=len(open_trade.buy_entries) + 1 if open_trade.buy_entries else 2,
                        date=bar_date_str,
                        bar_index=int(orig_bar),
                        price=round(p_buy, 2),
                        shares=round(new_shares, 4),
                        capital=round(add_cap, 2),
                        strategy_sub_id=buy_sig.strategy_sub_id,
                        strategy_label=labels_map.get(buy_sig.strategy_sub_id, buy_sig.strategy_sub_id),
                    )

                    if open_trade.buy_entries is None:
                        open_trade.buy_entries = []
                    open_trade.buy_entries.append(sub_entry)
                    open_trade.num_entries = len(open_trade.buy_entries)
                    open_trade.total_shares = round(shares, 4)
                    open_trade.shares = round(shares, 4)
                    open_trade.total_invested = round(open_trade.total_invested + add_cap, 2)
                    open_trade.entry_capital = open_trade.total_invested
                    open_trade.average_buy_price = round(open_trade.total_invested / open_trade.total_shares, 4)
                    open_trade.buy_price = open_trade.average_buy_price

        # 3. Mark-to-market equity at bar i
        c_price = float(close_sliced[i])
        cur_eq = cash + (shares * c_price)
        timeline_equity[i] = cur_eq
        timeline_invested[i] = cumulative_invested

    # 4. Handle still open trade at end of timeline
    last_close = float(series.close[timeline_idx[-1]])
    if in_pos and open_trade is not None:
        cur_val = shares * last_close
        avg_p = open_trade.average_buy_price if open_trade.average_buy_price > 0 else open_trade.buy_price
        ret_pct = ((last_close - avg_p) / avg_p) * 100.0
        pnl = cur_val - open_trade.total_invested

        open_trade.sell_strategy_sub_id = None
        open_trade.sell_strategy_label = "Posição Aberta a Mercado"
        open_trade.sell_date = "Em Aberto"
        open_trade.sell_price = round(last_close, 2)
        open_trade.sell_bar_index = int(timeline_idx[-1])
        open_trade.return_pct = round(ret_pct, 2)
        open_trade.profit_loss = round(pnl, 2)
        open_trade.duration_bars = int(timeline_idx[-1]) - open_trade.buy_bar_index
        open_trade.exit_capital = round(cur_val, 2)
        open_trade.status = "ABERTO"
        trades.append(open_trade)

    # 5. Compute summary metrics with exact K-buys generic capital accounting
    # Base capital: if contributions are cumulative without compounding (reinvesting cash),
    # total capital is initial_capital + all subsequent buy contributions across cycles.
    # Otherwise, it's the peak capital deployed from the investor's balance.
    final_eq = float(timeline_equity[-1]) if len(timeline_equity) > 0 else initial_capital
    base_capital = float(initial_capital)
    
    # If the user performed additional contributions within cycles, base capital includes them
    total_added_contributions = sum(
        sum(be.capital for be in (t.buy_entries[1:] if t.buy_entries and len(t.buy_entries) > 1 else []))
        for t in trades
    )
    total_invested_capital = base_capital + total_added_contributions

    net_profit = final_eq - total_invested_capital
    tot_ret_pct = ((final_eq / total_invested_capital) - 1.0) * 100.0 if total_invested_capital > 0 else 0.0

    closed_trades = [t for t in trades if t.status == "FECHADO"]
    winning_trades = [t for t in closed_trades if t.return_pct > 0]
    losing_trades = [t for t in closed_trades if t.return_pct <= 0]
    win_rate = (len(winning_trades) / len(closed_trades) * 100.0) if closed_trades else 0.0
    avg_ret = float(np.mean([t.return_pct for t in closed_trades])) if closed_trades else 0.0
    avg_bars = float(np.mean([t.duration_bars for t in closed_trades])) if closed_trades else 0.0

    # Max Drawdown
    if len(timeline_equity) > 0:
        peak = np.maximum.accumulate(timeline_equity)
        drawdowns = (timeline_equity - peak) / np.where(peak > 0, peak, 1.0) * 100.0
        max_dd = float(np.min(drawdowns))
    else:
        max_dd = 0.0

    # Buy and Hold Return
    first_close = float(close_sliced[0]) if len(close_sliced) > 0 else 1.0
    bnh_ret = ((last_close - first_close) / first_close) * 100.0 if first_close > 0 else 0.0

    # Profit Factor (Gross Profits / Gross Losses)
    gross_profit = sum(t.profit_loss for t in closed_trades if t.profit_loss > 0)
    gross_loss = abs(sum(t.profit_loss for t in closed_trades if t.profit_loss < 0))
    if gross_loss > 0:
        profit_factor = round(gross_profit / gross_loss, 2)
    elif gross_profit > 0:
        profit_factor = 999.0
    else:
        profit_factor = 0.0

    # Average entries per cycle
    total_cycle_entries = sum(t.num_entries for t in trades)
    avg_entries = (total_cycle_entries / len(trades)) if trades else 1.0

    return CycleSimulationResult(
        total_invested=round(total_invested_capital, 2),
        final_equity=round(final_eq, 2),
        net_profit=round(net_profit, 2),
        return_on_capital_pct=round(tot_ret_pct, 2),
        total_trades_count=len(trades),
        closed_trades_count=len(closed_trades),
        winning_trades_count=len(winning_trades),
        losing_trades_count=len(losing_trades),
        win_rate_pct=round(win_rate, 2),
        avg_trade_return_pct=round(avg_ret, 2),
        avg_trade_bars=round(avg_bars, 1),
        max_drawdown_pct=round(max_dd, 2),
        current_market_price=round(last_close, 2),
        buy_and_hold_return_pct=round(bnh_ret, 2),
        profit_factor=profit_factor,
        avg_entries_per_cycle=round(avg_entries, 2),
        trades=trades,
        timeline_timestamps=t_stamps,
        timeline_invested=timeline_invested,
        timeline_equity=timeline_equity,
    )


def simulate_accumulation(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    contribution_amount: float = 100.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy_labels_map: Optional[Dict[str, str]] = None,
) -> Dict[str, SimulationResult]:
    """
    Runs fixed capital accumulation simulation for each strategy_sub_id present in signals.
    Filters executions strictly within [start_date, end_date] if provided.
    """
    if contribution_amount <= 0:
        raise ValueError("contribution_amount must be > 0")

    n_bars = series.length
    if n_bars == 0:
        return {}

    labels_map = strategy_labels_map or {}
    ts_series = pd.to_datetime(series.timestamps)

    # Date mask filter
    mask_date = np.ones(n_bars, dtype=bool)
    if start_date:
        mask_date &= (ts_series >= pd.to_datetime(start_date))
    if end_date:
        mask_date &= (ts_series <= pd.to_datetime(end_date))

    # Group signals by strategy_sub_id
    grouped_signals: Dict[str, List[SignalRecord]] = {}
    for sig in signals:
        t_exec = sig.execution_bar_index
        if 0 <= t_exec < n_bars and mask_date[t_exec]:
            grouped_signals.setdefault(sig.strategy_sub_id, []).append(sig)

    results: Dict[str, SimulationResult] = {}
    current_price = float(series.close[-1])

    # Sliced timeline within active range
    timeline_idx = np.flatnonzero(mask_date)
    if len(timeline_idx) == 0:
        timeline_idx = np.arange(n_bars)

    t_stamps = series.timestamps[timeline_idx]
    close_sliced = series.close[timeline_idx]

    for sub_id, strat_signals in grouped_signals.items():
        # Track shares and cash invested at each bar in timeline_idx
        # Map original bar index to position in timeline_idx
        orig_to_pos = {int(bar_idx): pos for pos, bar_idx in enumerate(timeline_idx)}

        shares_added = np.zeros(len(timeline_idx), dtype=np.float64)
        cash_added = np.zeros(len(timeline_idx), dtype=np.float64)

        for sig in strat_signals:
            p_exec = float(sig.execution_price)
            if p_exec > 0 and sig.execution_bar_index in orig_to_pos:
                pos = orig_to_pos[sig.execution_bar_index]
                shares = contribution_amount / p_exec
                shares_added[pos] += shares
                cash_added[pos] += contribution_amount

        cum_shares = np.cumsum(shares_added)
        cum_invested = np.cumsum(cash_added)
        cum_equity = cum_shares * close_sliced

        total_invested = float(cum_invested[-1]) if len(cum_invested) > 0 else 0.0
        total_shares = float(cum_shares[-1]) if len(cum_shares) > 0 else 0.0
        final_equity = float(total_shares * current_price)
        net_profit = final_equity - total_invested
        ret_on_cap = ((final_equity / total_invested) - 1.0) * 100.0 if total_invested > 0 else 0.0
        avg_price = (total_invested / total_shares) if total_shares > 0 else 0.0

        label = labels_map.get(sub_id, sub_id)

        results[sub_id] = SimulationResult(
            strategy_sub_id=sub_id,
            strategy_label=label,
            total_invested=round(total_invested, 2),
            total_shares=round(total_shares, 4),
            current_equity=round(final_equity, 2),
            net_profit=round(net_profit, 2),
            return_on_capital_pct=round(ret_on_cap, 2),
            average_buy_price=round(avg_price, 2),
            current_price=round(current_price, 2),
            num_contributions=len(strat_signals),
            timeline_timestamps=t_stamps,
            timeline_invested=cum_invested,
            timeline_equity=cum_equity,
        )

    return results


def optimize_strategy_pairs(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    initial_capital: float = 1000.0,
    min_trades: int = 2,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy_labels_map: Optional[Dict[str, str]] = None,
    top_n: int = 15,
) -> Tuple[Optional[StrategyPairRankItem], List[StrategyPairRankItem]]:
    """
    Scans all pairs of (Buy Strategy, Sell Strategy) that produce trades.
    Evaluates compounded return, win rate, net profit, and max drawdown in milliseconds.
    Returns (champion, top_combinations) sorted by total_return_pct descending.
    """
    n_bars = series.length
    if n_bars == 0 or not signals:
        return None, []

    labels_map = strategy_labels_map or {}
    ts_series = pd.to_datetime(series.timestamps)

    mask_date = np.ones(n_bars, dtype=bool)
    if start_date:
        mask_date &= (ts_series >= pd.to_datetime(start_date))
    if end_date:
        mask_date &= (ts_series <= pd.to_datetime(end_date))

    valid_signals = [
        s for s in signals
        if 0 <= s.execution_bar_index < n_bars and mask_date[s.execution_bar_index]
    ]

    buys_by_id: Dict[str, List[SignalRecord]] = {}
    sells_by_id: Dict[str, List[SignalRecord]] = {}

    for s in valid_signals:
        if s.direction == "BUY":
            buys_by_id.setdefault(s.strategy_sub_id, []).append(s)
        elif s.direction == "SELL":
            sells_by_id.setdefault(s.strategy_sub_id, []).append(s)

    last_close = float(series.close[-1])

    def _eval_pair(b_sigs: List[SignalRecord], s_sigs: List[SignalRecord], req_min_trades: int):
        merged = sorted(b_sigs + s_sigs, key=lambda x: (x.execution_bar_index, 0 if x.direction == "BUY" else 1))
        cash = float(initial_capital)
        entry_p = 0.0
        entry_bar = -1
        in_pos = False
        closed_trades = 0
        wins = 0
        peak = float(initial_capital)
        max_dd = 0.0

        for s in merged:
            bar = s.execution_bar_index
            p = float(s.execution_price)
            if in_pos and s.direction == "SELL" and bar > entry_bar and p > 0:
                ret = (p - entry_p) / entry_p
                cash = cash * (1.0 + ret)
                closed_trades += 1
                if ret > 0:
                    wins += 1
                if cash > peak:
                    peak = cash
                dd = (cash - peak) / peak * 100.0
                if dd < max_dd:
                    max_dd = dd
                in_pos = False
            elif not in_pos and s.direction == "BUY" and p > 0:
                entry_p = p
                entry_bar = bar
                in_pos = True

        if in_pos and entry_p > 0:
            ret = (last_close - entry_p) / entry_p
            equity = cash * (1.0 + ret)
        else:
            equity = cash

        if closed_trades < req_min_trades:
            return None

        tot_ret_pct = ((equity / initial_capital) - 1.0) * 100.0
        win_rate = (wins / closed_trades * 100.0) if closed_trades > 0 else 0.0

        return {
            "closed_trades": closed_trades,
            "winning_trades": wins,
            "has_open_trade": in_pos,
            "win_rate_pct": round(win_rate, 1),
            "total_return_pct": round(tot_ret_pct, 1),
            "net_profit": round(equity - initial_capital, 2),
            "final_equity": round(equity, 2),
            "max_drawdown_pct": round(max_dd, 1),
        }

    pair_results = []
    for b_id, b_sigs in buys_by_id.items():
        for s_id, s_sigs in sells_by_id.items():
            r = _eval_pair(b_sigs, s_sigs, req_min_trades=min_trades)
            if r:
                pair_results.append((b_id, s_id, r))

    if not pair_results and min_trades > 1:
        for b_id, b_sigs in buys_by_id.items():
            for s_id, s_sigs in sells_by_id.items():
                r = _eval_pair(b_sigs, s_sigs, req_min_trades=1)
                if r:
                    pair_results.append((b_id, s_id, r))

    pair_results.sort(key=lambda x: x[2]["total_return_pct"], reverse=True)

    ranked_items: List[StrategyPairRankItem] = []
    for idx, (b_id, s_id, r) in enumerate(pair_results[:top_n], start=1):
        b_label = labels_map.get(b_id, b_id)
        s_label = labels_map.get(s_id, s_id)
        ranked_items.append(
            StrategyPairRankItem(
                rank=idx,
                buy_sub_id=b_id,
                buy_label=b_label,
                sell_sub_id=s_id,
                sell_label=s_label,
                closed_trades=r["closed_trades"],
                winning_trades=r["winning_trades"],
                win_rate_pct=r["win_rate_pct"],
                total_return_pct=r["total_return_pct"],
                net_profit=r["net_profit"],
                max_drawdown_pct=r["max_drawdown_pct"],
                has_open_trade=r["has_open_trade"],
                final_equity=r["final_equity"],
            )
        )

    champion = ranked_items[0] if ranked_items else None
    return champion, ranked_items
