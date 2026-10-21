# Tasks: Refinamento de Padrões Duplos, UX e Performance do Radar

**Input**: Design documents from `specs/006-pattern-refinement-radar-performance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/radar-api.md, quickstart.md

**Tests**: Incluídos (Constituição exige testes anti-look-ahead e de contrato).

> [!IMPORTANT]
> **Commit por tarefa (Constituição v2.0.0)**: ao concluir cada tarefa, marcar `[X]` e fazer `git commit` com a mensagem `<tipo>(006): T### descrição` antes de iniciar a próxima.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Adicionar `redis>=5.0.0` em `requirements.txt`
- [X] T002 [P] Adicionar variável opcional `REDIS_URL` (sync: false) em `render.yaml` e documentar em `README.md`

---

## Phase 2: Foundational (bloqueia US1–US3)

- [X] T003 Extrair a detecção atual do fundo duplo de `run_double_bottom_bos` para helper `_detect_double_bottom_raw(o,h,l,c) -> List[(t, b1_idx, b2_idx, neckline)]` em `src/strategies/classic_engines.py`, sem mudar comportamento
- [X] T004 Extrair a detecção atual do topo duplo de `run_sell_double_top_bos` para helper `_detect_double_top_raw(...)` em `src/strategies/classic_engines.py`, sem mudar comportamento
- [X] T005 Adicionar helpers vetorizados de contexto em `src/strategies/classic_engines.py`: `_sma(c, n)`, `_rolling_max_prev(h, n)` e `_rolling_min_prev(l, n)` (janela excluindo t, via `pd.Series.rolling(n).max().shift(1)`), e dataclass `DoublePatternParams` com defaults do data-model.md
- [X] T006 [P] Criar fixture de dados sintéticos OHLCV (alta vertical, queda real + fundo duplo, topo após alta) em `tests/fixtures_double_patterns.py`

---

## Phase 3: US1 – Fundo Duplo + BOS corrigido (P1) 🎯 MVP

**Independent Test**: `pytest tests/test_double_patterns.py -k bottom` — nenhum sinal na máxima de 60 barras, acima da SMA50 sem queda, ou com RSI fora dos limites.

- [X] T007 [P] [US1] Testes em `tests/test_double_patterns.py`: (a) alta vertical → 0 sinais; (b) `close[t] >= max(High[t-60:t])` → descartado; (c) RSI dos fundos ≥ 45 ou RSI[t] > 60 → descartado; (d) cenário válido → 1 sinal; (e) anti-look-ahead: truncar a série em t dá o mesmo resultado
- [X] T008 [US1] Implementar filtro de tendência (FR-001: B1 e B2 abaixo da SMA50 OU queda ≥ 6% da máxima recente) em `run_double_bottom_bos` em `src/strategies/classic_engines.py`
- [X] T009 [US1] Implementar filtro de posição relativa (FR-002: descartar se `c[t] >= _rolling_max_prev(h,60)[t]`) em `run_double_bottom_bos`
- [X] T010 [US1] Implementar filtro de RSI (FR-003: min RSI em B1/B2 < 45 e RSI[t] ≤ 60, usando `compute_rsi`) em `run_double_bottom_bos`
- [X] T011 [US1] Implementar profundidade mínima (FR-004: queda ≥ 6% da máxima nas 40 barras antes de B1) e descarte quando o histórico é insuficiente/NaN em `run_double_bottom_bos`
- [ ] T012 [US1] Atualizar a descrição da estratégia no catálogo `/api/strategies` em `src/api/server.py` e no guia em `src/web/index.html`

---

## Phase 4: US2 – Topo Duplo + BOS corrigido (P1)

**Independent Test**: `pytest tests/test_double_patterns.py -k top`

- [ ] T013 [P] [US2] Testes espelhados do T007 para o topo em `tests/test_double_patterns.py` (queda vertical → 0; `c[t] <= min(Low[t-60:t])` → descartado; RSI máximo ≤ 55 ou RSI[t] < 40 → descartado; válido → 1; anti-look-ahead)
- [ ] T014 [US2] Implementar filtro de tendência (FR-006) em `run_sell_double_top_bos` em `src/strategies/classic_engines.py`
- [ ] T015 [US2] Implementar filtro de posição relativa (FR-007) em `run_sell_double_top_bos`
- [ ] T016 [US2] Implementar filtro de RSI (FR-008: max RSI em T1/T2 > 55, RSI[t] ≥ 40) em `run_sell_double_top_bos`
- [ ] T017 [US2] Implementar alta prévia mínima (FR-009) e descarte por histórico insuficiente em `run_sell_double_top_bos`
- [ ] T018 [US2] Atualizar a descrição no catálogo em `src/api/server.py` e no guia em `src/web/index.html`

---

## Phase 5: US4 – Radar paginado + cache diário (P1)

**Independent Test**: `pytest tests/test_radar_pagination.py`; abrir o radar 2x — a segunda abertura retorna `cached: true` em ≤ 1s.

