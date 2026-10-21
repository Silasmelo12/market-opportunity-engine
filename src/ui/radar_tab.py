"""
Aba 1: Radar de Mercado & Scanner de Oportunidades (Home Executiva).
Scans monitored assets, lists active setups, and applies the Timing Status badge ("Comprei Atrasado?").
Allows 1-click navigation to the Terminal analysis tab via st.session_state.
"""

from typing import List, Dict, Any
import pandas as pd
import streamlit as st

from ..data_loader import DataLoader
from ..strategies import StrategyCatalog
from ..evaluator import evaluate_all_strategies, classify_timing_status
from .theme import get_friendly_label, get_asset_name

DEFAULT_RADAR_BASKET = [
    ("PETR4.SA", "Ações Brasil"),
    ("VALE3.SA", "Ações Brasil"),
    ("BBAS3.SA", "Ações Brasil"),
    ("HGLG11.SA", "FIIs Brasil"),
    ("AAPL", "Ações EUA"),
    ("NVDA", "Ações EUA"),
    ("BTC-USD", "Criptomoedas"),
    ("CL=F", "Commodities"),
]


def render_radar_tab(interval: str = "1d", horizon_x: int = 60) ->None:
    """
    Renders Aba 1: Radar de Mercado & Scanner de Oportunidades.
    """
    st.markdown("###  Radar de Mercado & Oportunidades")
    st.caption("Varredura em tempo real da carteira monitorada identificando onde estão as melhores assimetrias de compra hoje.")

    # Controls row
    col_cesta, col_refresh = st.columns([4, 1])
    with col_cesta:
        selected_basket = st.multiselect(
            "Ativos no Scanner",
            options=[t[0] for t in DEFAULT_RADAR_BASKET],
            default=[t[0] for t in DEFAULT_RADAR_BASKET],
            help="Selecione os ativos que deseja monitorar no Radar.",
        )
    with col_refresh:
        st.write("")
        st.write("")
        refresh_btn = st.button(" Atualizar Scanner", use_container_width=True)

    if not selected_basket:
        st.info("Selecione pelo menos um ativo para varredura no Radar.")
        return

    opportunities = []

    progress_bar = st.progress(0, text="Processando varredura quantitativa...")
    for idx, ticker in enumerate(selected_basket):
        progress_bar.progress((idx + 1) / len(selected_basket), text=f"Analisando {ticker}...")
        try:
            series = DataLoader.load_asset_data(ticker=ticker, interval=interval, period="2y", use_cache=not refresh_btn)
        except Exception:
            continue

        if series.length < 20:
            continue

        current_price = float(series.close[-1])
        catalog = StrategyCatalog(lookback_n=10, retest_window_m=5, tolerance_pct=0.005)
        results = catalog.run_all(series)

        signals = results["signals"]
        prop_state = results["prop_current_state"]
        pending = results["pending_signals"]

        # Evaluate summaries
        summaries = evaluate_all_strategies(
            series=series,
            signals=signals,
            horizon_bars=horizon_x,
            total_signals_by_sub_id=results["total_signals_by_sub_id"],
        )
        summary_map = {s.strategy_sub_id: s for s in summaries}

        # 1. Check pending signals on final bar
        if pending:
            for p in pending:
                sub_id = p.get("strategy_sub_id", "")
                p_exec = p.get("reference_line_price") or current_price
                s_stat = summary_map.get(sub_id)
                mean_ret = s_stat.mean_forward_return if s_stat else None
                timing = classify_timing_status(
                    current_price=current_price,
                    recommended_price=p_exec,
                    strategy_sub_id=sub_id,
                    strategy_label=get_friendly_label(sub_id),
                    mean_forward_return=mean_ret,
                )
                opportunities.append(
                    {
                        "Ativo": f"{get_asset_name(ticker)} ({ticker})",
                        "Estratégia": get_friendly_label(sub_id),
                        "strategy_sub_id": sub_id,
                        "Status do Sinal": "Formado na Barra",
                        "Semáforo Timing": timing.status_label,
                        "timing_category": timing.status_category,
                        "Distância (%)": timing.distance_pct,
                        "Preço Recomendado": timing.recommended_price,
                        "Preço Atual": current_price,
                        "Histórico Entradas (N)": s_stat.executed_buys if s_stat else 0,
                        "Win Rate Histórico (%)": s_stat.win_rate if s_stat else 0.0,
                        "Recomendação": timing.advice_text,
                    }
                )

        # 2. Check active reference lines waiting for retest
        for sub_id, st_info in prop_state.items():
            if st_info.get("status") == "AGUARDANDO_RETESTE":
                ref_line = st_info.get("active_line_price") or current_price
                s_stat = summary_map.get(sub_id)
                mean_ret = s_stat.mean_forward_return if s_stat else None
                timing = classify_timing_status(
                    current_price=current_price,
                    recommended_price=ref_line,
                    strategy_sub_id=sub_id,
                    strategy_label=get_friendly_label(sub_id),
                    mean_forward_return=mean_ret,
                    is_awaiting_retest=True,
                )
                opportunities.append(
                    {
                        "Ativo": f"{get_asset_name(ticker)} ({ticker})",
                        "Estratégia": get_friendly_label(sub_id),
                        "strategy_sub_id": sub_id,
                        "Status do Sinal": f"Reteste ({st_info.get('retest_bars_remaining')}b rest.)",
                        "Semáforo Timing": timing.status_label,
                        "timing_category": timing.status_category,
                        "Distância (%)": timing.distance_pct,
                        "Preço Recomendado": timing.recommended_price,
                        "Preço Atual": current_price,
                        "Histórico Entradas (N)": s_stat.executed_buys if s_stat else 0,
                        "Win Rate Histórico (%)": s_stat.win_rate if s_stat else 0.0,
                        "Recomendação": timing.advice_text,
                    }
                )

        # 3. Check most recent executed signal (within last 5 bars)
        if signals:
            recent_sig = signals[-1]
            if recent_sig.execution_bar_index >= series.length - 5:
                sub_id = recent_sig.strategy_sub_id
                s_stat = summary_map.get(sub_id)
                mean_ret = s_stat.mean_forward_return if s_stat else None
                timing = classify_timing_status(
                    current_price=current_price,
                    recommended_price=recent_sig.execution_price,
                    strategy_sub_id=sub_id,
                    strategy_label=get_friendly_label(sub_id),
                    mean_forward_return=mean_ret,
                )
                opportunities.append(
                    {
                        "Ativo": f"{get_asset_name(ticker)} ({ticker})",
                        "Estratégia": get_friendly_label(sub_id),
                        "strategy_sub_id": sub_id,
                        "Status do Sinal": f"Comprado há {series.length - 1 - recent_sig.execution_bar_index}b",
                        "Semáforo Timing": timing.status_label,
                        "timing_category": timing.status_category,
                        "Distância (%)": timing.distance_pct,
                        "Preço Recomendado": timing.recommended_price,
                        "Preço Atual": current_price,
                        "Histórico Entradas (N)": s_stat.executed_buys if s_stat else 0,
                        "Win Rate Histórico (%)": s_stat.win_rate if s_stat else 0.0,
                        "Recomendação": timing.advice_text,
                    }
                )

    progress_bar.empty()

    if not opportunities:
        st.info("Nenhuma oportunidade ativa ou sinal recente detectado na carteira monitorada no momento.")
        return

    df_opp = pd.DataFrame(opportunities)
    df_opp["Win Rate Visual"] = df_opp["Win Rate Histórico (%)"] / 100.0

    # Summary metrics row
    c1, c2, c3, c4 = st.columns(4)
    n_ideal = len(df_opp[df_opp["timing_category"] == "IDEAL"])
    n_extended = len(df_opp[df_opp["timing_category"] == "EXTENDED"])
    n_late = len(df_opp[df_opp["timing_category"] == "LATE"])

    c1.metric("Oportunidades Mapeadas", len(df_opp))
    c2.metric(" Zona Ideal de Entrada", n_ideal)
    c3.metric(" Estendido (Cautela)", n_extended)
    c4.metric(" Atrasado (Bonde Andou)", n_late)

    st.markdown("#### Tabela de Oportunidades Ativas & Semáforo de Timing")

    # Table with click interaction
    st.dataframe(
        df_opp,
        column_config={
            "Ativo": st.column_config.TextColumn("Ativo", help="Clique no seletor abaixo para abrir o Terminal"),
            "Estratégia": st.column_config.TextColumn("Estratégia Acionada"),
            "Semáforo Timing": st.column_config.TextColumn("Semáforo de Timing"),
            "Distância (%)": st.column_config.NumberColumn("Distância da Entrada", format="%+.2f%%"),
            "Preço Atual": st.column_config.NumberColumn(format="R$ %.2f"),
            "Preço Recomendado": st.column_config.NumberColumn(format="R$ %.2f"),
            "Win Rate Visual": st.column_config.ProgressColumn(
                "Win Rate Histórico",
                format="%.1f%%",
                min_value=0.0,
                max_value=1.0,
            ),
            "Win Rate Histórico (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Histórico Entradas (N)": st.column_config.NumberColumn(),
            "strategy_sub_id": None,
            "timing_category": None,
        },
        use_container_width=True,
        hide_index=True,
    )

    # 1-Click navigation selector
    st.markdown("---")
    col_sel, col_action = st.columns([3, 1])
    with col_sel:
        target_asset = st.selectbox(
            "Abrir Análise Detalhada no Terminal:",
            options=sorted(df_opp["Ativo"].unique()),
            key="radar_asset_choice",
        )
    with col_action:
        st.write("")
        st.write("")
        if st.button(" Ir para o Terminal", use_container_width=True):
            st.session_state["selected_ticker"] = target_asset
            st.session_state["active_tab_index"] = 1
            st.rerun()
