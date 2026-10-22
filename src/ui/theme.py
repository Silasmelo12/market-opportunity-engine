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
    "price_action_double_bottom_bos": "Fundo Duplo + BOS (Refinado)",
    "double_bottom_bos": "Fundo Duplo + BOS (Refinado)",
    "buy_double_top_inverted": "Topo Duplo Invertido (Compra)",
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
    "sell_rebal_rv_rf": "Rebalanceamento Variável ->Renda Fixa",
    "sell_rebal_relative_strength": "Exaustão de Força Relativa",
    "sell_value_proxy": "Prêmio Excessivo / Estiramento Valuation",
    "sell_double_top_bos": "Topo Duplo + BOS (Refinado)",
    "sell_double_bottom_inverted": "Fundo Duplo Invertido (Venda)",
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
    # Quantitative Technical Indicators (Feature 013)
    "bollinger_close_in": "Bandas de Bollinger (Fechou Fora/Dentro)",
    "bb_reversal_buy": "Bollinger Fundo (Fechou Fora/Dentro)",
    "bb_reversal_sell": "Bollinger Topo (Fechou Fora/Dentro)",
    "keltner_squeeze": "Keltner Squeeze (Compressão/Expansão)",
    "squeeze_breakout_buy": "Keltner Squeeze Rompimento Alta",
    "squeeze_breakout_sell": "Keltner Squeeze Rompimento Baixa",
    "zscore_extreme": "Z-Score de Preço em Extremos",
    "zscore_bottom_buy": "Z-Score Fundo Extremo (<-2.0)",
    "zscore_top_sell": "Z-Score Topo Extremo (>+2.0)",
    "rsi_divergence": "Divergência de IFR/RSI",
    "rsi_bullish_div": "IFR/RSI Divergência de Alta",
    "rsi_bearish_div": "IFR/RSI Divergência de Baixa",
    "stochastic_extreme": "Estocástico Lento em Extremos",
    "stoch_oversold_cross": "Estocástico Sobrevenda (<25)",
    "stoch_overbought_cross": "Estocástico Sobrecompra (>75)",
    "macd_momentum": "MACD Histogram Momentum",
    "macd_bottom_turn": "MACD Inflexão Alta (Fundo)",
    "macd_top_turn": "MACD Inflexão Baixa (Topo)",
    "vwap_bands": "Bandas de VWAP",
    "vwap_band_buy": "VWAP Retorno à Banda Inferior",
    "vwap_band_sell": "VWAP Retorno à Banda Superior",
    "mfi_extreme": "Money Flow Index (MFI) Extremo",
    "mfi_bottom_buy": "MFI Fluxo Sobrevenda (<20)",
    "mfi_top_sell": "MFI Fluxo Sobrecompra (>80)",
    "volume_climax_vsa": "Volume Clímax / VSA Absorção",
    "vsa_absorption_buy": "VSA Absorção de Fundo (Clímax)",
    "vsa_climax_sell": "VSA Distribuição de Topo (Clímax)",
    "supertrend_trailing": "SuperTrend / ATR Trailing",
    "supertrend_bull_flip": "SuperTrend Virada Compradora",
    "supertrend_bear_flip": "SuperTrend Virada Vendedora",
}

FAMILY_LABELS_PT: Dict[str, str] = {
    "prop_reversal": "Estratégia Proprietária (Negação 2x2)",
    "classic": "Estratégias Quantitativas & Price Action",
    "mql5_candles": "Padrões Clássicos de Velas (MQL5)",
}

