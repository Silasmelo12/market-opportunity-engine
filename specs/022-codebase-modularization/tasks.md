# Tasks: Modularização Incremental e Segura do Frontend (Fase 4A)

**Feature Branch**: `022-codebase-modularization`  
**Status**: Proposta Refinada para Revisão  
**Parent Plan**: [plan.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/022-codebase-modularization/plan.md)  
**Parent Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/022-codebase-modularization/spec.md)

---

## Baseline Oficial e Comando Canônico de Validação
- **Total Coletado**: 130 testes (97 unit + 18 e2e + 15 raiz)
- **Status Exigido**: 128 PASSED, 2 SKIPPED (em planilhas opcionais B3), 0 FAILED
- **Comando Canônico de Validação**:
  ```powershell
  $env:PYTHONPATH="."; pytest tests/ -v
  ```
- **Regra de Execução**: Se um teste falhar em qualquer tarefa, reverter imediatamente a alteração antes de continuar.

---

## Bloco 1: Constantes Estáticas e Dicionários (Dependência Zero)

- [x] **Task 1.1**: Criar `src/web/modules/constants.js` contendo `TICKER_ALIASES`, `ASSET_NAMES`, `CANONICAL_ROUTES`, `ROUTE_ALIASES` e `ALLOWED_RETURN_ROUTES`, garantindo exportação compatível com o navegador.
- [x] **Task 1.2**: Atualizar `src/web/index.html` e `src/web/app.js` para consumir `constants.js` sem quebrar o acesso em tempo de inicialização.
- [x] **Task 1.3**: Executar validação de integridade:
  - `node --check` nos arquivos JavaScript alterados (`constants.js`, `app.js`).
  - `git diff --check`.
  - `pytest tests/test_normalizer_suffix.py tests/unit/test_ui_contracts.py tests/test_radar_pagination.py -v` (15 passed, 0 failed).
  - Validação Playwright no navegador confirmando escopo global (`window.*`) e funções dependentes (`resolveTicker`, `getAssetName`).

---

## Bloco 2: Funções Puras de Formatação e Utilitários

- [x] **Task 2.1**: Criar `src/web/modules/formatters.js` com `formatPrice`, `stripCorporateSuffix`, `resolveTicker`, `sanitizeTickerParam` e `getAssetName`.
- [x] **Task 2.2**: Atualizar `src/web/index.html` e `src/web/app.js` para utilizar os formatadores do novo módulo mantendo compatibilidade global.
- [x] **Task 2.3**: Executar validação de formatação e nomes:
  - `node --check` em `constants.js`, `formatters.js` e `app.js`.
  - `git diff --check`.
  - `pytest tests/test_normalizer_suffix.py tests/unit/test_ui_contracts.py -v` (10 passed).
  - `pytest tests/e2e/test_dashboard_navigation.py` em testes E2E específicos de coerência matemática, ticker e títulos limpos (3 passed).
  - Validação Playwright no navegador confirmando exportação, moedas BRL/USD, pontos e sanitização.

---

## Bloco 3: Feedback Visual e Notificações (Toast e Loading)

- [x] **Task 3.1**: Criar `src/web/modules/toast.js` com `showToastNotification`, `hideToastNotification`, `showLoading` e `hideLoading`.
- [x] **Task 3.2**: Conectar `toast.js` ao `src/web/index.html` e substituir chamadas diretas em `src/web/app.js`.
- [x] **Task 3.3**: Executar validação de UI:
  - `node --check` em `constants.js`, `formatters.js`, `toast.js` e `app.js`.
  - `git diff --check`.
  - `pytest tests/unit/test_ui_contracts.py -v` (9 passed).
  - Validação Playwright no navegador confirmando exportação global de `showToastNotification`, `hideToastNotification`, `showLoading`, `hideLoading` e comportamento visual de classes e textos.
  - *Critério de parada*: Reverter se o toast ou o overlay de loading falharem nos testes de importação.

---

## Bloco 4: Módulo Isolado de Proventos

