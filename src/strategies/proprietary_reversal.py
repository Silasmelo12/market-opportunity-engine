"""
Proprietary Reversal Strategy Engine (2x2 State Machine for BUY and SELL).
Monitors:
- BUY (Fundos): Bearish breakouts of reference lows (Type 1: t-1, Type 2: Rolling N-bar low),
  tracks active support lines with dynamic overwrite on successive breakouts,
  and executes buys upon bullish negation (Close[t] > support) in Open (t+1) or Retest (1..M) mode.
- SELL (Topos): Bullish breakouts of reference highs (Type 1: t-1, Type 2: Rolling N-bar high),
  tracks active resistance lines with dynamic overwrite on successive breakouts,
  and executes sells upon bearish negation (Close[t] < resistance) in Open (t+1) or Retest (1..M) mode.

Strictly adheres to FR-004 and Zero Look-Ahead Bias (Constitution Principle II).
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from .base import OHLCVSeries, SignalRecord, ReferenceLineSegment

# Finite State Machine states
STATE_IDLE = 0
STATE_LINE_ACTIVE = 1
STATE_WAIT_RETEST = 2


class ProprietaryReversalEngine:
    """
    O(N) NumPy State Machine for the Proprietary Breakout Negation Strategy.
    Evaluates BUY (Bottoms) and SELL (Tops) variants independently:
      BUY Variants:
        - t1_open:   Breakout of Low[t-1]         + Buy at Open[t+1]
        - t1_retest: Breakout of Low[t-1]         + Buy on Retest within M bars
        - t2_open:   Breakout of min(Low[t-N:t])  + Buy at Open[t+1]
        - t2_retest: Breakout of min(Low[t-N:t])  + Buy on Retest within M bars
      SELL Variants:
        - sell_t1_open:   Breakout of High[t-1]        + Sell at Open[t+1]
        - sell_t1_retest: Breakout of High[t-1]        + Sell on Retest within M bars
        - sell_t2_open:   Breakout of max(High[t-N:t]) + Sell at Open[t+1]
        - sell_t2_retest: Breakout of max(High[t-N:t]) + Sell on Retest within M bars
    """

    BUY_VARIANTS = (
        ("t1_open", "t1", "open"),
        ("t1_retest", "t1", "retest"),
        ("t2_open", "t2", "open"),
        ("t2_retest", "t2", "retest"),
    )

    SELL_VARIANTS = (
        ("sell_t1_open", "t1", "open"),
        ("sell_t1_retest", "t1", "retest"),
        ("sell_t2_open", "t2", "open"),
        ("sell_t2_retest", "t2", "retest"),
    )

    VARIANTS = BUY_VARIANTS + SELL_VARIANTS

    def __init__(
        self,
        lookback_n: int = 10,
        retest_window_m: int = 5,
        tolerance_pct: float = 0.0,
    ) -> None:
        if lookback_n < 1:
            raise ValueError("lookback_n must be >= 1")
        if retest_window_m < 1:
            raise ValueError("retest_window_m must be >= 1")
        if tolerance_pct < 0.0:
            raise ValueError("tolerance_pct must be >= 0.0")

        self.lookback_n = int(lookback_n)
        self.retest_window_m = int(retest_window_m)
        self.tolerance_pct = float(tolerance_pct)

        self.last_state_by_variant: Dict[str, Dict[str, Any]] = {}
        self.pending_signals: List[Dict[str, Any]] = []
        self.total_signals_by_variant: Dict[str, int] = {}

    @staticmethod
    def _compute_reference_lows(low_arr: np.ndarray, candle_b_type: str, lookback_n: int) -> np.ndarray:
        """
        Precomputes candidate reference low array causally in O(N).
        For 't1': candidate at index t is Low[t-1] (valid for t >= 1).
        For 't2': candidate at index t is min(Low[t-N : t]) (valid for t >= lookback_n).
        """
        n = len(low_arr)
        cand_lows = np.full(n, np.nan, dtype=np.float64)
        if n <= 1:
            return cand_lows

        if candle_b_type == "t1":
            cand_lows[1:] = low_arr[:-1]
        elif candle_b_type == "t2":
            if n > lookback_n:
                s_low = pd.Series(low_arr)
                rolling_min = s_low.shift(1).rolling(window=lookback_n, min_periods=lookback_n).min()
                cand_lows = rolling_min.to_numpy(dtype=np.float64)
        else:
            raise ValueError(f"Unknown candle_b_type: {candle_b_type}")

        return cand_lows

    @staticmethod
    def _compute_reference_highs(high_arr: np.ndarray, candle_b_type: str, lookback_n: int) -> np.ndarray:
        """
        Precomputes candidate reference high array causally in O(N).
        For 't1': candidate at index t is High[t-1] (valid for t >= 1).
        For 't2': candidate at index t is max(High[t-N : t]) (valid for t >= lookback_n).
        """
        n = len(high_arr)
        cand_highs = np.full(n, np.nan, dtype=np.float64)
        if n <= 1:
            return cand_highs

        if candle_b_type == "t1":
            cand_highs[1:] = high_arr[:-1]
        elif candle_b_type == "t2":
            if n > lookback_n:
                s_high = pd.Series(high_arr)
                rolling_max = s_high.shift(1).rolling(window=lookback_n, min_periods=lookback_n).max()
                cand_highs = rolling_max.to_numpy(dtype=np.float64)
        else:
            raise ValueError(f"Unknown candle_b_type: {candle_b_type}")

        return cand_highs

    def _run_single_variant(
        self,
        open_arr: np.ndarray,
        high_arr: np.ndarray,
        low_arr: np.ndarray,
        close_arr: np.ndarray,
        sub_id: str,
        candle_b_type: str,
        exec_mode: str,
        direction: str = "BUY",
    ) -> Tuple[List[SignalRecord], List[ReferenceLineSegment], Dict[str, Any], int]:
        """
        Executes a single O(N) pass over contiguous 1D NumPy arrays for one specific variant (BUY or SELL).
        Guarantees complete state isolation and zero look-ahead bias.
        """
        n_bars = len(close_arr)
        is_buy = (direction == "BUY")
        line_type = "SUPPORT" if is_buy else "RESISTANCE"

        if is_buy:
            cand_refs = self._compute_reference_lows(low_arr, candle_b_type, self.lookback_n)
        else:
            cand_refs = self._compute_reference_highs(high_arr, candle_b_type, self.lookback_n)

        signals: List[SignalRecord] = []
        segments: List[ReferenceLineSegment] = []

        state: int = STATE_IDLE
        active_ref_line: float = np.nan
        breakout_bar: int = -1
        negation_bar: int = -1
        retest_deadline: int = -1
        total_negation_signals: int = 0

        last_bar_event: str = "NEUTRO"
        tol_mult_buy: float = 1.0 + self.tolerance_pct
        tol_mult_sell: float = 1.0 - self.tolerance_pct

        for t in range(n_bars):
            c_t = close_arr[t]
            o_t = open_arr[t]
            h_t = high_arr[t]
            l_t = low_arr[t]
            cand_ref = cand_refs[t]

            # 1. Currently waiting for a retest in window [negation_bar + 1, negation_bar + M]
            if state == STATE_WAIT_RETEST:
                if is_buy:
                    limit_level = active_ref_line * tol_mult_buy
                    touched = (l_t <= limit_level)
                    gap_fill = (o_t < limit_level)
                else:
                    limit_level = active_ref_line * tol_mult_sell
                    touched = (h_t >= limit_level)
                    gap_fill = (o_t > limit_level)

                if touched:
                    exec_price = float(o_t) if gap_fill else float(active_ref_line)
                    fill_type = "retest_gap" if gap_fill else "retest_touch"

                    signals.append(
                        SignalRecord(
                            strategy_id="prop_reversal",
                            strategy_sub_id=sub_id,
                            direction=direction,
                            signal_bar_index=negation_bar,
                            execution_bar_index=t,
                            execution_price=exec_price,
                            reference_line_price=float(active_ref_line),
                            metadata={
                                "breakout_bar_index": breakout_bar,
                                "negation_bar_index": negation_bar,
                                "mode": exec_mode,
                                "candle_b_type": candle_b_type,
                                "fill_type": fill_type,
                                "retest_bar_offset": t - negation_bar,
                            },
                        )
                    )
                    segments.append(
                        ReferenceLineSegment(
                            start_bar_index=breakout_bar,
                            end_bar_index=t,
                            price_level=float(active_ref_line),
                            status="NEGATED_EXECUTED",
                            line_type=line_type,
                            direction=direction,
                            variation_id=sub_id,
                        )
                    )

                    if t == n_bars - 1:
                        last_bar_event = "COMPRA_EXECUTADA_HOJE" if is_buy else "VENDA_EXECUTADA_HOJE"

                    # Consume line and finish single cycle
                    state = STATE_IDLE
                    active_ref_line = np.nan
                    breakout_bar = -1
                    negation_bar = -1
                    retest_deadline = -1
                    continue
                else:
                    if t >= retest_deadline:
                        segments.append(
                            ReferenceLineSegment(
                                start_bar_index=breakout_bar,
                                end_bar_index=t,
                                price_level=float(active_ref_line),
                                status="EXPIRED",
                                line_type=line_type,
                                direction=direction,
                                variation_id=sub_id,
                            )
                        )
                        state = STATE_IDLE
                        active_ref_line = np.nan
                        breakout_bar = -1
                        negation_bar = -1
                        retest_deadline = -1
                    continue

            # 2. Currently holding an Active Reference Line waiting for Negation (or overwrite)
            if state == STATE_LINE_ACTIVE:
                is_negation = (c_t > active_ref_line) if is_buy else (c_t < active_ref_line)
                is_new_breakout = ((not np.isnan(cand_ref)) and (c_t < cand_ref)) if is_buy else \
                                  ((not np.isnan(cand_ref)) and (c_t > cand_ref))

                if is_negation:
                    total_negation_signals += 1
                    negation_bar = t

                    if exec_mode == "open":
                        if t + 1 < n_bars:
                            exec_price = float(open_arr[t + 1])
                            signals.append(
                                SignalRecord(
                                    strategy_id="prop_reversal",
                                    strategy_sub_id=sub_id,
                                    direction=direction,
                                    signal_bar_index=t,
                                    execution_bar_index=t + 1,
                                    execution_price=exec_price,
                                    reference_line_price=float(active_ref_line),
                                    metadata={
                                        "breakout_bar_index": breakout_bar,
                                        "negation_bar_index": t,
                                        "mode": exec_mode,
                                        "candle_b_type": candle_b_type,
                                        "fill_type": "next_open",
                                    },
                                )
                            )
                            segments.append(
                                ReferenceLineSegment(
                                    start_bar_index=breakout_bar,
                                    end_bar_index=t + 1,
                                    price_level=float(active_ref_line),
                                    status="NEGATED_EXECUTED",
                                    line_type=line_type,
                                    direction=direction,
                                    variation_id=sub_id,
                                )
                            )
                            if t + 1 == n_bars - 1:
                                last_bar_event = "COMPRA_EXECUTADA_HOJE" if is_buy else "VENDA_EXECUTADA_HOJE"
                        else:
                            last_bar_event = "COMPRA_GATILHO_ABERTURA" if is_buy else "VENDA_GATILHO_ABERTURA"
                            segments.append(
                                ReferenceLineSegment(
                                    start_bar_index=breakout_bar,
                                    end_bar_index=t,
                                    price_level=float(active_ref_line),
                                    status="ACTIVE_PENDING",
                                    line_type=line_type,
                                    direction=direction,
                                    variation_id=sub_id,
                                )
                            )
                            self.pending_signals.append(
                                {
                                    "strategy_id": "prop_reversal",
                                    "strategy_sub_id": sub_id,
                                    "direction": direction,
                                    "signal_bar_index": t,
                                    "reference_line_price": float(active_ref_line),
                                    "status": "AGUARDANDO_ABERTURA_T+1",
                                }
                            )

                        state = STATE_IDLE
                        active_ref_line = np.nan
                        breakout_bar = -1
                        negation_bar = -1
                        continue
                    else:
                        state = STATE_WAIT_RETEST
                        retest_deadline = t + self.retest_window_m
                        continue

                elif is_new_breakout:
                    # Successive breakout before negation: overwrite active reference line!
                    segments.append(
                        ReferenceLineSegment(
                            start_bar_index=breakout_bar,
                            end_bar_index=t,
                            price_level=float(active_ref_line),
                            status="CANCELLED",
                            line_type=line_type,
                            direction=direction,
                            variation_id=sub_id,
                        )
                    )
                    active_ref_line = float(cand_ref)
                    breakout_bar = t
                    continue

            # 3. Currently IDLE: check for new breakout
            if state == STATE_IDLE:
                is_breakout = ((not np.isnan(cand_ref)) and (c_t < cand_ref)) if is_buy else \
                              ((not np.isnan(cand_ref)) and (c_t > cand_ref))
                if is_breakout:
                    state = STATE_LINE_ACTIVE
                    active_ref_line = float(cand_ref)
                    breakout_bar = t

        # Post-loop check
        last_close = float(close_arr[-1]) if n_bars > 0 else np.nan
        current_status = last_bar_event
        retest_remaining: Optional[int] = None
        dist_pct: Optional[float] = None
        active_line_out: Optional[float] = None

        if state == STATE_LINE_ACTIVE and n_bars > 0:
            current_status = "AGUARDANDO_NEGACAO"
            active_line_out = float(active_ref_line)
            if active_line_out > 0:
                dist_pct = ((last_close / active_line_out) - 1.0) * 100.0
            segments.append(
                ReferenceLineSegment(
                    start_bar_index=breakout_bar,
                    end_bar_index=n_bars - 1,
                    price_level=float(active_ref_line),
                    status="ACTIVE_PENDING",
                    line_type=line_type,
                    direction=direction,
                    variation_id=sub_id,
                )
            )
        elif state == STATE_WAIT_RETEST and n_bars > 0:
            current_status = "AGUARDANDO_RETESTE"
            active_line_out = float(active_ref_line)
            retest_remaining = max(0, retest_deadline - (n_bars - 1))
            if active_line_out > 0:
                dist_pct = ((last_close / active_line_out) - 1.0) * 100.0
            segments.append(
                ReferenceLineSegment(
                    start_bar_index=breakout_bar,
                    end_bar_index=n_bars - 1,
                    price_level=float(active_ref_line),
                    status="ACTIVE_PENDING",
                    line_type=line_type,
                    direction=direction,
                    variation_id=sub_id,
                )
            )
            self.pending_signals.append(
                {
                    "strategy_id": "prop_reversal",
                    "strategy_sub_id": sub_id,
                    "direction": direction,
                    "signal_bar_index": negation_bar,
                    "reference_line_price": float(active_ref_line),
                    "retest_bars_remaining": retest_remaining,
                    "status": "AGUARDANDO_RETESTE",
                }
            )

        for sig in signals:
            if sig.metadata is not None:
                sig.metadata["total_variant_signals"] = total_negation_signals

        state_snapshot = {
            "strategy_sub_id": sub_id,
            "direction": direction,
            "status": current_status,
            "active_line_price": active_line_out,
            "breakout_bar_index": breakout_bar if breakout_bar >= 0 else None,
            "negation_bar_index": negation_bar if negation_bar >= 0 else None,
            "retest_bars_remaining": retest_remaining,
            "last_close": last_close,
            "distance_to_line_pct": dist_pct,
            "total_negation_signals": total_negation_signals,
            "executed_signals": len(signals),
        }

        return signals, segments, state_snapshot, total_negation_signals

    def generate_signals(
        self,
        series: OHLCVSeries,
        variant_filter: Optional[List[str]] = None,
        direction_filter: Optional[str] = None,
    ) -> Tuple[List[SignalRecord], List[ReferenceLineSegment]]:
        """
        Runs state machines on OHLCVSeries for BUY and/or SELL variants.
        """
        all_signals: List[SignalRecord] = []
        all_segments: List[ReferenceLineSegment] = []
        self.last_state_by_variant = {}
        self.pending_signals = []
        self.total_signals_by_variant = {}

        if series.length == 0:
            return all_signals, all_segments

        variants_to_run = []
        if direction_filter is None or direction_filter == "ALL":
            variants_to_run = [(v[0], v[1], v[2], "BUY") for v in self.BUY_VARIANTS] + \
                              [(v[0], v[1], v[2], "SELL") for v in self.SELL_VARIANTS]
        elif direction_filter == "BUY":
            variants_to_run = [(v[0], v[1], v[2], "BUY") for v in self.BUY_VARIANTS]
        elif direction_filter == "SELL":
            variants_to_run = [(v[0], v[1], v[2], "SELL") for v in self.SELL_VARIANTS]
        else:
            raise ValueError(f"Unknown direction_filter: {direction_filter}")

        for sub_id, candle_b_type, exec_mode, direction in variants_to_run:
            if variant_filter is not None and sub_id not in variant_filter:
                continue

            sigs, segs, snapshot, total_sigs = self._run_single_variant(
                open_arr=series.open,
                high_arr=series.high,
                low_arr=series.low,
                close_arr=series.close,
                sub_id=sub_id,
                candle_b_type=candle_b_type,
                exec_mode=exec_mode,
                direction=direction,
            )
            all_signals.extend(sigs)
            all_segments.extend(segs)
            self.last_state_by_variant[sub_id] = snapshot
            self.total_signals_by_variant[sub_id] = total_sigs

        return all_signals, all_segments

    def get_current_state(self) -> Dict[str, Dict[str, Any]]:
        return self.last_state_by_variant
