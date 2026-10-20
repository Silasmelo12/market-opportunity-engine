from typing import Dict, Any
import streamlit as st

POPULAR_ASSETS = {
    "Ações Brasil (B3)": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "WEGE3.SA"],
    "FIIs (B3)": ["HGLG11.SA", "KNIP11.SA", "XPLG11.SA", "MXRF11.SA"],
    "Ações EUA": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"],
    "Criptomoedas": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Commodities & Futuros": ["CL=F", "GC=F", "SI=F"],
}

SUPPORTED_INTERVALS = ["5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d", "1wk"]


def render_sidebar() -> Dict[str, Any]:
    """
    Renders sidebar controls and returns configuration parameters.
    """
    st.sidebar.title("Configurações")

    # Check if a ticker was requested from Radar navigation in session_state
    session_ticker = st.session_state.get("selected_ticker", "PETR4.SA")

    # 1. Market & Asset Selection
    st.sidebar.subheader("Ativo & Timeframe")
    category = st.sidebar.selectbox("Classe de Ativo", list(POPULAR_ASSETS.keys()), index=0)
    preset_tickers = POPULAR_ASSETS[category]

    col_t1, col_t2 = st.sidebar.columns([2, 1])
    def_idx = preset_tickers.index(session_ticker) if session_ticker in preset_tickers else 0
    selected_ticker = col_t1.selectbox("Ticker Sugerido", preset_tickers, index=def_idx)
    custom_ticker = col_t2.text_input("Outro Ticker", value="").strip().upper()

    final_ticker = custom_ticker if custom_ticker else selected_ticker

    interval = st.sidebar.selectbox(
        "Timeframe",
        SUPPORTED_INTERVALS,
        index=SUPPORTED_INTERVALS.index("1d"),
        help="Sub-hora (5m-30m): máx 60 dias. Horas (1h-12h): máx 730 dias via resampling.",
    )
    period = st.sidebar.selectbox("Histórico Base", ["60d", "1y", "2y", "5y", "max"], index=3)

    # 2. Evaluation Horizon (Critério Holder)
    st.sidebar.subheader("Avaliador Holder")
    horizon_x = st.sidebar.select_slider(
        "Horizonte X (barras pós-compra)",
        options=[20, 60, 120, 252],
        value=60,
        help="Quantidade de barras futuras avaliadas prospectivamente para cálculo de Win Rate, Retorno Médio e MAE.",
    )

    # 3. Proprietary Strategy Parameters
    st.sidebar.subheader("Estratégia Proprietária (2x2)")
    lookback_n = st.sidebar.slider("Lookback Fundo N (Tipo 2)", min_value=3, max_value=30, value=10)
    retest_m = st.sidebar.slider("Janela de Reteste M", min_value=1, max_value=15, value=5)
    tol_pct_display = st.sidebar.slider("Tolerância Toque na Linha (%)", min_value=0.0, max_value=3.0, value=0.5, step=0.1)
    tolerance_pct = tol_pct_display / 100.0

    # 4. Filter visible strategies on chart
    st.sidebar.subheader("Filtro de Sinais no Gráfico")
    show_prop = st.sidebar.checkbox("Estratégia Proprietária (4 variações)", value=True)
    show_classic = st.sidebar.checkbox("Estratégias Clássicas (DCA, Rebal, Value, BOS, Spring)", value=True)
    show_mql5 = st.sidebar.checkbox("Padrões de Velas MQL5 (8 formações)", value=False)

    return {
        "ticker": final_ticker,
        "interval": interval,
        "period": period,
        "horizon_x": horizon_x,
        "lookback_n": lookback_n,
        "retest_m": retest_m,
        "tolerance_pct": tolerance_pct,
        "show_prop": show_prop,
        "show_classic": show_classic,
        "show_mql5": show_mql5,
    }
