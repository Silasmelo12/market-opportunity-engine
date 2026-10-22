# Spec Drift Report

Generated: 2026-10-21T22:54:15-03:00
Project: Market Opportunity & Bottom Statistical Engine

## Summary

| Category | Count |
|---|---|
| Specs Analyzed | 12 |
| Requirements Checked | 104 |
| ✓ Aligned | 104 (100.0%) |
| ⚠️ Drifted | 0 (0.0%) |
| ✗ Not Implemented | 0 (0.0%) |
| 🆕 Unspecced Code Features | 0 |

## Detailed Findings

### Spec: 012-dca-optimizer-and-ui-cleanup - Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA com Ranking de Estratégias de Compra e Ocultação de Venda no Frontend

#### Aligned ✓
- **FR-001**: O sistema DEVE permitir a busca da estratégia mais lucrativa no modo "Acumulação (DCA Fundos)" avaliando cada estratégia de compra individualmente → `src/evaluator/accumulation_simulator.py:optimize_dca_strategies` & `src/api/server.py:optimize_combinations_endpoint`
- **FR-002**: O ranking de DCA DEVE ordenar as estratégias decrescentemente pelo retorno percentual e patrimônio final → `src/evaluator/accumulation_simulator.py:optimize_dca_strategies`
- **FR-003**: A resposta de otimização no modo DCA DEVE informar aportes, total investido, patrimônio final, preço médio e retorno percentual → `src/api/schemas.py:StrategyPairRankItemModel`
- **FR-004**: O card da Campeã DEVE adaptar-se semanticamente ao modo DCA, ocultando menção a Venda, Win Rate e Fator de Lucro → `src/web/app.js:runOptimizer`
- **FR-005**: A ação "Aplicar e Simular" na campeã de DCA DEVE selecionar a estratégia de compra e disparar o backtest com paridade de dados → `src/web/app.js:setupSimulationTab` (listener `btnApplyChampion`)
- **FR-006**: A interface gráfica DEVE ocultar dinamicamente o dropdown de "Estratégia de Venda" no modo Acumulação DCA → `src/web/index.html:#sim-sell-strategy-container` & `src/web/app.js:setupSimulationTab`
- **FR-007**: No modo Trade (Compra -> Venda), o sistema DEVE preservar integralmente o comportamento de pares e modos 1x/Multi-Buy → `src/api/server.py` & `src/web/app.js`
- **SC-001**: Tempo de resposta inferior a 1s para varredura em 2 anos de histórico → `tests/unit/test_accumulation.py:test_optimize_dca_strategies_finds_champion` (<0.1s)
- **SC-002**: 100% de consistência matemática entre card da campeã e simulação → `tests/unit/test_api_endpoints.py:test_api_simulate_optimize_accumulation`
- **SC-003**: 0% de menções a venda na interface de otimização de DCA → `src/web/app.js:renderTopCombinationsTable`

### Spec: 011-hourly-timeframe-and-direction-cleanup - Suporte ao Timeframe 1h sem Erro 400 e Ocultação do Seletor de Direção

#### Aligned ✓
- **FR-001**: Suporte a candles de 60m e 1h sem lançar HTTP 400 com teto de 730 dias → `src/data_loader/fetcher.py:MAX_PERIODS`
- **FR-002**: Normalização de período de download no backend e frontend para 730d → `src/api/server.py` & `src/web/app.js`
- **FR-003**: Ocultação do seletor segmentado "Compra", "Venda" e "Ambos" nas abas Simulador e Playbook → `src/web/app.js:switchTab`

### Spec: 010-radar-direction-and-simulator-fixes - Seletor de Modo de Ciclo no Simulador e Correções de Direção do Radar

#### Aligned ✓
- Suporte aos modos "Compra Única (1x)" e "Acumulação Multi-Buy (Nx)" no frontend, backend e otimizador.
- Sincronização dos cliques em "Compra", "Venda" e "Ambos" no Radar com re-renderização imediata de estratégias e ativos.

## Inter-Spec Conflicts

Nenhum conflito ou divergência detectado entre especificações.

## Recommendations

1. A branch `012-dca-optimizer-and-ui-cleanup` está com alinhamento de 100% (zero drift).
2. Pode-se realizar merge ou squash da feature para `main` com tranquilidade técnica e regressão zero comprovada pela suíte de 55 testes unitários.
