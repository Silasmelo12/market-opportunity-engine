# Spec Drift Report

Generated: 2026-10-22T06:56:45-03:00
Project: Market Opportunity & Bottom Statistical Engine

## Summary

| Category | Count |
|---|---|
| Specs Analyzed | 16 |
| Requirements Checked | 139 |
| ✓ Aligned | 139 (100.0%) |
| ⚠️ Drifted | 0 (0.0%) |
| ✗ Not Implemented | 0 (0.0%) |
| 🆕 Unspecced Code | 0 |

## Detailed Findings

### Spec: 016-portfolio-manager-simulator - Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

#### Aligned ✓
- **FR-001**: Nova aba principal "Carteira" (`#tab-portfolio`) no menu de navegação, com ocultação dinâmica de `#global-direction-selector` quando ativa → `src/web/index.html`, `src/web/app.js:switchTab` & `tests/unit/test_api_endpoints.py:test_portfolio_tab_dom_and_ergonomics`.
- **FR-002**: Painel configurável com Caixa Disponível, Editor dinâmico de Posições Atuais, Universo Alvo, Tempo Gráfico, Período e Limite Máximo por Ativo (%) → `src/web/index.html:#tab-portfolio` & `src/web/app.js:setupPortfolioTab`.
- **FR-003**: Persistência de Caixa, Posições Atuais e Parâmetros em `localStorage` (`market_engine_portfolio_v1`) com restauração automática → `src/web/app.js:loadPortfolioStorage` / `savePortfolioStorage`.
- **FR-004**: Identificação automática do Par de Estratégias Campeão por ativo e cálculo determinístico do Score de Potencial (0 a 100) ponderando Win Rate (35%), Retorno Histórico (30%), Max Drawdown (15%) e Timing (20%) → `src/evaluator/portfolio_simulator.py:calculate_potential_score` / `compute_asset_opportunity_profile`.
- **FR-005**: Consultor de Rebalanceamento Hoje gerando ordens classificadas em `COMPRAR`, `VENDER TOTAL`, `VENDER PARCIAL / REBALANCEAR`, `ROTACIONAR` e `MANTER` → `src/evaluator/portfolio_simulator.py:advise_portfolio_rebalance` & `src/api/server.py:advise_portfolio_endpoint` (`POST /api/portfolio/advise`).
- **FR-006**: Detalhamento completo de cada recomendação com Ticker, Ação, Estratégia Campeã, Score, Status de Timing, Preço de Referência, Quantidade em cotas, Valor financeiro em R$ e Pesos Atual vs. Alvo (%) → `src/api/schemas.py:PortfolioActionRecommendationModel` & `src/web/app.js:renderPortfolioAdviseSection`.
- **FR-007**: Simulador Histórico Multiativos cronológico barra a barra com estrito *Zero Look-Ahead Bias* (execuções na abertura de $t+1$) → `src/evaluator/portfolio_simulator.py:simulate_portfolio_multi_asset` & `tests/unit/test_portfolio_simulator.py:test_simulate_portfolio_multi_asset_zero_lookahead_and_cash_conservation`.
- **FR-008**: Ordem de precedência operacional na barra (Liquidações Venda Total -> Rebalanceamento Parcial por teto -> Rotação Tática -> Compras proporcionais ao Score) com gestão de caixa único → `src/evaluator/portfolio_simulator.py:simulate_portfolio_multi_asset`.
- **FR-009**: Cálculo comparativo com Benchmark Buy & Hold Equal-Weight da Cesta e curvas temporais de patrimônio, caixa e drawdown → `src/evaluator/portfolio_simulator.py:PortfolioSimulationResult` & `src/web/app.js:renderPortfolioEquityChart`.
- **FR-010**: Cards de KPIs institucionais no frontend: Patrimônio Final, Lucro Líquido, Retorno %, Buy & Hold da Cesta vs Alfa, Win Rate com contagem de saídas, Max Drawdown % e Total de Operações/Rotações → `src/web/index.html`, `src/web/app.js:renderPortfolioSimulationKPIs`.
- **FR-011**: Tabela de Livro Razão Histórico de Operações e Rebalanceamentos detalhando data, ativo, tipo de ordem, estratégia, score, preço, cotas, valor financeiro, PnL realizado e saldo de caixa → `src/web/index.html:#portfolio-ledger-tbody` & `src/web/app.js:renderPortfolioLedgerTable`.
- **SC-001**: Tempo de execução < 5s para cesta padrão de ativos em cache → Validado em testes e execução local.
- **SC-002**: 100% de conservação estrita de caixa e respeito a teto máximo por ativo → `tests/unit/test_portfolio_simulator.py:test_advise_portfolio_10k_cash_respects_max_weight_cap_and_cash_conservation`.
- **SC-003**: 100% de invariância a truncamento temporal (Zero Look-Ahead Bias) → `tests/unit/test_portfolio_simulator.py:test_simulate_portfolio_multi_asset_zero_lookahead_and_cash_conservation`.
- **SC-004**: Persistência de dados e suporte total a temas Claro/Escuro sem perda de estado → `src/web/app.js`, `src/web/styles.css` & `tests/unit/test_api_endpoints.py:test_portfolio_tab_dom_and_ergonomics`.
- **SC-005**: 100% dos testes da suíte passando sem regressões (91/91 testes aprovados) → `pytest tests/ -v`.

