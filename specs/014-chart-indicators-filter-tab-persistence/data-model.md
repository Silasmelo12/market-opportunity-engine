# Data Model: Estruturas de Interface e Persistência de Navegação

## 1. Entities & UI State

### 1.1 ActiveTabState
Representa o estado de navegação da Single Page Application (SPA):

| Propriedade | Tipo | Valores Permitidos | Padrão | Origem |
|---|---|---|---|---|
| `activeTab` | `string` | `"tab-radar"`, `"tab-terminal"`, `"tab-simulator"`, `"tab-playbook"` | `"tab-radar"` | URL hash / LocalStorage |
| `urlHash` | `string` | `"#radar"`, `"#terminal"`, `"#simulator"`, `"#playbook"` | `"#radar"` | `window.location.hash` |

### 1.2 SidebarStrategyItem
Definição dos novos checkboxes no DOM da barra lateral do gráfico:

| Atributo | Valor | Descrição |
|---|---|---|
| `class` | `"strategy-cb"` | Identifica checkbox para o listener de ativação |
| `data-id` | `string` | ID canônico do indicador técnico (ex: `"bollinger_close_in"`) |
| `data-dir` | `"BUY"` ou `"SELL"` | Direção associada ao grupo |

### 1.3 Aliases Map (Frontend `app.js`)
Extensão de `STRATEGY_ALIASES`:

```javascript
const STRATEGY_ALIASES = {
  // ... existentes
  'bollinger_close_in': ['bollinger_close_in', 'bb_reversal_buy', 'bb_reversal_sell'],
  'keltner_squeeze': ['keltner_squeeze', 'squeeze_breakout_buy', 'squeeze_breakout_sell'],
  'zscore_extreme': ['zscore_extreme', 'zscore_bottom_buy', 'zscore_top_sell'],
  'rsi_divergence': ['rsi_divergence', 'rsi_bullish_div', 'rsi_bearish_div'],
  'stochastic_extreme': ['stochastic_extreme', 'stoch_oversold_cross', 'stoch_overbought_cross'],
  'macd_momentum': ['macd_momentum', 'macd_bottom_turn', 'macd_top_turn'],
  'vwap_bands': ['vwap_bands', 'vwap_band_buy', 'vwap_band_sell'],
  'mfi_extreme': ['mfi_extreme', 'mfi_bottom_buy', 'mfi_top_sell'],
  'volume_climax_vsa': ['volume_climax_vsa', 'vsa_absorption_buy', 'vsa_climax_sell'],
  'supertrend_trailing': ['supertrend_trailing', 'supertrend_bull_flip', 'supertrend_bear_flip'],
};
```
