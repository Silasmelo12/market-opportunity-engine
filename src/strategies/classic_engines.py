"""
Classic Quantitative, Portfolio Rebalancing, Value Proxy, and Price Action Strategy Engines.
Implements:
BUY Engines (Fundos / direction="BUY"):
  1. dca_dynamic (DCA Dinâmico - Desvio Estatístico)
  2. rebal_rf_rv (Rebalanceamento Renda Fixa vs. Renda Variável)
  3. rebal_relative_strength (Rebalanceamento entre Ativos Variáveis - Z-Score)
  4. value_proxy (Análise Fundamentalista / Value Proxy com Fallback Quantitativo)
  5. price_action_double_bottom_bos (Fundo Duplo com Falha de Continuação + BOS)
  6. price_action_wyckoff_spring (Falso Rompimento de Mínima / Wyckoff Spring)

SELL Engines (Topos / direction="SELL"):
  1. sell_overbought_stat (Excesso Estatístico / Realização Parcial)
  2. sell_rebal_rv_rf (Rebalanceamento Variável -> Renda Fixa)
  3. sell_rebal_relative_strength (Exaustão de Força Relativa)
  4. sell_value_proxy (Prêmio Excessivo / Estiramento de Valuation)
  5. sell_double_top_bos (Topo Duplo + Quebra de Estrutura Bearish BOS)
  6. sell_wyckoff_upthrust (Varredura de Topo / Wyckoff Upthrust - UTAD)

All strategies are strictly causal (Zero Look-Ahead Bias) and execute at Open[t + 1].
Signals confirmed on the final bar (t == len - 1) are recorded in pending_signals.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from .base import OHLCVSeries, SignalRecord, ReferenceLineSegment


def compute_rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    """
    Computes causal Wilder/Rolling RSI(period) on a 1D float64 array.
    """
    n = len(close)
    if n < 2:
        return np.full(n, 50.0, dtype=np.float64)

    delta = np.zeros(n, dtype=np.float64)
    delta[1:] = np.diff(close)

    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=period).mean().to_numpy(dtype=np.float64)
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=period).mean().to_numpy(dtype=np.float64)

    rs = np.divide(avg_gain, avg_loss, out=np.full(n, np.nan, dtype=np.float64), where=avg_loss > 1e-12)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = np.where((avg_loss <= 1e-12) & (avg_gain > 0), 100.0, rsi)
    return rsi


def _detect_double_bottom_raw(
    open_prices: np.ndarray,
    high_prices: np.ndarray,
    low_prices: np.ndarray,
    close_prices: np.ndarray,
    window: int = 40,
) -> List[Tuple[int, int, int, float]]:
    """
    Detects classic raw double bottom breakout triggers (t, b1_idx, b2_idx, neckline).
    Returns list of tuples: (breakout_bar_t, b1_abs_index, b2_abs_index, neckline_price).
    """
    c = close_prices
    l = low_prices
    h = high_prices
    n = len(c)
    if n < 15:
        return []

    results: List[Tuple[int, int, int, float]] = []
    cooldown_until = -1

    for t in range(15, n):
        if t <= cooldown_until:
            continue

        start_idx = max(0, t - window)
        sub_lows = l[start_idx:t]
        sub_highs = h[start_idx:t]
        m = len(sub_lows)
        if m < 10:
            continue

        mid_split = m // 2
        b1_rel = int(np.argmin(sub_lows[:mid_split]))
        b1_low = sub_lows[b1_rel]

        second_start = max(mid_split, b1_rel + 3)
        if second_start >= m - 1:
            continue

        b2_rel = second_start + int(np.argmin(sub_lows[second_start:]))
        b2_low = sub_lows[b2_rel]

        if b2_rel <= b1_rel + 2:
            continue

        neckline = float(np.max(sub_highs[b1_rel + 1 : b2_rel]))
        if b1_low <= 0:
            continue
        rel_diff = (b2_low - b1_low) / b1_low
        is_valid_double_bottom = (-0.03 <= rel_diff <= 0.02) and (neckline > b1_low * 1.015)

        if is_valid_double_bottom and (c[t - 1] <= neckline) and (c[t] > neckline):
            b1_abs = start_idx + b1_rel
            b2_abs = start_idx + b2_rel
            results.append((t, b1_abs, b2_abs, neckline))
            cooldown_until = t + 10

    return results


def _detect_double_top_raw(
    open_prices: np.ndarray,
    high_prices: np.ndarray,
    low_prices: np.ndarray,
    close_prices: np.ndarray,
    window: int = 40,
) -> List[Tuple[int, int, int, float]]:
    """
    Detects classic raw double top breakdown triggers (t, t1_idx, t2_idx, neckline).
    Returns list of tuples: (breakout_bar_t, t1_abs_index, t2_abs_index, neckline_price).
    """
    c = close_prices
    l = low_prices
    h = high_prices
    n = len(c)
    if n < 15:
        return []

    results: List[Tuple[int, int, int, float]] = []
    cooldown_until = -1

    for t in range(15, n):
        if t <= cooldown_until:
            continue

        start_idx = max(0, t - window)
        sub_lows = l[start_idx:t]
        sub_highs = h[start_idx:t]
        m = len(sub_highs)
        if m < 10:
            continue

        mid_split = m // 2
        t1_rel = int(np.argmax(sub_highs[:mid_split]))
        t1_high = sub_highs[t1_rel]

        second_start = max(mid_split, t1_rel + 3)
        if second_start >= m - 1:
            continue

        t2_rel = second_start + int(np.argmax(sub_highs[second_start:]))
        t2_high = sub_highs[t2_rel]

        if t2_rel <= t1_rel + 2:
            continue

        neckline = float(np.min(sub_lows[t1_rel + 1 : t2_rel]))
        if t1_high <= 0:
            continue
        rel_diff = (t2_high - t1_high) / t1_high
        is_valid_double_top = (-0.02 <= rel_diff <= 0.03) and (neckline < t1_high * 0.985)

        if is_valid_double_top and (c[t - 1] >= neckline) and (c[t] < neckline):
            t1_abs = start_idx + t1_rel
            t2_abs = start_idx + t2_rel
            results.append((t, t1_abs, t2_abs, neckline))
            cooldown_until = t + 10

    return results


class ClassicStrategiesEngine:
    """
    Unified engine for 6 classic BUY + 6 classic SELL quantitative/price-action strategies.
    """

    BUY_STRATEGIES = (
        "dca_dynamic",
        "rebal_rf_rv",
        "rebal_relative_strength",
        "value_proxy",
        "price_action_double_bottom_bos",
        "price_action_wyckoff_spring",
    )

    SELL_STRATEGIES = (
        "sell_overbought_stat",
        "sell_rebal_rv_rf",
        "sell_rebal_relative_strength",
        "sell_value_proxy",
        "sell_double_top_bos",
        "sell_wyckoff_upthrust",
    )

    STRATEGIES = BUY_STRATEGIES + SELL_STRATEGIES

    def __init__(
        self,
        dca_std_k: float = 2.0,
        dca_rsi_threshold: float = 30.0,
        sell_rsi_threshold: float = 70.0,
        rf_rv_target_weight: float = 0.50,
        rf_rv_band_tol: float = 0.05,
        rel_zscore_threshold: float = -2.0,
        sell_rel_zscore_threshold: float = 2.0,
        wyckoff_lookback_n: int = 20,
    ) -> None:
        self.dca_std_k = float(dca_std_k)
        self.dca_rsi_threshold = float(dca_rsi_threshold)
        self.sell_rsi_threshold = float(sell_rsi_threshold)
        self.rf_rv_target_weight = float(rf_rv_target_weight)
        self.rf_rv_band_tol = float(rf_rv_band_tol)
        self.rel_zscore_threshold = float(rel_zscore_threshold)
        self.sell_rel_zscore_threshold = float(sell_rel_zscore_threshold)
        self.wyckoff_lookback_n = int(wyckoff_lookback_n)
        self.pending_signals: List[Dict[str, Any]] = []

    def _emit_from_mask(
        self,
        series: OHLCVSeries,
        mask: np.ndarray,
        strategy_id: str,
        strategy_sub_id: str,
        direction: str = "BUY",
        ref_prices: Optional[np.ndarray] = None,
        extra_meta: Optional[Dict[str, Any]] = None,
    ) -> List[SignalRecord]:
        signals: List[SignalRecord] = []
        n = series.length
        indices = np.flatnonzero(mask)
        total_sigs = int(len(indices))

        for idx_val in indices:
            t = int(idx_val)
            ref_val = float(ref_prices[t]) if (ref_prices is not None and not np.isnan(ref_prices[t])) else None
            if t + 1 < n:
                meta = {
                    "fill_type": "next_open",
                    "total_variant_signals": total_sigs,
                }
                if extra_meta:
                    meta.update(extra_meta)
                signals.append(
                    SignalRecord(
                        strategy_id=strategy_id,
                        strategy_sub_id=strategy_sub_id,
                        direction=direction,
                        signal_bar_index=t,
                        execution_bar_index=t + 1,
                        execution_price=float(series.open[t + 1]),
                        reference_line_price=ref_val,
                        metadata=meta,
                    )
                )
            else:
                self.pending_signals.append(
                    {
                        "strategy_id": strategy_id,
                        "strategy_sub_id": strategy_sub_id,
                        "direction": direction,
                        "signal_bar_index": t,
                        "reference_line_price": ref_val,
                        "status": "AGUARDANDO_ABERTURA_T+1",
                    }
                )
        return signals

    # -------------------------------------------------------------
    # BUY METHODS
    # -------------------------------------------------------------
    def run_dca_dynamic(self, series: OHLCVSeries) -> List[SignalRecord]:
        c = series.close
        s_close = pd.Series(c)
        sma200 = s_close.rolling(window=200, min_periods=20).mean().to_numpy(dtype=np.float64)
        std200 = s_close.rolling(window=200, min_periods=20).std(ddof=0).to_numpy(dtype=np.float64)
        lower_band = sma200 - self.dca_std_k * std200
        rsi14 = compute_rsi(c, period=14)

        cond_band = (~np.isnan(lower_band)) & (c < lower_band)
        cond_rsi = (~np.isnan(rsi14)) & (rsi14 < self.dca_rsi_threshold)
        raw_mask = cond_band | cond_rsi

        prev_mask = np.zeros(len(c), dtype=bool)
        prev_mask[1:] = raw_mask[:-1]
        edge_mask = raw_mask & (~prev_mask)

        return self._emit_from_mask(
            series=series,
            mask=edge_mask,
            strategy_id="dca_dynamic",
            strategy_sub_id="dca_dynamic",
            direction="BUY",
            ref_prices=lower_band,
        )

    def run_rebal_rf_rv(self, series: OHLCVSeries) -> List[SignalRecord]:
        c = series.close
        n = len(c)
        if n < 10:
            return []

        mask = np.zeros(n, dtype=bool)
        rf_rate = (1.0 + 0.08) ** (1.0 / 52.0) - 1.0 if series.interval == "1wk" else (1.0 + 0.08) ** (1.0 / 252.0) - 1.0
        w_target = self.rf_rv_target_weight
        threshold_w = w_target - self.rf_rv_band_tol

        rv_val = w_target * 100.0
        rf_val = (1.0 - w_target) * 100.0

        for t in range(1, n):
            ret_rv = (c[t] / c[t - 1]) - 1.0 if c[t - 1] > 0 else 0.0
            rv_val = rv_val * (1.0 + ret_rv)
            rf_val = rf_val * (1.0 + rf_rate)
            total_val = rv_val + rf_val

            if total_val > 0:
                current_w = rv_val / total_val
                if current_w <= threshold_w:
                    mask[t] = True
                    rv_val = total_val * w_target
                    rf_val = total_val * (1.0 - w_target)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="rebal_rf_rv",
            strategy_sub_id="rebal_rf_rv",
            direction="BUY",
        )

    def run_rebal_relative_strength(
        self,
        series: OHLCVSeries,
        benchmark_close: Optional[np.ndarray] = None,
    ) -> List[SignalRecord]:
        c = series.close
        n = len(c)
        if n < 20:
            return []

        if benchmark_close is not None and len(benchmark_close) == n:
            bench = np.where(benchmark_close > 0, benchmark_close, np.nan)
        else:
            bench = pd.Series(c).ewm(span=120, min_periods=10).mean().to_numpy(dtype=np.float64)

        ratio = np.divide(c, bench, out=np.ones(n, dtype=np.float64), where=bench > 0)
        s_ratio = pd.Series(ratio)
        mean60 = s_ratio.rolling(window=60, min_periods=20).mean().to_numpy(dtype=np.float64)
        std60 = s_ratio.rolling(window=60, min_periods=20).std(ddof=0).to_numpy(dtype=np.float64)

        zscore = np.divide(ratio - mean60, std60, out=np.zeros(n, dtype=np.float64), where=std60 > 1e-12)
        z_prev = np.zeros(n, dtype=np.float64)
        z_prev[1:] = zscore[:-1]

        inflection = (
            ((z_prev <= self.rel_zscore_threshold) & (zscore > z_prev))
            | ((zscore <= self.rel_zscore_threshold) & (series.close > series.open))
        )
        prev_inflection = np.zeros(n, dtype=bool)
        prev_inflection[1:] = inflection[:-1]
        mask = inflection & (~prev_inflection)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="rebal_relative_strength",
            strategy_sub_id="rebal_relative_strength",
            direction="BUY",
        )

    def run_value_proxy(self, series: OHLCVSeries) -> List[SignalRecord]:
        c = series.close
        n = len(c)
        if n < 20:
            return []

        sma200 = pd.Series(c).rolling(window=200, min_periods=20).mean().to_numpy(dtype=np.float64)
        ticker_up = series.ticker.upper()
        is_crypto_or_comm = ticker_up.endswith("-USD") or ticker_up.endswith("=F")

        has_dividends = (
            (not is_crypto_or_comm)
            and (series.dy_rolling_12m is not None)
            and (len(series.dy_rolling_12m) == n)
            and (np.nanmax(series.dy_rolling_12m) > 0.0)
        )

        if has_dividends:
            dy = series.dy_rolling_12m
            p80 = pd.Series(dy).rolling(window=252, min_periods=20).quantile(0.80).to_numpy(dtype=np.float64)
            raw_cond = (~np.isnan(p80)) & (~np.isnan(sma200)) & (dy >= p80) & (dy > 0) & (c < sma200)
            mode_used = "dy_rolling_sma200"
        else:
            mayer = np.divide(c, sma200, out=np.ones(n, dtype=np.float64), where=sma200 > 0)
            p15 = pd.Series(mayer).rolling(window=252, min_periods=20).quantile(0.15).to_numpy(dtype=np.float64)
            raw_cond = (~np.isnan(p15)) & (~np.isnan(sma200)) & (mayer <= p15) & (mayer < 0.95)
            mode_used = "mayer_multiple_fallback"

        prev_cond = np.zeros(n, dtype=bool)
        prev_cond[1:] = raw_cond[:-1]
        mask = raw_cond & (~prev_cond)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="value_proxy",
            strategy_sub_id="value_proxy",
            direction="BUY",
            ref_prices=sma200,
            extra_meta={"valuation_mode": mode_used},
        )

    def run_double_bottom_bos(self, series: OHLCVSeries) -> List[SignalRecord]:
        c = series.close
        l = series.low
        h = series.high
        o = series.open
        n = len(c)
        mask = np.zeros(n, dtype=bool)
        necklines = np.full(n, np.nan, dtype=np.float64)

        raw_signals = _detect_double_bottom_raw(o, h, l, c)
        for t, b1_idx, b2_idx, neckline in raw_signals:
            mask[t] = True
            necklines[t] = neckline

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="price_action_double_bottom_bos",
            strategy_sub_id="double_bottom_bos",
            direction="BUY",
            ref_prices=necklines,
        )

    def run_wyckoff_spring(self, series: OHLCVSeries) -> List[SignalRecord]:
        c = series.close
        l = series.low
        v = series.volume
        n = len(c)
        if n <= self.wyckoff_lookback_n:
            return []

        support_low = (
            pd.Series(l)
            .shift(1)
            .rolling(window=self.wyckoff_lookback_n, min_periods=5)
            .min()
            .to_numpy(dtype=np.float64)
        )
        vol_sma20 = (
            pd.Series(v)
            .rolling(window=20, min_periods=5)
            .mean()
            .to_numpy(dtype=np.float64)
        )

        has_volume = np.nanmax(v) > 0
        vol_ok = (v > vol_sma20) if has_volume else np.ones(n, dtype=bool)

        mask = (
            (~np.isnan(support_low))
            & (l < support_low)
            & (c > support_low)
            & vol_ok
        )

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="price_action_wyckoff_spring",
            strategy_sub_id="wyckoff_spring",
            direction="BUY",
            ref_prices=support_low,
        )

    # -------------------------------------------------------------
    # SELL METHODS (TOPOS)
    # -------------------------------------------------------------
    def run_sell_overbought_stat(self, series: OHLCVSeries) -> List[SignalRecord]:
        """
        1. Excesso Estatístico / Realização Parcial (SELL):
        Close[t] > SMA(200)[t] + k * StdDev(200)[t] OR RSI(14)[t] > 70.
        """
        c = series.close
        s_close = pd.Series(c)
        sma200 = s_close.rolling(window=200, min_periods=20).mean().to_numpy(dtype=np.float64)
        std200 = s_close.rolling(window=200, min_periods=20).std(ddof=0).to_numpy(dtype=np.float64)
        upper_band = sma200 + self.dca_std_k * std200
        rsi14 = compute_rsi(c, period=14)

        cond_band = (~np.isnan(upper_band)) & (c > upper_band)
        cond_rsi = (~np.isnan(rsi14)) & (rsi14 > self.sell_rsi_threshold)
        raw_mask = cond_band | cond_rsi

        prev_mask = np.zeros(len(c), dtype=bool)
        prev_mask[1:] = raw_mask[:-1]
        edge_mask = raw_mask & (~prev_mask)

        return self._emit_from_mask(
            series=series,
            mask=edge_mask,
            strategy_id="sell_overbought_stat",
            strategy_sub_id="sell_overbought_stat",
            direction="SELL",
            ref_prices=upper_band,
        )

    def run_sell_rebal_rv_rf(self, series: OHLCVSeries) -> List[SignalRecord]:
        """
        2. Rebalanceamento Variável -> Renda Fixa (SELL):
        Triggers when equity run-up pushes equity weight >= target + tolerance (+5%).
        """
        c = series.close
        n = len(c)
        if n < 10:
            return []

        mask = np.zeros(n, dtype=bool)
        rf_rate = (1.0 + 0.08) ** (1.0 / 52.0) - 1.0 if series.interval == "1wk" else (1.0 + 0.08) ** (1.0 / 252.0) - 1.0
        w_target = self.rf_rv_target_weight
        threshold_w = w_target + self.rf_rv_band_tol

        rv_val = w_target * 100.0
        rf_val = (1.0 - w_target) * 100.0

        for t in range(1, n):
            ret_rv = (c[t] / c[t - 1]) - 1.0 if c[t - 1] > 0 else 0.0
            rv_val = rv_val * (1.0 + ret_rv)
            rf_val = rf_val * (1.0 + rf_rate)
            total_val = rv_val + rf_val

            if total_val > 0:
                current_w = rv_val / total_val
                if current_w >= threshold_w:
                    mask[t] = True
                    rv_val = total_val * w_target
                    rf_val = total_val * (1.0 - w_target)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="sell_rebal_rv_rf",
            strategy_sub_id="sell_rebal_rv_rf",
            direction="SELL",
        )

    def run_sell_rebal_relative_strength(
        self,
        series: OHLCVSeries,
        benchmark_close: Optional[np.ndarray] = None,
    ) -> List[SignalRecord]:
        """
        3. Exaustão de Força Relativa (SELL):
        Z-Score of Ratio = Close / Benchmark reaches >= +2.0 with negative inflection.
        """
        c = series.close
        n = len(c)
        if n < 20:
            return []

        if benchmark_close is not None and len(benchmark_close) == n:
            bench = np.where(benchmark_close > 0, benchmark_close, np.nan)
        else:
            bench = pd.Series(c).ewm(span=120, min_periods=10).mean().to_numpy(dtype=np.float64)

        ratio = np.divide(c, bench, out=np.ones(n, dtype=np.float64), where=bench > 0)
        s_ratio = pd.Series(ratio)
        mean60 = s_ratio.rolling(window=60, min_periods=20).mean().to_numpy(dtype=np.float64)
        std60 = s_ratio.rolling(window=60, min_periods=20).std(ddof=0).to_numpy(dtype=np.float64)

        zscore = np.divide(ratio - mean60, std60, out=np.zeros(n, dtype=np.float64), where=std60 > 1e-12)
        z_prev = np.zeros(n, dtype=np.float64)
        z_prev[1:] = zscore[:-1]

        inflection = (
            ((z_prev >= self.sell_rel_zscore_threshold) & (zscore < z_prev))
            | ((zscore >= self.sell_rel_zscore_threshold) & (series.close < series.open))
        )
        prev_inflection = np.zeros(n, dtype=bool)
        prev_inflection[1:] = inflection[:-1]
        mask = inflection & (~prev_inflection)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="sell_rebal_relative_strength",
            strategy_sub_id="sell_rebal_relative_strength",
            direction="SELL",
        )

    def run_sell_value_proxy(self, series: OHLCVSeries) -> List[SignalRecord]:
        """
        4. Prêmio Excessivo / Estiramento de Valuation (SELL):
        - Mayer Multiple (Close / SMA(200)) >= causal historical 85th percentile (and > 1.25)
        - Or DY Rolling 12m <= causal historical 20th percentile (and Close > SMA(200)).
        """
        c = series.close
        n = len(c)
        if n < 20:
            return []

        sma200 = pd.Series(c).rolling(window=200, min_periods=20).mean().to_numpy(dtype=np.float64)
        ticker_up = series.ticker.upper()
        is_crypto_or_comm = ticker_up.endswith("-USD") or ticker_up.endswith("=F")

        has_dividends = (
            (not is_crypto_or_comm)
            and (series.dy_rolling_12m is not None)
            and (len(series.dy_rolling_12m) == n)
            and (np.nanmax(series.dy_rolling_12m) > 0.0)
        )

        if has_dividends:
            dy = series.dy_rolling_12m
            p20 = pd.Series(dy).rolling(window=252, min_periods=20).quantile(0.20).to_numpy(dtype=np.float64)
            raw_cond = (~np.isnan(p20)) & (~np.isnan(sma200)) & (dy <= p20) & (c > sma200)
            mode_used = "dy_rolling_low_sma200"
        else:
            mayer = np.divide(c, sma200, out=np.ones(n, dtype=np.float64), where=sma200 > 0)
            p85 = pd.Series(mayer).rolling(window=252, min_periods=20).quantile(0.85).to_numpy(dtype=np.float64)
            raw_cond = (~np.isnan(p85)) & (~np.isnan(sma200)) & (mayer >= p85) & (mayer > 1.20)
            mode_used = "mayer_multiple_top"

        prev_cond = np.zeros(n, dtype=bool)
        prev_cond[1:] = raw_cond[:-1]
        mask = raw_cond & (~prev_cond)

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="sell_value_proxy",
            strategy_sub_id="sell_value_proxy",
            direction="SELL",
            ref_prices=sma200,
            extra_meta={"valuation_mode": mode_used},
        )

    def run_sell_double_top_bos(self, series: OHLCVSeries) -> List[SignalRecord]:
        """
        5. Topo Duplo + Quebra de Estrutura Bearish BOS (SELL):
        Detects two tops in a resistance zone confirmed by a close below intermediate trough (Neckline / BOS).
        """
        c = series.close
        l = series.low
        h = series.high
        o = series.open
        n = len(c)
        mask = np.zeros(n, dtype=bool)
        necklines = np.full(n, np.nan, dtype=np.float64)

        raw_signals = _detect_double_top_raw(o, h, l, c)
        for t, t1_idx, t2_idx, neckline in raw_signals:
            mask[t] = True
            necklines[t] = neckline

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="sell_double_top_bos",
            strategy_sub_id="sell_double_top_bos",
            direction="SELL",
            ref_prices=necklines,
        )

    def run_sell_wyckoff_upthrust(self, series: OHLCVSeries) -> List[SignalRecord]:
        """
        6. Varredura de Topo / Wyckoff Upthrust - UTAD (SELL):
        High pierces above N-bar resistance (High[t] > max(High[t-N : t]))
        with immediate rejection closing below resistance (Close[t] < max(High[t-N : t]))
        AND volume > 20-bar average.
        """
        c = series.close
        h = series.high
        v = series.volume
        n = len(c)
        if n <= self.wyckoff_lookback_n:
            return []

        res_high = (
            pd.Series(h)
            .shift(1)
            .rolling(window=self.wyckoff_lookback_n, min_periods=5)
            .max()
            .to_numpy(dtype=np.float64)
        )
        vol_sma20 = (
            pd.Series(v)
            .rolling(window=20, min_periods=5)
            .mean()
            .to_numpy(dtype=np.float64)
        )

        has_volume = np.nanmax(v) > 0
        vol_ok = (v > vol_sma20) if has_volume else np.ones(n, dtype=bool)

        mask = (
            (~np.isnan(res_high))
            & (h > res_high)
            & (c < res_high)
            & vol_ok
        )

        return self._emit_from_mask(
            series=series,
            mask=mask,
            strategy_id="sell_wyckoff_upthrust",
            strategy_sub_id="sell_wyckoff_upthrust",
            direction="SELL",
            ref_prices=res_high,
        )

    def generate_signals(
        self,
        series: OHLCVSeries,
        strategy_filter: Optional[List[str]] = None,
        direction_filter: Optional[str] = None,
        benchmark_close: Optional[np.ndarray] = None,
    ) -> Tuple[List[SignalRecord], List[ReferenceLineSegment]]:
        """
        Runs classic strategy families (BUY and SELL) and returns standardized signals.
        """
        self.pending_signals = []
        all_signals: List[SignalRecord] = []
        if series.length == 0:
            return all_signals, []

        buy_runners = [
            ("dca_dynamic", lambda: self.run_dca_dynamic(series)),
            ("rebal_rf_rv", lambda: self.run_rebal_rf_rv(series)),
            ("rebal_relative_strength", lambda: self.run_rebal_relative_strength(series, benchmark_close)),
            ("value_proxy", lambda: self.run_value_proxy(series)),
            ("price_action_double_bottom_bos", lambda: self.run_double_bottom_bos(series)),
            ("price_action_wyckoff_spring", lambda: self.run_wyckoff_spring(series)),
        ]

        sell_runners = [
            ("sell_overbought_stat", lambda: self.run_sell_overbought_stat(series)),
            ("sell_rebal_rv_rf", lambda: self.run_sell_rebal_rv_rf(series)),
            ("sell_rebal_relative_strength", lambda: self.run_sell_rebal_relative_strength(series, benchmark_close)),
            ("sell_value_proxy", lambda: self.run_sell_value_proxy(series)),
            ("sell_double_top_bos", lambda: self.run_sell_double_top_bos(series)),
            ("sell_wyckoff_upthrust", lambda: self.run_sell_wyckoff_upthrust(series)),
        ]

        active_runners = []
        if direction_filter is None or direction_filter == "ALL":
            active_runners = buy_runners + sell_runners
        elif direction_filter == "BUY":
            active_runners = buy_runners
        elif direction_filter == "SELL":
            active_runners = sell_runners

        for strat_id, fn in active_runners:
            if strategy_filter is not None and strat_id not in strategy_filter:
                continue
            all_signals.extend(fn())

        return all_signals, []