- [ ] T019 [P] [US4] Testes em `tests/test_radar_pagination.py` (TestClient, `_scan_single_ticker` mockado): envelope `RadarPage`, ≤ page_size ativos, página fora do range → `items` vazio, filtro de direção/estratégias, `REDIS_URL` inválida → 200
- [ ] T020 [US4] Criar `src/api/cache.py` com a classe `DailyCache` (`get(key)`, `set(key, value, ttl=93600)`, `backend` = "redis"|"disk"); Redis via `REDIS_URL` com `socket_timeout=0.5`; qualquer exceção → fallback memória+disco em `.cache/radar`
- [ ] T021 [US4] Adicionar o modelo `RadarPage` em `src/api/schemas.py` conforme data-model.md
- [ ] T022 [US4] Envolver `_scan_single_ticker` em `src/api/server.py` com o cache por ticker, chave `radar:v6:{interval}:{horizon}:{ticker}:{last_bar_date}`
- [ ] T023 [US4] Refatorar `GET /api/radar` em `src/api/server.py` com params `page`, `page_size`, `direction`, `strategies`: fatiar a cesta, escanear só a página (ThreadPool), filtrar, ordenar por timing e retornar `RadarPage` (contracts/radar-api.md)
- [ ] T024 [US4] Adicionar `cache_backend` em `GET /api/health` em `src/api/server.py`
- [ ] T025 [US4] Pré-aquecer em background thread no startup a categoria `featured` (página 1) em `src/api/server.py`
- [ ] T026 [US4] Consumir `RadarPage` em `src/web/app.js` (ler `items`, enviar `page/page_size/direction/strategies`) e adicionar controles Anterior/Próxima + "Página X de Y" em `src/web/index.html`; mostrar "Nenhuma oportunidade encontrada" e ocultar a paginação quando vazio

---

## Phase 6: US3 – Estratégias invertidas (P2)

**Independent Test**: as datas dos sinais das invertidas == as datas do `_detect_*_raw` (SC-006).

- [ ] T027 [P] [US3] Testes em `tests/test_double_patterns.py`: datas de `sell_double_bottom_inverted` == `_detect_double_bottom_raw`, com direction SELL; idem `buy_double_top_inverted`/BUY; validar os 5 campos do contrato
- [ ] T028 [US3] Implementar `run_sell_double_bottom_inverted` (SELL, label "Fundo Duplo Invertido (Venda)") em `src/strategies/classic_engines.py`, usando o helper raw
- [ ] T029 [US3] Implementar `run_buy_double_top_inverted` (BUY, label "Topo Duplo Invertido (Compra)") em `src/strategies/classic_engines.py`
- [ ] T030 [US3] Registrar as duas no `STRATEGY_IDS` e no dispatcher `run_all` de `ClassicStrategiesEngine` em `src/strategies/classic_engines.py`
- [ ] T031 [US3] Expor no catálogo `/api/strategies`, nos labels do radar/analyze em `src/api/server.py` e nas opções do simulador em `src/web/index.html`/`src/web/app.js`

---

## Phase 7: US5 – Defaults e filtro de estratégias do radar (P2)

**Independent Test**: abrir o app → modo Compra ativo, ordem Compra|Venda|Ambos, filtro todo desmarcado.

- [ ] T032 [US5] Reordenar os botões de direção para Compra, Venda, Ambos em `src/web/index.html`
- [ ] T033 [US5] Definir `state.activeDirection = 'BUY'` como inicial e remover o reset para `'BOTH'` (≈ app.js:812) em `src/web/app.js`
- [ ] T034 [US5] Adicionar o dropdown multi-checkbox "Estratégias" no cabeçalho do radar em `src/web/index.html`
- [ ] T035 [US5] Popular o filtro a partir de `/api/strategies` filtrando pela direção ativa, estado inicial vazio (= todas), reenviar `strategies` CSV e voltar à página 1 ao mudar; ignorar marcações de outra direção em `src/web/app.js`

---

## Phase 8: US6 – Zoom e limpeza visual (P3)

**Independent Test**: os botões +/−/Reset funcionam; os textos removidos não aparecem.

- [ ] T036 [P] [US6] Adicionar botões +, −, Reset sobre o container do gráfico em `src/web/index.html`
- [ ] T037 [US6] Implementar zoom ±20% via `getVisibleLogicalRange/setVisibleLogicalRange` e reset via `fitContent()`, com limites mínimo/máximo, em `src/web/app.js`
- [ ] T038 [P] [US6] Remover o badge `v4.0 60FPS`, o subtítulo "Terminal Quantitativo…" e "60fps" do `<title>` em `src/web/index.html`, e o contador de FPS em `src/web/app.js`
- [ ] T039 [P] [US6] Remover o card/texto "Zona Ideal (Topo)" em `src/web/index.html` e `src/web/app.js`
- [ ] T040 [US6] Criar `strip_corporate_suffix()` (S.A., S/A, SA final) em `src/data_loader/normalizer.py`, aplicar em `asset_name` em `src/api/server.py`, e criar `stripCorporateSuffix()` equivalente em `src/web/app.js`; incluir um teste unitário em `tests/test_normalizer_suffix.py`

---

## Phase 9: Polish

- [ ] T041 Rodar a suíte completa `pytest -q` e corrigir regressões
- [ ] T042 [P] Executar a validação manual do `quickstart.md` e medir SC-003/004
- [ ] T043 [P] Atualizar `README.md` (novas estratégias, Redis, paginação)

---

## Dependencies

- Setup → Foundational → {US1, US2, US3} ; US4 depende só do Setup (T001) ; US5 depende de US4 (T026) e de US3 para o catálogo completo ; US6 é independente.
- Ordem sugerida: US1 → US2 → US4 → US3 → US5 → US6 → Polish.

## Parallel Examples

- US1: T007 em paralelo com T013/T019 (arquivos de teste distintos).
- US6: T036, T038 e T039 em paralelo (trechos distintos do HTML; atenção a conflitos de merge).
- **Nota**: como cada tarefa gera um commit, execute sequencialmente na prática; [P] indica apenas a ausência de dependência lógica.

## Implementation Strategy

- **MVP**: Phases 1–3 (fundo duplo corrigido).
- Incremento 2: US2 + US4 (qualidade dos sinais de venda + performance).
- Incremento 3: US3, US5, US6.
