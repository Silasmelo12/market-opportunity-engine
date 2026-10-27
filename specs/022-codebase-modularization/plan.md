# Implementation Plan: Modularização Segura e Incremental do Frontend

**Feature Branch**: `022-codebase-modularization`  
**Created**: 2026-10-24  
**Last Updated**: 2026-10-24 (Decomposição Independente da Etapa 7)  
**Status**: Proposta Refinada para Revisão (Fase 4A — Planejamento)  
**Parent Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/022-codebase-modularization/spec.md)

---

## 1. Filosofia de Execução: Micropassos e Reversibilidade Total

Cada etapa define com precisão:
1. **Arquivos envolvidos** (origem, destino e index.html).
2. **Critérios de aceitação objetivos**.
3. **Testes específicos de validação rápida** e validação canônica completa.
4. **Condição de parada / aborto imediato**.

Comando Canônico de Validação Global:
```powershell
$env:PYTHONPATH="."; pytest tests/ -v
```

---

## 2. Detalhamento das Etapas de 1 a 6 (Fundação, Utilitários, Roteamento)

### Etapa 1: Constantes Estáticas e Dicionários
* **Arquivos envolvidos**: `src/web/modules/constants.js`, `src/web/index.html`, `src/web/app.js`.
* **O que é extraído**: `TICKER_ALIASES`, `ASSET_NAMES`, `CANONICAL_ROUTES`, `ALLOWED_RETURN_ROUTES`.
* **Critérios de Aceitação**: Constantes disponíveis no escopo global ou namespace. Tickers e nomes amigáveis continuam operacionais.
* **Testes Específicos**: `pytest tests/test_normalizer_suffix.py`, `pytest tests/unit/test_ui_contracts.py`.
* **Condição de Aborto**: Se nomes de ativos ficarem indefinidos ou qualquer teste falhar, reverter.

### Etapa 2: Funções Puras e Formatadores
* **Arquivos envolvidos**: `src/web/modules/formatters.js`, `src/web/index.html`, `src/web/app.js`.
* **O que é extraído**: `formatPrice`, `stripCorporateSuffix`, `resolveTicker`, `sanitizeTickerParam`, `getAssetName`.
* **Critérios de Aceitação**: Formatações de moeda BRL/USD idênticas à baseline.
* **Testes Específicos**: `pytest tests/test_normalizer_suffix.py`, `pytest tests/e2e/test_dashboard_navigation.py::test_dashboard_math_is_internally_coherent`.
* **Condição de Aborto**: Divergência numérica ou em rótulos monetários.

### Etapa 3: Feedback Visual e Notificações (Toast e Loading)
* **Arquivos envolvidos**: `src/web/modules/toast.js`, `src/web/index.html`, `src/web/app.js`.
* **O que é extraído**: `showToastNotification`, `hideToastNotification`, `showLoading`, `hideLoading`.
* **Critérios de Aceitação**: Notificações toast e spinner de loading preservados.
* **Testes Específicos**: `pytest tests/e2e/test_dashboard_navigation.py::test_import_controls_open_the_shared_picker_and_csv_imports`.
* **Condição de Aborto**: Erro de referência ao disparar toast ou importar arquivos.

### Etapa 4: Módulo Isolado de Proventos (Aba `#tab-proventos`)
* **Arquivos envolvidos**: `src/web/modules/proventos.js`, `src/web/index.html`, `src/web/app.js`.
* **O que é extraído**: `renderProventosTabChart(mode)`, `setupProventosControls()`.
* **Critérios de Aceitação**: Alternância Mensal/Anual e enquadramento de gráfico perfeitos.
* **Testes Específicos**: `pytest tests/e2e/test_proventos_layout.py` (3 testes dedicados).
* **Condição de Aborto**: Falha de renderização ou mojibake em proventos.

### Etapa 5: Auditoria e Mapeamento Seguro do Estado Global
* **Arquivos envolvidos**: `src/web/modules/state.js`, `src/web/app.js`.
* **O que é extraído**: `window.appState` inicial e rotinas de persistência (`loadPortfolioStorage`, `savePortfolioStorage`, `getUserMetas`, `saveUserMetas`).
* **Critérios de Aceitação**: `window.appState` permanece acessível no Playwright.
* **Testes Específicos**: `pytest tests/e2e/test_dashboard_navigation.py::test_radar_state_preservation_and_chart_title`.
* **Condição de Aborto**: Inacessibilidade ou perda de reatividade de `window.appState`.

