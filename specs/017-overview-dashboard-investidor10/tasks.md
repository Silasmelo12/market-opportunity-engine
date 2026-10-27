# Tasks: Painel Executivo Visão Geral e Correção dos 9 Pontos de Dados

- [x] **Task 1: Backend - Endpoint de Cotações com Cache de 1h (`POST /api/portfolio/quotes`)**
  - Implementado no `src/api/server.py` o modelo Pydantic e a rota com normalização de tickers e cache TTL de 1 hora.
  - Criado e aprovado teste automatizado em `tests/unit/test_quotes_endpoint.py`.

- [x] **Task 2: Frontend - Integração de Cotações e Correção dos Cards de KPI (Cards 1, 2 e 3)**
  - Adicionada função `fetchPortfolioQuotes(tickers)` em `src/web/app.js`.
  - Corrigida a fórmula contábil do Card 1 (Patrimônio Total vs. Total Investido com precisão de 2 casas decimais).
  - Corrigido Card 2 (Destaques com melhor e pior ativos reais).
  - Corrigido Card 3 (Contagem precisa de posições no lucro vs. prejuízo, como BRKM5 no prejuízo).

- [x] **Task 3: Frontend - Ocultar Seletor de Direção na Visão Geral**
  - Ajustado `switchTab` em `src/web/app.js` adicionando `tabId === 'tab-overview'` na lista de ocultação de `#global-direction-selector`.

- [x] **Task 4: Frontend - Tabela "Meus Ativos" com Lucro/Prejuízo R$ e %**
  - Atualizada a tabela de cada grupo em `renderOverviewGroupedHoldings` com as colunas de retorno financeiro e percentual.

- [x] **Task 5: Frontend - Modal de Configuração de Metas Customizadas**
  - Criado modal `#modal-overview-metas` e botão "Ajustar Metas" no `src/web/index.html`.
  - Implementada edição de Meta de Patrimônio e Meta de FIIs com persistência em `localStorage`.

- [x] **Task 6: Frontend - Sincronização do Modo Claro nos Gráficos da Visão Geral**
  - Incluídos `overview-stacked-bar-chart` e `overview-donut-chart` na função `updateChartsTheme` e re-renderização em troca de tema.

- [x] **Task 7: Validação e Testes Automatizados**
  - Executada suíte de testes com `pytest tests/` (93 testes aprovados).
  - Executado detector de design `.agents/skills/impeccable/scripts/impeccable.cmd detect --json src/web/index.html` (0 warnings).
