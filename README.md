# Market Opportunity & Bottom Statistical Engine

Indicador Geral de Oportunidades de Mercado e Avaliador Estatístico de Fundos para perfil Holder / Acumulação.
Aplicação 100% Python via **Streamlit** (Single-Repo), com dados do **Yahoo Finance (`yfinance`)**, cache persistente em **Parquet**, e rigor matemático contra viés de antecipação (**Zero Look-Ahead Bias**).

---

## 🚀 Como Executar

### 1. Pré-Requisitos
- Python 3.10+ instalado.
- Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Rodar a Aplicação Web
```bash
streamlit run src/app.py
```
Acesse no navegador: `http://localhost:8501`.

### 3. Rodar a Suíte de Testes Unitários e Integração
```bash
python -m pytest -v
```

---

## 🏛️ Princípios & Arquitetura

O projeto é regido pela [Constituição v1.0.0](.specify/memory/constitution.md) e implementa 4 módulos desacoplados:

1. **`src/data_loader/`**:
   - Ingestão via `yfinance` para 5 classes de ativos: Ações EUA (`AAPL`), Ações B3 (`PETR4.SA`), FIIs (`HGLG11.SA`), Criptomoedas (`BTC-USD`) e Commodities (`CL=F`).
   - Normalização para arrays NumPy 1D contíguos (`open`, `high`, `low`, `close`, `volume`).
   - Cálculo automático de **Dividend Yield Rolling 12m**.
   - Camada de cache persistente em disco em `.cache/data/{ticker}_{interval}.parquet`.

2. **`src/strategies/`**:
   - **Estratégia Proprietária de Negação de Rompimento (2x2)**: Máquina de estados $O(N)$ em NumPy puro rastreando as 4 combinações:
     - `t1_open`: Rompimento da barra anterior (`t-1`) + Compra na Abertura (`Open t+1`).
     - `t1_retest`: Rompimento da barra anterior (`t-1`) + Compra no Reteste (janela sequencial de $M$ barras com ciclo único e tratamento de gap de baixa).
     - `t2_open`: Rompimento de Mínima de Fundo de $N$ barras + Compra na Abertura (`Open t+1`).
     - `t2_retest`: Rompimento de Mínima de Fundo de $N$ barras + Compra no Reteste ($M$ barras).
     - Sobrescrita dinâmica da linha em rompimentos sucessivos antes da negação.
     - Captura do estado atual (`get_current_state()`) indicando a linha ativa aguardando negação ou reteste.
   - **8 Padrões Clássicos de Velas MQL5 (Artigo 101 - CCandlePattern)**:
     - Martelo, Engolfo de Alta, Linha Perfurante, Estrela da Manhã, Harami de Alta, Três Por Dentro, Três Por Fora e Três Soldados Brancos com `AvgBody = SMA(abs(Close - Open), 12)` e filtro de baixa `Close < SMA(20)`.
   - **6 Estratégias Clássicas**:
     - DCA Dinâmico (Desvio de 2 StdDev ou RSI 14 < 30).
     - Rebalanceamento RF vs. RV (banda de tolerância de 5% de drawdown).
     - Força Relativa vs. Benchmark (Z-Score de 60 períodos $\le -2.0$).
     - Value Proxy com Fallback Quantitativo (DY Rolling $\ge$ P80 + SMA200 ou Mayer Multiple $\le$ P15).
     - Price Action Fundo Duplo com falha de continuação + BOS.
     - Wyckoff Spring (sweep de suporte com rejeição e volume acima da média de 20).

3. **`src/evaluator/`**:
   - Avaliação prospectiva em $X$ barras pós-compra (20, 60, 120, 252).
   - Cálculo de:
     - **Win Rate (%)**: percentual onde $Close[t_{exec} + X] > P_{exec}$.
     - **Forward Return (%)**: retorno médio e mediano.
     - **MAE (%)**: Excursão Máxima Adversa (maior drawdown sofrido após a entrada).
     - **Taxa de Reteste (%)**: percentual de retestes preenchidos vs. total de negações.
     - **Efficiency Score**: score ponderado de risco/retorno.
   - Separação estrita: sinais com $t_{exec} + X \ge len(close)$ são marcados como `is_open=True` e exibidos no gráfico e cards, mas excluídos do cálculo fechado histórico para não distorcer estatísticas.

4. **`src/ui/`**:
   - **Monitor de Estado**: Mostra a Linha de Referência Ativa do ativo hoje e alertas da última barra.
   - **Gráfico de Preços (Candlesticks)**: Gráfico interativo com marcadores de compra (diferenciando concluídos de abertos) e linhas de referência horizontais.
   - **Painel Estatístico**: Ranking de Win Rate em barras horizontais e gráfico de dispersão Risco x Retorno (Calor MAE vs. Retorno Médio).
