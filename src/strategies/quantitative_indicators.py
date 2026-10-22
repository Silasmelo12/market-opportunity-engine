"""
Quantitative Indicators Strategy Engine.
Implements 10 quantitative technical indicators across 4 families:
1. Mean Reversion: Bollinger Close-In, Keltner Squeeze, Z-Score Extremes.
2. Oscillators & Divergences: RSI Divergence, Stochastic Extremes, MACD Histogram Momentum.
3. Institutional Volume & Flow: VWAP Bands, Money Flow Index (MFI), Volume Climax / VSA Absorption.
4. Volatility & Trend: SuperTrend / ATR Trailing.

Strictly adheres to Zero Look-Ahead Bias:
- Calculations at bar t incorporate data up to Close[t].
- Fill/execution occurs at Open[t+1] on the subsequent bar.
- Fully vectorized via NumPy and Pandas.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

from .base import OHLCVSeries, SignalRecord, ReferenceLineSegment


# ==========================================
# Contiguous Vectorized Helpers (Anti-Lookahead)
# ==========================================

def compute_sma(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Simple Moving Average using rolling window."""
    s = pd.Series(arr)
    return s.rolling(window=period, min_periods=period).mean().to_numpy()


def compute_ema(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Exponential Moving Average."""
    s = pd.Series(arr)
    return s.ewm(span=period, adjust=False).mean().to_numpy()


def compute_rolling_std(arr: np.ndarray, period: int) -> np.ndarray:
    """Calculates Rolling Standard Deviation."""
    s = pd.Series(arr)
    return s.rolling(window=period, min_periods=period).std().to_numpy()


def compute_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    """Calculates Average True Range (Wilder/EMA smoothed)."""
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]

    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    s_tr = pd.Series(tr)
    return s_tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()


def compute_rsi_series(close: np.ndarray, period: int = 14) -> np.ndarray:
    """Calculates Relative Strength Index (RSI)."""
    diff = np.diff(close, prepend=close[0])
    gain = np.where(diff > 0, diff, 0.0)
    loss = np.where(diff < 0, -diff, 0.0)

    s_gain = pd.Series(gain)
    s_loss = pd.Series(loss)

    avg_gain = s_gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()
    avg_loss = s_loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean().to_numpy()

    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi[avg_loss == 0] = 100.0
    return rsi


def convert_signals_to_records(
    series: OHLCVSeries,
    condition_mask: np.ndarray,
    strategy_id: str,
    strategy_sub_id: str,
    direction: str,
    ref_prices: Optional[np.ndarray] = None,
    metadata_list: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[SignalRecord], List[Dict[str, Any]]]:
    """
    Standard converter converting boolean signal masks to SignalRecord instances.
    Enforces strict Zero Look-Ahead Bias:
      - Signal occurs at index t (condition_mask[t] is True).
      - Execution fill occurs at index t + 1 (execution_price = Open[t + 1]).
      - If signal occurs at the very last bar (t == len - 1), it is cataloged
        as a pending alert for the next live bar.
    """
    n = series.length
    records: List[SignalRecord] = []
    pending: List[Dict[str, Any]] = []

    # Indices where condition is triggered
    triggered_indices = np.where(condition_mask)[0]

    for idx in triggered_indices:
        ref_price = float(ref_prices[idx]) if ref_prices is not None and not np.isnan(ref_prices[idx]) else None
        meta = metadata_list[idx] if metadata_list is not None and idx < len(metadata_list) else {}

        if idx + 1 < n:
            # Historical signal with confirmed fill on next bar
            records.append(
                SignalRecord(
                    strategy_id=strategy_id,
                    strategy_sub_id=strategy_sub_id,
                    signal_bar_index=int(idx),
                    execution_bar_index=int(idx + 1),
                    execution_price=float(series.open[idx + 1]),
                    reference_line_price=ref_price,
                    direction=direction,
                    metadata=meta,
                )
            )
        else:
            # Alert on the latest bar (pending tomorrow's open)
            pending.append({
                "strategy_id": strategy_id,
                "strategy_sub_id": strategy_sub_id,
                "signal_bar_index": int(idx),
                "signal_date": str(pd.to_datetime(series.timestamps[idx], unit="s")),
                "direction": direction,
                "reference_price": ref_price,
                "metadata": meta,
            })

    return records, pending




class QuantitativeIndicatorsEngine:
    """
    Engine executing quantitative technical indicator strategies.
    """

    SUPPORTED_STRATEGIES = [
        "bollinger_close_in",
        "keltner_squeeze",
        "zscore_extreme",
        "rsi_divergence",
        "stochastic_extreme",
        "macd_momentum",
        "vwap_bands",
        "mfi_extreme",
        "volume_climax_vsa",
        "supertrend_trailing",
    ]

    def __init__(self) -> None:
        self.supported_strategies = list(self.SUPPORTED_STRATEGIES)
        self.pending_signals: List[Dict[str, Any]] = []

    def generate_bollinger_close_in(
        self,
        series: OHLCVSeries,
        period: int = 20,
        num_std: float = 2.0,
    ) -> Tuple[List[SignalRecord], List[SignalRecord]]:
        """
        Bollinger Close-Outside then Close-Inside Reversal.
        - BUY (Fundo): Close[t-1] < LowerBand[t-1] and Close[t] >= LowerBand[t].
        - SELL (Topo): Close[t-1] > UpperBand[t-1] and Close[t] <= UpperBand[t].
        """
        n = series.length
        if n < period + 2:
            return [], []

        sma = compute_sma(series.close, period)
        std = compute_rolling_std(series.close, period)
        upper = sma + num_std * std
        lower = sma - num_std * std

        prev_close = np.roll(series.close, 1)
        prev_lower = np.roll(lower, 1)
        prev_upper = np.roll(upper, 1)

        valid = ~np.isnan(prev_lower) & ~np.isnan(lower)

        # Buy condition (reversal from bottom)
        buy_mask = valid & (prev_close < prev_lower) & (series.close >= lower)
        buy_mask[:period + 1] = False

        # Sell condition (reversal from top)
        sell_mask = valid & (prev_close > prev_upper) & (series.close <= upper)
        sell_mask[:period + 1] = False

        buy_records, buy_pending = convert_signals_to_records(
            series=series,
            condition_mask=buy_mask,
            strategy_id="bollinger_close_in",
            strategy_sub_id="bb_reversal_buy",
            direction="BUY",
            ref_prices=lower,
        )

        sell_records, sell_pending = convert_signals_to_records(
            series=series,
            condition_mask=sell_mask,
            strategy_id="bollinger_close_in",
            strategy_sub_id="bb_reversal_sell",
            direction="SELL",
            ref_prices=upper,
        )

        self.pending_signals.extend(buy_pending + sell_pending)
        return buy_records, sell_records

    def generate_keltner_squeeze(
        self,
        series: OHLCVSeries,
        period: int = 20,
        bb_mult: float = 2.0,
        kc_mult: float = 1.5,
    ) -> Tuple[List[SignalRecord], List[SignalRecord]]:
        """
        Keltner Squeeze Breakout Strategy.
        - Squeeze is ON when Bollinger Bands are completely inside Keltner Channel.
        - Breakout fires when BB leaves KC (Squeeze turns OFF), signaled with momentum.
        """
        n = series.length
        if n < period + 2:
            return [], []

        sma = compute_sma(series.close, period)
        std = compute_rolling_std(series.close, period)
        atr = compute_atr(series.high, series.low, series.close, period)

        bb_upper = sma + bb_mult * std
        bb_lower = sma - bb_mult * std

        kc_upper = sma + kc_mult * atr
        kc_lower = sma - kc_mult * atr

        # Squeeze definition: BB inside KC
        squeeze_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)
        prev_squeeze = np.roll(squeeze_on, 1)

        # Fired when previous bar was in squeeze and current is out
        squeeze_fired = prev_squeeze & (~squeeze_on)

        # Momentum direction: close > sma or momentum positive
        mom = series.close - np.roll(series.close, 5)

        buy_mask = squeeze_fired & (mom > 0) & (series.close > sma)
        sell_mask = squeeze_fired & (mom < 0) & (series.close < sma)

        buy_mask[:period + 5] = False
        sell_mask[:period + 5] = False

        buy_records, buy_pending = convert_signals_to_records(
            series=series,
            condition_mask=buy_mask,
            strategy_id="keltner_squeeze",
            strategy_sub_id="squeeze_breakout_buy",
            direction="BUY",
            ref_prices=kc_upper,
        )

        sell_records, sell_pending = convert_signals_to_records(
            series=series,
            condition_mask=sell_mask,
            strategy_id="keltner_squeeze",
            strategy_sub_id="squeeze_breakout_sell",
            direction="SELL",
            ref_prices=kc_lower,
        )

        self.pending_signals.extend(buy_pending + sell_pending)
        return buy_records, sell_records

    def generate_zscore_extreme(
        self,
        series: OHLCVSeries,
        period: int = 20,
        threshold: float = 2.0,
    ) -> Tuple[List[SignalRecord], List[SignalRecord]]:
        """
        Price Z-Score Reversal from Extremes.
        - BUY (Fundo): Z[t-1] < -threshold and Z[t] > Z[t-1] (bottom inflection).
        - SELL (Topo): Z[t-1] > +threshold and Z[t] < Z[t-1] (top inflection).
        """
        n = series.length
        if n < period + 2:
            return [], []

        sma = compute_sma(series.close, period)
        std = compute_rolling_std(series.close, period)

        zscore = np.divide(series.close - sma, std, out=np.zeros_like(sma), where=std > 0)
        prev_z = np.roll(zscore, 1)

        valid = ~np.isnan(sma) & (std > 0)

        buy_mask = valid & (prev_z < -threshold) & (zscore > prev_z)
        sell_mask = valid & (prev_z > threshold) & (zscore < prev_z)

        buy_mask[:period + 2] = False
        sell_mask[:period + 2] = False

        buy_records, buy_pending = convert_signals_to_records(
            series=series,
            condition_mask=buy_mask,
            strategy_id="zscore_extreme",
            strategy_sub_id="zscore_bottom_buy",
            direction="BUY",
            ref_prices=sma - threshold * std,
        )

        sell_records, sell_pending = convert_signals_to_records(
            series=series,
            condition_mask=sell_mask,
            strategy_id="zscore_extreme",
            strategy_sub_id="zscore_top_sell",
            direction="SELL",
            ref_prices=sma + threshold * std,
        )

        self.pending_signals.extend(buy_pending + sell_pending)
        return buy_records, sell_records



