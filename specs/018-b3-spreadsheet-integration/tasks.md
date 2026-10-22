# Tasks: B3 Spreadsheet Integration & Portfolio Tracking

**Input**: Design documents from `specs/018-b3-spreadsheet-integration/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tarefas executáveis em paralelo (arquivos distintos, sem dependências diretas)
- **[Story]**: Mapeamento para história de usuário (`US1`, `US2`, `US3`)

---

## Phase 1: Setup & Data Models (Foundational)

**Purpose**: Estruturas de dados Pydantic e base do parser da B3

- [x] T001 [P] [US1] Adicionar modelos `B3MovementRecord`, `B3Holding`, `B3MonthlyIncome` e `B3ParseResult` em `src/api/schemas.py`
- [x] T002 [P] [US1] Criar módulo base do parser `src/data_loader/b3_parser.py` com tipagem e leitura inicial de `.xlsx` com `openpyxl` e `pandas`

---

## Phase 2: User Story 1 - Integração e Cálculo da Carteira da B3 (Priority: P1) 🎯 MVP

**Goal**: Processar planilha oficial da B3 apurando custódia líquida, preço médio contábil ponderado e total de proventos.

**Independent Test**: Executar `pytest tests/unit/test_b3_parser.py` validando o cálculo de PM e quantidade líquida com o arquivo real `B3/movimentacao-2026-10-22-13-32-52.xlsx`.

- [x] T003 [US1] Implementar algoritmo contábil cronológico de Preço Médio e custódia líquida em `src/data_loader/b3_parser.py`
- [x] T004 [US1] Implementar extração e agrupamento mensal de Proventos (Dividendos, JCP, Rendimentos) em `src/data_loader/b3_parser.py`
- [x] T005 [P] [US1] Criar testes unitários em `tests/unit/test_b3_parser.py` testando compras, vendas parciais, zeragem de posição e soma de proventos
- [x] T006 [US1] Criar endpoints FastAPI `GET /api/b3/sync-local` e `POST /api/b3/parse` em `src/api/server.py`

**Checkpoint**: Backend processa qualquer planilha oficial da B3 e expõe a custódia e proventos via API.

---

## Phase 3: User Story 2 - Alimentação Completa da Aba Visão Geral (Priority: P1)

**Goal**: Exibir dados reais da B3 nos cards de Resumo, na tabela de Posições e na evolução de Proventos da Visão Geral, mantendo o layout e as sub-abas intactos.

**Independent Test**: Carregar a aplicação no navegador e verificar se a aba "Visão Geral" exibe os cards com os valores reais da B3 (R$ 683,39+ em proventos, total investido e cotação a mercado).

- [x] T007 [US2] Adicionar função `loadB3SpreadsheetData()` em `src/web/app.js` para chamar `/api/b3/sync-local` na inicialização
- [x] T008 [US2] Atualizar o botão/área de importação de carteira em `src/web/index.html` para aceitar `.xlsx` (B3) e `.csv`
- [x] T009 [US2] Integrar proventos totais e mensais no painel da Visão Geral em `src/web/app.js`
- [x] T010 [US2] Atualizar tabela de Posições da Visão Geral com Preço Médio e Custódia da B3 em `src/web/app.js`

**Checkpoint**: A aba Visão Geral está 100% preenchida com os dados oficiais da B3.

---

## Phase 4: User Story 3 - Sincronização com Terminal Gráfico, Radar e Rebalanceamento (Priority: P2)

**Goal**: Disponibilizar os ativos da B3 no Radar, no seletor de gráficos e traçar a linha de Preço Médio no gráfico de velas.

**Independent Test**: Selecionar um ativo da B3 no Terminal Gráfico (ex: `PETR4.SA`) e verificar a linha horizontal de referência no Preço Médio.

- [x] T011 [US3] Atualizar a cesta de ativos sugeridos / monitorados no Radar com os ativos da carteira B3 em `src/web/app.js`
- [x] T012 [US3] Adicionar linha horizontal de Preço Médio do investidor no gráfico TradingView Lightweight Charts em `src/web/app.js`
- [x] T013 [US3] Sincronizar o estado da aba Carteira (rebalanceamento) com a custódia apurada da B3 em `src/web/app.js`

---

## Phase 5: Polish & Validação Final

- [x] T014 Executar suite completa de testes com `pytest` (100 testes passando)
- [x] T015 Teste manual ponta a ponta com a planilha oficial `B3/movimentacao-2026-10-22-13-32-52.xlsx`
- [x] T016 Commit final na branch `018-b3-spreadsheet-integration`
