---
description: "Tasks for feature 009: Fluxo de Caixa Realista e Reinvestimento de Vendas no Simulador de Ciclo"
---

# Tasks: Fluxo de Caixa Realista e Reinvestimento de Vendas no Simulador de Ciclo

**Input**: Design documents from `specs/009-portfolio-cash-accounting-reinvestment/`  
**Prerequisites**: spec.md, plan.md  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(009): T### <descrição>` deve ser executado imediatamente.

---

## Phase 1: User Story 1 - Reinvestimento de Caixa e Contabilidade de Fluxo de Caixa

**Goal**: Implementar a máquina de fluxo de caixa onde vendas retornam ao caixa e compras consomem o saldo existente antes de exigir novo capital do bolso.

- [X] T001 [US1] Criar teste unitário em `tests/unit/test_accumulation.py` (`test_simulate_cycle_trade_cash_reinvestment`) validando que os lucros e principal de uma venda anterior são reutilizados em compras subsequentes sem aumentar o capital investido do bolso.
- [ ] T002 [US1] Implementar o gerenciamento de `cash` e `cumulative_external_invested` em `simulate_cycle_trade` dentro de `src/evaluator/accumulation_simulator.py`, debitando compras prioritariamente de `cash` e creditando vendas integralmente em `cash`.
- [ ] T003 [US1] Atualizar o cálculo de retorno global da estratégia e a série temporal `timeline_invested` em `src/evaluator/accumulation_simulator.py` para refletir o capital externo desembolsado.
- [ ] T004 [US1] Sincronizar o preenchimento de métricas e curvas no frontend em `src/web/app.js` para garantir clareza no capital investido do bolso versus patrimônio líquido.

---

## Phase 2: Validação & Documentação

- [ ] T005 Executar a suíte de testes unitários (`pytest tests/unit/ -v`) comprovando 100% de aprovação e regressão zero.
- [ ] T006 Atualizar o `README.md` documentando a modelagem realista de fluxo de caixa e reinvestimento automático de vendas.
