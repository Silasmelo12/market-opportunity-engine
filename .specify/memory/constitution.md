<!--
Sync Impact Report:
- Version change: Uninitialized Template -> v1.0.0
- List of modified principles:
  * [PRINCIPLE_1_NAME] -> I. Arquitetura 100% Python & Otimização de Performance
  * [PRINCIPLE_2_NAME] -> II. Rigor Financeiro e Zero Look-Ahead Bias (NON-NEGOTIABLE)
  * [PRINCIPLE_3_NAME] -> III. Robustez Multi-Mercado & Fallback Quantitativo
  * [PRINCIPLE_4_NAME] -> IV. Modularidade Estrita e Contratos de Dados Padronizados
- Sections replaced:
  * [SECTION_2_NAME] -> Performance & Cache Standards
  * [SECTION_3_NAME] -> Quality Gates & Development Workflow
- Follow-up TODOs: None
-->

# Market Opportunity & Bottom Statistical Engine Constitution

## Core Principles

### I. Arquitetura 100% Python & Otimização de Performance
- A aplicação DEVE ser 100% Python, executada e renderizada via interface web interativa com Streamlit em arquitetura Single-Repository, maximizando a eficiência de contexto e economia de tokens.
- O carregamento de dados DEVE ser centralizado no motor `yfinance`, obrigatoriamente acoplado a uma camada de cache local (`st.cache_data` e/ou persistência em formato Parquet) para prevenir rate-limiting e re-downloads redundantes.
- Indicadores clássicos e detecção de padrões de velas (referência MQL5 Artigo 101) DEVEM ser estritamente vetorizados via `pandas` e `numpy`.
- Estratégias dependentes de trajetória / path-dependent (como a Estratégia Proprietária de Negação de Rompimento) DEVEM ser implementadas como Máquinas de Estados Finitos com arrays NumPy puros em passagem única $O(N)$ ou compiladas via `@numba.njit` com controle explícito de variáveis de estado. É terminantemente proibido o uso de iterações lentas com `DataFrame.iterrows()` ou `DataFrame.apply()` em caminhos críticos de backtesting/sinais.
- A visualização gráfica principal de Candlesticks (OHLCV) com linhas de referência e marcadores de compra DEVE utilizar `streamlit-lightweight-charts` (Canvas do TradingView) ou Plotly otimizado com aceleração WebGL (`Scattergl`). Gráficos e painéis analíticos/comparativos DEVEM utilizar `plotly`.

### II. Rigor Financeiro e Zero Look-Ahead Bias (NON-NEGOTIABLE)
- Nenhuma decisão, filtro ou sinal de compra executado na barra $t$ PODE incorporar informações conhecidas apenas em $t+1$ ou barras posteriores. O viés de antecipação (look-ahead bias) é considerado falta gravíssima.
- Para estratégias de entrada por Ordem Limite / Reteste em até $M$ barras subsequentes à barra de negação $t$, a compra só DEVE ser registrada na barra exata $t + k$ (onde $1 \le k \le M$) em que a mínima da barra satisfizer a condição de execução (`Low[t+k] <= Preço_de_Referência`). Se nenhuma barra no horizonte de reteste atingir a condição, a ordem DEVE expirar sem execução.
- O módulo `statistical_evaluator` é o ÚNICO componente do sistema expressamente autorizado a consultar $X$ barras futuras a partir do preço/momento de execução da compra, e tal autorização se restringe estritamente ao cálculo do retorno prospectivo (Critério Holder) e do Drawdown Pós-Compra (Maximum Adverse Excursion - MAE).

### III. Robustez Multi-Mercado & Fallback Quantitativo
- O sistema DEVE fornecer suporte nativo e consistente a diferentes classes de ativos nos timeframes Diário (`1d`) e Semanal (`1wk`):
  - Ações dos EUA (ex: `AAPL`, `MSFT`);
  - Ações B3 (tickers com sufixo `.SA`);
  - Fundos Imobiliários B3 (FIIs com sufixo `.SA`);
  - Criptomoedas (pares cotados em dólar com sufixo `-USD`);
  - Commodities e Minérios (futuros com sufixo `=F`).