- [x] **Task 4.1**: Criar `src/web/modules/proventos.js` com `renderProventosTabChart(mode)` e `setupProventosControls()`.
- [x] **Task 4.2**: Atualizar `src/web/index.html` e `src/web/app.js` mantendo a delegação limpa da aba `#tab-proventos`.
- [x] **Task 4.3**: Executar validação da aba de proventos:
  - `pytest tests/e2e/test_proventos_layout.py` (3 testes: layout do gráfico, alternância mensal/anual e ausência de mojibake).
  - `$env:PYTHONPATH="."; pytest tests/ -v` (128 passed, 2 skipped).
  - *Critério de parada*: Reverter imediatamente se o gráfico de proventos vazar o card ou falhar na alternância.

---

## Ponto de Controle: Avaliação após Etapas 1–4 e Recomendação
- **Status das Etapas 1 a 4**: Concluídas com sucesso. Criados `constants.js`, `formatters.js`, `toast.js` e `proventos.js`.
- **Auditoria de `toast-message`**: Confirmada como correção legítima de codificação UTF-8 (reparação de mojibake herdado).
- **Decisão sobre Etapas 5 e 6**: **Adiar** as extrações de Estado Global e Roteador.
  - *Justificativa*: Acoplamento bidirecional denso (>340 referências a `state.` e chamadas diretas de renderização no roteador). A extração prematura aumentaria a complexidade e o risco de quebra de testes sem gerar desacoplamento funcional expressivo sem bundler.
- **Recomendação Oficial**: **Adiar** novas extrações e consolidar o estado atual.

---

## Bloco 5: Auditoria e Mapeamento Seguro do Estado Global (`appState`)

- [ ] **Task 5.1**: Mapear detalhadamente os 32 campos de `window.appState` e as rotinas de persistência (`loadPortfolioStorage`, `savePortfolioStorage`, `getUserMetas`, `saveUserMetas`).
- [ ] **Task 5.2**: Criar `src/web/modules/state.js` mantendo a referência `window.appState` perfeitamente acessível para os scripts do navegador e avaliações do Playwright.
- [ ] **Task 5.3**: Executar validação de preservação de estado:
  - `pytest tests/e2e/test_dashboard_navigation.py::test_radar_state_preservation_and_chart_title`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_zero_cost_basis_displays_na_and_non_zero_cash_in_equity`
  - `$env:PYTHONPATH="."; pytest tests/ -v` (128 passed, 2 skipped).
  - *Critério de parada*: Reverter caso `window.appState` fique inacessível ou inconsistente para o Playwright.

---

## Bloco 6: Motor de Roteamento Hash e Navegação

- [ ] **Task 6.1**: Criar `src/web/modules/router.js` com `parseHashRoute`, `resolveRouteString`, `determineActiveRoute`, `navigateToRoute`, `switchTab` e listeners de `hashchange`/`popstate`.
- [ ] **Task 6.2**: Preservar os hooks globais invocados pelo Playwright (`window.applyTheme`, `location.hash`).
- [ ] **Task 6.3**: Executar validação completa de navegação:
  - `pytest tests/e2e/test_dashboard_navigation.py` (todos os 15 testes de roteamento, precedência e links contextuais).
  - `$env:PYTHONPATH="."; pytest tests/ -v` (128 passed, 2 skipped).
  - *Critério de parada*: Reverter caso ocorra falha de fallback de hash ou histórico quebrado.

---

## Bloco 7: Telas de Domínio (Decompostas em Tarefas Independentes)

### Tarefa 7.1: Módulo Overview (Visão Geral e Metas)
- [ ] **Task 7.1.1**: Extrair `src/web/modules/overview.js` com `renderOverviewDashboard`, `renderOverviewStackedBarChart`, `renderOverviewDonutChart`, `renderOverviewGroupedHoldings`, `updateOverviewMetasProgress` e modal de metas.
- [ ] **Task 7.1.2**: Integrar com `index.html` e delegar chamadas da Visão Geral em `app.js`.
- [ ] **Task 7.1.3**: Validar com testes específicos e canônicos:
  - `pytest tests/unit/test_ui_contracts.py::test_spa_has_investidor10_hero_kpis_and_charts`
  - `pytest tests/unit/test_ui_contracts.py::test_regression_chart_container_no_flex_and_no_duplicate_overview`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_dashboard_math_is_internally_coherent`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_zero_cost_basis_displays_na_and_non_zero_cash_in_equity`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_fourth_kpi_excludes_missing_quotes_from_denominator`
  - `$env:PYTHONPATH="."; pytest tests/ -v`
