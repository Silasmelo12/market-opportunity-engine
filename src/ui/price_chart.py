"""
Price Candlestick Chart component with support for Lightweight Charts and Plotly WebGL fallback.
Renders OHLCV candlesticks, reference line segments, and buy markers.
Guarantees clean 'YYYY-MM-DD' dates and explicit conversion of numpy floats/ints to native Python types.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from ..strategies.base import OHLCVSeries, SignalRecord, ReferenceLineSegment

try:
    from streamlit_lightweight_charts import renderLightweightCharts
    LIGHTWEIGHT_AVAILABLE = True
except ImportError:
    LIGHTWEIGHT_AVAILABLE = False


def _format_date(ts: Any) -> str:
    """Formats a numpy timestamp to 'YYYY-MM-DD' string."""
    dt = pd.to_datetime(ts)
    return dt.strftime("%Y-%m-%d")


def render_price_chart_plotly(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    reference_lines: List[ReferenceLineSegment],
    max_reference_lines: int = 50,
) -> None:
    """
    Renders high-performance Plotly WebGL Candlestick chart with Reference Lines and Buy Markers.
    """
    dates = [_format_date(ts) for ts in series.timestamps]

    fig = go.Figure()

    # 1. Candlestick series
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=series.open.tolist(),
            high=series.high.tolist(),
            low=series.low.tolist(),
            close=series.close.tolist(),
            name=series.ticker,
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        )
    )

    # 2. Reference Line Segments (Proprietary Strategy)
    # Take latest active or executed reference lines to avoid visual clutter
    filtered_lines = [
        line for line in reference_lines
        if line.status in ("NEGATED_EXECUTED", "ACTIVE_PENDING")
    ][-max_reference_lines:]

    for line in filtered_lines:
        if line.start_bar_index >= len(dates):
            continue
        start_d = dates[line.start_bar_index]
        end_idx = min(line.end_bar_index, len(dates) - 1)
        end_d = dates[end_idx]
        color = "#2962FF" if line.status == "NEGATED_EXECUTED" else "#FF9800"
        dash_style = "dash" if line.status == "ACTIVE_PENDING" else "solid"

        fig.add_shape(
            type="line",
            x0=start_d,
            y0=float(line.price_level),
            x1=end_d,
            y1=float(line.price_level),
            line=dict(color=color, width=1.5, dash=dash_style),
        )

    # 3. Buy Markers
    if signals:
        closed_x, closed_y, closed_text = [], [], []
        open_x, open_y, open_text = [], [], []

        for sig in signals:
            idx = sig.execution_bar_index
            if idx >= len(dates):
                continue
            d = dates[idx]
            p = float(sig.execution_price)
            is_open = sig.metadata.get("is_open", False) if sig.metadata else False

            info = f"{sig.strategy_sub_id}<br>Preço: {p:.2f}"
            if is_open:
                open_x.append(d)
                open_y.append(p)
                open_text.append(f"Em Aberto: {info}")
            else:
                closed_x.append(d)
                closed_y.append(p)
                closed_text.append(info)

        if closed_x:
            fig.add_trace(
                go.Scatter(
                    x=closed_x,
                    y=closed_y,
                    mode="markers",
                    marker=dict(symbol="triangle-up", size=10, color="#00E676"),
                    name="Compras Concluídas",
                    text=closed_text,
                    hoverinfo="text+x+y",
                )
            )

        if open_x:
            fig.add_trace(
                go.Scatter(
                    x=open_x,
                    y=open_y,
                    mode="markers",
                    marker=dict(symbol="circle", size=9, color="#FFD600", line=dict(width=1, color="#000")),
                    name="Compras em Aberto",
                    text=open_text,
                    hoverinfo="text+x+y",
                )
            )

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=580,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Preço"),
        xaxis=dict(title="Data"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_price_chart_lightweight(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    reference_lines: List[ReferenceLineSegment],
) -> bool:
    """
    Renders TradingView Canvas via streamlit-lightweight-charts.
    Returns True if successfully rendered, False on fallback.
    """
    if not LIGHTWEIGHT_AVAILABLE:
        return False

    try:
        dates = [_format_date(ts) for ts in series.timestamps]
        candles_data = []

        for i in range(series.length):
            candles_data.append(
                {
                    "time": dates[i],
                    "open": float(series.open[i]),
                    "high": float(series.high[i]),
                    "low": float(series.low[i]),
                    "close": float(series.close[i]),
                }
            )

        markers = []
        for sig in signals:
            idx = sig.execution_bar_index
            if idx < len(dates):
                is_open = sig.metadata.get("is_open", False) if sig.metadata else False
                color = "#FFD600" if is_open else "#00E676"
                shape = "circle" if is_open else "arrowUp"
                markers.append(
                    {
                        "time": dates[idx],
                        "position": "belowBar",
                        "color": color,
                        "shape": shape,
                        "text": f"{sig.strategy_sub_id} ({float(sig.execution_price):.2f})",
                    }
                )

        chart_options = {
            "layout": {
                "textColor": "#d1d4dc",
                "background": {"type": "solid", "color": "#131722"},
            },
            "grid": {
                "vertLines": {"color": "rgba(42, 46, 57, 0.5)"},
                "horzLines": {"color": "rgba(42, 46, 57, 0.5)"},
            },
            "timeScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
        }

        series_config = [
            {
                "type": "Candlestick",
                "data": candles_data,
                "options": {
                    "upColor": "#26a69a",
                    "downColor": "#ef5350",
                    "borderVisible": False,
                    "wickUpColor": "#26a69a",
                    "wickDownColor": "#ef5350",
                },
                "markers": markers,
            }
        ]

        renderLightweightCharts([{"chart": chart_options, "series": series_config}], key="tv_main_chart")
        return True
    except Exception:
        return False


def render_main_chart(
    series: OHLCVSeries,
    signals: List[SignalRecord],
    reference_lines: List[ReferenceLineSegment],
    use_lightweight: bool = False,
) -> None:
    """
    Main chart entry point with automatic Plotly fallback for maximum reliability.
    """
    if use_lightweight and LIGHTWEIGHT_AVAILABLE:
        success = render_price_chart_lightweight(series, signals, reference_lines)
        if not success:
            render_price_chart_plotly(series, signals, reference_lines)
    else:
        render_price_chart_plotly(series, signals, reference_lines)
