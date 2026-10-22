# Research: Pacote de Estratégias Quantitativas com Indicadores Técnicos

## 1. Contexto e Objetivos

Esta pesquisa estabelece as definições matemáticas, regras de disparo estritas contra look-ahead bias e a arquitetura de vetorização para 10 estratégias quantitativas organizadas em 4 famílias operacionais:
1. **Reversão à Média**: Bollinger Fechou Fora/Dentro, Keltner Squeeze, Z-Score de Preço.
2. **Osciladores & Divergências**: Divergência Regular de IFR/RSI (Bullish/Bearish), Estocástico Lento em Extremos, MACD Histogram Momentum.
3. **Volume & Fluxo Institucional**: Bandas de VWAP, Money Flow Index (MFI), Volume Clímax / VSA (Absorção de Fundo/Topo).
4. **Volatilidade & Tendência Dinâmica**: SuperTrend / Canais de ATR.

---

## 2. Decisões Arquiteturais e Algorítmicas

### 2.1 Família 1: Reversão à Média

#### Bollinger Fechou Fora / Fechou Dentro
- **Decisão**: Sinal de Fundo (BUY) ocorre na barra $t$ quando $Close[t-1] < LowerBand[t-1]$ e $Close[t] \ge LowerBand[t]$. Sinal de Topo (SELL) ocorre na barra $t$ quando $Close[t-1] > UpperBand[t-1]$ e $Close[t] \le UpperBand[t]$.
- **Parâmetros**: Período 20, Desvio Padrão 2.0.
- **Rigor Anti-Lookahead**: Execução estrita na barra $t+1$ ao preço $Open[t+1]$.
- **Alternativas consideradas**: Rompimento simples de banda (gerava excesso de falso rompimento em tendências fortes; o padrão "fechou fora e voltou a fechar dentro" filtra a exaustão com maior assertividade).

#### Keltner Squeeze
- **Decisão**: Identifica compressão de volatilidade quando as Bandas de Bollinger (20, 2.0) estão contidas dentro dos Canais de Keltner (20, 1.5 ATR). O "Squeeze Fired" ocorre quando a Bollinger Band sai para fora do canal de Keltner. A direção é dada pelo sinal do momentum do fechamento ou inclinação da regressão/SMA na barra de liberação $t$.
- **Rigor Anti-Lookahead**: O rompimento do Squeeze confirmado no fechamento de $t$ gera execução na abertura de $t+1$.

#### Z-Score de Preço em Extremos
- **Decisão**: Z-Score calculado como $Z_t = \frac{Close_t - SMA(Close, N)}{\sigma(Close, N)}$. Fundo estatístico ocorre quando $Z_t < -2.0$ e começa a infletir ($Z_t > Z_{t-1}$). Topo quando $Z_t > +2.0$ e $Z_t < Z_{t-1}$.
- **Parâmetros**: Janela $N = 20$.
- **Vetorização**: `pd.Series.rolling(20).mean()` e `std()` com operações NumPy contíguas.

---

### 2.2 Família 2: Osciladores e Divergências

#### Divergência Regular de IFR/RSI
- **Decisão**: Algoritmo vetorizado de detecção de pivôs locais com lookback fixo $k=3$ (sem repintura!). Uma divergência de alta (Bullish) ocorre quando o preço faz um fundo mais baixo ($Low_{p2} < Low_{p1}$) enquanto o RSI faz um fundo mais alto ($RSI_{p2} > RSI_{p1}$ com $RSI < 45$).
- **Rigor Anti-Lookahead**: A confirmação de um pivô com raio $k=2$ ou $3$ só é conhecida após $k$ barras. Portanto, a barra de sinal $t$ é a barra exata em que a confirmação matemática foi concluída, e a compra é executada em $t+1$.
- **Alternativas consideradas**: Repintar pivôs no gráfico retroativamente (rejeitado categoricamente pela Constituição do projeto).

#### Estocástico Lento em Extremos
- **Decisão**: $\%K$ rápido baseado na posição do fechamento dentro da faixa High/Low de 14 períodos; $\%K$ lento suavizado por média móvel de 3 períodos; linha $\%D$ (sinal) por média de 3 períodos sobre $\%K$ lento. Compra disparada quando $\%K < 20$ e $\%K$ cruza para cima de $\%D$. Venda quando $\%K > 80$ e cruza para baixo de $\%D$.
- **Execução**: No fechamento do cruzamento $t$, execução em $Open[t+1]$.

#### MACD Histogram Momentum
- **Decisão**: MACD clássico (12, 26, 9). O Histograma $H_t = MACD_t - Signal_t$. Sinal de reversão de fundo ocorre quando $H_t < 0$, $H_{t-1} < 0$, mas $H_t > H_{t-1}$ (duas barras sucessivas de perda de força vendedora e inflexão positiva). Topo quando $H_t > 0$ e $H_t < H_{t-1}$.

---

### 2.3 Família 3: Fluxo de Volume Institucional

#### Bandas de VWAP
- **Decisão**: VWAP cumulativa rolling ou ancorada por sessão/janela de 20 períodos para swing trade ($VWAP_t = \frac{\sum (TP \cdot Vol)}{\sum Vol}$, onde $TP = (H+L+C)/3$). Bandas calculadas com $\pm 2$ desvios padrão ponderados pelo volume. Sinal de retorno à média quando preço ultrapassa a banda inferior e re-cruza para dentro.
- **Rigor Anti-Lookahead**: Preço de referência é a banda inferior calculada até $t$, execução em $Open[t+1]$.

#### Money Flow Index (MFI)
- **Decisão**: Oscilador ponderado por volume entre 0 e 100 (período 14). Condição de sobrevenda extrema institucional: $MFI < 20$ com inflexão ascendente. Condição de sobrecompra institucional: $MFI > 80$ com inflexão descendente.

#### Volume Clímax / VSA Absorção
- **Decisão**: Vela de alto spread ($High - Low > 1.5 \cdot ATR(14)$) com volume no percentil 95+ dos últimos 20 dias ($Volume_t > SMA(Volume, 20) \times 2.0$), fechando no terço superior da vela para compra (absorção de liquidez de venda com cauda inferior expressiva) ou fechando no terço inferior com cauda superior para venda.

---

### 2.4 Família 4: Volatilidade e Tendência Dinâmica

#### SuperTrend / ATR Trailing
- **Decisão**: Cálculo clássico de SuperTrend utilizando $ATR(10)$ com multiplicador 3.0. Quando o fechamento cruza acima do limite superior de volatilidade, vira tendência compradora; quando cruza abaixo do limite inferior, encerra ou abre posição vendida.
- **Implementação**: Algoritmo recursivo $O(N)$ em passagem única rápida compatível com NumPy.

---

## 3. Integração ao Catálogo e Sistema

- **Arquivo de Destino**: `src/strategies/quantitative_indicators.py` conterá os motores de cálculo e a classe `QuantitativeIndicatorsEngine`.
- **Exposição**: Registrado no `StrategyCatalog` (`src/strategies/__init__.py`), adicionando 10 novas estratégias mapeáveis no Radar, no Simulador Clássico e no Simulador DCA.
- **Contratos**: Garantia estrita dos atributos `signal_bar_index`, `execution_bar_index`, `execution_price`, `reference_line_price` e `strategy_sub_id`.
