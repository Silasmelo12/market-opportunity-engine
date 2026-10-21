---
description: "Tasks for feature 008: Matemática Multi-Buy Genérica, Tema Claro Global e Multi-Timeframe 5m"
---

# Tasks: Matemática Multi-Buy Genérica, Tema Claro Global e Multi-Timeframe 5m

**Input**: Design documents from `specs/008-multibuy-math-full-light-theme-multitimeframe/`  
**Prerequisites**: spec.md, plan.md  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(008): T### <descrição>` deve ser executado imediatamente.

---

## Phase 1: User Story 1 - Rigor Matemático Genérico para K Compras

**Goal**: Corrigir a matemática do simulador para que o capital investido reflita fielmente todos os aportes monetários de cada compra e o retorno percentual reflita a rentabilidade real sobre o dinheiro desembolsado.

- [X] T001 [US1] Escrever teste unitário em `tests/unit/test_accumulation.py` validando o cálculo genérico de $K$ compras (ex.: 3 compras de R$ 1.000 com preços 10, 8, 6 e venda a 10 gerando exatamente R$ 3.000 investidos, preço médio R$ 7,66 e retorno +30,5%).
- [X] T002 [US1] Atualizar `simulate_cycle_trade` em `src/evaluator/accumulation_simulator.py` para calcular o Capital Total Investido como a soma real de todos os aportes realizados nas $K$ compras de todos os ciclos, corrigindo o cálculo de `return_on_capital_pct = (net_profit / total_invested) * 100`.
- [X] T003 [US1] Atualizar o endpoint `/api/simulate` em `src/api/server.py` e o preenchimento no frontend em `src/web/app.js` para garantir consistência entre Capital Investido, PnL e Retorno da Estratégia.

---

## Phase 2: User Story 2 - Tema Claro Global e Consistência Visual em Todo o Sistema

**Goal**: Garantir que o Tema Claro estilize uniformemente todo o sistema (cabeçalho, barra lateral, cards, tabelas, modais, acordions e inputs), eliminando qualquer elemento preto residual.

- [X] T004 [P] [US2] Estender regras de CSS em `src/web/styles.css` sob o seletor `[data-theme="light"]` cobrindo todas as classes do Tailwind usadas na aplicação (`bg-fintech-surface`, `bg-fintech-bg`, `bg-gray-800`, `bg-gray-900`, `border-gray-700`, `text-gray-300`, tabelas, inputs e badges).
- [X] T005 [US2] Harmonizar badges semânticos e contrastes no `src/web/index.html` e `src/web/app.js` para que elementos de lucro (verde), prejuízo (vermelho) e status fiquem perfeitamente nítidos no tema claro.

---

## Phase 3: User Story 3 - Simulação e Análise em Múltiplos Tempos Gráficos (5m, 15m, 60m)

**Goal**: Adicionar suporte a tempos gráficos intradiários (`5m`, `15m`, `60m`) no simulador e na análise técnica.

- [ ] T006 [US3] Adicionar seletor de tempo gráfico (`interval`: 5m, 15m, 60m, 1d) no formulário do simulador em `src/web/index.html`.
- [ ] T007 [US3] Atualizar `src/web/app.js` para enviar o `interval` selecionado nas requisições do simulador e tratar dinamicamente períodos compatíveis com dados intradiários (ex.: `5d`, `1mo` para 5m).
- [ ] T008 [US3] Validar e garantir tratamento no backend em `src/api/server.py` para carregamento e simulação causal de dados intradiários (`5m`).

---

## Phase 4: Validação & Polish

- [ ] T009 Executar suíte completa de testes (`pytest tests/unit/ -v`) garantindo regressão zero e aprovação de todos os testes.
- [ ] T010 Atualizar o `README.md` destacando a matemática genérica multi-buy e o suporte completo a múltiplos tempos gráficos intradiários.
