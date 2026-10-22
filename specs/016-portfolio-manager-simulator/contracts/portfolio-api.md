# API & UI Contracts: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Feature**: `016-portfolio-manager-simulator`  
**Date**: 2026-10-22

---

## 1. REST Endpoint: `POST /api/portfolio/advise`
Analisa a carteira atual do usuário (caixa + posições atuais) contra o universo alvo selecionado, identifica o Par de Estratégias Campeão e o Score de Potencial (0–100) de cada ativo, e retorna o **Plano de Ação de Hoje** (o que comprar, quanto comprar, o que vender, quanto vender, rotacionar ou manter).

### Request Payload (`PortfolioAdviseRequest`)
```json
{
  "available_cash": 10000.0,
  "holdings": [
    {
      "ticker": "PETR4.SA",
      "shares": 100.0,
      "average_buy_price": 35.50
    }
  ],
  "universe_category": "featured",
  "custom_tickers": [],
  "interval": "1d",
  "period": "2y",
  "max_weight_pct": 25.0,
  "rebalance_band_pct": 5.0,
  "min_rotation_score_delta": 15.0
}
```

### Response Payload (`PortfolioAdviseResponse`)
```json
{
  "universe_category": "featured",
  "interval": "1d",
  "period": "2y",
  "current_cash": 10000.0,
  "current_holdings_value": 3820.0,
  "total_portfolio_equity": 13820.0,
  "projected_cash_after": 1240.0,
  "projected_invested_after": 12580.0,
  "max_weight_pct": 25.0,
  "holdings_evaluated": [
    {
      "ticker": "PETR4.SA",
      "asset_name": "Petrobras",
      "shares": 100.0,
      "average_buy_price": 35.50,
      "current_price": 38.20,
      "market_value": 3820.0,
      "invested_value": 3550.0,
      "unrealized_pnl_value": 270.0,
      "unrealized_pnl_pct": 7.61,
      "current_weight_pct": 27.64
    }
  ],
  "recommendations": [
    {
      "ticker": "VALE3.SA",
      "asset_name": "Vale",
      "action_type": "BUY",
      "action_label": "COMPRAR",
      "reason_text": "Sinal de compra ativo em Timing IDEAL na estratégia campeã (Score 86.4/100).",
      "strategy_sub_id": "t1_retest",
      "strategy_label": "Negação Barra Ant. (Reteste)",
      "potential_score": 86.4,
      "timing_category": "IDEAL",
      "current_price": 61.20,
      "reference_price": 60.80,
      "current_shares": 0.0,
      "recommended_shares_delta": 56.0,
      "target_shares": 56.0,
      "order_value": 3427.20,
      "current_weight_pct": 0.0,
      "target_weight_pct": 24.80
    }
  ],
  "opportunity_ranking": [
    {
      "ticker": "VALE3.SA",
      "asset_name": "Vale",
      "category": "Ações Brasil",
      "current_price": 61.20,
      "champion_buy_id": "t1_retest",
      "champion_buy_label": "Negação Barra Ant. (Reteste)",
      "champion_sell_id": "sell_double_top_bos",
      "champion_sell_label": "Topo Duplo + BOS",
      "win_rate_pct": 78.5,
      "historical_return_pct": 64.2,
      "max_drawdown_pct": -8.4,
      "closed_trades": 6,
      "active_direction": "BUY",
      "timing_category": "IDEAL",
      "timing_label": "Ideal / Reteste Válido",
      "distance_pct": 0.65,
      "recommended_price": 60.80,
      "potential_score": 86.4
    }
  ]
}
```

---

## 2. REST Endpoint: `POST /api/portfolio/simulate`
Executa o Backtest Histórico Multiativos (Zero Look-Ahead Bias) iniciando com o capital configurado (ex: R$ 10.000,00), alocando proporcionalmente ao Score de Potencial nas estratégias campeãs de cada ativo e aplicando as 3 regras causais de rebalanceamento/rotação.

### Request Payload (`PortfolioSimulateRequest`)
```json
{
  "initial_capital": 10000.0,
  "universe_category": "featured",
  "custom_tickers": [],
  "interval": "1d",
  "period": "2y",
  "max_weight_pct": 25.0,
  "rebalance_band_pct": 5.0,
  "min_rotation_score_delta": 15.0,
  "start_date": null,
  "end_date": null
}
```

