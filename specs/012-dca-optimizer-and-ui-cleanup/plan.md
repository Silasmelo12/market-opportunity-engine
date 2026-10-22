# Implementation Plan: Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA com Ranking de Estratégias de Compra e Ocultação de Venda no Frontend

**Branch**: `012-dca-optimizer-and-ui-cleanup` | **Spec**: [spec.md](./spec.md)

## Summary of Feature
Permite que o botão "Mais Lucrativa" no simulador funcione com precisão matemática no modo "Acumulação (DCA Fundos)", varrendo e rankeando as estratégias de compra por retorno e patrimônio acumulado, além de ocultar dinamicamente o seletor de venda na interface web quando a acumulação estiver ativa.

---

## Technical Context

- **Linguagem / Backend**: Python 3.11+ / FastAPI / NumPy / Pandas
- **Frontend**: HTML5 / Vanilla JavaScript / Tailwind CSS / TradingView Lightweight Charts / Plotly.js
- **Arquitetura de Avaliação**: `src/evaluator/accumulation_simulator.py` e `src/api/server.py`
- **Armazenamento / Cache**: `src/data_loader/fetcher.py` com Parquet local

---

## Constitution Check

- **Zero Look-Ahead Bias**: Preservado integralmente. As estratégias de compra continuam sendo confirmadas no fechamento de $t$ e executadas na abertura de $t+1$.
- **Performance & Vetorização**: Otimização vetorial com ordenação rápida em memória.
- **Commit por Tarefa**: Rigorosamente 1 commit atômico por tarefa implementada.
- **Transparência de UI**: Sincronização exata entre os cards da Campeã e o painel de KPIs.

---

## Implementation Phases

### Phase 1: Core Engine & Modelos
- Estender `src/api/schemas.py` com suporte ao campo `simulation_mode` e métricas enriquecidas de DCA em `OptimizeCombinationsRequest` e `StrategyPairRankItemModel`.
- Implementar a função `optimize_dca_strategies` em `src/evaluator/accumulation_simulator.py`.
- Integrar a nova função no endpoint `/api/simulate/optimize` em `src/api/server.py`, roteando para `optimize_dca_strategies` quando `simulation_mode == 'accumulation'`.

### Phase 2: Frontend & Ergonomia Contextual
- Em `src/web/index.html`, adicionar ID semântico `#sim-sell-strategy-container` ao wrapper da Estratégia de Venda.
- Em `src/web/app.js`:
  - Ocultar `#sim-sell-strategy-container` ao selecionar "Acumulação (DCA Fundos)" e reexibi-lo em "Trade".
  - Atualizar `runOptimizer()` para enviar `simulation_mode: mode` e `contribution_amount: capitalVal`.
  - Adaptar a renderização do Card da Campeã e da tabela de ranking para o modo DCA.
  - Sincronizar o botão "Aplicar e Simular" para aplicar a estratégia de compra campeã no modo DCA sem afetar vendas.

### Phase 3: Validação de Testes & Documentação
- Criar testes unitários em `tests/unit/test_accumulation.py` e `tests/unit/test_api_endpoints.py`.
- Executar a suíte de testes globais garantindo 100% de aprovação e regressão zero.
- Atualizar o `README.md`.
