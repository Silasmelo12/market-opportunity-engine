# Tasks: Feature 004 - Bidirectional Market Opportunity & Top/Bottom Statistical Engine

**Input**: Design documents from `/specs/004-bidirectional-top-bottom-engine/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`)  
**Prerequisites**: Feature 001, Feature 002 e Feature 003  
**Status**: Concluído (100% dos testes unitários e de integração passando)  

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefas paralelizáveis (arquivos distintos, sem dependência mútua)
- **[Story]**: Mapeamento para história de usuário correspondente (`US1`, `US2`, `US3`, `US4`)

---

## Phase 1: Contratos Base Bidirecionais e Máquina de Venda Proprietária 2x2 [US2]
- [x] T001 [US2] Atualizar `src/strategies/base.py` adicionando o campo `direction: str = "BUY"` em `SignalRecord`, `ReferenceLineSegment` (incluindo `line_type: str = "SUPPORT"`) e `StrategyStatsSummary`, garantindo 100% de compatibilidade com os testes existentes.
- [x] T002 [US2] Implementar em `src/strategies/proprietary_reversal.py` o motor simétrico de VENDA de rompimento de máxima e negação de topo (`sell_t1_open`, `sell_t1_retest`, `sell_t2_open`, `sell_t2_retest`).
- [x] T003 [P] [US2] Criar teste unitário `tests/unit/test_proprietary_top_reversal.py` validando as 4 variantes de venda, sobrescrita de resistências, gap em reteste e invariância Zero Look-Ahead Bias.

---

## Phase 2: Velas de Topo, Price Action de Venda e Avaliador Estatístico Invertido [US2, US3]
- [x] T004 [US2] Expandir `src/strategies/mql5_candles.py` implementando vetorizadamente os 14 padrões clássicos de topo com filtro `Close > SMA(20)` e execução estrita em `Open[t+1]` com `direction="SELL"`.
- [x] T005 [US2] Expandir `src/strategies/classic_engines.py` com os métodos de venda: `sell_double_top_bos`, `sell_wyckoff_upthrust`, `sell_overbought_stat`, `sell_rebal_rv_rf`, `sell_rebal_relative_strength` e `sell_value_proxy`.
- [x] T006 [US3] Atualizar `src/evaluator/statistical_engine.py` e `src/evaluator/timing_classifier.py` aplicando as regras de cálculo específicas para `direction == "SELL"`.
- [x] T007 [P] [US2, US3] Criar testes unitários `tests/unit/test_mql5_top_candles.py` e `tests/unit/test_directional_evaluator.py` validando os padrões bearish e as métricas matemáticas de retorno/risco na venda.

---

## Phase 3: Backend FastAPI, Dicionário Amigável e Catálogo 48 Estratégias [US1, US3, US4]
- [x] T008 [US2] Atualizar `src/ui/theme.py` e `src/strategies/__init__.py` registrando os nomes comerciais em português das 24 estratégias de venda em `STRATEGY_LABELS_PT`, orquestrando as 48 estratégias totais no `StrategyCatalog`.
- [x] T009 [US1, US3] Atualizar `src/api/schemas.py` e `src/api/server.py` incluindo o campo `direction` em `SignalItem`, `ReferenceLineItem` e `StrategySummaryItem`, e integrando sinais de compra e venda no payload de `/api/analyze` e no `/api/radar`.
- [x] T010 [P] [US1] Atualizar `tests/unit/test_api_endpoints.py` validando o retorno de sinais bidirecionais (`BUY` e `SELL`) com integridade de esquemas JSON.

---

## Phase 4: Frontend SPA Institucional com Seletor 3-Way e Setas Vermelhas [US1, US4]
- [x] T011 [US1] Atualizar `src/web/index.html` e `src/web/styles.css` adicionando o Seletor Segmentado de Direção no topo do Terminal (`[🟢 Compra | 🔴 Venda | ⚡ Compra e Venda]`), organizando os checkboxes da barra lateral com separação clara de Compra e Venda, e adicionando as explicações de topo no Playbook (Aba 4).
- [x] T012 [US1, US4] Atualizar `src/web/app.js` implementando estado reativo `state.activeDirection`, filtragem client-side em 0ms, marcadores vermelhos (`#FF5252`, `aboveBar`, `arrowDown`) para VENDA e verdes (`#00E676`, `belowBar`, `arrowUp`) para COMPRA, além de linhas de suporte e resistência pontilhadas.
- [x] T013 [US1, US2, US3, US4] Execução completa do pipeline de testes com `pytest` (39/39 passando).