#### Drifted ⚠️
*Nenhum desvio detectado.*

#### Not Implemented ✗
*Nenhum item pendente.*

---

### Spec: 015-radar-table-ux-refactor - Refatoração da Tabela do Radar

#### Aligned ✓
- **FR-001** a **FR-007**: Tabela simplificada de 8 colunas sem poluição visual, semáforo minimalista com bolinha e tooltip, direção compacta C/V, ordenação dinâmica por quantidade de sinais $N$ e Win Rate (%) → `src/web/index.html`, `src/web/app.js` & `tests/test_radar_pagination.py`.
- **SC-001** a **SC-005**: Conformidade de colunas, ordenação client-side instantânea e zero regressões.

---

### Spec: 014-chart-indicators-filter-tab-persistence - Exibição de Indicadores e Persistência de Aba

#### Aligned ✓
- **FR-001** a **FR-007**: 10 novos indicadores com checkboxes e visualização no gráfico, filtragem inicial pela direção e restauração de aba ativa via hash/localStorage → `src/web/index.html`, `src/web/app.js`.

---

### Spec: 013-quantitative-indicators-package - Pacote de Estratégias Quantitativas

#### Aligned ✓
- **FR-001** a **FR-009**: 10 estratégias quantitativas (Bollinger, Keltner, Z-Score, IFR/RSI, Estocástico, MACD, VWAP, MFI, Volume Clímax, SuperTrend) vetorizadas com numpy/pandas, zero look-ahead bias e integração no catálogo `/api/strategies` → `src/strategies/quantitative_indicators.py` & `tests/unit/test_quantitative_indicators.py`.

---

## Inter-Spec Conflicts

Nenhum conflito entre especificações foi identificado. As regras de governança, convenções de rotas da API, isolamento de abas e modularização de estratégias mantêm consistência estrita em todas as 16 especificações do projeto.

## Recommendations

1. **Feature 016 Pronta para Integração Principal**: A implementação do Gestor, Consultor de Rebalanceamento e Simulador Multiativos está 100% aderente à especificação funcional e critérios de sucesso, com cobertura de testes unitários, de integração causal e de contrato DOM.
2. **Qualidade e Estabilidade Verificadas**: A suíte de 91 testes automatizados do repositório foi executada e obteve 100% de aprovação (0 falhas, 0 erros).
3. **Documentação de Drift Atualizada**: Os relatórios `.specify/sync/drift-report.md` e `.specify/sync/drift-report.json` foram atualizados refletindo 0% de drift no projeto.