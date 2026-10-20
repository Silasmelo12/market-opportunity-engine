"""
Institutional Theme, FinTech Dark styling, and Portuguese Strategy Label mappings.
"""

from typing import Dict, Any, Optional
import streamlit as st

# Centralized mapping from technical IDs to friendly institutional Portuguese names
STRATEGY_LABELS_PT: Dict[str, str] = {
    # Proprietary Reversal 2x2
    "t1_open": "Negação Barra Anterior (Entrada Abertura)",
    "t1_retest": "Negação Barra Anterior (Entrada Reteste)",
    "t2_open": "Negação de Fundo N Barras (Entrada Abertura)",
    "t2_retest": "Negação de Fundo N Barras (Entrada Reteste)",
    # Classic Strategies
    "dca_dynamic": "DCA Dinâmico (Desconto Estatístico)",
    "rebal_rf_rv": "Rebalanceamento Renda Fixa x Variável",
    "rebal_relative_strength": "Rebalanceamento de Força Relativa (Z-Score)",
    "value_proxy": "Desconto Fundamentalista (Value Proxy)",
    "price_action_double_bottom_bos": "Fundo Duplo + Quebra de Estrutura (BOS)",
    "double_bottom_bos": "Fundo Duplo + Quebra de Estrutura (BOS)",
    "price_action_wyckoff_spring": "Varredura de Liquidez (Wyckoff Spring)",
    "wyckoff_spring": "Varredura de Liquidez (Wyckoff Spring)",
    # MQL5 Bullish Candlestick Patterns
    "hammer": "Vela: Martelo",
    "inverted_hammer": "Vela: Martelo Invertido",
    "bullish_engulfing": "Vela: Engolfo de Alta",
    "piercing_line": "Vela: Piercing Line (Linha Perfurante)",
    "morning_star": "Vela: Estrela da Manhã",
    "bullish_harami": "Vela: Harami de Alta",
    "three_inside_up": "Vela: Três Por Dentro de Alta",
    "three_outside_up": "Vela: Três Por Fora de Alta",
    "three_white_soldiers": "Vela: Três Soldados Brancos",
    "tweezer_bottom": "Vela: Pinça de Fundo (Tweezer Bottom)",
    "dragonfly_doji": "Vela: Doji Libélula (Dragonfly)",
    "abandoned_baby_bullish": "Vela: Bebê Abandonado de Alta",
    "bullish_kicker": "Vela: Chute de Alta (Bullish Kicker)",
    "climactic_pinbar": "Vela: Pinbar Clímax de Volume",
    # Proprietary Top Reversal 2x2 (SELL)
    "sell_t1_open": "Negação Máxima Anterior (Venda Abertura)",
    "sell_t1_retest": "Negação Máxima Anterior (Venda Reteste)",
    "sell_t2_open": "Negação de Topo N Barras (Venda Abertura)",
    "sell_t2_retest": "Negação de Topo N Barras (Venda Reteste)",
    # Classic Strategies (SELL)
    "sell_overbought_stat": "Excesso Estatístico / Realização Parcial",
    "sell_rebal_rv_rf": "Rebalanceamento Variável -> Renda Fixa",
    "sell_rebal_relative_strength": "Exaustão de Força Relativa",
    "sell_value_proxy": "Prêmio Excessivo / Estiramento Valuation",
    "sell_double_top_bos": "Topo Duplo + Quebra de Estrutura (BOS)",
    "sell_wyckoff_upthrust": "Varredura de Topo (Wyckoff Upthrust / UTAD)",
    # MQL5 Bearish Candlestick Patterns (SELL)
    "shooting_star": "Vela Topo: Estrela Cadente (Shooting Star)",
    "hanging_man": "Vela Topo: Enforcado (Hanging Man)",
    "bearish_engulfing": "Vela Topo: Engolfo de Baixa",
    "dark_cloud_cover": "Vela Topo: Nuvem Negra (Dark Cloud Cover)",
    "evening_star": "Vela Topo: Estrela da Tarde (Evening Star)",
    "bearish_harami": "Vela Topo: Harami de Baixa",
    "three_inside_down": "Vela Topo: Três Por Dentro de Baixa",
    "three_outside_down": "Vela Topo: Três Por Fora de Baixa",
    "three_black_crows": "Vela Topo: Três Corvos Negros",
    "tweezer_top": "Vela Topo: Pinça de Topo (Tweezer Top)",
    "gravestone_doji": "Vela Topo: Doji Lápide (Gravestone)",
    "abandoned_baby_bearish": "Vela Topo: Bebê Abandonado de Baixa",
    "bearish_kicker": "Vela Topo: Chute de Baixa (Bearish Kicker)",
    "climactic_bearish_pinbar": "Vela Topo: Pinbar Clímax de Topo com Volume",
}

FAMILY_LABELS_PT: Dict[str, str] = {
    "prop_reversal": "Estratégia Proprietária (Negação 2x2)",
    "classic": "Estratégias Quantitativas & Price Action",
    "mql5_candles": "Padrões Clássicos de Velas (MQL5)",
}


def get_friendly_label(strategy_sub_id: str) -> str:
    """Returns friendly commercial Portuguese label for any strategy sub-id."""
    return STRATEGY_LABELS_PT.get(strategy_sub_id, strategy_sub_id.replace("_", " ").title())


def inject_institutional_theme():
    """
    Injects FinTech Dark custom CSS:
    - Background: #0B0E14
    - Surface: #151924 with border #262B38
    - Monospaced typography for tabular numbers
    - Clean compact padding
    """
    st.markdown(
        """
        <style>
        /* Base page styling */
        .stApp {
            background-color: #0B0E14;
            color: #E0E6ED;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Reduced top padding */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 98% !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #0B0E14;
            padding-bottom: 8px;
            border-bottom: 1px solid #262B38;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #151924;
            border: 1px solid #262B38;
            border-radius: 6px;
            padding: 8px 18px;
            color: #94A3B8;
            font-weight: 500;
            font-size: 0.95rem;
        }

        .stTabs [aria-selected="true"] {
            background-color: #1E293B !important;
            border-color: #2962FF !important;
            color: #FFFFFF !important;
        }

        /* Metric card styling */
        [data-testid="stMetric"] {
            background-color: #151924;
            border: 1px solid #262B38;
            border-radius: 8px;
            padding: 12px 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }

        [data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace !important;
            font-size: 1.4rem !important;
            font-weight: 600 !important;
        }

        /* Custom FinTech Card container */
        .fintech-card {
            background-color: #151924;
            border: 1px solid #262B38;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 14px;
        }

        .fintech-card-header {
            color: #94A3B8;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }

        .fintech-badge-ideal {
            background-color: rgba(0, 230, 118, 0.15);
            color: #00E676;
            border: 1px solid #00E676;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .fintech-badge-extended {
            background-color: rgba(255, 193, 7, 0.15);
            color: #FFC107;
            border: 1px solid #FFC107;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .fintech-badge-late {
            background-color: rgba(255, 82, 82, 0.15);
            color: #FF5252;
            border: 1px solid #FF5252;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* Tables & DataFrames */
        .stDataFrame {
            border: 1px solid #262B38;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
