# Plan de Implementação: Visão Geral Executiva & Correção dos 9 Pontos de Dados

**Feature**: `017-overview-dashboard-investidor10`  
**Data**: 2026-10-22  
**Status**: Ready for Implementation  

---

## Fases de Execução

### Fase 1: Backend & Contrato de Cotações com Cache de 1h (FR-001)
1. **Endpoint `POST /api/portfolio/quotes`:**
   - Entrada: `{ "tickers": ["TASA4", "BRKM5", ...] }`
   - Resolução de tickers B3 com sufixo `.SA` automático (ex: `TASA4` -> `TASA4.SA`).
   - Obtenção do último preço (`Close` mais recente) via cache em memória com TTL de 3600 segundos (1 hora).
   - Retorno: `{ "quotes": { "TASA4.SA": { "price": 4.85, "change_pct": -1.2 }, "BRKM5.SA": { "price": 5.82, "change_pct": -2.1 } } }`
2. **Testes Unitários:** Adicionar teste `tests/unit/test_quotes_endpoint.py`.

### Fase 2: Cálculos Contábeis & Correção dos Cards 1 a 5 (FR-002, FR-003, FR-006)
1. **Carregamento Assíncrono de Cotações na Visão Geral:**
   - Chamar `/api/portfolio/quotes` ao abrir a Visão Geral ou ao mudar a carteira.
2. **Cálculo Correto do Card 1 (Patrimônio Total):**
   - Variação contábil: `((totalCurrentValue - totalInvested) / totalInvested) * 100`.
   - Se investido R$ 2.558,80 e atual R$ 2.560,21 -> exibe `+0.06%` em verde.
3. **Card 2 (Destaques da Carteira):**
   - Comparar `(currentPrice - avgPrice) / avgPrice * 100` para cada ativo com cotação real.
   - Encontrar o melhor e o pior ativo reais.
4. **Card 3 (Posições no Lucro):**
   - Ativo no lucro somente se `currentPrice > avgPrice`. Se menor (como BRKM5), conta como prejuízo.
5. **Tabela "Meus Ativos":**
   - Inserir colunas de Lucro/Prejuízo (R$) e Rentabilidade (%).

### Fase 3: Ergonomia, Contexto e Metas Customizadas (FR-004, FR-005, FR-007)
1. **Ocultar Seletor de Direção na Visão Geral:**
   - Adicionar `tabId === 'tab-overview'` na regra que oculta `#global-direction-selector`.
2. **Modal de Configuração de Metas:**
   - Criar modal `#modal-overview-metas` permitindo editar Meta de Patrimônio e Meta de FIIs.
   - Salvar no `localStorage` sob a chave `market_engine_user_metas`.
3. **Sincronização de Tema Claro nos Gráficos:**
   - Adicionar `overview-stacked-bar-chart` e `overview-donut-chart` na função `updateChartsTheme(theme)`.
