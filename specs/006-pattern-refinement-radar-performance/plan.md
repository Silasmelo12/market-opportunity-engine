# Implementation Plan: Refinamento de Padrões Duplos, UX e Performance do Radar

**Branch**: `006-pattern-refinement-radar-performance` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

## Summary

1. Corrigir `run_double_bottom_bos` / `run_sell_double_top_bos` em `src/strategies/classic_engines.py` com 4 filtros vetorizados (tendência SMA50/queda prévia, posição relativa 60 barras, RSI, profundidade mínima).
2. Preservar a lógica antiga como duas novas estratégias invertidas: `sell_double_bottom_inverted` (venda) e `buy_double_top_inverted` (compra).
3. Radar: endpoint paginado + filtro de estratégias, cache diário por ativo em Redis (opcional via `REDIS_URL`) com fallback ao cache em disco/memória atual.
4. Frontend (`src/web/index.html`, `src/web/app.js`): zoom +/−/reset, limpeza de textos, ordem Compra/Venda/Ambos com default Compra, remoção de "S.A.", filtro de estratégias desmarcado, controles de paginação.

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript vanilla (frontend)
**Primary Dependencies**: FastAPI, pandas, numpy, yfinance, Lightweight Charts (TradingView), **novo**: `redis>=5.0` (cliente Python)
**Storage**: Redis (cache diário, opcional) → fallback disco `.cache/radar` + memória
**Testing**: pytest (`tests/`)
**Target Platform**: Servidor web (Render — `render.yaml`) + browser desktop/mobile
**Project Type**: Web service + SPA estática
**Performance Goals**: 1ª página do radar ≤ 3s a frio, ≤ 1s com cache (SC-003/004)
**Constraints**: zero look-ahead; sem `iterrows/apply`; app funcional sem Redis
**Scale/Scope**: ~153 ativos, ~20 estratégias, 2 timeframes principais

## Constitution Check

| Princípio | Status | Observação |
|---|---|---|
| I. Python + performance vetorizada | ✅ | Filtros novos via numpy (rolling max/min, SMA, RSI já existente `compute_rsi`). Stack FastAPI + SPA conforme Constituição v2.0.0. |
| Commit por tarefa | ✅ | `/speckit-implement` fará 1 commit por task (`feat(006): T### ...`). |
| I. Cache local obrigatório | ✅ | Redis complementa; cache em disco/memória continua como fallback. |
| II. Zero look-ahead | ✅ | Todos os filtros usam apenas barras ≤ t (máxima de `High[t-60:t]` excluindo t; SMA/RSI até t). |
| III. Multi-mercado | ✅ | Filtros em % e indicadores relativos, válidos para todas as classes. Remoção de "S.A." afeta só exibição. |
| IV. Modularidade / contratos | ✅ | Novas estratégias retornam `SignalRecord` padrão; RadarItem inalterado, resposta paginada em envelope novo. |

**Gate**: PASS (pré e pós-design).

## Project Structure

### Documentation (this feature)

```text
specs/006-pattern-refinement-radar-performance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── radar-api.md
└── checklists/requirements.md
```

### Source Code (afetado)

```text
src/
├── strategies/classic_engines.py   # filtros + 2 estratégias invertidas
├── api/
│   ├── server.py                   # /api/radar paginado, filtro, catálogo, _get_group_id
│   ├── schemas.py                  # RadarPage
│   └── cache.py                    # NOVO: DailyCache (Redis + fallback)
├── web/
│   ├── index.html                  # textos removidos, ordem botões, zoom, filtro, paginação
│   └── app.js                      # default BUY, zoom/reset, filtro, paginação, strip S.A.
tests/
├── test_double_patterns.py         # NOVO
└── test_radar_pagination.py        # NOVO
requirements.txt                    # + redis
render.yaml                         # + REDIS_URL (opcional)
```

**Structure Decision**: Manter estrutura atual; adicionar apenas `src/api/cache.py`.

## Complexity Tracking

| Item | Justificativa | Alternativa rejeitada |
|---|---|---|
| Dependência Redis | Pedido explícito do usuário; cache compartilhado entre workers/restarts | Só disco: não compartilha entre instâncias no Render |
