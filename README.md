# Market Opportunity & Bottom Statistical Engine

Indicador Geral de Oportunidades de Mercado e Avaliador Estatístico de Fundos para perfil Holder / Acumulação.
Aplicação 100% Python via **Streamlit** (Single-Repo), com dados do **Yahoo Finance (`yfinance`)**, cache persistente em **Parquet**, e rigor matemático contra viés de antecipação (**Zero Look-Ahead Bias**).

---

## 🚀 Como Executar

### 1. Pré-Requisitos
- Python 3.10+ instalado.
- (Opcional) Instância do Redis para cache distribuído de alto desempenho via variável `REDIS_URL` (ex: `REDIS_URL=redis://localhost:6379/0`).
- Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Rodar a Aplicação Web
```bash
python run_server.py
```
Acesse no navegador: `http://localhost:8000`.

---

## 🏛️ Princípios & Arquitetura

O projeto é regido pela [Constituição v2.0.0](.specify/memory/constitution.md) (FastAPI backend + Web SPA frontend) e implementa:

1. **`src/data_loader/`**:
   - Ingestão via `yfinance` para 5 classes de ativos: Ações EUA (`AAPL`), Ações B3 (`PETR4.SA`), FIIs (`HGLG11.SA`), Criptomoedas (`BTC-USD`) e Commodities (`CL=F`).
   - Normalização para arrays NumPy 1D contíguos (`open`, `high`, `low`, `close`, `volume`).
   - Cálculo automático de **Dividend Yield Rolling 12m**.
   - Sanitização de nomes de ativos (remoção de sufixos `S.A.`, `S/A`, `SA`).
   - Cache persistente diário e opcional em Redis (`REDIS_URL`).

2. **`src/strategies/`**:
   - **Estratégias Proprietárias (4 variantes Compra + 4 variantes Venda)**.
   - **Padrões de Velas MQL5 (14 Compra + 14 Venda)**.
   - **Estratégias Clássicas e Institucionais (Total de 50 estratégias)**:
     - Fundo Duplo + BOS (Refinado com filtros de tendência SMA50, anti-máxima de 60 barras, RSI e profundidade).
     - Topo Duplo + BOS (Refinado com filtros de tendência SMA50, anti-mínima de 60 barras, RSI e profundidade).
     - Fundo Duplo Invertido (Venda - lógica empírica original).
     - Topo Duplo Invertido (Compra - lógica empírica original).
     - Wyckoff Spring e Wyckoff Upthrust (UTAD).
     - DCA Dinâmico, Rebalanceamento de Carteira e Value Proxy.

3. **`src/api/` e `src/web/`**:
   - **FastAPI REST API**: endpoints `/api/health`, `/api/strategies`, `/api/analyze`, `/api/radar` (paginado por ativo, com cache diário e fallback), `/api/simulate`.
   - **Terminal Web**: TradingView Lightweight Charts com botões de zoom in (+), zoom out (-) e reset, alternância de direção Compra / Venda / Ambos, e filtros dinâmicos de estratégia no Radar.

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
