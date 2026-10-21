---
description: "Task list for feature 007: Multi-Buy Cycle Trade, Light Theme & Enhanced Professional Simulator"
---

# Tasks: Multi-Buy Cycle Trade, Light Theme & Enhanced Professional Simulator

**Input**: Design documents from `/specs/007-multi-buy-cycle-simulator-and-light-theme/`  
**Prerequisites**: [plan.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/plan.md), [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/spec.md), [research.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/research.md), [data-model.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/data-model.md), [contracts/simulate-contract.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20%26%20Bottom%20Statistical%20Engine/specs/007-multi-buy-cycle-simulator-and-light-theme/contracts/simulate-contract.md)  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(007): T### <descrição>` deve ser executado imediatamente.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tarefa paralelizável (arquivos diferentes, sem dependências de tarefas incompletas)
- **[Story]**: Mapeamento para Histórias de Usuário ([US1], [US2], [US3])
- Caminhos absolutos/relativos exatos especificados para cada tarefa

---

## Phase 1: Setup & Foundational Prerequisites

**Purpose**: Preparar modelos e contratos de dados para acomodar múltiplas compras por ciclo e métricas institucionais estendidas.

- [X] T001 Definir dataclass `BuyEntryRecord` e atualizar dataclass `TradeRecord` em `src/evaluator/accumulation_simulator.py` com campos `buy_entries`, `num_entries`, `average_buy_price`, `total_invested` e `total_shares`.
- [X] T002 Atualizar schemas Pydantic em `src/api/schemas.py` (`SimulateRequest`, `SimulationMetricSummary`, `TradeRecordSchema`) incluindo `contribution_amount`, `profit_factor`, `win_rate_pct`, `buy_and_hold_return_pct`, `avg_entries_per_cycle` e lista `buy_entries`.

---

## Phase 2: User Story 1 - Multi-Buy Cycle Accumulation & Complete Exit (Priority: P1) [MVP]

**Goal**: Permitir que a simulação no modo "Trade (Compra -> Venda)" compre em absolutamente todos os sinais de compra confirmados antes do sinal de venda, acumulando cotas e recalculando o preço médio ponderado, e liquidando 100% da posição acumulada ao ocorrer um sinal de venda.

**Independent Test**: Executar `pytest tests/unit/test_accumulation.py -k "test_simulate_cycle_trade_multi_buy"` comprovando que 3 sinais consecutivos de compra acumulam cotas com preço médio correto e o sinal de venda subsequente liquida a totalidade com retorno e PnL consolidados.

### Testes & Implementação da História 1

- [X] T003 [US1] Criar teste unitário em `tests/unit/test_accumulation.py` (`test_simulate_cycle_trade_multi_buy`) cobrindo 3 compras consecutivas e 1 venda, validando cotas acumuladas, preço médio ponderado e PnL consolidado.
- [X] T004 [US1] Implementar a máquina de estados de múltiplas compras em `simulate_cycle_trade` dentro de `src/evaluator/accumulation_simulator.py`, permitindo compras subsequentes quando `in_pos == True`, calculando `average_buy_price = total_invested / total_shares`.
- [X] T005 [US1] Implementar a liquidação unificada de todas as cotas acumuladas no primeiro sinal de venda confirmado (`SELL`) em `src/evaluator/accumulation_simulator.py`, calculando retorno sobre o preço médio ponderado e marcando o ciclo como `"FECHADO"`.
- [X] T006 [US1] Tratar ciclo que permanece aberto na última barra do histórico em `src/evaluator/accumulation_simulator.py`, marcando como `"ABERTO"` e computando valor a mercado flutuante com base em `Close[-1]`.
- [X] T007 [US1] Integrar o parâmetro `contribution_amount` e o parsing das múltiplas compras no endpoint `/api/simulate` em `src/api/app.py`.

---

## Phase 3: User Story 2 - Modo Visual Claro / Escuro (Theme Toggle) (Priority: P2)

