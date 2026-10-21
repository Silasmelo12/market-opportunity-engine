# Research: Feature 006

## R1. Filtros do Fundo Duplo + BOS (vetorização, sem look-ahead)
- **Decision**: Pré-calcular arrays `sma50`, `rsi14` (`compute_rsi`), `roll_max_high_60` = max(High[t-60:t]) (exclui t, via `pd.Series.rolling(60).max().shift(1)`), `roll_max_prior` para profundidade. No loop existente de detecção (já O(N)), aplicar:
  - Tendência: `c[b1] < sma50[b1] and c[b2] < sma50[b2]` OR `(max_high_before_b1 - b1_low)/max_high_before_b1 >= 0.06`.
  - Posição: descartar se `c[t] >= roll_max_high_60[t]`.
  - RSI: `min(rsi[b1_window ∪ b2_window]) < 45` e `rsi[t] <= 60`.
  - Profundidade: queda ≥ 6% da máxima na janela (padrão 40 barras) antes de B1 até `b1_low`.
- **Rationale**: Reaproveita loop atual, custo O(N), conforme Constituição I/II.
- **Alternatives**: numba — desnecessário para N ≈ 2.000 barras.

## R2. Topo Duplo + BOS (espelho)
- **Decision**: Mesmos filtros com sinais trocados: acima da SMA50 ou alta ≥ 6%; descartar se `c[t] <= min(Low[t-60:t])`; `max(rsi) > 55` nos topos e `rsi[t] >= 40`.

## R3. Estratégias invertidas
- **Decision**: Extrair a lógica atual para helpers `_detect_double_bottom_raw` / `_detect_double_top_raw` (retornam índices). Original corrigida = raw + filtros. Invertidas = raw com direção trocada:
  - `sell_double_bottom_inverted` — "Fundo Duplo Invertido (Venda)", direction SELL.
  - `buy_double_top_inverted` — "Topo Duplo Invertido (Compra)", direction BUY.
- **Rationale**: Garante SC-006 (mesmas datas) por construção.
- `_get_group_id` já classifica por substring `double_bottom`/`double_top` → `price_action`.

## R4. Cache diário
- **Decision**: `DailyCache` em `src/api/cache.py`. Chave `radar:v6:{interval}:{horizon}:{ticker}:{last_bar_date}`, valor JSON da lista de `RadarItem` do ticker; TTL 26h. Cliente `redis.from_url(REDIS_URL, socket_timeout=0.5)`; qualquer exceção → fallback para cache disco/memória atual (FR-018). Granularidade por ticker permite paginação calcular só a página.
- **Rationale**: `last_bar_date` invalida naturalmente na virada do pregão; por-ticker evita recalcular tudo.
- **Alternatives**: cachear lista completa por categoria (atual) — força cálculo total, causa da lentidão.
- Bônus: pré-aquecimento opcional em background thread no startup para a categoria `featured`.

## R5. Paginação
- **Decision**: Paginação **por ativo** (cesta ordenada alfabeticamente/pela ordem atual), `page`, `page_size=20`. Servidor escaneia só os tickers da página (paralelo, ThreadPool já existente), aplica filtro `direction` e `strategies`, devolve envelope `RadarPage`. Quando há filtro de estratégias, o total de oportunidades é por página; `total_assets`/`total_pages` derivam da cesta.
- **Rationale**: Paginar por oportunidade exigiria calcular tudo antes (contraria FR-015).
- **Trade-off**: ordenação por timing é dentro da página. Aceito.

## R6. Frontend
- Zoom: `chart.timeScale()` — ler `getVisibleLogicalRange()`, encolher/expandir 20% em torno do centro, `setVisibleLogicalRange`; reset = `fitContent()`.
- Remover: badge `v4.0 60FPS` (index.html:50), subtítulo "Terminal Quantitativo…" (index.html:52), "60fps" do `<title>`, contador FPS em app.js, card "Zona Ideal (Topo)" quando o valor é 0,0% (remover o elemento por completo).
- Ordem dos botões: Compra, Venda, Ambos; `state.activeDirection = 'BUY'` inicial (app.js:812 fixava `BOTH`).
- `stripCorporateSuffix(name)`: regex `/\s*[-,]?\s*\b(S\.?\/?A\.?)\s*$/i` aplicada na exibição; também no backend em `asset_name` para consistência.
- Filtro de estratégias: dropdown multi-checkbox populado de `/api/strategies` filtrando pela direção ativa; estado inicial vazio.
