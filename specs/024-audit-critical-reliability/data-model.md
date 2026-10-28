# Data Model: Confiabilidade Crítica e Experiência Operacional

## Entidades existentes afetadas

### B3ParseResult

- `filename`, `total_movements`, `holdings`, `total_invested`, `total_income`, `monthly_income`, `timeline`.
- A importação não transporta caixa. O frontend deve tratar caixa como estado separado.

### SimulationResult

- `total_invested`, `total_shares`, `current_equity`, `current_price`, `num_contributions`, `timeline_*`.
- `current_price` passa a representar o último close dentro da janela.
- `num_contributions` passa a contar apenas sinais BUY executados.

### SimulationMetricSummary

- `max_drawdown_pct`: derivado da curva.
- `dca_regular_final_value` e `alpha_vs_dca_pct`: passam a aceitar `null` quando não houver benchmark definido.

### RadarItem

- `historical_win_rate` é o campo canônico; o deck deve consumi-lo.

## Regras de integridade

1. Nenhum aporte em sinal SELL.
2. Nenhum preço posterior a `end_date` influencia a valuation.
3. Nenhum dado sintético é exibido sem rótulo de demonstração.
4. Nenhum caixa padrão é inferido após importação B3.
5. Nenhum benchmark é inventado; ausência é explícita.

## Contratos que não podem quebrar

- Rotas `/api/*` existentes.
- IDs de elementos usados por testes/E2E e handlers.
- Campos existentes de `RadarItem`, `SimulateResponse`, `B3ParseResult`.
- Estrutura de localStorage `market_engine_portfolio_v1`.
