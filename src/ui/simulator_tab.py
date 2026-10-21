"""
Aba 3: Simulador de Patrimônio & Aportes (Backtest Financeiro).
Isolated reactive execution via @st.fragment to prevent whole-page reloads.
Answers: "Se eu tivesse aportado R$ 100,00 a cada sinal desta estratégia, quanto eu teria hoje?"
"""

from typing import List, Dict
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from ..strategies.base import OHLCVSeries, SignalRecord
from ..evaluator import simulate_accumulation, SimulationResult
from .theme import STRATEGY_LABELS_PT, get_friendly_label


@st.fragment
def render_simulator_fragment(
    series: OHLCVSeries,
    signals: List[SignalRecord],
) ->None:
    """
    Reactive simulation fragment. Parameter adjustments re-execute only this block.
    """
    st.markdown("###  Simulador de Patrimônio & Aportes Periódicos")
    st.caption("Simulação realista de compras fracionárias: 'Se eu tivesse aportado R$ X a cada sinal de compra, quanto eu teria hoje?'")

    if not signals:
        st.info("Nenhum sinal gerado para o ativo selecionado nos filtros atuais.")
        return

    # User Controls
    col_v, col_dates = st.columns([1, 2])
    with col_v:
        contribution = st.number_input(
            "Valor do Aporte por Entrada (R$ / US$):",
            min_value=10.0,
            max_value=100000.0,
            value=100.0,
            step=50.0,
            help="Quantia fixa em dinheiro injetada na compra a cada sinal disparado pela estratégia.",
        )

    with col_dates:
        min_date = pd.to_datetime(series.timestamps[0]).date()
        max_date = pd.to_datetime(series.timestamps[-1]).date()
        date_range = st.date_input(
            "Janela Temporal da Simulação:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    start_d = str(date_range[0]) if isinstance(date_range, (tuple, list)) and len(date_range) >0 else None
    end_d = str(date_range[1]) if isinstance(date_range, (tuple, list)) and len(date_range) >1 else None

    # Run vectorized accumulation simulation
    sim_results = simulate_accumulation(
        series=series,
        signals=signals,
        contribution_amount=float(contribution),
        start_date=start_d,
        end_date=end_d,
        strategy_labels_map=STRATEGY_LABELS_PT,
    )

    if not sim_results:
        st.warning("Nenhum sinal foi executado no intervalo de datas selecionado.")
        return

    # Strategy selector for chart display
    strat_choices = list(sim_results.keys())
    col_strat, _ = st.columns([2, 1])
    with col_strat:
        selected_sub_id = st.selectbox(
            "Estratégia em Destaque no Gráfico:",
            options=strat_choices,
            format_func=lambda s: get_friendly_label(s),
            index=0,
        )

    target_sim = sim_results[selected_sub_id]

    # KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Capital Desembolsado (Bolso)",
        f"R$ {target_sim.total_invested:,.2f}",
        help=f"{target_sim.num_contributions} compras de R$ {contribution:.2f}",
    )
    c2.metric(
        "Patrimônio Acumulado Hoje",
        f"R$ {target_sim.current_equity:,.2f}",
        delta=f"R$ {target_sim.net_profit:+,.2f} ({target_sim.return_on_capital_pct:+.2f}%)",
    )
    c3.metric(
        "Preço Médio Acumulado",
        f"R$ {target_sim.average_buy_price:.2f}",
        delta=f"{((target_sim.current_price / target_sim.average_buy_price) - 1.0) * 100:+.1f}% vs atual",
    )
    c4.metric(
        "Total de Cotas Acumuladas",
        f"{target_sim.total_shares:.4f}",
        help="Cotas totais no final do período",
    )

    # Plotly Evolution Area/Line Chart
    st.markdown("#### Evolução Patrimonial: Valor das Cotas vs. Total Desembolsado")

    fig = go.Figure()

    # Timeline dates
    t_dates = [pd.to_datetime(ts).strftime("%Y-%m-%d") for ts in target_sim.timeline_timestamps]

    # 1. Cumulative Invested Capital (Step line)
    fig.add_trace(
        go.Scatter(
            x=t_dates,
            y=target_sim.timeline_invested.tolist(),
            mode="lines",
            name="Capital Desembolsado (Bolso)",
            line=dict(color="#94A3B8", width=2, dash="dash"),
        )
    )

    # 2. Cumulative Equity (Market value area)
    fig.add_trace(
        go.Scatter(
            x=t_dates,
            y=target_sim.timeline_equity.tolist(),
            mode="lines",
            name="Patrimônio a Mercado",
            fill="tonexty",
            fillcolor="rgba(0, 230, 118, 0.12)",
            line=dict(color="#00E676", width=2.5),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0B0E14",
        paper_bgcolor="#0B0E14",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(title="Valor em Dinheiro (R$ / US$)", tickprefix="R$ "),
        xaxis=dict(title="Data"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Ranking Table across all simulated strategies
    st.markdown("#### Ranking Financeiro Comparativo (Qual estratégia rendeu mais?)")

    rank_data = []
    for sub, sim in sim_results.items():
        rank_data.append(
            {
                "Estratégia": sim.strategy_label,
                "Aportes": sim.num_contributions,
                "Total Investido": sim.total_invested,
                "Patrimônio Final": sim.current_equity,
                "Lucro Líquido": sim.net_profit,
                "Rentabilidade (%)": sim.return_on_capital_pct,
                "Preço Médio": sim.average_buy_price,
                "Preço Atual": sim.current_price,
            }
        )
    df_rank = pd.DataFrame(rank_data).sort_values(by="Patrimônio Final", ascending=False).reset_index(drop=True)

    st.dataframe(
        df_rank,
        column_config={
            "Total Investido": st.column_config.NumberColumn(format="R$ %.2f"),
            "Patrimônio Final": st.column_config.NumberColumn(format="R$ %.2f"),
            "Lucro Líquido": st.column_config.NumberColumn(format="R$ %+.2f"),
            "Rentabilidade (%)": st.column_config.NumberColumn(format="%+.2f%%"),
            "Preço Médio": st.column_config.NumberColumn(format="R$ %.2f"),
            "Preço Atual": st.column_config.NumberColumn(format="R$ %.2f"),
        },
        use_container_width=True,
        hide_index=True,
    )