### Etapa 6: Motor de Roteamento e Navegação Hash
* **Arquivos envolvidos**: `src/web/modules/router.js`, `src/web/app.js`.
* **O que é extraído**: `parseHashRoute`, `resolveRouteString`, `determineActiveRoute`, `navigateToRoute`, `switchTab`, `activateInvestidor10Tab`, listeners `hashchange`/`popstate`.
* **Critérios de Aceitação**: Precedência Hash > Storage > Default e histórico intactos.
* **Testes Específicos**: `pytest tests/e2e/test_dashboard_navigation.py` (15 testes).
* **Condição de Aborto**: Falha de roteamento ou perda de histórico contextual.

---

---

## 4. Ponto de Controle: Avaliação após Etapas 1–4 e Decisão sobre Etapas 5 e 6

### 4.1 Status Atual da Execução (Etapas 1 a 4 Concluídas)
* **Módulos criados**:
  1. `src/web/modules/constants.js`: Dicionários e constantes de mapeamento estático.
  2. `src/web/modules/formatters.js`: Funções puras de formatação monetária e sanitização de tickers.
  3. `src/web/modules/toast.js`: Utilitários de feedback visual (toast notification e loading overlay).
  4. `src/web/modules/proventos.js`: Renderização de gráficos Plotly e controles de proventos mensais/anuais.
* **Impacto no monólito**: `src/web/app.js` reduziu de 5.210 para 4.740 linhas (~470 linhas isoladas em módulos de responsabilidade única).
* **Validação dos Testes**: Baseline rigorosamente mantida (128 passed, 2 skipped).

### 4.2 Avaliação Técnica: Etapas 5 (Estado Global) e 6 (Roteador Hash)

#### Etapa 5: Extração do Estado Global (`appState` e Persistência)
* **Benefícios**:
  - Centraliza a inicialização da estrutura de dados reativa e funções utilitárias de persistência (`localStorage`).
  - Redução modesta (~120–180 linhas de app.js).
* **Riscos e Complexidade**:
  - Alto acoplamento em leitura/escrita: `state.` possui mais de 340 ocorrências diretas espalhadas em 86 funções em `app.js`.
  - Fragilidade com automação E2E: Testes Playwright avaliam diretamente `window.appState` (`radarActiveCategory`, `portfolioHoldings`, etc.).
  - Sem um sistema de módulos com bundler ou event-bus reativo, separar apenas a declaração de `window.appState` em `state.js` cria uma dependência de ordem estrita de `<script>` sem ganhos significativos de encapsulamento real.
* **Testes Necessários**:
  - `pytest tests/e2e/test_dashboard_navigation.py::test_radar_state_preservation_and_chart_title`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_zero_cost_basis_displays_na_and_non_zero_cash_in_equity`
  - Suíte canônica completa.
* **Custo de Manutenção**: Moderado a alto no curto prazo sem ganho arquitetural expressivo (permanecerá um objeto global mutável em `window`).

#### Etapa 6: Extração do Roteador Hash (`router.js`)
* **Benefícios**:
  - Isola o algoritmo de resolução de rotas (`parseHashRoute`, `resolveRouteString`, `determineActiveRoute`) e os listeners `hashchange`/`popstate`.
  - Isola ~250 linhas bem delimitadas.
* **Riscos e Complexidade**:
  - O roteador atual invoca diretamente callbacks de renderização das abas (`renderOverviewDashboard`, `renderRadarTable`, `renderCustodyCategories`, `initTradingViewChart`).
  - Extrair o roteador antes de extrair as telas de domínio exige passar uma tabela de despacho (*dispatcher/callback registry*) ou manter chamadas globais penduradas em `window`.
  - Alto risco de quebra de fluxo nos 15 testes E2E de navegação.
* **Testes Necessários**:
  - `pytest tests/e2e/test_dashboard_navigation.py` (todos os 15 testes de histórico, precedência e links contextuais).
  - Suíte canônica completa.
* **Custo de Manutenção**: Médio; se feito sem isolamento prévio dos módulos de domínio, introduz indireção desnecessária.

### 4.3 Auditoria de Codificação: Alteração do `#toast-message` em `index.html`
* **Constatação**: Durante a Etapa 4, o texto de `#toast-message` foi ajustado de `AÃ§Ã£o concluÃ­da com sucesso.` para `Ação concluída com sucesso.` (assim como o ícone de `âœ“` para `✓` e o título do modal de metas).
* **Veredito**: **Correção legítima de codificação (correção de mojibake)**.
  - No commit histórico `a7c6fbb`, o texto original foi introduzido em UTF-8 válido (`Ação concluída com sucesso.`).
  - No commit `2a64115`, uma gravação acidental com codificação corrompida (double-encoding / Windows-1252) transformou acentos e símbolos em mojibake (`AÃ§Ã£o`, `âœ“`).
  - A restauração realizada na Etapa 4 repõe a integridade original UTF-8 sem alterar IDs, seletores CSS ou lógica de execução, alinhada com as diretrizes de sanitização do projeto.

