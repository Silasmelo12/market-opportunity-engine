# Implementation Plan: Feature 004 - Bidirectional Market Opportunity & Top/Bottom Statistical Engine

**Feature**: `004-bidirectional-top-bottom-engine`  
**Date**: 2026-10-20  
**Status**: Ready for Tasks  

---

## Technical Architecture & Core Changes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BROWSER SPA (Web Terminal 60fps)                      │
│                                                                             │
│  [🟢 Compra (24)]  [🔴 Venda (24)]  [⚡ Compra e Venda (48)]  <-- 0ms JS    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Lightweight Charts:                                                      │
│      - BUY:  arrowUp   / belowBar / #00E676 (Verde)                         │
│      - SELL: arrowDown / aboveBar / #FF5252 (Vermelho)                      │
│      - Suportes (Verde/Amarelo) & Resistências (Magenta/Vermelho)           │
│  • Plotly.js: Ranking & Scatter adaptados para Direção                      │
│  • Radar & Tabela Comparativa de Alocação Bidirecional                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ JSON Payload (/api/analyze)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI SERVER & API                              │
│                                                                             │
│  • Schemas: SignalItem (direction: "BUY"|"SELL"), ReferenceLineItem         │
│  • Cache TTL em memória consolidando BUY + SELL                             │
│  • /api/radar: Varredura com Semáforo de Fundo e de Topo                    │
│  • /api/simulate: Acumulação e Giro de Lucro / Venda no Topo                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│     MOTORES MATEMÁTICOS      │              │    AVALIADOR ESTATÍSTICO     │
│                              │              │                              │
│ 1. Prop. Reversal Machine    │              │ • Condicional por direction: │
│    - BUY:  Mínima rompida    │              │   - BUY: Win se Close > P    │
│    - SELL: Máxima rompida    │              │   - SELL: Win se Close < P   │
│ 2. Price Action de Topo/Fundo│              │ • Forward Return % & MAE %   │
│    - BOS & Wyckoff Upthrust  │              │ • Timing Classifier de Topo  │
│ 3. 14 Velas Bearish (MQL5)   │              │   (IDEAL, EXTENDED, LATE)    │
│ 4. Alocação & Realização     │              │ • Zero Look-Ahead Bias       │
└──────────────────────────────┘              └──────────────────────────────┘
```

---

## Proposed Changes by Component

### 1. Contratos Base (`src/strategies/base.py`)
- Adicionar o campo `direction: str = "BUY"` em:
  - `SignalRecord(frozen=True)`: padronizado com `"BUY"` ou `"SELL"`.
  - `ReferenceLineSegment(frozen=True)`: com `line_type: str = "SUPPORT"` (`"SUPPORT"` para fundos e `"RESISTANCE"` para topos) e `direction: str = "BUY"`.
  - `StrategyStatsSummary`: com `direction: str = "BUY"`.
- Garantir 100% de retrocompatibilidade com default `"BUY"`.

### 2. Motores Matemáticos de Venda / Topo
- **`src/strategies/proprietary_reversal.py`**:
  - Implementar suporte simétrico bidirecional (`direction="SELL"`):
    - Rompimento de alta: `Close[t] > High_Ref_B` ativa resistência.
    - Sobrescrita de resistência em novos topos: `c_t > cand_high`.
    - Gatilho de Negação de Topo: `Close[t] < active_resistance_line`.
    - Execução em Abertura: `Open[t+1]`.
    - Execução em Reteste na janela $M$: no primeiro toque da linha (`High[t+k] >= Linha * (1 - tol)`), se abrir em gap acima executa em `Open[t+k]`, senão executa na `Linha`.
    - 4 variantes de venda: `sell_t1_open`, `sell_t1_retest`, `sell_t2_open`, `sell_t2_retest`.
- **`src/strategies/mql5_candles.py`**:
  - Implementar os 14 padrões clássicos de topo (Shooting Star, Hanging Man, Bearish Engulfing, Dark Cloud Cover, Evening Star, Bearish Harami, Three Inside Down, Three Outside Down, Three Black Crows, Tweezer Top, Gravestone Doji, Abandoned Baby Bearish, Bearish Kicker, Climactic Bearish Pinbar).
  - Filtro prévio obrigatório de alta: `Close > SMA(Close, 20)`.
  - Corpo médio: `SMA(abs(Close - Open), 12)`.
  - Execução estrita em `Open[t+1]` com `direction="SELL"`.
- **`src/strategies/classic_engines.py`**:
  - Implementar:
    - `sell_double_top_bos`: dois topos com rompimento da neckline para baixo.
    - `sell_wyckoff_upthrust`: rompimento de máxima de resistência com fechamento de rejeição abaixo + volume alto.
    - `sell_overbought_stat`: desvio superior ou RSI(14) > 70.
    - `sell_rebal_rv_rf`, `sell_rebal_relative_strength`, `sell_value_proxy`.

### 3. Avaliador Estatístico Bidirecional (`src/evaluator/`)
- **`src/evaluator/statistical_engine.py`**:
  - Para sinais onde `direction == "SELL"`:
    $$\text{is\_win} = \text{Close}[t_{\text{exec}} + X] < P_{\text{exec}}$$
    $$\text{forward\_return\_pct} = \frac{P_{\text{exec}} - \text{Close}[t_{\text{exec}} + X]}{P_{\text{exec}}} \times 100$$
    $$\text{mae\_pct} = -\max\left(0, \frac{\max(\text{High}[t_{\text{exec}} : t_{\text{exec}} + X + 1]) - P_{\text{exec}}}{P_{\text{exec}}}\right) \times 100$$
  - Sinais de venda abertos (`t_exec + X >= len(close)`) continuam excluídos do Win Rate fechado.
- **`src/evaluator/timing_classifier.py`**:
  - Adicionar suporte a `direction="SELL"` no classificador de timing:
    - `IDEAL`: Preço na resistência ou recuo $\le 1.5\%$ abaixo de $P_{\text{exec}}$.
    - `EXTENDED`: Queda entre $1.5\%$ e $4.0\%$.
    - `LATE`: Preço já caiu mais de $4.0\%$.

### 4. Dicionário de Nomes e Catálogo (`src/ui/theme.py` & `src/strategies/__init__.py`)
- Adicionar os nomes comerciais em português para as 24 novas variantes de venda no `STRATEGY_LABELS_PT`.
- Catalogar os 48 sub-IDs (24 Compra + 24 Venda).

### 5. Backend FastAPI (`src/api/server.py` & `src/api/schemas.py`)
- Atualizar `SignalItem` e `StrategySummaryItem` com o campo `direction`.
- `/api/analyze`: Retorna lista consolidada de sinais de compra e venda.
- `/api/radar`: Inclui oportunidades de compra e venda com a devida categorização.

### 6. Frontend SPA Web Terminal 60fps (`src/web/`)
- **`index.html`**:
  - Adicionar o Seletor Segmentado de Direção de 3 estados no topo do terminal:
    - `[ 🟢 Compra | 🔴 Venda | ⚡ Compra e Venda ]`.
  - Atualizar os accordions da barra lateral com tabs ou seções claras separando Compra (24) e Venda (24).
- **`styles.css`**:
  - Adicionar estilos para botões segmentados de direção e badges de venda.
- **`app.js`**:
  - Adicionar `state.activeDirection = 'BOTH'` (`'BUY'`, `'SELL'`, `'BOTH'`).
  - Função `applyClientSideFiltering()` filtra instantaneamente em 0ms:
    ```javascript
    const dirFilter = state.activeDirection;
    const filteredSignals = allSignals.filter(s =>
      (dirFilter === 'BOTH' || s.direction === dirFilter) && isStrategyActive(s.strategy_sub_id)
    );
    ```
  - **Lightweight Charts Markers**:
    - Se `sig.direction === 'SELL'`: `position: 'aboveBar'`, `shape: 'arrowDown'`, `color: '#FF5252'`.
    - Se `sig.direction === 'BUY'`: `position: 'belowBar'`, `shape: 'arrowUp'`, `color: '#00E676'`.

---

## Verification Plan

### Automated Tests
1. **Contratos e Invariantes**:
   - `tests/unit/test_bidirectional_contracts.py`: testar default `direction="BUY"` e `direction="SELL"`.
2. **Motores de Topo (Zero Look-Ahead Bias)**:
   - `tests/unit/test_proprietary_top_reversal.py`: sobrescrita de resistências, gap de alta em reteste, consumo em toque único.
   - `tests/unit/test_mql5_top_candles.py`: 14 padrões bearish com filtro `Close > SMA(20)` e execução em $t+1$.
3. **Avaliador Estatístico de Venda**:
   - `tests/unit/test_directional_evaluator.py`: verificar se queda gera retorno positivo e alta gera MAE negativo.
4. **API e Endpoints**:
   - `tests/unit/test_api_endpoints.py`: checar se `/api/analyze` entrega `direction` em cada sinal.
5. **Regressão Global**:
   - Executar `python -m pytest tests/ -v` garantindo que os 32 testes anteriores + novos testes passem com 100% de sucesso.
