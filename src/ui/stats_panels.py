"""
Statistical comparative panels and Risk vs. Return charts.
Refined for institutional FinTech dark layout:
- Win Rate Ranking horizontal bars with xaxis range [0, 118] to prevent label clipping.
- Label format with count: '85.7% (14 entradas)'.
- Normalized Viridis/Plasma scale with clip at 90th percentile of score for distinct visual gradient.
- Risk x Return Scatter Plot with generous padding, quadrant reference lines (Gold Quadrant highlight), and rich tooltips.
- st.column_config.ProgressColumn formatting for dataframes.
"""

from typing import List
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ..strategies.base import StrategyStatsSummary
from .theme import get_friendly_label


def render_stats_panels(summaries: List[StrategyStatsSummary], horizon_x: int) ->None:
    """
    Renders Efficiency Ranking, Risk x Return Scatter Plot, and Full Metrics Table.
    """
    if not summaries:
        st.info("Nenhuma estratégia gerou dados para os filtros selecionados.")
        return

    data = []
    for s in summaries:
        lbl = get_friendly_label(s.strategy_sub_id)
        data.append(
            {
                "Estratégia": lbl,
                "strategy_sub_id": s.strategy_sub_id,
                "Família": s.strategy_id,
                "Win Rate (%)": s.win_rate,
                "Retorno Médio (%)": s.mean_forward_return,
                "Retorno Mediano (%)": s.median_forward_return,
                "Calor Médio MAE (%)": s.mean_mae,
                "Pior MAE (%)": s.max_mae,
                "Score Eficiência": s.efficiency_score,
                "Total Sinais": s.total_signals,
                "Compras Executadas": s.executed_buys,
                "Taxa de Reteste (%)": s.retest_fill_rate,
                "Sinais em Aberto": s.open_signals_count,
            }
        )
    df = pd.DataFrame(data)

    st.subheader(f"Avaliação Quantitativa de Fundo (Horizonte Holder: {horizon_x} barras)")

    col_rank, col_scatter = st.columns(2)

    with col_rank:
        st.markdown("#### Ranking de Eficiência (Win Rate %)")
        df_sorted = df.sort_values(by="Win Rate (%)", ascending=True).copy()

        # Format custom text: '85.7% (14 entradas)'
        df_sorted["bar_text"] = df_sorted.apply(
            lambda r: f"{r['Win Rate (%)']:.1f}% ({r['Compras Executadas']} entradas)", axis=1
        )

        # Normalize efficiency score color using 90th percentile clip
        scores = df_sorted["Score Eficiência"].to_numpy()
        p90 = float(np.percentile(scores, 90)) if len(scores) >1 and np.percentile(scores, 90) >0 else 1.0
        df_sorted["clipped_score"] = np.clip(scores, 0.0, max(p90, 0.1))

        fig_bar = px.bar(
            df_sorted,
            x="Win Rate (%)",
            y="Estratégia",
            orientation="h",
            color="clipped_score",
            color_continuous_scale="Viridis",
            text="bar_text",
            template="plotly_dark",
            height=460,
        )
        # Position text outside and expand xaxis range to [0, 118] to avoid cutting 100% labels
        fig_bar.update_traces(textposition="outside", textfont=dict(size=11, family="monospace"))
        fig_bar.update_layout(
            margin=dict(l=10, r=40, t=20, b=20),
            xaxis=dict(range=[0, 118], title="Taxa de Acerto (Win Rate %)", dtick=20),
            yaxis=dict(title=""),
            coloraxis_showscale=False,
            plot_bgcolor="#0B0E14",
            paper_bgcolor="#0B0E14",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_scatter:
        st.markdown("#### Matriz Risco x Retorno (Calor MAE vs. Retorno Médio)")

        mean_mae_avg = float(df["Calor Médio MAE (%)"].mean())
        mean_ret_avg = float(df["Retorno Médio (%)"].mean())

        # Determine custom padding
        min_x = float(df["Calor Médio MAE (%)"].min())
        max_x = float(df["Calor Médio MAE (%)"].max())
        min_y = float(df["Retorno Médio (%)"].min())
        max_y = float(df["Retorno Médio (%)"].max())

        span_x = max(abs(max_x - min_x), 5.0)
        span_y = max(abs(max_y - min_y), 5.0)

        fig_scatter = px.scatter(
            df,
            x="Calor Médio MAE (%)",
            y="Retorno Médio (%)",
            size="Compras Executadas",
            color="Win Rate (%)",
            hover_name="Estratégia",
            hover_data={
                "Compras Executadas": True,
                "Win Rate (%)": ":.1f",
                "Retorno Médio (%)": ":.2f",
                "Calor Médio MAE (%)": ":.2f",
                "Score Eficiência": ":.3f",
                "Estratégia": False,
            },
            color_continuous_scale="Turbo",
            template="plotly_dark",
            height=460,
        )

        # Draw quadrant lines
        fig_scatter.add_vline(x=mean_mae_avg, line_dash="dash", line_color="#334155", annotation_text="MAE Médio")
        fig_scatter.add_hline(y=mean_ret_avg, line_dash="dash", line_color="#334155", annotation_text="Retorno Médio")
        fig_scatter.add_hline(y=0, line_dash="dot", line_color="#64748B")

        # Quadrant of Gold annotation in upper right
        fig_scatter.add_annotation(
            xref="paper", yref="paper",
            x=0.98, y=0.98,
            text=" Quadrante de Ouro (Alto Retorno & Baixo Calor)",
            showarrow=False,
            font=dict(size=10, color="#FFD600"),
            align="right"
        )

        fig_scatter.update_layout(
            margin=dict(l=30, r=30, t=30, b=30),
            xaxis=dict(
                title="Calor Médio Suportado (MAE %)",
                range=[min_x - 0.15 * span_x, max_x + 0.15 * span_x],
            ),
            yaxis=dict(
                title=f"Retorno Médio em {horizon_x} barras (%)",
                range=[min_y - 0.15 * span_y, max_y + 0.15 * span_y],
            ),
            plot_bgcolor="#0B0E14",
            paper_bgcolor="#0B0E14",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Tabela Comparativa de Eficiência Estatística")
    
    # Configure progress column and monetary format
    display_df = df.sort_values(by="Win Rate (%)", ascending=False).reset_index(drop=True)
    display_df["Win Rate Progress"] = display_df["Win Rate (%)"] / 100.0

    st.dataframe(
        display_df,
        column_config={
            "Win Rate Progress": st.column_config.ProgressColumn(
                "Win Rate (Visual)",
                help="Taxa de acerto histórica de fundo",
                format="%.1f%%",
                min_value=0.0,
                max_value=1.0,
            ),
            "Win Rate (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Retorno Médio (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Retorno Mediano (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Calor Médio MAE (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Pior MAE (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Score Eficiência": st.column_config.NumberColumn(format="%.3f"),
            "Taxa de Reteste (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "strategy_sub_id": None,
        },
        use_container_width=True,
        hide_index=True,
    )