### Response Payload (`PortfolioSimulateResponse`)
```json
{
  "universe_category": "featured",
  "interval": "1d",
  "period": "2y",
  "metrics": {
    "initial_capital": 10000.0,
    "final_equity": 16450.80,
    "final_cash": 1820.30,
    "final_invested_value": 14630.50,
    "net_profit": 6450.80,
    "total_return_pct": 64.51,
    "benchmark_return_pct": 28.40,
    "alpha_vs_benchmark_pct": 36.11,
    "max_drawdown_pct": -9.85,
    "win_rate_pct": 76.47,
    "profit_factor": 2.85,
    "total_events_count": 32,
    "closed_exits_count": 17,
    "winning_exits_count": 13,
    "losing_exits_count": 4,
    "rebalance_rotations_count": 6
  },
  "final_holdings": [
    {
      "ticker": "ITUB4.SA",
      "asset_name": "Itaú Unibanco",
      "shares": 110.0,
      "average_buy_price": 31.20,
      "current_price": 35.80,
      "market_value": 3938.0,
      "invested_value": 3432.0,
      "unrealized_pnl_value": 506.0,
      "unrealized_pnl_pct": 14.74,
      "current_weight_pct": 23.94
    }
  ],
  "curve": [
    {
      "date": "2024-10-22",
      "portfolio_equity": 10000.0,
      "cash_balance": 10000.0,
      "invested_equity": 0.0,
      "benchmark_equity": 10000.0,
      "drawdown_pct": 0.0
    }
  ],
  "ledger_events": [
    {
      "event_id": 1,
      "date": "2024-11-04",
      "ticker": "PETR4.SA",
      "asset_name": "Petrobras",
      "event_type": "BUY",
      "event_label": "COMPRA",
      "strategy_sub_id": "price_action_double_bottom_bos",
      "strategy_label": "Fundo Duplo + BOS (Refinado)",
      "potential_score": 84.2,
      "execution_price": 34.80,
      "shares_delta": 71.0,
      "trade_value": 2470.80,
      "realized_pnl_value": null,
      "realized_pnl_pct": null,
      "weight_before_pct": 0.0,
      "weight_after_pct": 24.71,
      "cash_after": 7529.20,
      "portfolio_equity_after": 10000.0
    }
  ],
  "opportunity_ranking": []
}
```

---

## 3. Frontend UI Contract (`src/web/index.html` & `src/web/app.js`)

1. **Navigation Tab**:
   - `<button class="nav-tab-btn" data-tab="tab-portfolio">Carteira</button>` no `#main-nav-tabs`.
   - Ao ativar `tab-portfolio`, ocultar `#global-direction-selector` (mesmo comportamento ergonômico de `tab-simulator` e `tab-playbook`).
2. **LocalStorage Persistence Key**:
   - `market_engine_portfolio_v1`: armazena `{ availableCash, holdings: [{ticker, shares, averageBuyPrice}], universeCategory, customTickers, interval, period, maxWeightPct }`.
3. **Interactive Sections in `#tab-portfolio`**:
   - **Left Sidebar / Configuration Panel**:
     - Input de Caixa Disponível (`#portfolio-cash-input`, padrão `10000`);
     - Editor de Posições Atuais (`#portfolio-holdings-list` + formulário rápido para adicionar Ticker, Qtd e Preço Médio + botão "Limpar / 100% em Caixa");
     - Seletor de Universo Alvo (`#portfolio-universe-select`: Destaques, Ações Brasil, FIIs Brasil, Ações EUA, Commodities, Criptomoedas, Lista Personalizada);
     - Seletor de Tempo Gráfico (`#portfolio-interval-select`), Período (`#portfolio-period-select`) e Teto Máx. por Ativo (`#portfolio-max-weight-input`, padrão `25%`);
     - Botão Principal de Ação (`#btn-run-portfolio`: "Gerar Plano de Hoje & Simular Carteira").
   - **Main Content Area**:
     - **Seção 1 — Plano de Ação & Rebalanceamento Hoje**:
       - Resumo rápido (Patrimônio Atual, Caixa Livre Atual $\rightarrow$ Caixa Projetado Pós-Ordens, % Alocado Projetado);
       - Tabela/Cards de Ordens Acionáveis (`#portfolio-recommendations-tbody`) com badges semânticos (`COMPRAR` verde, `VENDER TOTAL` vermelho, `VENDER PARCIAL / REBALANCEAR` âmbar, `ROTACIONAR` ciano/roxo, `MANTER` neutro), estratégia campeã, Score de Potencial (barra de progresso 0–100), Preço, Cotas, Valor em R$ e Peso Atual $\rightarrow$ Alvo;
       - Botão opcional **"Aplicar Ordens na Minha Carteira"** (`#btn-apply-portfolio-orders`) para que o usuário possa atualizar sua carteira simulada local com 1 clique caso decida executar as recomendações.
     - **Seção 2 — KPIs e Gráficos do Simulador Histórico Multiativos**:
       - 6 Cards de KPIs Institucionais (Patrimônio Final, Lucro Líquido, Retorno % vs. Buy & Hold da Cesta, Win Rate %, Max Drawdown % e Total de Operações/Rotações);
       - Gráfico Plotly de Evolução Patrimonial (`#portfolio-equity-chart`: Carteira Gerenciada vs. Buy & Hold Equal-Weight vs. Caixa) + Gráfico de Composição de Alocação (`#portfolio-allocation-chart`);
       - Ranking de Potencial dos Ativos do Universo (`#portfolio-ranking-tbody`) e Histórico Cronológico de Operações/Rebalanceamentos (`#portfolio-ledger-tbody`).
