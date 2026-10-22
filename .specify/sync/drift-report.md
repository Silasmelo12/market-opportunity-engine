# Spec Drift Report

Generated: 2026-10-22T12:23:30-03:00
Project: Market Opportunity & Bottom Statistical Engine

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Specs Analyzed | 17 | Specs 001 a 017 |
| Requirements Checked | 154 | Cobertura total das specs |
| ✓ Aligned | 154 (100%) | Todas as regras implementadas e testadas |
| ⚠️ Drifted | 0 (0%) | Nenhuma divergência ativa |
| ✗ Not Implemented | 0 (0%) | Todos os requisitos atendidos |
| 🆕 Unspecced Code | 0 | Aba Visão Geral agora coberta pela Spec 017 |

## Detailed Findings

### Spec: 017-overview-dashboard-investidor10 - Painel Executivo Visão Geral
- FR-001: Endpoint `POST /api/portfolio/quotes` com cache de 1h -> `src/api/server.py` e `tests/unit/test_quotes_endpoint.py`
- FR-002: Variação percentual contábil real com sinal e 2 casas decimais -> `src/web/app.js`
- FR-003: Destaques com melhor e pior ativo reais com cotações de mercado -> `src/web/app.js`
- FR-004: Ocultação contextual do seletor global de direção na Visão Geral -> `src/web/app.js`
- FR-005: Modal de ajuste e persistência de metas financeiras em localStorage -> `src/web/index.html` e `src/web/app.js`
- FR-006: Colunas de Lucro/Prejuízo R$ e Rentabilidade % na tabela Meus Ativos -> `src/web/app.js`
- FR-007: Sincronização do tema claro em gráficos Plotly da Visão Geral -> `src/web/app.js`
- FR-008: Documentação do modelo CSV com suporte opcional a Data_Compra -> `specs/017-overview-dashboard-investidor10/spec.md`