**Goal**: Adicionar alternador de Tema Claro / Escuro com paleta fintech institucional, contraste acessível, persistência no `localStorage` e adaptação dinâmica dos gráficos TradingView e Plotly.

**Independent Test**: Alternar o botão de tema no cabeçalho em `http://localhost:8000`, verificar que fundos, cards, textos, e eixos dos gráficos comutam instantaneamente sem quebra de contraste e a preferência persiste ao recarregar a página.

### Implementação da História 2

- [X] T008 [P] [US2] Adicionar variáveis de tema claro (`data-theme="light"`) e botão seletor de tema (ícone Sol/Lua) no cabeçalho em `src/web/index.html`.
- [X] T009 [US2] Implementar script de detecção inicial e alternância de tema no `src/web/app.js`, salvando e recuperando o estado via `localStorage.getItem('terminal_theme')`.
- [X] T010 [US2] Implementar função de atualização de estilo do TradingView Lightweight Charts (`applyOptions`) e gráficos Plotly (`Plotly.relayout`) no `src/web/app.js` ao alternar entre Claro e Escuro.

---

## Phase 4: User Story 3 - Simulador Visualmente Aprimorado, Didático e Profissional (Priority: P2)

**Goal**: Transformar o simulador em uma ferramenta executiva/institucional, com cards de KPIs financeiros em destaque (Retorno Estratégia vs. Buy & Hold, Win Rate, Fator de Lucro, Max Drawdown) e tabela de histórico com detalhamento das compras parciais por ciclo.

**Independent Test**: Rodar uma simulação na aba "Simulador" da SPA e verificar a renderização dos cartões KPI semânticos e a tabela de trades com badge de status, quantidade de compras, preço médio ponderado e histórico expansível.

### Implementação da História 3

- [X] T011 [US3] Implementar o cálculo de métricas institucionais estendidas (`profit_factor`, `max_drawdown_pct`, `win_rate_pct`, `avg_entries_per_cycle`, `buy_and_hold_return_pct`) em `src/evaluator/accumulation_simulator.py`.
- [X] T012 [P] [US3] Redesenhar o layout do cabeçalho de resultados do simulador em `src/web/index.html`, criando cards KPI profissionais (Retorno Estratégia vs. Buy & Hold, Win Rate, Profit Factor, Drawdown Máximo, Preço Médio vs. Saída).
- [X] T013 [US3] Atualizar a função de renderização do simulador em `src/web/app.js` para preencher os novos cards KPI institucionais e colorir comparativos com cores semânticas (verde/vermelho).
- [X] T014 [US3] Redesenhar a tabela de histórico de trades do simulador em `src/web/app.js` e `src/web/index.html`, incluindo badges de status ("FECHADO - LUCRO", "FECHADO - PREJUÍZO", "EM ABERTO"), preço médio de compra, quantidade de aportes no ciclo e visualizador de sub-entradas.

---

## Phase 5: Polish, Validação & README Executivo

**Purpose**: Validação end-to-end com a suíte de testes do projeto e criação de um README de padrão internacional para o GitHub.

- [ ] T015 Executar suíte completa de testes (`pytest tests/unit/ -v`) garantindo regressão zero em todas as estratégias e novos testes de acúmulo passando.
- [ ] T016 Atualizar e enriquecer o `README.md` do repositório com visual profissional, badges de qualidade, arquitetura FastAPI + SPA, demonstração do simulador multi-buy, modo claro/escuro e instruções claras de execução para recrutadores e avaliadores.

---

## Dependencies & Execution Order

```text
Foundational (T001 -> T002)
       │
       ▼
User Story 1: Multi-Buy Cycle (T003 -> T004 -> T005 -> T006 -> T007)  [MVP]
       │
       ├────────────────────────────────┐
       ▼                                ▼
User Story 2: Light Theme (T008-T010)  User Story 3: Enhanced Simulator (T011-T014)
       │                                │
       └────────────────────────────────┘
                       │
                       ▼
Polish & README Executivo (T015 -> T016)
```