ASSET_NAMES_PT: Dict[str, str] = {
    # Commodities
    "GC=F": "Gold (Ouro / XAUUSD)",
    "XAUUSD": "Gold (Ouro / XAUUSD)",
    "XAUUSD=X": "Gold (Ouro / XAUUSD)",
    "GOLD": "Gold (Ouro / XAUUSD)",
    "SI=F": "Silver (Prata)",
    "CL=F": "Crude Oil WTI (Petróleo)",
    "BZ=F": "Brent Oil (Petróleo Brent)",
    "HG=F": "Copper (Cobre)",
    "NG=F": "Natural Gas (Gás Natural)",
    "ZC=F": "Corn (Milho)",
    "ZS=F": "Soybeans (Soja)",
    "ZW=F": "Wheat (Trigo)",
    "KC=F": "Coffee (Café Arábica)",
    "CT=F": "Cotton (Algodão)",
    "SB=F": "Sugar (Açúcar)",
    "LE=F": "Live Cattle (Boi Gordo)",
    "HE=F": "Lean Hogs (Suínos)",
    # Mini Contratos B3 & Câmbio
    "^BVSP": "Mini Índice / Ibovespa (WIN)",
    "WIN": "Mini Índice (WIN)",
    "USDBRL=X": "Mini Dólar (WDO / USDBRL)",
    "WDO": "Mini Dólar (WDO)",
    "BRL=X": "Mini Dólar (WDO / BRL)",
    # Forex
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "USDCHF=X": "USD/CHF",
    "AUDUSD=X": "AUD/USD",
    "USDCAD=X": "USD/CAD",
    "NZDUSD=X": "NZD/USD",
    "EURJPY=X": "EUR/JPY",
    "GBPJPY=X": "GBP/JPY",
    "EURCHF=X": "EUR/CHF",
    # Criptomoedas
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    # Ações Brasil
    "PETR4.SA": "Petrobras PN",
    "VALE3.SA": "Vale ON",
    "ITUB4.SA": "Itaú Unibanco PN",
    "BBDC4.SA": "Bradesco PN",
    "BBAS3.SA": "Banco do Brasil ON",
    "ABEV3.SA": "Ambev ON",
    "WEGE3.SA": "WEG ON",
    "RENT3.SA": "Localiza ON",
    "EGIE3.SA": "Engie Brasil ON",
    "PRIO3.SA": "PRIO ON",
    "BRSR6.SA": "Banrisul PNB",
    "KLBN4.SA": "Klabin PN",
    "CXSE3.SA": "Caixa Seguridade ON",
    "BMGB4.SA": "Banco BMG PN",
    "BRKM5.SA": "Braskem PNA",
    "TASA4.SA": "Taurus Armas PN",
    "PMAM3.SA": "Paranapanema ON",
    "CMIG4.SA": "Cemig PN",
    "CPFE3.SA": "CPFL Energia ON",
    "POMO4.SA": "Marcopolo PN",
    "TAEE11.SA": "Taesa Unit",
    "BBSE3.SA": "BB Seguridade ON",
    "SUZB3.SA": "Suzano ON",
    "GGBR4.SA": "Gerdau PN",
    "CSNA3.SA": "Siderúrgica Nacional ON",
    # FIIs Brasil
    "HGLG11.SA": "CSHG Logística",
    "KNRI11.SA": "Kinea Renda Imob.",
    "MXRF11.SA": "Maxi Renda",
    "VISC11.SA": "Vinci Shopping",
    "BTLG11.SA": "BTG Logística",
    "HGRE11.SA": "CSHG Real Estate",
    "KNIP11.SA": "Kinea Índices",
    "HSML11.SA": "HSI Malls",
    "GGRC11.SA": "GGR Covepi",
    "RBRR11.SA": "RBR Rendimento",
    "RBVA11.SA": "Rio Bravo Renda",
    "SNCI11.SA": "Suno Recebíveis",
    "TRXF11.SA": "TRX Real Estate",
    "XPLG11.SA": "XP Log",
    "CPTS11.SA": "Capitânia Securities",
    "VGIR11.SA": "Valora RE",
    "VRTA11.SA": "Fator Verita",
    "VINO11.SA": "Vinci Offices",
    "RECR11.SA": "REC Renda Imob.",
    "HFOF11.SA": "Hedge FOF",
    "BTAL11.SA": "BTG Agro Logística",
    # BDRs Brasil
    "NVDC34.SA": "Nvidia BDR",
    "AAPL34.SA": "Apple BDR",
    "MSFT34.SA": "Microsoft BDR",
    "GOGL34.SA": "Alphabet (Google) BDR",
    "AMZO34.SA": "Amazon BDR",
    "M1TA34.SA": "Meta Platforms BDR",
    "TSLA34.SA": "Tesla BDR",
    "AVGO34.SA": "Broadcom BDR",
    "TSMC34.SA": "TSMC BDR",
    "A1MD34.SA": "AMD BDR",
    "TMCO34.SA": "Toyota BDR",
    "BERK34.SA": "Berkshire Hathaway BDR",
    "JPMC34.SA": "JPMorgan Chase BDR",
    "VISA34.SA": "Visa BDR",
    "MSCD34.SA": "Mastercard BDR",
    "BOAC34.SA": "Bank of America BDR",
    "GSGI34.SA": "Goldman Sachs BDR",
    "WALM34.SA": "Walmart BDR",
    "COCA34.SA": "Coca-Cola BDR",
    "PEPB34.SA": "PepsiCo BDR",
    "MCDC34.SA": "McDonald's BDR",
    "DISB34.SA": "Disney BDR",
    "NFLX34.SA": "Netflix BDR",
    "NIKE34.SA": "Nike BDR",
    "COWC34.SA": "Costco BDR",
    "LILY34.SA": "Eli Lilly BDR",
    "N1VO34.SA": "Novo Nordisk BDR",
    "JNJB34.SA": "Johnson & Johnson BDR",
    "UNHH34.SA": "UnitedHealth BDR",
    "PFIZ34.SA": "Pfizer BDR",
    "EXXO34.SA": "Exxon Mobil BDR",
    "CHVX34.SA": "Chevron BDR",
    "CATP34.SA": "Caterpillar BDR",
    "BOEI34.SA": "Boeing BDR",
    "IVVB11.SA": "iShares S&P 500 Fundo de Índice",
    "BIVB39.SA": "iShares Core S&P 500 BDR",
    "NASD11.SA": "Trend ETF Nasdaq 100",
    "BNDA39.SA": "Invesco QQQ Trust BDR",
    "ACWI11.SA": "Trend ETF MSCI ACWI",
    "BACW39.SA": "iShares MSCI ACWI BDR",
    # Ações EUA
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google (Alphabet)",
    "AMZN": "Amazon",
    "NVDA": "Nvidia",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "JNJ": "Johnson & Johnson",
    "WMT": "Walmart",
    "PG": "Procter & Gamble",
    "MA": "Mastercard",
    "UNH": "UnitedHealth",
    "HD": "Home Depot",
    "DIS": "Disney",
    "ADBE": "Adobe",
    "NFLX": "Netflix",
    "CRM": "Salesforce",
    "KO": "Coca-Cola",
    "AMD": "AMD",
    "INTC": "Intel",
    "CSCO": "Cisco",
    "ABBV": "AbbVie",
    "CVX": "Chevron",
    "XOM": "Exxon Mobil",
    "PFE": "Pfizer",
    "IBM": "IBM",
    "MMM": "3M",
    "VZ": "Verizon",
    "T": "AT&T",
    "BA": "Boeing",
    "CAT": "Caterpillar",
    "GE": "General Electric",
    "GM": "General Motors",
    "F": "Ford",
    "UBER": "Uber",
    "LYFT": "Lyft",
    "TM": "Toyota",
    "SNAP": "Snap",
    "PINS": "Pinterest",
    "PYPL": "PayPal",
    "SHOP": "Shopify",
    "ZM": "Zoom",
    "DOCU": "DocuSign",
    "CRWD": "CrowdStrike",
    "NET": "Cloudflare",
    "O": "Realty Income",
    "SPG": "Simon Property",
    "PLD": "Prologis",
    "AMT": "American Tower",
    "CCI": "Crown Castle",
    "EQIX": "Equinix",
    "PSA": "Public Storage",
    "DLR": "Digital Realty",
    "WELL": "Welltower",
    "AVB": "AvalonBay",
    "EQR": "Equity Residential",
    "BXP": "Boston Properties",
    "VTR": "Ventas",
    "ARE": "Alexandria RE",
    "MAA": "Mid-America Apt.",
    "UDR": "UDR Inc.",
    "KIM": "Kimco Realty",
    "REG": "Regency Centers",
    "HST": "Host Hotels",
    "FRT": "Federal Realty",
    "NNN": "NNN REIT",
    "WPC": "W. P. Carey",
    "GLPI": "Gaming and Leisure",
}


def get_asset_name(ticker: str) ->str:
    """Returns friendly institutional Portuguese name for any ticker."""
    return ASSET_NAMES_PT.get(ticker, ticker)


def get_friendly_label(strategy_sub_id: str) ->str:
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
