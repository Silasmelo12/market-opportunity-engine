# Tasks: Feature 003 - FastAPI High-Performance Engine + 60fps TradingView Web Terminal & Granular Strategy Controls

**Input**: Design documents from `/specs/003-fastapi-tradingview-terminal/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`
**Organization**: Tarefas agrupadas em 4 fases sequenciais para entrega direta e funcional da nova arquitetura de alta performance.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefas paralelizáveis (arquivos distintos, sem dependência mútua)
- **[Story]**: Mapeamento para história de usuário correspondente (`US1`, `US2`, `US3`, `US4`)

---

## Phase 1: Expansão de Velas para 14 Padrões e Catálogo Atualizado [US2]

**Goal**: Implementar os 6 novos padrões de reversão de fundo de alta probabilidade em `mql5_candles.py` e atualizar o catálogo com nomes amigáveis em português para as 24 estratégias totais.

- [x] T001 [US2] Expandir `src/strategies/mql5_candles.py` implementando vetorizadamente os 6 novos padrões: `inverted_hammer`, `tweezer_bottom`, `dragonfly_doji`, `abandoned_baby_bullish`, `bullish_kicker` e `climactic_pinbar`, mantendo o filtro `Close < SMA(20)` e execução estrita em `Open[t+1]`.
- [x] T002 [US2] Atualizar `src/ui/theme.py` e `src/strategies/__init__.py` registrando todos os 24 sub-IDs e seus nomes amigáveis padronizados no dicionário `STRATEGY_LABELS_PT`.
- [x] T003 [P] [US2] Criar teste unitário `tests/unit/test_mql5_expansion.py` validando os 6 novos padrões de vela e garantindo Zero Look-Ahead Bias.

---

## Phase 2: Backend FastAPI de Alta Performance e Serialização JSON [US1, US3, US4]

**Goal**: Criar o servidor FastAPI com cache em memória TTL/LRU, ThreadPoolExecutor concorrente no Radar e serialização JSON rápida para tipos NumPy.

- [x] T004 [US1] Criar `src/api/schemas.py` com dataclasses/Pydantic schemas e helper de serialização segura convertendo `np.float64`, `np.int64` e `np.ndarray` para tipos nativos do Python.
- [x] T005 [US1, US3, US4] Criar `src/api/server.py` implementando a aplicação FastAPI com:
  - Cache em memória com TTL;
  - `GET /api/analyze`: entrega candles OHLCV, 24 estratégias calculadas, linhas de referência, resumos estatísticos e timing status;
  - `GET /api/radar`: varredura multi-ativos concorrente via `ThreadPoolExecutor`;
  - `POST /api/simulate`: simulação financeira de aportes fixos;
  - Montagem de arquivos estáticos servindo a pasta `src/web/` na raiz `/`.

---

## Phase 3: Frontend SPA Institucional e Filtragem Client-Side 0ms [US1, US2, US3, US4]

**Goal**: Desenvolver o SPA em HTML5, TailwindCSS, TradingView Lightweight Charts nativo e Plotly.js com estado reativo client-side a 60fps.

- [x] T006 [US1, US2] Criar `src/web/index.html` com o layout FinTech Dark estruturado em 4 abas superiores (`🌐 Radar`, `📈 Terminal`, `💰 Simulador`, `📘 Playbook`), barra lateral com 4 accordions expansíveis com checkboxes individuais para as 24 estratégias e botões rápidos "Todos"/"Nenhum" por grupo, e barra de timeframes no topo do gráfico.
- [x] T007 [US1] Criar `src/web/styles.css` com paleta FinTech Dark (`#0B0E14`, `#151924`, `#262B38`), badges coloridas do Semáforo de Timing, scrollbars finas e tipografia tabular.
- [x] T008 [US1, US2, US3, US4] Criar `src/web/app.js` implementando:
  - Inicialização do TradingView Lightweight Charts com Canvas HTML5 nativo;
  - **Motor de Filtragem Client-Side (0ms)**: alternar qualquer checkbox recalcula marcadores no canvas e gráficos Plotly instantaneamente sem chamar o servidor;
  - Renderização do Ranking Plotly até 118% com `N entradas` e Scatter Plot com quadrantes médios;
  - Aba 1 (Radar com Semáforo e navegação com 1 clique para o gráfico);
  - Aba 3 (Simulador interativo de cotas e curva patrimonial);
  - Aba 4 (Playbook interativo detalhando todas as 24 estratégias).

---

## Phase 4: Ponto de Entrada Uvicorn e Testes de Integração da API [US1, US2, US3, US4]

**Goal**: Script de inicialização único e validação automatizada dos endpoints REST e do carregamento do frontend.

- [x] T009 Criar `src/main.py` e `run_server.py` na raiz para inicialização direta do servidor FastAPI na porta `8000` via Uvicorn.
- [x] T010 [P] Criar teste de integração `tests/unit/test_api_endpoints.py` validando os endpoints `/api/analyze`, `/api/radar` e `/api/simulate` com HTTP status 200 e integridade dos esquemas JSON.
- [x] T011 Executar a suíte completa de testes (`python -m pytest -v`) confirmando que 100% dos testes passam sem regressão.
