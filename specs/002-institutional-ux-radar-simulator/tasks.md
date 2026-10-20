# Tasks: Feature 002 - Institutional UX/UI Design, Multi-Timeframe Intraday, Radar Scanner, Simulador de Acumulação e Guia de Estratégias

**Input**: Design documents from `/specs/002-institutional-ux-radar-simulator/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`
**Organization**: Tarefas agrupadas em 5 fases coesas para execução linear e sem fragmentação excessiva de contexto.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefas paralelizáveis (arquivos distintos, sem bloqueio mútuo)
- **[Story]**: Mapeamento para história de usuário correspondente (`US1`, `US2`, `US3`, `US4`, `US5`)

---

## Phase 1: Resampling Multi-Timeframe e Camada de Dados [US4]

**Goal**: Suportar timeframes intraday (`5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`) com teto dinâmico de período e agregação matemática causal no `data_loader`.

- [X] T001 [US4] Implementar em `src/data_loader/normalizer.py` a função `resample_ohlcv` para agregar barras de `1h` em `2h`, `4h` e `12h` (`open=first`, `high=max`, `low=min`, `close=last`, `volume=sum`) e descartar períodos sem negociação.
- [X] T002 [US4] Atualizar `src/data_loader/fetcher.py` para aplicar limites máximos de período do `yfinance` (`60d` para sub-hora `5m/15m/30m`, `730d` para base horária) e integrar o pipeline de resampling em `load_asset_data`.
- [X] T003 [P] [US4] Criar teste unitário `tests/unit/test_resampler.py` comprovando a consistência dos preços agregados e a ausência de barras vazias.

---

## Phase 2: Simulador Financeiro e Semáforo de Timing [US1, US3]

**Goal**: Motores analíticos da simulação de cotas patrimoniais e do semáforo de atraso de entrada.

- [X] T004 [US3] Implementar em `src/evaluator/accumulation_simulator.py` a função `simulate_accumulation` computando aportes fixos por sinal ($V / P_{exec}$), patrimônio a mercado diário, capital desembolsado, preço médio e resumo por estratégia.
- [X] T005 [P] [US1] Implementar em `src/evaluator/timing_classifier.py` a função `classify_timing_status` gerando o objeto `TimingStatus` em 3 faixas (IDEAL, EXTENDED, LATE) com base na distância de $P_{exec}$ e percentual do retorno médio.
- [X] T006 [P] [US1, US3] Criar testes unitários `tests/unit/test_accumulation.py` e `tests/unit/test_timing_classifier.py` validando os cálculos de cotas, preço médio e as transições do semáforo.

---

## Phase 3: Design System Institucional e Refinamento de Gráficos [US2]

**Goal**: Tema FinTech Dark, dicionário imutável de nomes comerciais e correção visual dos painéis Plotly.

- [X] T007 [US2] Criar `src/ui/theme.py` contendo o CSS Dark institucional (`#0B0E14`), o dicionário imutável `STRATEGY_LABELS_PT` (mapeando os 18 sub-IDs para nomes em português) e helper HTML para KPI cards padronizados.
- [X] T008 [US2] Atualizar `src/ui/stats_panels.py` para usar `STRATEGY_LABELS_PT`, definir `xaxis.range=[0, 118]` no Ranking sem cortar rótulos de 100%, exibir `Win Rate % (N entradas)` nas barras, e traçar os quadrantes médios no Scatter Plot com linhas divisórias de referência e margens amplas.

---

## Phase 4: Implementação das Novas Abas [US1, US3, US5]

**Goal**: Construção modular das páginas de Radar, Simulador de Aportes e Playbook Educacional.

- [X] T009 [US1] Implementar `src/ui/radar_tab.py` (Aba 1: Scanner de Oportunidades com cesta multi-ativos, badges do Semáforo de Timing e navegação rápida para o Terminal via `st.session_state`).
- [X] T010 [US3] Implementar `src/ui/simulator_tab.py` (Aba 3: Simulador de Patrimônio & Aportes isolado com `@st.fragment`, controles de valor/período, KPIs e gráfico de evolução Patrimônio vs. Desembolso).
- [X] T011 [P] [US5] Implementar `src/ui/guide_tab.py` (Aba 4: Playbook estruturado para todas as 18 variações com Conceito Simples, Regra Matemática, Psicologia de Fundo e Dica de Timing).

---

## Phase 5: Integração no App e Validação End-to-End [US1, US2, US3, US4, US5]

**Goal**: Orquestração das 4 abas no `src/app.py`, suporte à navegação reativa e execução da suíte completa de testes.

- [X] T012 Atualizar `src/app.py` integrando a barra de navegação com as 4 abas superiores (`🌐 Radar`, `📈 Terminal`, `💰 Simulador`, `📘 Playbook`), sincronizando o `session_state` e os seletores multi-timeframe.
- [X] T013 Executar a suíte completa de testes (`python -m pytest -v`) garantindo que 100% dos testes novos e pré-existentes passem sem regressão.