### 4.4 Recomendação Objetiva da Engenharia
* **Recomendação**: **ADIAR** as Etapas 5 (`state.js`) e 6 (`router.js`) neste momento.
* **Justificativa**:
  - As etapas 1 a 4 extraíram com sucesso as camadas de menor risco e maior reuso (constantes, formatadores, toast e proventos).
  - `state.js` e `router.js` possuem acoplamento bidirecional intenso com todas as rotinas de renderização que ainda residem em `app.js`. Extraí-los agora gera refatoração prematura de orquestração sem benefício real de desacoplamento.
  - A modularização deve ser pausada (ou concluída como Fase 4A bem-sucedida) com a suíte perfeitamente verde e zero regressões em produção. Caso se decida continuar a modularização futuramente, a prioridade deve ser desacoplar as telas de domínio (Etapa 7) antes do roteador e do estado.

### Etapa 7.1: Módulo Overview (Visão Geral e Metas)
* **Arquivos envolvidos**:
  * Criação: `src/web/modules/overview.js`
  * Modificação: `src/web/index.html` e `src/web/app.js` (L1652 a L2334 de `app.js`).
* **O que é extraído**:
  * `renderOverviewDashboard()` (4 cards de KPIs auditados: Patrimônio Total, Ganho Não Realizado, Proventos, Posições Acima do Preço Médio).
  * `renderOverviewStackedBarChart()` e `renderOverviewDonutChart()` (gráficos Plotly de Aportes e Alocação por Classe).
  * `renderOverviewGroupedHoldings()`, `updateOverviewMetasProgress()`, `setupOverviewMetasModal()`.
* **Critérios de Aceitação**:
  * Os 4 cards de KPIs exibem exatamente os valores calculados da custódia.
  * O gráfico de Aportes/Patrimônio empilhado e o donut de alocação renderizam sem sobreposição nem vazamento.
  * O modal de metas abre, salva no `localStorage` e atualiza as barras de progresso.
* **Testes Específicos**:
  * `pytest tests/unit/test_ui_contracts.py::test_spa_has_investidor10_hero_kpis_and_charts`
  * `pytest tests/unit/test_ui_contracts.py::test_regression_chart_container_no_flex_and_no_duplicate_overview`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_dashboard_math_is_internally_coherent`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_zero_cost_basis_displays_na_and_non_zero_cash_in_equity`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_fourth_kpi_excludes_missing_quotes_from_denominator`
* **Condição de Aborto**: Se qualquer KPI divergir, os gráficos Plotly não renderizarem ou houver falha nos testes acima, reverter imediatamente a extração de `overview.js`.

---

### Etapa 7.2: Módulo Custódia & Portfólio (Posições & Integração B3)
* **Arquivos envolvidos**:
  * Criação: `src/web/modules/portfolio.js`
  * Modificação: `src/web/index.html` e `src/web/app.js` (L4096 a L5116 de `app.js`).
* **O que é extraído**:
  * `syncPortfolioInputsFromState()`, `readPortfolioInputsToState()`.
  * `renderPortfolioHoldingsEditor()`, `setupPortfolioTab()`.
  * `uploadMultipleB3Spreadsheets()`, `applyB3ParsedResult()`, `importPortfolioHoldingsFromCsv()`.
  * `renderPortfolioAdviseSection()`, `openPreFlightOrderModal()`, `applyRecommendedPortfolioOrders()`, `undoAppliedPortfolioOrders()`.
  * `runPortfolioAdviseAndSimulate()`, `renderPortfolioSimulationKPIs()`, `renderPortfolioLedgerTable()`.
* **Critérios de Aceitação**:
  * Importação de arquivos CSV/XLSX atualiza a tabela de posições e o saldo em caixa.
  * A edição manual de ativos e preços médios recalcula o valor total de custódia.
  * O modal de pré-flight de ordens permite aplicar recomendações e suporta o botão "Desfazer".
* **Testes Específicos**:
  * `pytest tests/unit/test_ui_contracts.py::test_spa_has_investidor10_category_accordions`
  * `pytest tests/unit/test_b3_parser.py` (todos os testes unitários do parser B3).
  * `pytest tests/unit/test_portfolio_simulator.py` (simulação de alocação e ordens).
  * `pytest tests/e2e/test_dashboard_navigation.py::test_import_controls_open_the_shared_picker_and_csv_imports`
* **Condição de Aborto**: Falha na importação de extratos, cálculo incorreto de custódia ou quebra no modal pré-flight acarreta reversão imediata.

---

### Etapa 7.3: Módulo Radar Quantitativo
* **Arquivos envolvidos**:
  * Criação: `src/web/modules/radar.js`
  * Modificação: `src/web/index.html` e `src/web/app.js` (L2453 a L2777 e L3924 a L4095 de `app.js`).
* **O que é extraído**:
  * `loadRadarData()`, `renderRadarTable()`, `updateRadarPagination()`, `updateRadarExecutiveDeck()`.
  * `sortRadarItems()`, `setupRadarTableSorting()`.
  * `setupRadarCategoryPills()`, `setupRadarStrategyFilter()`, `renderRadarStratMenu()`, `updateRadarStratBadge()`, `updateRadarStratCheckboxes()`.
* **Critérios de Aceitação**:
  * O radar carrega ativos categorizados (Ações Brasil, FIIs, Cripto, Commodities, Índices).
  * Paginação e filtros por direção (BUY/SELL/BOTH) e estratégias operam sem lentidão.
  * Preservação de rolagem e página ao navegar para o gráfico e retornar.
* **Testes Específicos**:
  * `pytest tests/test_radar_pagination.py` (5 testes de paginação, limites e direção).
  * `pytest tests/e2e/test_dashboard_navigation.py::test_radar_state_preservation_and_chart_title`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_radar_commodities_clf_and_clean_title`
