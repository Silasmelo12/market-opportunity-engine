# Research: Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA

## Contexto & Desafios Técnicos
Na versão anterior, o otimizador `/api/simulate/optimize` foi concebido estritamente para o modelo de `cycle_trade`, no qual pares de `(Compra, Venda)` são testados com liquidação total ao atingir a venda. No modo `accumulation` (DCA de Cotas), não ocorrem vendas: o investidor adquire cotas fixas em todos os sinais de compra confirmados.

## Decisões Técnicas

### 1. Endpoint Unificado vs. Novo Endpoint
- **Decisão**: Estender o endpoint existente `/api/simulate/optimize` para aceitar o campo `simulation_mode: str = "cycle_trade"`.
- **Justificativa**: Preserva a assinatura do frontend e centraliza toda a lógica de otimização em um único contrato `/api/simulate/optimize`, alinhando os parâmetros de requisição com o endpoint `/api/simulate`.
- **Alternativas consideradas**: Criar um endpoint `/api/simulate/optimize-dca`. Descartado para não fragmentar a API e manter o frontend com uma única chamada declarativa.

### 2. Algoritmo de Otimização DCA (`optimize_dca_strategies`)
- **Decisão**: Implementar `optimize_dca_strategies` em `src/evaluator/accumulation_simulator.py`.
- **Lógica**:
  1. Filtrar sinais apenas com `direction == "BUY"` no intervalo de datas solicitado.
  2. Executar `simulate_accumulation` para todas as estratégias de compra ativas no catálogo.
  3. Descartar estratégias que geraram 0 aportes.
  4. Ordenar decrescentemente por `return_on_capital_pct` (e secundariamente por `current_equity`).
  5. Retornar `champion` e `top_strategies`.

### 3. Modelo de Dados da Resposta da Otimização
- **Decisão**: Adaptar `OptimizeCombinationsResponse` para suportar tanto pares de trade quanto itens de ranking de DCA (`DCAStrategyRankItemModel` ou campos polimórficos em `StrategyPairRankItemModel`).
- **Campos do Item de DCA**:
  - `rank`: int (1, 2, 3...)
  - `buy_sub_id`: str (ID da estratégia de compra)
  - `buy_label`: str (Rótulo amigável)
  - `sell_sub_id`: None ou "-"
  - `sell_label`: "-"
  - `total_contributions`: int (Aportes realizados)
  - `total_invested`: float (Total aportado em R$)
  - `final_equity`: float (Patrimônio final acumulado em R$)
  - `total_return_pct`: float (Retorno percentual)
  - `net_profit`: float (Lucro líquido patrimonial)
  - `average_buy_price`: float (Preço médio ponderado)
  - `current_price`: float (Preço de fechamento atual)
  - `max_drawdown_pct`: float (Drawdown patrimonial)

### 4. Ocultação Dinâmica da Estratégia de Venda no Frontend
- **Decisão**: Em `setupSimulationTab()` em `src/web/app.js`:
  - Quando `elements.simMode.value === 'accumulation'`:
    - Adicionar a classe `hidden` ao container da Estratégia de Venda (`#sim-sell-strategy-container`).
  - Quando `elements.simMode.value === 'cycle_trade'`:
    - Remover a classe `hidden` do container da Estratégia de Venda.
- **Card da Campeã**: Quando `data.champion.simulation_mode === 'accumulation'` ou `selectedMode === 'accumulation'`, adaptar o cabeçalho e as colunas do card da campeã e da tabela de ranking para focar em aportes e patrimônio acumulado em vez de vendas e win rate.