- Motores de estratégias que utilizem métricas fundamentalistas ou de valuation DEVEM aplicar automaticamente um *Fallback Quantitativo* transparente caso séries históricas longas de demonstrativos contábeis não estejam disponíveis no feed gratuito do `yfinance`:
  - Para Ações e FIIs: utilizar Dividend Yield Rolling 12m acumulado + Desconto percentual em relação à Média Móvel Simples de 200 períodos (SMA 200);
  - Para Criptomoedas e Commodities: utilizar Mayer Multiple (razão Preço / SMA 200) e desvios estatísticos da tendência.

### IV. Modularidade Estrita e Contratos de Dados Padronizados
- A base de código DEVE manter separação estrita e desacoplada em exatamente 4 módulos de domínio:
  1. `data_loader`: responsável por ingestão de dados, cacheamento, sanitização OHLCV e normalização de tickers multi-mercado;
  2. `strategy_engines`: responsável por processar indicadores e máquinas de estado, gerando pontos de entrada e gatilhos de compra;
  3. `statistical_evaluator`: responsável por backtests prospectivos, métricas estatísticas pós-compra (retornos em janelas fixas, MAE, taxas de acerto) sem interferir nos motores de estratégia;
  4. `ui_dashboard`: responsável pela renderização da interface Streamlit, gráficos interativos leves e dashboards comparativos.
- Todos os motores de estratégia (`strategy_engines`) DEVEM retornar uma estrutura padronizada (DataFrame estruturado ou TypedDict/dataclass), contendo obrigatoriamente os seguintes campos:
  - `signal_bar_index`: índice/data da barra de gatilho do sinal;
  - `execution_bar_index`: índice/data da barra em que a ordem foi de fato preenchida;
  - `execution_price`: preço efetivo da execução da compra;
  - `reference_line_price`: nível de preço de referência ou gatilho da negação/reteste (quando aplicável);
  - `strategy_sub_id`: identificador categórico do padrão, subtipo ou variação da estratégia.

## Performance & Cache Standards
- Todas as consultas de cotação via `data_loader` DEVEM passar pela camada de cache em disco/memória para minimizar latência na navegação do dashboard.
- Atualizações de filtros ou seletores de ativos no Streamlit DEVEM recalcular apenas os pipelines impactados, sem recarregar o dataset bruto caso o intervalo e o ticker permaneçam inalterados.
- Gráficos pesados não devem saturar a memória do navegador; séries temporais longas exibidas via Plotly devem ser otimizadas com WebGL (`Scattergl`) ou renderizadas diretamente via WebAssembly/Canvas (`streamlit-lightweight-charts`).

## Quality Gates & Development Workflow
- **Validação de Anti-Look-Ahead**: Qualquer alteração ou nova estratégia introduzida deve ser acompanhada de asserções unitárias comprovando que a entrada em $t$ independe de dados em $t+1$.
- **Testes de Contrato de Estratégia**: Todas as saídas de `strategy_engines` devem validar a presença e tipagem dos 5 campos obrigatórios do contrato padrão.
- **Eficiência Computacional**: Testes de benchmark devem validar que laços explícitos em Python (`iterrows`) não estão presentes em funções críticas de detecção de sinal.

## Governance
- Esta Constituição é o documento de governança suprema do projeto "Market Opportunity & Bottom Statistical Engine". Todas as especificações técnicas, planos de implementação e código-fonte DEVEM obedecer rigorosamente aos seus princípios.
- Qualquer alteração nos princípios estabelecidos requer formalização de emenda através do processo `/speckit-constitution`, justificativa clara e versionamento semântico:
  - **MAJOR**: Alterações ou quebras de princípios inegociáveis (ex: alteração de stack, contratos centrais de dados ou relaxamento de diretrizes anti-viés);
  - **MINOR**: Inclusão de novas classes de ativos, novos módulos ou novos requisitos de governança;
  - **PATCH**: Correções de grafia, detalhamentos explicativos ou ajustes menores de redação.
- Todos os planos e tarefas gerados via Spec Kit (`/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) devem validar a conformidade com as cláusulas deste documento.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19
