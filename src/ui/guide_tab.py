"""
Aba 4: Guia de Estratégias & Playbook Institucional (Educacional).
Structured interactive encyclopedia with concept, exact entry rule, market psychology, and anti-late execution tips.
"""

import streamlit as st


PLAYBOOK_ENTRIES = {
    "Estratégia Proprietária (Negação 2x2)": [
        {
            "title": "Negação Barra Anterior (Entrada Abertura)",
            "sub_id": "t1_open",
            "concept": "Monitora o fechamento abaixo da mínima da barra imediatamente anterior (t-1). Quando o preço fecha novamente acima desse nível, confirma a rejeição da baixa e compra no Open seguinte.",
            "formula": "Rompimento: Close[t] < Low[t-1] -> Linha = Low[t-1]. Negação: Close[t] > Linha. Compra: Open[t+1].",
            "psychology": "A quebra da mínima atrai vendedores apressados (venda de rompimento) e aciona stops de compradores. O fechamento imediato acima da linha aprisiona os vendedores (short trap), provocando cobertura compulsiva.",
            "profile": "Alta Frequência • Indicada para ativos de alta volatilidade e swing trades curtos.",
            "timing_rule": "Compre imediatamente no Open[t+1]. Se o preço abrir em gap de alta > 1.5%, aguarde reteste.",
        },
        {
            "title": "Negação Barra Anterior (Entrada Reteste)",
            "sub_id": "t1_retest",
            "concept": "Após a negação, o investidor não compra na euforia: aguarda até M barras pelo recuo do preço para tocar novamente na Linha de Referência rompida (pullback no suporte).",
            "formula": "Negação em t. Aguarda k em [1..M]: se Low[t+k] <= Linha * (1+tol), compra em Linha (ou Open se gap de baixa).",
            "psychology": "O reteste testa a convicção do mercado: a antiga resistência rompida agora atua como suporte comprador genuíno.",
            "profile": "Calor Mínimo (Baixo MAE) • Maior rentabilidade por trade, com menor taxa de execução.",
            "timing_rule": "Ideal no toque exato da linha. Se o preço fechar abaixo da linha sem reagir, o setup expira.",
        },
        {
            "title": "Negação de Fundo N Barras (Entrada Abertura)",
            "sub_id": "t2_open",
            "concept": "Monitora o rompimento de um suporte estrutural relevante (mínima dos últimos N períodos, ex: 10 barras). Ao recuperar o suporte com fechamento acima, executa no Open seguinte.",
            "formula": "Rompimento: Close[t] < min(Low[t-N:t]). Negação: Close[t] > Linha. Compra: Open[t+1].",
            "psychology": "Rompimento de fundo estrutural aciona liquidações maciças e ordens de stop institucionais. A recuperação rápida indica absorção institucional de liquidez.",
            "profile": "Perfil Holder / Acumulação • Sinais de alta relevância técnica em fundos de mercado.",
            "timing_rule": "Compre na abertura seguinte. Se o movimento já estendeu > 2.0%, prefira a variante de reteste.",
        },
        {
            "title": "Negação de Fundo N Barras (Entrada Reteste)",
            "sub_id": "t2_retest",
            "concept": "Combina a relevância de um fundo estrutural com a disciplina cirúrgica de entrada no reteste do suporte em até M barras.",
            "formula": "Negação de Fundo N em t. Reteste em t+k (1..M): Low[t+k] <= Linha * (1+tol).",
            "psychology": "Máxima assimetria de risco/retorno: o investidor entra com preço muito próximo ao suporte institucional testado.",
            "profile": "Precisão Cirúrgica • Ideal para posições de longo prazo em grandes fundos.",
            "timing_rule": "Excelente relação risco/retorno. Não corra atrás do preço se o reteste não acontecer.",
        },
    ],
    "Price Action Institucional": [
        {
            "title": "Fundo Duplo + Quebra de Estrutura (BOS)",
            "sub_id": "double_bottom_bos",
            "concept": "Formação clássica de W em zona de suporte, onde o segundo fundo não renova mínimas e há fechamento acima do topo intermediário (Neckline).",
            "formula": "Dois fundos em [t-40..t] com tolerância de -3% a +2%, seguidos de Close[t] > Neckline.",
            "psychology": "Exaustão da força vendedora e reversão formal da estrutura de pivôs de baixa para pivôs de alta.",
            "profile": "Alta Confiabilidade • Reversões estruturais de tendência.",
            "timing_rule": "Compre no rompimento do topo intermediário. Cuidado com falsos rompimentos se o volume for fraco.",
        },
        {
            "title": "Varredura de Liquidez (Wyckoff Spring)",
            "sub_id": "wyckoff_spring",
            "concept": "Perfuração temporária da mínima de suporte com forte rejeição na mesma barra e volume expressivo (Sweep de Liquidez).",
            "formula": "Low[t] < min(Low[t-N:t]), Close[t] > min(Low[t-N:t]) e Volume[t] > SMA(Volume, 20).",
            "psychology": "Grandes players 'pescam' liquidez abaixo do suporte para encher seus livros sem empurrar o preço para cima.",
            "profile": "Agilidade e Reversão Rápida • Excelente em criptomoedas e ações líquidas.",
            "timing_rule": "Entrada obrigatória no Open seguinte à vela de rejeição com volume.",
        },
    ],
    "Alocação & Métricas Quantitativas": [
        {
            "title": "DCA Dinâmico (Desconto Estatístico)",
            "sub_id": "dca_dynamic",
            "concept": "Aporte disciplinado disparado exclusivamente quando o ativo entra em zonas extremas de sobrevenda estatística.",
            "formula": "Close[t] < SMA(200)[t] - 2.0 * StdDev(200)[t] OU RSI(14)[t] < 30.",
            "psychology": "Aproveita momentos de pânico e capitulação do mercado onde o pessimismo exagerado deprime as cotações.",
            "profile": "Holder Passivo Inteligente • Reduz drasticamente o preço médio de aquisição.",
            "timing_rule": "Aportes fracionados. Não aloque todo o capital em uma única entrada.",
        },
        {
            "title": "Desconto Fundamentalista (Value Proxy)",
            "sub_id": "value_proxy",
            "concept": "Para ações/FIIs, sinaliza quando o Dividend Yield está no percentil >= 80% aliado a desconto sobre média longa. Em Cripto, usa o Mayer Multiple no percentil <= 15%.",
            "formula": "Ações/FIIs: DY Rolling 12m >= P80 e Close < SMA200. Cripto/Commodities: Preço / SMA200 <= P15.",
            "psychology": "Foco em fluxo de caixa e retorno pelo dividendo quando o preço está em liquidação.",
            "profile": "Foco Previdenciário / Renda Passiva • Ideal para carteiras de dividendos.",
            "timing_rule": "Timing de longo prazo. Permite acumulações em momentos de pessimismo macroeconômico.",
        },
        {
            "title": "Rebalanceamento Renda Fixa x Variável",
            "sub_id": "rebal_rf_rv",
            "concept": "Dispara compras toda vez que a desvalorização da renda variável reduz seu peso relativo abaixo da banda de tolerância (ex: -5% do peso alvo).",
            "formula": "Simulação causal de carteira teórica: w_rv <= w_target - 0.05. Reequilibra no Open seguinte.",
            "psychology": "Implementa matematicamente o princípio de comprar na baixa vendendo o que está na alta sem apego emocional.",
            "profile": "Gestão Patrimonial Macro • Reduz a volatilidade total da carteira.",
            "timing_rule": "Execução mecânica nos rebalanceamentos trimestrais ou por banda.",
        },
    ],
    "Padrões Clássicos de Velas (MQL5 Artigo 101)": [
        {
            "title": "Velas de Reversão Altista (MQL5)",
            "sub_id": "mql5_candles",
            "concept": "8 padrões clássicos do MQL5 CCandlePattern (Martelo, Engolfo de Alta, Piercing Line, Estrela da Manhã, Harami, Três Por Dentro, Três Por Fora e Três Soldados Brancos) com tamanho médio de corpo (AvgBody 12) e filtro de tendência de baixa (Close < SMA 20).",
            "formula": "Formação geométrica precisa da vela + Close[t] < SMA(Close, 20)[t]. Compra: Open[t+1].",
            "psychology": "Equilíbrio de forças entre touros e ursos evidenciado no formato das sombras e corpos das velas.",
            "profile": "Sinais Rápidos de Confluência • Devem ser usados preferencialmente alinhados a suportes.",
            "timing_rule": "Entrada na abertura do candle seguinte à confirmação da figura.",
        },
    ],
}


def render_guide_tab() -> None:
    """
    Renders Aba 4: Guia de Estratégias & Playbook Institucional.
    """
    st.markdown("### 📘 Guia de Estratégias & Playbook Operacional")
    st.caption("Enciclopédia quantitativa detalhando o racional matemático, psicologia de fundo e melhores práticas para cada uma das estratégias do sistema.")

    category_choice = st.radio(
        "Selecione a Família de Estratégias:",
        options=list(PLAYBOOK_ENTRIES.keys()),
        horizontal=True,
    )

    entries = PLAYBOOK_ENTRIES.get(category_choice, [])

    for item in entries:
        with st.expander(f"📌 {item['title']}", expanded=True):
            col_left, col_right = st.columns([3, 2])
            with col_left:
                st.markdown(f"**Conceito Simples:** {item['concept']}")
                st.code(item['formula'], language="text")
                st.markdown(f"**🧠 Psicologia por trás do Fundo:** {item['psychology']}")
            with col_right:
                st.info(f"**🎯 Perfil Ideal:** {item['profile']}")
                st.warning(f"**⏱️ Como Não Comprar Atrasado:** {item['timing_rule']}")
