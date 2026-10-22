# Contract: Quantitative Indicators API & Strategy Catalog

## 1. Endpoint: `/api/strategies`

### 1.1 Response Contract (Extensão)
O endpoint de listagem de estratégias deve incluir a nova lista com categorização e direções:

```json
{
  "strategies": [
    {
      "id": "bollinger_close_in",
      "name": "Bandas de Bollinger (Fechou Fora/Dentro)",
      "family": "reversao_media",
      "directions": ["BUY", "SELL"],
      "description": "Exaustão estatística e retorno à banda."
    },
    {
      "id": "keltner_squeeze",
      "name": "Keltner Squeeze (Compressão/Expansão)",
      "family": "reversao_media",
      "directions": ["BUY", "SELL"],
      "description": "Rompimento de volatilidade saindo de squeeze."
    },
    {
      "id": "zscore_extreme",
      "name": "Z-Score de Preço em Extremos",
      "family": "reversao_media",
      "directions": ["BUY", "SELL"],
      "description": "Desvio estatístico extremo em relação à média móvel."
    },
    {
      "id": "rsi_divergence",
      "name": "Divergência de IFR/RSI",
      "family": "osciladores",
      "directions": ["BUY", "SELL"],
      "description": "Divergência regular entre fundos/topos de preço e IFR."
    },
    {
      "id": "stochastic_extreme",
      "name": "Estocástico Lento em Extremos",
      "family": "osciladores",
      "directions": ["BUY", "SELL"],
      "description": "Cruzamento de %K e %D em sobrevenda/sobrecompra."
    },
    {
      "id": "macd_momentum",
      "name": "MACD Histogram Momentum",
      "family": "osciladores",
      "directions": ["BUY", "SELL"],
      "description": "Perda de força contrária e inflexão do histograma."
    },
    {
      "id": "vwap_bands",
      "name": "Bandas de VWAP",
      "family": "volume_fluxo",
      "directions": ["BUY", "SELL"],
      "description": "Retorno à média ponderada por volume e desvios institucionais."
    },
    {
      "id": "mfi_extreme",
      "name": "Money Flow Index (MFI) Extremo",
      "family": "volume_fluxo",
      "directions": ["BUY", "SELL"],
      "description": "Fluxo de dinheiro em sobrevenda ou sobrecompra."
    },
    {
      "id": "volume_climax_vsa",
      "name": "Volume Clímax / VSA Absorção",
      "family": "volume_fluxo",
      "directions": ["BUY", "SELL"],
      "description": "Absorção de liquidez com volume percentil 95+ e rejeição."
    },
    {
      "id": "supertrend_trailing",
      "name": "SuperTrend / ATR Trailing",
      "family": "volatilidade",
      "directions": ["BUY", "SELL"],
      "description": "Rastreamento de tendência e stop dinâmico por volatilidade."
    }
  ]
}
```

---

## 2. Compatibilidade com Endpoints Existentes
- `/api/radar/scan`: Aceita os novos `strategy_id` e executa a varredura normal.
- `/api/simulate/run`: Executa backtests com qualquer um dos novos IDs tanto em `buy_strategy` quanto em `sell_strategy`.
- `/api/simulate/optimize`: Itera sobre o catálogo expandido de estratégias tanto para combinações de trade quanto para rankings de acumulação DCA.
