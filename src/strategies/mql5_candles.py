"""
Vectorized MQL5 Candlestick Pattern Engine (based on MQL5 Article 101 - CCandlePattern).
Detects:
- 14 classic bullish reversal patterns (Fundos / BUY) using 12-period AvgBody & SMA(20) downtrend (Close < SMA(20)).
- 14 classic bearish reversal patterns (Topos / SELL) using 12-period AvgBody & SMA(20) uptrend (Close > SMA(20)).

All confirmed patterns at bar t execute strictly at Open[t + 1] (Zero Look-Ahead Bias).
If a pattern forms on the final bar (t == len - 1), it is registered as a pending alert.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from .base import OHLCVSeries, SignalRecord, ReferenceLineSegment


class MQL5CandleEngine:
    """
    Vectorized detector for 14 bullish + 14 bearish MQL5 CCandlePattern formations:
      Bullish Patterns (direction="BUY"):
        - hammer
        - inverted_hammer
        - bullish_engulfing
        - piercing_line
        - morning_star
        - bullish_harami
        - three_inside_up
        - three_outside_up
        - three_white_soldiers
        - tweezer_bottom
        - dragonfly_doji
        - abandoned_baby_bullish
        - bullish_kicker
        - climactic_pinbar
      Bearish Patterns (direction="SELL"):
        - shooting_star
        - hanging_man
        - bearish_engulfing
        - dark_cloud_cover
        - evening_star
        - bearish_harami
        - three_inside_down
        - three_outside_down
        - three_black_crows
        - tweezer_top
        - gravestone_doji
        - abandoned_baby_bearish
        - bearish_kicker
        - climactic_bearish_pinbar
    """

    BULLISH_PATTERNS = (
        "hammer",
        "inverted_hammer",
        "bullish_engulfing",
        "piercing_line",
        "morning_star",
        "bullish_harami",
        "three_inside_up",
        "three_outside_up",
        "three_white_soldiers",
        "tweezer_bottom",
        "dragonfly_doji",
        "abandoned_baby_bullish",
        "bullish_kicker",
        "climactic_pinbar",
    )

    BEARISH_PATTERNS = (
        "shooting_star",
        "hanging_man",
        "bearish_engulfing",
        "dark_cloud_cover",
        "evening_star",
        "bearish_harami",
        "three_inside_down",
        "three_outside_down",
        "three_black_crows",
        "tweezer_top",
        "gravestone_doji",
        "abandoned_baby_bearish",
        "bearish_kicker",
        "climactic_bearish_pinbar",
    )

    PATTERNS = BULLISH_PATTERNS + BEARISH_PATTERNS

    def __init__(self, body_ma_period: int = 12, trend_ma_period: int = 20) -> None:
        self.body_ma_period = int(body_ma_period)
        self.trend_ma_period = int(trend_ma_period)
        self.pending_signals: List[Dict[str, Any]] = []

    @staticmethod
    def _shift(arr: np.ndarray, k: int) -> np.ndarray:
        res = np.full_like(arr, np.nan, dtype=np.float64)
        if k == 0:
            return arr.copy()
        if len(arr) > k:
            res[k:] = arr[:-k]
        return res

    def compute_pattern_masks(self, series: OHLCVSeries) -> Dict[str, np.ndarray]:
        """
        Computes boolean masks (length N) for all 14 bullish and 14 bearish candlestick patterns.
        """
        n = series.length
        if n == 0:
            return {p: np.zeros(0, dtype=bool) for p in self.PATTERNS}

        o0 = series.open
        h0 = series.high
        l0 = series.low
        c0 = series.close
        v0 = series.volume

        body0 = np.abs(c0 - o0)
        avg_body0 = (
            pd.Series(body0)
            .rolling(window=self.body_ma_period, min_periods=1)
            .mean()
            .to_numpy(dtype=np.float64)
        )
        sma_trend0 = (
            pd.Series(c0)
            .rolling(window=self.trend_ma_period, min_periods=1)
            .mean()
            .to_numpy(dtype=np.float64)
        )
        sma_vol0 = (
            pd.Series(v0)
            .rolling(window=20, min_periods=1)
            .mean()
            .to_numpy(dtype=np.float64)
        )

        downtrend = c0 < sma_trend0
        uptrend = c0 > sma_trend0

        o1 = self._shift(o0, 1)
        h1 = self._shift(h0, 1)
        l1 = self._shift(l0, 1)
        c1 = self._shift(c0, 1)
        body1 = np.abs(c1 - o1)

        o2 = self._shift(o0, 2)
        h2 = self._shift(h0, 2)
        l2 = self._shift(l0, 2)
        c2 = self._shift(c0, 2)
        body2 = np.abs(c2 - o2)
        avg_body2 = self._shift(avg_body0, 2)

        upper_shadow0 = h0 - np.maximum(o0, c0)
        lower_shadow0 = np.minimum(o0, c0) - l0
        eff_body0 = np.maximum(body0, 1e-6)

        upper_shadow1 = h1 - np.maximum(o1, c1)
        lower_shadow1 = np.minimum(o1, c1) - l1
        eff_body1 = np.maximum(body1, 1e-6)

        # -----------------------------
        # 14 BULLISH PATTERNS (BUY)
        # -----------------------------
        hammer_mask = (
            downtrend
            & (lower_shadow0 >= 2.0 * eff_body0)
            & (upper_shadow0 <= 0.2 * eff_body0)
            & ((h0 - l0) >= 0.5 * avg_body0)
        )
        inverted_hammer_mask = (
            downtrend
            & (upper_shadow0 >= 2.0 * eff_body0)
            & (lower_shadow0 <= 0.3 * eff_body0)
            & ((h0 - l0) >= 0.5 * avg_body0)
        )
        bullish_engulfing_mask = (
            downtrend
            & (c1 < o1)
            & (c0 > o0)
            & (o0 <= c1)
            & (c0 >= o1)
            & (body0 > body1)
        )
        piercing_line_mask = (
            downtrend
            & (c1 < o1)
            & (body1 > 0.5 * avg_body0)
            & (o0 < l1)
            & (c0 > 0.5 * (o1 + c1))
            & (c0 < o1)
        )
        mid2 = 0.5 * (o2 + c2)
        morning_star_mask = (
            downtrend
            & (c2 < o2)
            & (body2 > 0.5 * avg_body2)
            & (body1 < 0.5 * avg_body2)
            & (np.maximum(o1, c1) < np.minimum(o2, c2))
            & (c0 > o0)
            & (c0 > mid2)
        )
        bullish_harami_mask = (
            downtrend
            & (c1 < o1)
            & (body1 > 0.5 * avg_body0)
            & (o0 >= c1)
            & (c0 <= o1)
            & (body0 < body1)
        )
        three_inside_up_mask = (
            downtrend
            & (c2 < o2)
            & (body2 > 0.5 * avg_body2)
            & (o1 >= c2)
            & (c1 <= o2)
            & (body1 < body2)
            & (c0 > o0)
            & (c0 > mid2)
        )
        engulf_prev_bull = (
            (c2 < o2)
            & (c1 > o1)
            & (o1 <= c2)
            & (c1 >= o2)
            & (body1 > body2)
        )
        three_outside_up_mask = (
            downtrend
            & engulf_prev_bull
            & (c0 > o0)
            & (c0 > c1)
        )
        three_white_soldiers_mask = (
            downtrend
            & (c2 > o2)
            & (c1 > o1)
            & (c0 > o0)
            & (c1 > c2)
            & (c0 > c1)
            & (o1 >= o2)
            & (o1 <= c2)
            & (o0 >= o1)
            & (o0 <= c1)
        )
        tweezer_bottom_mask = (
            downtrend
            & (c1 < o1)
            & (c0 > o0)
            & (np.abs(l0 - l1) <= np.maximum(0.0015 * c0, 1e-4))
        )
        dragonfly_doji_mask = (
            downtrend
            & (body0 <= 0.1 * (h0 - l0 + 1e-6))
            & (upper_shadow0 <= 0.15 * (h0 - l0 + 1e-6))
            & (lower_shadow0 >= 0.6 * (h0 - l0 + 1e-6))
            & ((h0 - l0) >= 0.5 * avg_body0)
        )
        abandoned_baby_bull_mask = (
            downtrend
            & (o2 - c2 > 0.5 * avg_body2)
            & (body1 <= 0.15 * (h1 - l1 + 1e-6))
            & (h1 < l2)
            & (l0 > h1)
            & (c0 > o0)
        )
        bullish_kicker_mask = (
            downtrend
            & (c1 < o1)
            & (o0 >= o1)
            & (c0 > o0)
            & (body0 > 0.5 * avg_body0)
        )
        climactic_pinbar_mask = (
            downtrend
            & (lower_shadow0 >= 2.5 * eff_body0)
            & (upper_shadow0 <= 0.4 * eff_body0)
            & (v0 >= 1.5 * sma_vol0)
        )

        # -----------------------------
        # 14 BEARISH PATTERNS (SELL)
        # -----------------------------
        # 1. Shooting Star (Estrela Cadente)
        shooting_star_mask = (
            uptrend
            & (upper_shadow0 >= 2.0 * eff_body0)
            & (lower_shadow0 <= 0.2 * eff_body0)
            & ((h0 - l0) >= 0.5 * avg_body0)
        )

        # 2. Hanging Man (Enforcado)
        hanging_man_mask = (
            uptrend
            & (lower_shadow0 >= 2.0 * eff_body0)
            & (upper_shadow0 <= 0.2 * eff_body0)
            & ((h0 - l0) >= 0.5 * avg_body0)
        )

        # 3. Bearish Engulfing (Engolfo de Baixa)
        bearish_engulfing_mask = (
            uptrend
            & (c1 > o1)
            & (c0 < o0)
            & (o0 >= c1)
            & (c0 <= o1)
            & (body0 > body1)
        )

        # 4. Dark Cloud Cover (Nuvem Negra)
        dark_cloud_cover_mask = (
            uptrend
            & (c1 > o1)
            & (body1 > 0.5 * avg_body0)
            & (o0 > h1)
            & (c0 < 0.5 * (o1 + c1))
            & (c0 > o1)
        )

        # 5. Evening Star (Estrela da Tarde)
        mid2_bear = 0.5 * (o2 + c2)
        evening_star_mask = (
            uptrend
            & (c2 > o2)
            & (body2 > 0.5 * avg_body2)
            & (body1 < 0.5 * avg_body2)
            & (np.minimum(o1, c1) > np.maximum(o2, c2))
            & (c0 < o0)
            & (c0 < mid2_bear)
        )

        # 6. Bearish Harami (Harami de Baixa)
        bearish_harami_mask = (
            uptrend
            & (c1 > o1)
            & (body1 > 0.5 * avg_body0)
            & (o0 <= c1)
            & (c0 >= o1)
            & (body0 < body1)
        )

        # 7. Three Inside Down (Três Por Dentro de Baixa)
        three_inside_down_mask = (
            uptrend
            & (c2 > o2)
            & (body2 > 0.5 * avg_body2)
            & (o1 <= c2)
            & (c1 >= o2)
            & (body1 < body2)
            & (c0 < o0)
            & (c0 < mid2_bear)
        )

        # 8. Three Outside Down (Três Por Fora de Baixa)
        engulf_prev_bear = (
            (c2 > o2)
            & (c1 < o1)
            & (o1 >= c2)
            & (c1 <= o2)
            & (body1 > body2)
        )
        three_outside_down_mask = (
            uptrend
            & engulf_prev_bear
            & (c0 < o0)
            & (c0 < c1)
        )

        # 9. Three Black Crows (Três Corvos Negros)
        three_black_crows_mask = (
            uptrend
            & (c2 < o2)
            & (c1 < o1)
            & (c0 < o0)
            & (c1 < c2)
            & (c0 < c1)
            & (o1 <= o2)
            & (o1 >= c2)
            & (o0 <= o1)
            & (o0 >= c1)
        )

        # 10. Tweezer Top (Pinça de Topo)
        tweezer_top_mask = (
            uptrend
            & (c1 > o1)
            & (c0 < o0)
            & (np.abs(h0 - h1) <= np.maximum(0.0015 * c0, 1e-4))
        )

        # 11. Gravestone Doji (Doji Lápide)
        gravestone_doji_mask = (
            uptrend
            & (body0 <= 0.1 * (h0 - l0 + 1e-6))
            & (lower_shadow0 <= 0.15 * (h0 - l0 + 1e-6))
            & (upper_shadow0 >= 0.6 * (h0 - l0 + 1e-6))
            & ((h0 - l0) >= 0.5 * avg_body0)
        )

        # 12. Abandoned Baby Bearish (Bebê Abandonado de Baixa)
        abandoned_baby_bear_mask = (
            uptrend
            & (c2 - o2 > 0.5 * avg_body2)
            & (body1 <= 0.15 * (h1 - l1 + 1e-6))
            & (l1 > h2)
            & (h0 < l1)
            & (c0 < o0)
        )

        # 13. Bearish Kicker (Chute de Baixa)
        bearish_kicker_mask = (
            uptrend
            & (c1 > o1)
            & (o0 <= o1)
            & (c0 < o0)
            & (body0 > 0.5 * avg_body0)
        )

        # 14. Climactic Bearish Pinbar (Pinbar Clímax de Topo com Volume)
        climactic_bearish_pinbar_mask = (
            uptrend
            & (upper_shadow0 >= 2.5 * eff_body0)
            & (lower_shadow0 <= 0.4 * eff_body0)
            & (v0 >= 1.5 * sma_vol0)
        )

        return {
            # Bullish
            "hammer": np.nan_to_num(hammer_mask, nan=False).astype(bool),
            "inverted_hammer": np.nan_to_num(inverted_hammer_mask, nan=False).astype(bool),
            "bullish_engulfing": np.nan_to_num(bullish_engulfing_mask, nan=False).astype(bool),
            "piercing_line": np.nan_to_num(piercing_line_mask, nan=False).astype(bool),
            "morning_star": np.nan_to_num(morning_star_mask, nan=False).astype(bool),
            "bullish_harami": np.nan_to_num(bullish_harami_mask, nan=False).astype(bool),
            "three_inside_up": np.nan_to_num(three_inside_up_mask, nan=False).astype(bool),
            "three_outside_up": np.nan_to_num(three_outside_up_mask, nan=False).astype(bool),
            "three_white_soldiers": np.nan_to_num(three_white_soldiers_mask, nan=False).astype(bool),
            "tweezer_bottom": np.nan_to_num(tweezer_bottom_mask, nan=False).astype(bool),
            "dragonfly_doji": np.nan_to_num(dragonfly_doji_mask, nan=False).astype(bool),
            "abandoned_baby_bullish": np.nan_to_num(abandoned_baby_bull_mask, nan=False).astype(bool),
            "bullish_kicker": np.nan_to_num(bullish_kicker_mask, nan=False).astype(bool),
            "climactic_pinbar": np.nan_to_num(climactic_pinbar_mask, nan=False).astype(bool),
            # Bearish
            "shooting_star": np.nan_to_num(shooting_star_mask, nan=False).astype(bool),
            "hanging_man": np.nan_to_num(hanging_man_mask, nan=False).astype(bool),
            "bearish_engulfing": np.nan_to_num(bearish_engulfing_mask, nan=False).astype(bool),
            "dark_cloud_cover": np.nan_to_num(dark_cloud_cover_mask, nan=False).astype(bool),
            "evening_star": np.nan_to_num(evening_star_mask, nan=False).astype(bool),
            "bearish_harami": np.nan_to_num(bearish_harami_mask, nan=False).astype(bool),
            "three_inside_down": np.nan_to_num(three_inside_down_mask, nan=False).astype(bool),
            "three_outside_down": np.nan_to_num(three_outside_down_mask, nan=False).astype(bool),
            "three_black_crows": np.nan_to_num(three_black_crows_mask, nan=False).astype(bool),
            "tweezer_top": np.nan_to_num(tweezer_top_mask, nan=False).astype(bool),
            "gravestone_doji": np.nan_to_num(gravestone_doji_mask, nan=False).astype(bool),
            "abandoned_baby_bearish": np.nan_to_num(abandoned_baby_bear_mask, nan=False).astype(bool),
            "bearish_kicker": np.nan_to_num(bearish_kicker_mask, nan=False).astype(bool),
            "climactic_bearish_pinbar": np.nan_to_num(climactic_bearish_pinbar_mask, nan=False).astype(bool),
        }

    def generate_signals(
        self,
        series: OHLCVSeries,
        pattern_filter: Optional[List[str]] = None,
        direction_filter: Optional[str] = None,
    ) -> Tuple[List[SignalRecord], List[ReferenceLineSegment]]:
        """
        Generates standardized SignalRecords for MQL5 candlestick patterns (BUY and SELL).
        Executes strictly at Open[t + 1]. Patterns confirmed on the last bar (t == len - 1)
        are stored in self.pending_signals without creating out-of-bounds execution indices.
        """
        signals: List[SignalRecord] = []
        self.pending_signals = []
        n = series.length
        if n == 0:
            return signals, []

        masks = self.compute_pattern_masks(series)
        open_arr = series.open

        for pattern_name, mask in masks.items():
            is_sell = pattern_name in self.BEARISH_PATTERNS
            direction = "SELL" if is_sell else "BUY"

            if direction_filter is not None and direction_filter != "ALL" and direction != direction_filter:
                continue

            if pattern_filter is not None and pattern_name not in pattern_filter:
                continue

            trigger_indices = np.flatnonzero(mask)
            total_pattern_signals = int(len(trigger_indices))

            for idx_val in trigger_indices:
                t = int(idx_val)
                if t + 1 < n:
                    signals.append(
                        SignalRecord(
                            strategy_id="mql5_candles",
                            strategy_sub_id=pattern_name,
                            direction=direction,
                            signal_bar_index=t,
                            execution_bar_index=t + 1,
                            execution_price=float(open_arr[t + 1]),
                            reference_line_price=None,
                            metadata={
                                "pattern": pattern_name,
                                "fill_type": "next_open",
                                "total_variant_signals": total_pattern_signals,
                            },
                        )
                    )
                else:
                    self.pending_signals.append(
                        {
                            "strategy_id": "mql5_candles",
                            "strategy_sub_id": pattern_name,
                            "direction": direction,
                            "signal_bar_index": t,
                            "reference_line_price": None,
                            "status": "AGUARDANDO_ABERTURA_T+1",
                        }
                    )

        return signals, []
