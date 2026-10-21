---
description: "Tasks for feature 010: Correção do Radar, Seletor de Modelo de Ciclo (1x vs Multi-Buy) e Alinhamento do Simulador"
---

# Tasks: Correção do Radar, Seletor de Modelo de Ciclo (1x vs Multi-Buy) e Alinhamento do Simulador

**Input**: Design documents from `specs/010-radar-direction-and-simulator-fixes/`  
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(010): T### <descrição>` deve ser executado imediatamente.

---

## Phase 1: Setup & Foundational

**Purpose**: Estruturas de dados e contratos compartilhados para suporte a modelo de ciclo configurável

- [X] T001 [P] Atualizar schemas Pydantic em `src/api/schemas.py` adicionando o campo `cycle_entry_mode` (`"multi_buy"` | `"single_buy"`, padrão `"multi_buy"`) em `SimulateRequest` e `OptimizeCombinationsRequest`.
- [X] T002 [P] Atualizar a dataclass `StrategyPairRankItem` em `src/evaluator/accumulation_simulator.py` adicionando o campo `cycle_entry_mode: str = "multi_buy"`.

---

## Phase 2: User Story 1 - Filtragem Reativa de Direção no Radar (Priority: P1) 🎯 MVP

**Goal**: Permitir que os botões Compra, Venda e Ambos no Radar atualizem a tabela imediatamente buscando oportunidades da direção selecionada no servidor e sincronizando o dropdown de estratégias.

**Independent Test**: Clicar em "Venda" na aba Radar e verificar que a tabela exibe oportunidades de venda/topo com os badges de timing corretos e que o menu de estratégias lista apenas filtros de venda.

- [X] T003 [US1] Corrigir `setupDirectionSelector` em `src/web/app.js` para atualizar `state.activeDirection`, resetar `state.radarPage = 1` e disparar `loadRadarData(false)` para requisitar os dados da direção ativa ao servidor.
- [X] T004 [US1] Atualizar `renderRadarStratMenu` em `src/web/app.js` ao alternar direção no radar para sincronizar os checkboxes de estratégia com a direção ativa (`BUY`, `SELL`, `BOTH`).
- [X] T005 [P] [US1] Adicionar teste unitário de endpoint em `tests/unit/test_api_endpoints.py` validando que `/api/radar` com `direction=SELL` e `direction=BOTH` retorna itens com as direções correspondentes.

---

## Phase 3: User Story 2 - Seletor de Modelo de Entrada no Ciclo (1x vs Multi-Buy) (Priority: P2)

**Goal**: Permitir ao usuário escolher explicitamente entre "Compra Única (1x por Ciclo)" e "Acumulação Multi-Buy (Nx por Ciclo)" no simulador.

**Independent Test**: Simular o mesmo ativo nos dois modos e verificar que em `single_buy` compras subsequentes no ciclo são ignoradas e o capital investido é estático, enquanto em `multi_buy` compras subsequentes adicionam cotas e recalculam o preço médio.

- [X] T006 [US2] Criar teste unitário em `tests/unit/test_accumulation.py` (`test_simulate_cycle_trade_single_buy_vs_multi_buy`) validando que no modo `single_buy` compras subsequentes no mesmo ciclo são ignoradas e o capital investido permanece inalterado.
- [X] T007 [US2] Implementar suporte a `cycle_entry_mode` (`"multi_buy"` vs `"single_buy"`) em `simulate_cycle_trade` dentro de `src/evaluator/accumulation_simulator.py`.
- [X] T008 [US2] Adicionar o seletor visual de modelo de entrada (`sim-cycle-mode`) no painel do Simulador em `src/web/index.html` com as opções "Compra Única (1x por Ciclo)" e "Acumulação Multi-Buy (Nx por Ciclo)".

---

## Phase 4: User Story 3 - Sincronização Fiel entre Otimizador e Simulador (Priority: P3)

**Goal**: Fazer com que o botão "Mais Lucrativa" avalie as combinações sob o tempo gráfico e o modelo de ciclo configurados no simulador, garantindo convergência de 100% ao clicar em "Aplicar e Simular".

**Independent Test**: Configurar tempo gráfico (ex: 5m) e modo de ciclo (1x ou Multi-Buy), clicar em "Mais Lucrativa", verificar o card campeão e clicar em "Aplicar e Simular", comprovando que os KPIs principais e o histórico de trades resultam em métricas idênticas.

- [X] T009 [US3] Atualizar `optimize_strategy_pairs` em `src/evaluator/accumulation_simulator.py` para receber `cycle_entry_mode` e avaliar o ranking sob o modelo de ciclo selecionado (1x ou Multi-Buy).
- [X] T010 [US3] Atualizar o endpoint `/api/simulate/optimize` em `src/api/server.py` para repassar `cycle_entry_mode` e limitar o período a `"60d"` para intervalos intraday (`5m`, `15m`, `60m`).
- [X] T011 [US3] Atualizar `runOptimizer()` e o botão de aplicação da campeã em `src/web/app.js` para ler `sim-interval`, limitar período em intraday, repassar `sim-cycle-mode` e garantir que o botão "Aplicar e Simular" execute com os mesmos parâmetros exatos.

---

## Phase 5: Polish & Validação Global

- [X] T012 Executar a suíte de testes unitários (`python -m pytest tests/unit/ -v`) garantindo 100% de aprovação e regressão zero.
- [X] T013 Atualizar a documentação executiva em `README.md` com as instruções do seletor de modelo de ciclo (1x vs Multi-Buy), alinhamento do otimizador e correção de direção no Radar.

---

## Dependencies & Execution Order

- **Phase 1 (Setup/Foundational)**: T001 e T002 podem rodar em paralelo. Bloqueiam Phases 3 e 4.
- **Phase 2 (User Story 1 - Radar)**: T003, T004 e T005 são independentes do simulador e podem ser validados como MVP imediato.
- **Phase 3 (User Story 2 - Seletor 1x vs Multi-Buy)**: T006 (teste) -> T007 (backend) -> T008 (frontend UI).
- **Phase 4 (User Story 3 - Otimizador e Alinhamento)**: Depende de T007; T009 -> T010 -> T011.
- **Phase 5 (Polish)**: Executar após a conclusão de todas as histórias.
