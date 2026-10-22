---
description: "Tasks for feature 012: Suporte ao Otimizador Mais Lucrativa para Acumulacao DCA"
---

# Tasks: Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA com Ranking de Estratégias de Compra e Ocultação de Venda no Frontend

**Input**: Design documents from `specs/012-dca-optimizer-and-ui-cleanup/`  
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, quickstart.md  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(012): T### <descrição>` deve ser executado imediatamente.

---

## Phase 1: Setup & Foundational

- [X] T001 [P] Atualizar schemas `OptimizeCombinationsRequest` e `StrategyPairRankItemModel` em `src/api/schemas.py` com suporte ao campo `simulation_mode`, `contribution_amount` e atributos enriquecidos de DCA (`total_invested`, `final_equity`, `average_buy_price`, `total_shares`).

---

## Phase 2: User Story 1 - Busca da Estratégia de Acumulação DCA Mais Lucrativa (Priority: P1) 🎯 MVP

**Goal**: Permitir a identificação da melhor estratégia de compra individual para Acumulação DCA e ranking de rentabilidade sobre capital aportado.

**Independent Test**: Executar uma requisição para `/api/simulate/optimize` com `simulation_mode="accumulation"` e obter retorno 200 contendo a estratégia de compra campeã e o ranking ordenado de estratégias de DCA.

- [X] T002 [P] [US1] Implementar a função `optimize_dca_strategies` em `src/evaluator/accumulation_simulator.py` filtrando sinais de compra, simulando aportes com `simulate_accumulation` e rankeando por rentabilidade percentual e patrimônio final.
- [X] T003 [US1] Criar teste unitário em `tests/unit/test_accumulation.py` (`test_optimize_dca_strategies_finds_champion`) validando que `optimize_dca_strategies` identifica a estratégia campeã e calcula retorno e patrimônio com exatidão.
- [X] T004 [US1] Atualizar o endpoint `/api/simulate/optimize` em `src/api/server.py` para rotear chamadas com `simulation_mode == 'accumulation'` para `optimize_dca_strategies`.
- [X] T005 [US1] Criar teste unitário em `tests/unit/test_api_endpoints.py` (`test_api_simulate_optimize_accumulation`) validando a rota `/api/simulate/optimize` no modo DCA.
- [X] T006 [US1] Atualizar `runOptimizer()` e `renderTopCombinationsTable` em `src/web/app.js` para enviar `simulation_mode` e adaptar o card da Campeã e tabela de ranking para métricas de acumulação (Total Aportado, Patrimônio, Preço Médio e Aportes).
- [X] T007 [US1] Ajustar o listener de `btnApplyChampion` em `src/web/app.js` para, no modo DCA, selecionar a estratégia de compra campeã e disparar `runSimulation()` mantendo consistência exata dos KPIs.

---

## Phase 3: User Story 2 - Ergonomia Visual Contextual para o Modo de Acumulação (Priority: P2)

**Goal**: Ocultar o dropdown de "Estratégia de Venda" quando o modo ativo for "Acumulação (DCA Fundos)".

**Independent Test**: Alternar o seletor de "Modo de Operação" e validar que o wrapper da estratégia de venda é ocultado no modo DCA e reexibido no modo Trade.

- [X] T008 [P] [US2] Adicionar wrapper identificado `#sim-sell-strategy-container` ao seletor de Estratégia de Venda em `src/web/index.html`.
- [ ] T009 [US2] Atualizar o listener do dropdown `sim-mode` em `src/web/app.js` para alternar a visibilidade de `#sim-sell-strategy-container` conforme o modo selecionado.

---

## Phase 4: Polish & Validação Global

- [ ] T010 Executar a suíte de testes unitários (`python -m pytest tests/unit/ -v`) garantindo 100% de aprovação e regressão zero.
- [ ] T011 Atualizar o `README.md` documentando o suporte ao otimizador de DCA e a ergonomia contextual no simulador.
