# Contract: Radar API

## GET /api/radar

| Query | Tipo | Default | Notas |
|---|---|---|---|
| interval | str | `1d` | |
| horizon_x | int | 60 | |
| category | str | `featured` | |
| refresh | bool | false | ignora cache |
| page | int | 1 | ≥1 |
| page_size | int | 20 | 1–100 |
| direction | str | `BUY` | `BUY`/`SELL`/`BOTH` |
| strategies | str | `""` | CSV de `strategy_sub_id`; vazio = todas |

**Response 200** — `RadarPage` (ver data-model.md):
```json
{
  "items": [{ "ticker": "PETR4.SA", "asset_name": "Petrobras", "direction": "BUY", "strategy_sub_id": "double_bottom_bos", "...": "..." }],
  "page": 1, "page_size": 20, "total_assets": 153, "total_pages": 8,
  "direction": "BUY", "strategies": [], "cached": true
}
```
- `page` > `total_pages` → `items: []`.
- Estratégias não pertencentes à direção são ignoradas.

> [!WARNING] Breaking change: resposta deixa de ser lista. Único consumidor é `src/web/app.js` (atualizado nesta feature).

## GET /api/strategies
Passa a incluir `sell_double_bottom_inverted` e `buy_double_top_inverted` com `direction`, usados para popular o filtro do radar.

## GET /api/health
Adiciona `"cache_backend": "redis" | "disk"`.
