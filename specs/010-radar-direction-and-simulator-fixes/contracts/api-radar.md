# Contract: /api/radar & Direction Filtering

**Feature**: `010-radar-direction-and-simulator-fixes`  
**Endpoint**: `GET /api/radar`  

---

## Parâmetros de Consulta

| Parâmetro | Tipo | Padrão | Descrição |
|---|:---:|:---:|---|
| `interval` | `str` | `1d` | Timeframe de análise (`1d`, `1wk`, `4h`, `1h`) |
| `category` | `str` | `featured` | Categoria de ativos |
| `direction` | `str` | `BUY` | Direção do sinal: `BUY`, `SELL` ou `BOTH` |
| `page` | `int` | `1` | Número da página (1-based) |
| `page_size` | `int` | `20` | Quantidade de itens por página |
| `strategies`| `str` | `""` | Filtro CSV de identificadores de estratégia |
| `refresh` | `bool` | `false` | Se força recálculo ignorando cache |

---

## Comportamento Esperado do Frontend ao Clicar na Direção

1. Ao clicar em **"Venda"**:
   - `GET /api/radar?direction=SELL&page=1&...`
   - Resposta contém apenas oportunidades com `direction == "SELL"`.
   - Dropdown de estratégias exibe apenas estratégias de venda.
2. Ao clicar em **"Ambos"**:
   - `GET /api/radar?direction=BOTH&page=1&...`
   - Resposta contém oportunidades de compra e venda mescladas.
   - Dropdown de estratégias exibe catálogo completo.
3. Ao clicar em **"Compra"**:
   - `GET /api/radar?direction=BUY&page=1&...`
   - Resposta contém apenas oportunidades com `direction == "BUY"`.
