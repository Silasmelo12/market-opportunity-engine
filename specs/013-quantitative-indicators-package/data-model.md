# Data Model: Pacote de Estratégias Quantitativas com Indicadores Técnicos

## 1. Entities & Data Contracts

### 1.1 QuantitativeIndicatorStrategy Definition

Representa os metadados de registro de cada uma das 10 estratégias quantitativas:

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | `str` | Identificador único da estratégia | `"bollinger_close_in"` |
| `name` | `str` | Nome legível amigável | `"Bollinger Fechou Fora/Dentro"` |
| `family` | `str` | Família operacional | `"reversao_media"`, `"osciladores"`, `"volume_fluxo"`, `"volatilidade"` |
| `directions` | `List[str]` | Direções suportadas | `["BUY", "SELL"]` |
| `parameters` | `Dict[str, Any]` | Parâmetros configuráveis com valores default | `{"period": 20, "std_dev": 2.0}` |
| `description` | `str` | Descrição técnica concisa | `"Detecta exaustão quando o preço fecha fora e retorna para dentro das bandas."` |

### 1.2 Catálogo Completo dos Novos Indicadores (IDs e Nomes)

1. **`bollinger_close_in`**: *Bandas de Bollinger (Fechou Fora / Fechou Dentro)*
   - `sub_id`: `bb_reversal_buy` / `bb_reversal_sell`
2. **`keltner_squeeze`**: *Keltner Squeeze (Compressão & Expansão de Volatilidade)*
   - `sub_id`: `squeeze_breakout_buy` / `squeeze_breakout_sell`
3. **`zscore_extreme`**: *Z-Score de Preço em Extremos*
   - `sub_id`: `zscore_bottom_buy` / `zscore_top_sell`
4. **`rsi_divergence`**: *Divergência Regular de IFR/RSI*
   - `sub_id`: `rsi_bullish_div` / `rsi_bearish_div`
5. **`stochastic_extreme`**: *Estocástico Lento em Extremos (<20 / >80)*
   - `sub_id`: `stoch_oversold_cross` / `stoch_overbought_cross`
6. **`macd_momentum`**: *MACD Histogram Momentum (Inflexão de Histograma)*
   - `sub_id`: `macd_bottom_turn` / `macd_top_turn`
7. **`vwap_bands`**: *Bandas de VWAP (Retorno à Média Institucional)*
   - `sub_id`: `vwap_band_buy` / `vwap_band_sell`
8. **`mfi_extreme`**: *Money Flow Index (MFI) em Extremos*
   - `sub_id`: `mfi_bottom_buy` / `mfi_top_sell`
9. **`volume_climax_vsa`**: *Volume Clímax & Absorção VSA*
   - `sub_id`: `vsa_absorption_buy` / `vsa_climax_sell`
10. **`supertrend_trailing`**: *SuperTrend / ATR Trailing*
    - `sub_id`: `supertrend_bull_flip` / `supertrend_bear_flip`

---

## 2. Signal Output Contract (Herança do SignalRecord)

Cada sinal gerado satisfaz estritamente a dataclass `SignalRecord`:
```python
@dataclass(frozen=True)
class SignalRecord:
    strategy_id: str             # ex: "bollinger_close_in"
    strategy_sub_id: str         # ex: "bb_reversal_buy"
    signal_bar_index: int        # Barra t onde a condição foi satisfeita
    execution_bar_index: int     # Barra t+1 onde a execução simulada ocorreu
    execution_price: float       # Preço Open da barra t+1
    reference_line_price: Optional[float] = None # Valor do indicador na barra de sinal
    direction: str = "BUY"       # "BUY" ou "SELL"
    metadata: Optional[Dict[str, Any]] = None # Ex: {"zscore": -2.45, "rsi": 26.2}
```

---

## 3. Diagrama de Transição de Estado e Regra Anti-Lookahead

```text
[ Barra t: Formação de Preço e Volume ]
       │
       ▼
[ Fechamento da Barra t (Close[t]) ]
       │
       ├── Cálculo dos Indicadores Vetorizados (Apenas [0..t])
       │
       ▼
[ Avaliação da Condição de Disparo ]
       │
       ├── Satisfeito? ──► Gera Sinal (signal_bar_index = t)
       │
       ▼
[ Abertura da Barra t+1 (Open[t+1]) ]
       │
       └── Execução Imediata a Mercado:
           execution_bar_index = t + 1
           execution_price = Open[t + 1]
```
