# Research & Technical Decisions: Market Opportunity & Bottom Statistical Engine

**Feature**: `001-market-opportunity-engine`
**Date**: 2026-10-19

## Technical Decisions & Trade-offs

### 1. Engine de Dados e Estratégia de Cache
- **Decision**: Camada dupla de cache utilizando `st.cache_data` em memória e persistência em arquivos Parquet (`.cache/data/{ticker}_{interval}.parquet`).
- **Rationale**: A API do `yfinance` impõe limites de requisição e latência de rede. O cache local garante recarregamento em < 50ms para ativos já baixados, mantendo compatibilidade com as execuções interativas do Streamlit.
- **Alternatives Considered**:
  - SQLite: Maior overhead de setup e serialização lenta de DataFrames inteiros.
  - CSV: Lento para I/O e perde tipos nativos de data e floats.

### 2. Máquina de Estados Finita O(N) para a Estratégia Proprietária
- **Decision**: Implementação sobre arrays 1D NumPy (`open_arr`, `high_arr`, `low_arr`, `close_arr`) utilizando passagem única iterativa em Python otimizada ou Numba, rastreando explicitamente as variáveis de estado:
  - `active_line_price`: float (última linha de referência não negada)
  - `breakout_bar_idx`: int (barra do rompimento)
  - `state`: enum/int (`IDLE`, `BREAKOUT_ACTIVE`, `NEGATED_PENDING_RETEST`)
  - `retest_bars_left`: int (contagem regressiva de $M$ barras)
- **Rationale**: Elimina `DataFrame.iterrows()`, atingindo execução em < 10ms para 1.000 barras. As regras de reteste cravadas no alinhamento prévio são avaliadas sequencialmente:
  - Primeiro toque em $t+k$ consome a linha (ciclo único).
  - Em gap de baixa (`Open[t+k] < Linha * (1 + tol)`), $P_{exec} = Open[t+k]$.
  - No toque padrão, $P_{exec} = Linha * (1 + tol)$ ou $Linha$.
- **Alternatives Considered**:
  - Vetorização pura com `np.where`: Inviável porque a linha de referência ativa depende dinamicamente de rompimentos anteriores não negados e horizonte de reteste limitado (path-dependent).

### 3. Vetorização Fiel do MQL5 CCandlePattern (Artigo 101)
- **Decision**: Vetorização pura em `pandas`/`numpy` calculando:
  - `Body = abs(Close - Open)`
  - `AvgBody = SMA(Body, 12)`
  - Filtro de tendência: `Close < SMA(Close, 20)`
  - Fórmulas dimensionais exatas do MQL5:
    - *Martelo (Hammer)*: Sombra inferior $\ge 2 \times Body$, sombra superior $\le 0.1 \times Body$, `Close < SMA(20)`.
    - *Engolfo de Alta (Bullish Engulfing)*: Vela $t-1$ de baixa, vela $t$ de alta com `Open[t] <= Close[t-1]` e `Close[t] >= Open[t-1]`.
    - *Linha Perfurante (Piercing Line)*: Vela $t-1$ de baixa, vela $t$ de alta abrindo abaixo de `Low[t-1]` e fechando acima de `50%` do corpo de $t-1$.
    - *Estrela da Manhã (Morning Star)*: Padrão de 3 velas (baixa longa, corpo pequeno abaixo, alta fechando acima de 50% da 1ª vela).
    - *Harami de Alta (Bullish Harami)*: Vela $t-1$ de baixa longa, vela $t$ totalmente contida no corpo de $t-1$.
    - *Três Por Dentro de Alta (Three Inside Up)*: Harami de alta seguido de vela $t$ fechando acima de `Close[t-2]`.
    - *Três Por Fora de Alta (Three Outside Up)*: Engolfo de alta seguido de vela $t$ fechando acima de `Close[t-1]`.
    - *Três Soldados Brancos (Three White Soldiers)*: Três velas de alta consecutivas fechando próximas às máximas.
  - Execução: Sempre na barra seguinte `t_exec = t_final + 1` com $P_{exec} = Open[t_exec]$.
- **Rationale**: Respeito estrito ao MQL5 e Zero Look-Ahead Bias garantido.

### 4. Avaliador Estatístico e Métricas Anti-Look-Ahead
- **Decision**: `statistical_evaluator` isolado calculando matrizes de retorno futuro por slicing relativo:
  - $Win = (Close[t_{exec} + X] > P_{exec})$
  - $ForwardReturn = (Close[t_{exec} + X] / P_{exec}) - 1.0$
  - $MAE = \min_{i \in [0, X]} (Low[t_{exec} + i] / P_{exec}) - 1.0$
- **Rationale**: Avalia a real tolerância de dor do investidor (calor máximo) e o retorno do ponto de vista de acumulação patrimonial.

### 5. Visualização Streamlit + Lightweight Charts Canvas
- **Decision**:
  - Gráfico Principal OHLCV: `streamlit-lightweight-charts` (Canvas nativo TradingView) para visualização rápida e sem travamentos. Marcadores de compra inseridos via API de markers; linhas de referência inseridas como price lines ou séries de linhas temporárias.
  - Gráficos Comparativos: `plotly.graph_objects` com WebGL para Scatter de Risco x Retorno e Barras horizontais de Ranking.
- **Rationale**: Máxima performance visual e responsividade no navegador.
