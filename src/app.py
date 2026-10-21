"""
Market Opportunity & Bottom Statistical Engine - Main Streamlit Application (Feature 002).
Institutional UX/UI with 4 Core Tabs:
  1.  Radar de Mercado & Oportunidades
  2.  Terminal de Análise & Gráficos
  3.  Simulador de Patrimônio & Aportes
  4.  Guia de Estratégias & Playbook
"""

import sys
from pathlib import Path

# Ensure root repository is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import numpy as np

st.set_page_config(
    page_title="Market Opportunity & Bottom Statistical Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import DataLoader
from src.strategies import StrategyCatalog
from src.evaluator import evaluate_all_strategies, classify_timing_status
from src.ui import (
    inject_institutional_theme,
    render_sidebar,
    render_main_chart,
    render_stats_panels,
    render_state_monitor,
    render_radar_tab,
    render_simulator_fragment,
    render_guide_tab,
    get_friendly_label,
)


@st.cache_data(show_spinner=False)
def get_cached_asset_data(ticker: str, interval: str, period: str):
    return DataLoader.load_asset_data(ticker=ticker, interval=interval, period=period, use_cache=True)


def main():
    # 1. Inject Institutional FinTech Dark Theme
    inject_institutional_theme()

    # Title & Subtitle Header
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Market Opportunity & Bottom Statistical Engine")
        st.caption("Plataforma Quantitativa de Análise de Fundo, Timing de Entrada e Simulação de Acumulação • Nível Institucional")

    # 2. Sidebar controls
    config = render_sidebar()
    ticker = config["ticker"]
    interval = config["interval"]
    period = config["period"]
    horizon_x = config["horizon_x"]

    # 3. 4 Top Navigation Tabs
    tab_titles = [
        " Radar de Mercado & Oportunidades",
        " Terminal de Análise & Gráficos",
        " Simulador de Patrimônio & Aportes",
        " Guia de Estratégias & Playbook",
    ]

    active_tab = st.tabs(tab_titles)

    # -------------------------------------------------------------
    # TAB 1: RADAR DE MERCADO & SCANNER
    # -------------------------------------------------------------
    with active_tab[0]:
        render_radar_tab(interval=interval, horizon_x=horizon_x)

    # -------------------------------------------------------------
    # TAB 2: TERMINAL DE ANÁLISE & GRÁFICOS
    # -------------------------------------------------------------
    with active_tab[1]:
        with st.spinner(f"Carregando dados de {ticker} ({interval})..."):
            try:
                series = get_cached_asset_data(ticker=ticker, interval=interval, period=period)
            except Exception as e:
                st.error(f"Erro ao carregar ativo '{ticker}': {e}")
                st.info("Verifique a conexão de rede ou a grafia do ticker (ex: PETR4.SA, AAPL, BTC-USD, CL=F).")
                series = None

        if series is not None:
            if series.length < 20:
                st.warning(f"O ativo {ticker} possui apenas {series.length} barras. É necessário pelo menos 20 barras.")
            else:
                # Process strategies
                catalog = StrategyCatalog(
                    lookback_n=config["lookback_n"],
                    retest_window_m=config["retest_m"],
                    tolerance_pct=config["tolerance_pct"],
                )
                results = catalog.run_all(series)
                all_signals = results["signals"]
                all_lines = results["reference_lines"]
                prop_state = results["prop_current_state"]
                pending = results["pending_signals"]
                total_signals_map = results["total_signals_by_sub_id"]

                # Filter visible signals
                active_sigs = []
                for sig in all_signals:
                    if sig.strategy_id == "prop_reversal" and config["show_prop"]:
                        active_sigs.append(sig)
                    elif sig.strategy_id in (
                        "dca_dynamic", "rebal_rf_rv", "rebal_relative_strength",
                        "value_proxy", "price_action_double_bottom_bos", "price_action_wyckoff_spring"
                    ) and config["show_classic"]:
                        active_sigs.append(sig)
                    elif sig.strategy_id == "mql5_candles" and config["show_mql5"]:
                        active_sigs.append(sig)

                # Statistical evaluation
                summaries = evaluate_all_strategies(
                    series=series,
                    signals=active_sigs,
                    horizon_bars=horizon_x,
                    total_signals_by_sub_id=total_signals_map,
                )

                # Asset Header & Timing Status Card
                current_price = float(series.close[-1])
                recent_p_exec = active_sigs[-1].execution_price if active_sigs else current_price
                recent_sub = active_sigs[-1].strategy_sub_id if active_sigs else "none"
                recent_summary = next((s for s in summaries if s.strategy_sub_id == recent_sub), None)
                timing = classify_timing_status(
                    current_price=current_price,
                    recommended_price=recent_p_exec,
                    strategy_sub_id=recent_sub,
                    strategy_label=get_friendly_label(recent_sub),
                    mean_forward_return=recent_summary.mean_forward_return if recent_summary else None,
                )

                h1, h2, h3 = st.columns([2, 1, 1])
                h1.metric(f"{ticker} ({interval})", f"R$ {current_price:.2f}", delta=f"{((current_price / series.close[-2]) - 1.0) * 100:+.2f}% no período")
                h2.metric("Semáforo do Último Sinal", timing.status_label, delta=f"{timing.distance_pct:+.2f}% da entrada")
                h3.metric("Recomendação", timing.status_category, help=timing.advice_text)

                # State Monitor & Confluences
                render_state_monitor(series, prop_state, pending)

                # Main Candlestick Chart
                st.markdown(f"#### Gráfico de Preços (OHLCV) • {ticker} ({interval})")
                render_main_chart(series, active_sigs, all_lines if config["show_prop"] else [])

                # Comparative Statistical Panels
                render_stats_panels(summaries, horizon_x=horizon_x)

    # -------------------------------------------------------------
    # TAB 3: SIMULADOR DE PATRIMÔNIO & APORTES (@st.fragment)
    # -------------------------------------------------------------
    with active_tab[2]:
        if "series" in locals() and series is not None and series.length >= 20:
            render_simulator_fragment(series=series, signals=active_sigs)
        else:
            st.info("Carregue um ativo no Terminal para executar o Simulador de Aportes.")

    # -------------------------------------------------------------
    # TAB 4: GUIA DE ESTRATÉGIAS & PLAYBOOK
    # -------------------------------------------------------------
    with active_tab[3]:
        render_guide_tab()


if __name__ == "__main__":
    main()