* **Condição de Aborto**: Se a paginação, a ordenação de colunas ou a preservação de filtros do radar falharem nos testes, reverter imediatamente.

---

### Etapa 7.4: Módulo Gráfico Interativo (TradingView Lightweight Charts)
* **Arquivos envolvidos**:
  * Criação: `src/web/modules/chart.js`
  * Modificação: `src/web/index.html` e `src/web/app.js` (L2335 a L2452 e L5179 a L5210 de `app.js`).
* **O que é extraído**:
  * `initTradingViewChart()`, `setupChartZoomControls()`, `resizeChartResponsive()`.
  * `updateTradingViewAveragePriceLine()` (linha de preço médio pontilhada vinda da custódia).
* **Critérios de Aceitação**:
  * Gráfico de velas renderiza os dados OHLCV com suporte a zoom e crosshair.
  * Ao carregar um ativo em carteira, a linha de preço médio é traçada na cotação correta.
  * O redimensionamento do container adapta a largura sem deformar a escala de tempo.
* **Testes Específicos**:
  * `pytest tests/unit/test_ui_contracts.py::test_spa_index_html_exists`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_positions_to_chart_contextual_navigation_and_return`
  * `pytest tests/e2e/test_dashboard_navigation.py::test_radar_to_chart_contextual_navigation_and_return`
* **Condição de Aborto**: Erro na biblioteca `LightweightCharts`, canvas não renderizado ou quebra na transição contextual Radar/Posições -> Gráfico.

---

### Etapa 7.5: Módulo Simulador & Análise (DCA e Estratégias)
* **Arquivos envolvidos**:
  * Criação: `src/web/modules/analysis_simulation.js`
  * Modificação: `src/web/index.html` e `src/web/app.js` (L2778 a L3923 de `app.js`).
* **O que é extraído**:
  * `loadAnalysisData()`, `applyClientSideFiltering()`.
  * `renderPlotlyRanking()`, `renderPlotlyScatter()`, `renderSignalsTable()`.
  * `setupSimulationTab()`, `runSimulation()`, `runOptimizer()`, `renderTopCombinationsTable()`, `renderSimulationTradesTable()`, `renderSimulationCurve()`.
* **Critérios de Aceitação**:
  * A análise individual calcula e plota as dispersões de retorno por estratégia.
  * O simulador executa o modelo de múltiplos aportes (DCA) e o otimizador ranqueia o campeão.
  * As curvas de equity do simulador e tabelas de trades encerram com os valores esperados.
* **Testes Específicos**:
  * `pytest tests/unit/test_accumulation.py` (11 testes de acumulação DCA, reinvestimento e otimização).
  * `pytest tests/unit/test_anti_lookahead.py` (6 testes de lookahead zero).
  * `pytest tests/unit/test_api_endpoints.py` (endpoints `/api/analyze` e `/api/simulate`).
* **Condição de Aborto**: Divergência nas métricas da simulação de trades ou falha nos gráficos de dispersão.