- *Critério de parada*: Reverter se qualquer KPI divergir ou os gráficos Plotly de aportes/alocação sobrepuserem o layout.

### Tarefa 7.2: Módulo Custódia & Portfólio (Posições & Integração B3)
- [ ] **Task 7.2.1**: Extrair `src/web/modules/portfolio.js` com editor de posições manuais, upload de extratos B3 (`uploadMultipleB3Spreadsheets`), modal pré-flight de ordens e simulação de rebalanceamento.
- [ ] **Task 7.2.2**: Integrar com `index.html` e delegar chamadas da aba de Posições em `app.js`.
- [ ] **Task 7.2.3**: Validar com testes específicos e canônicos:
  - `pytest tests/unit/test_ui_contracts.py::test_spa_has_investidor10_category_accordions`
  - `pytest tests/unit/test_b3_parser.py`
  - `pytest tests/unit/test_portfolio_simulator.py`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_import_controls_open_the_shared_picker_and_csv_imports`
  - `$env:PYTHONPATH="."; pytest tests/ -v`
- *Critério de parada*: Reverter se o upload de extratos falhar, se o saldo em caixa não atualizar ou se o modal pré-flight apresentar erro.

### Tarefa 7.3: Módulo Radar Quantitativo
- [ ] **Task 7.3.1**: Extrair `src/web/modules/radar.js` com tabela de radar, paginação, menu de estratégias, filtros de categorias e ordenação.
- [ ] **Task 7.3.2**: Integrar com `index.html` e conectar eventos de filtro em `app.js`.
- [ ] **Task 7.3.3**: Validar com testes específicos e canônicos:
  - `pytest tests/test_radar_pagination.py`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_radar_state_preservation_and_chart_title`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_radar_commodities_clf_and_clean_title`
  - `$env:PYTHONPATH="."; pytest tests/ -v`
- *Critério de parada*: Reverter se a paginação, a filtragem direcional (BUY/SELL) ou a rolagem vertical do radar quebrarem.

### Tarefa 7.4: Módulo Gráfico Interativo (TradingView Lightweight Charts)
- [ ] **Task 7.4.1**: Extrair `src/web/modules/chart.js` com `initTradingViewChart`, controles de zoom, redimensionamento responsivo e overlay de preço médio.
- [ ] **Task 7.4.2**: Integrar com `index.html` e conectar eventos de troca de ticker em `app.js`.
- [ ] **Task 7.4.3**: Validar com testes específicos e canônicos:
  - `pytest tests/e2e/test_dashboard_navigation.py::test_positions_to_chart_contextual_navigation_and_return`
  - `pytest tests/e2e/test_dashboard_navigation.py::test_radar_to_chart_contextual_navigation_and_return`
  - `$env:PYTHONPATH="."; pytest tests/ -v`
- *Critério de parada*: Reverter se o canvas do gráfico não carregar as velas ou a navegação contextual a partir de Custódia/Radar quebrar.

### Tarefa 7.5: Módulo Simulador & Análise (DCA e Estratégias)
- [ ] **Task 7.5.1**: Extrair `src/web/modules/analysis_simulation.js` com gráficos de ranking e dispersão Plotly, formulários de simulação DCA e otimizador de parâmetros.
- [ ] **Task 7.5.2**: Integrar com `index.html` e delegar execução de simulações em `app.js`.
- [ ] **Task 7.5.3**: Validar com testes específicos e canônicos:
  - `pytest tests/unit/test_accumulation.py`
  - `pytest tests/unit/test_anti_lookahead.py`
  - `pytest tests/unit/test_api_endpoints.py`
  - `$env:PYTHONPATH="."; pytest tests/ -v`
- *Critério de parada*: Reverter se o cálculo de múltiplos aportes, o ranqueamento do campeão ou a curva de equity divergirem.

### Tarefa 7.6: Consolidação Final do Frontend
- [ ] **Task 7.6.1**: Revisar `src/web/app.js` assegurando que ele atue exclusivamente como orquestrador limpo de DOM Ready e eventos.
- [ ] **Task 7.6.2**: Executar validação global com o comando canônico (`$env:PYTHONPATH="."; pytest tests/ -v`) e confirmar exatamente 128 passed, 2 skipped, 0 failed.
