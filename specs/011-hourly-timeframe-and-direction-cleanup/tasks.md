---
description: "Tasks for feature 011: Suporte ao Timeframe 1h sem Erro 400 e Ocultação do Seletor de Direção"
---

# Tasks: Suporte ao Timeframe 1h sem Erro 400 e Ocultação do Seletor de Direção

**Input**: Design documents from `specs/011-hourly-timeframe-and-direction-cleanup/`  
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, quickstart.md  
**Governance Constraint**: **Commit por Tarefa OBRIGATÓRIO**. Para cada tarefa implementada e marcada como `[X]`, um commit atômico no formato `<tipo>(011): T### <descrição>` deve ser executado imediatamente.

---

## Phase 1: Setup & Foundational

- [ ] T001 [P] Adicionar `"60m": "730d"` e suporte a teto de 730 dias no mapeamento `MAX_PERIODS` de `src/data_loader/fetcher.py`.

---

## Phase 2: User Story 1 - Simulação no Timeframe de 1h / 60m sem Erro 400 (Priority: P1) 🎯 MVP

**Goal**: Permitir simulações e otimizações no tempo de 60 minutos / 1 hora com até 2 anos de histórico sem erro HTTP 400.

**Independent Test**: Executar uma simulação com `interval="60m"` ou `"1h"` via API ou frontend e obter HTTP 200 com métricas e histórico de trades preenchidos.

- [ ] T002 [P] [US1] Criar teste unitário em `tests/unit/test_resampler.py` (`test_load_asset_data_hourly_60m_supported`) validando que `DataLoader.load_asset_data` com `interval="60m"` e `interval="1h"` retorna série temporal com sucesso sem lançar ValueError.
- [ ] T003 [US1] Atualizar `src/api/server.py` nos endpoints de simulação e otimização para aceitar e normalizar `60m` e limitar períodos horários ao teto de 730d.
- [ ] T004 [US1] Atualizar `src/web/app.js` em `runSimulation` e `runOptimizer` para ajustar períodos horários para `730d` (em vez de `60d` ou `5y`).

---

## Phase 3: User Story 2 - Ocultação Contextual do Seletor de Direção (Priority: P2)

**Goal**: Ocultar os botões de "Compra", "Venda" e "Ambos" nas abas Simulador e Playbook, exibindo-os somente no Radar e Gráfico.

**Independent Test**: Alternar entre as 4 abas e confirmar que `#global-direction-selector` é ocultado imediatamente em `tab-simulator` e `tab-playbook`, e exibido em `tab-radar` e `tab-terminal`.

- [ ] T005 [US2] Atualizar a função `switchTab` em `src/web/app.js` para ocultar `#global-direction-selector` nas abas `tab-simulator` e `tab-playbook`, e exibi-lo exclusivamente em `tab-radar` e `tab-terminal`.

---

## Phase 4: Polish & Validação Global

- [ ] T006 Executar a suíte de testes unitários (`python -m pytest tests/unit/ -v`) garantindo 100% de aprovação e regressão zero.
- [ ] T007 Atualizar o `README.md` documentando o suporte ao timeframe de 60m/1h e a ergonomia contextual do cabeçalho.
