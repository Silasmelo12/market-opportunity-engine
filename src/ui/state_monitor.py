"""
Current Market State and Confluence Monitor.
Highlights active reference lines, pending alerts, and real-time status of the asset.
"""

from typing import Dict, Any, List
import streamlit as st
from ..strategies.base import OHLCVSeries


def render_state_monitor(
    series: OHLCVSeries,
    current_state: Dict[str, Dict[str, Any]],
    pending_signals: List[Dict[str, Any]],
) -> None:
    """
    Renders top status cards for active reference lines and current bar opportunities.
    """
    last_close = float(series.close[-1]) if series.length > 0 else 0.0

    st.markdown("### Monitor de Estado Atual & Confluência")

    # 1. Check for pending alerts triggered on the latest bar
    if pending_signals:
        for alert in pending_signals:
            sub = alert.get("strategy_sub_id", alert.get("strategy_id", "Estratégia"))
            stat = alert.get("status", "SINAL_PENDENTE")
            ref_p = alert.get("reference_line_price")
            ref_txt = f" (Linha: {ref_p:.2f})" if ref_p else ""
            st.success(f"**Oportunidade em Formação na Última Barra**: `{sub}`{ref_txt} - Status: **{stat}**")

    # 2. Display 4 columns for the 4 Proprietary Reversal variants
    cols = st.columns(4)
    labels = {
        "t1_open": "Tipo 1 (t-1) • Abertura",
        "t1_retest": "Tipo 1 (t-1) • Reteste",
        "t2_open": "Tipo 2 (Fundo N) • Abertura",
        "t2_retest": "Tipo 2 (Fundo N) • Reteste",
    }

    for i, sub_id in enumerate(["t1_open", "t1_retest", "t2_open", "t2_retest"]):
        st_data = current_state.get(sub_id, {})
        status = st_data.get("status", "NEUTRO")
        line_price = st_data.get("active_line_price")
        dist = st_data.get("distance_to_line_pct")
        retest_left = st_data.get("retest_bars_remaining")

        with cols[i]:
            st.caption(labels.get(sub_id, sub_id))
            if status == "AGUARDANDO_NEGACAO" and line_price:
                dist_str = f"{dist:+.1f}%" if dist is not None else ""
                st.metric(
                    label="Linha Ativa (Suporte)",
                    value=f"{line_price:.2f}",
                    delta=f"{dist_str} do fechamento",
                    delta_color="normal",
                )
                st.info("Aguardando Negação")
            elif status == "AGUARDANDO_RETESTE" and line_price:
                st.metric(
                    label="Negação Feita • Espera Reteste",
                    value=f"{line_price:.2f}",
                    delta=f"{retest_left} barras restantes" if retest_left else "Janela M",
                )
                st.warning("Aguardando Reteste")
            elif status == "COMPRA_GATILHO_ABERTURA":
                st.metric(label="Gatilho de Compra", value=f"{last_close:.2f}")
                st.success("Compra na Abertura")
            elif status == "COMPRA_EXECUTADA_HOJE":
                st.metric(label="Executado Hoje", value=f"{last_close:.2f}")
                st.success("Comprado na Barra")
            else:
                st.metric(label="Estado", value="Neutro")
                st.text("Sem linha ativa")
