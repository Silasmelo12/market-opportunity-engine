# Tasks: Pacote de Estratégias Quantitativas com Indicadores Técnicos

**Input**: Design documents from `/specs/013-quantitative-indicators-package/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefa paralelizada
- **[Story]**: Mapeamento para a História de Usuário (US1, US2, US3, US4)
- Conforme a Constituição, cada tarefa concluída DEVE gerar 1 commit git atômico no formato: `feat(013): <TaskID> <descrição>`

---

## Phase 1: Setup & Estrutura Base

**Purpose**: Criação dos arquivos base e scaffolding de testes para o novo pacote de indicadores quantitativos.

- [x] T001 Criar módulo base `src/strategies/quantitative_indicators.py` com importações vetorizadas (`numpy`, `pandas`) e docstrings de governança anti-lookahead.
- [x] T002 [P] Criar arquivo de teste unitário base `tests/unit/test_quantitative_indicators.py` com fixtures de séries sintéticas OHLCV de teste.

---

## Phase 2: Foundational (Infraestrutura Compartilhada e Helpers Vetorizados)

**Purpose**: Funções matemáticas contíguas reutilizadas entre as diferentes famílias de indicadores (sem look-ahead bias).

- [ ] T003 Implementar helpers de cálculo contíguo vetorizado em `src/strategies/quantitative_indicators.py` para SMA, EMA, desvio padrão rolling e True Range / ATR.
- [ ] T004 Implementar função auxiliar de conversão de arrays de sinal booleano para a lista padronizada de `SignalRecord` com preenchimento estrito em `Open[t+1]` em `src/strategies/quantitative_indicators.py`.

---

## Phase 3: User Story 1 - Família de Reversão à Média (Priority: P1) 🎯 MVP

**Goal**: Implementar as 3 estratégias de reversão à média (Bollinger Fechou Fora/Dentro, Keltner Squeeze e Z-Score de Preço em extremos).

**Independent Test**: Executar `pytest tests/unit/test_quantitative_indicators.py -k "reversal or bollinger or squeeze or zscore"` e verificar sinais bidirecionais (BUY e SELL) gerados sem viés de antecipação.

- [ ] T005 [P] [US1] Adicionar testes unitários para Bandas de Bollinger Fechou Fora/Dentro, Keltner Squeeze e Z-Score em `tests/unit/test_quantitative_indicators.py`.
- [ ] T006 [US1] Implementar gerador de sinal de Bandas de Bollinger Fechou Fora/Dentro (`bollinger_close_in`) para compras (fundos) e vendas (topos) em `src/strategies/quantitative_indicators.py`.
- [ ] T007 [US1] Implementar gerador de sinal de Keltner Squeeze (`keltner_squeeze`) com identificação de compressão e rompimento de momentum em `src/strategies/quantitative_indicators.py`.
- [ ] T008 [US1] Implementar gerador de sinal de Z-Score de Preço em Extremos (`zscore_extreme`) em `src/strategies/quantitative_indicators.py`.

---

## Phase 4: User Story 2 - Família de Osciladores e Divergências (Priority: P2)

**Goal**: Implementar as 3 estratégias de osciladores (Divergência Regular de IFR/RSI, Estocástico Lento em Extremos e MACD Histogram Momentum).

**Independent Test**: Executar `pytest tests/unit/test_quantitative_indicators.py -k "oscillator or rsi or stoch or macd"` comprovando que extremos locais e inflexões não utilizam dados posteriores a $t$.

- [ ] T009 [P] [US2] Adicionar testes unitários para Divergência de IFR, Estocástico Lento e MACD Histogram Momentum em `tests/unit/test_quantitative_indicators.py`.
- [ ] T010 [US2] Implementar algoritmo quantitativo vetorizado de detecção de Divergência Regular de IFR/RSI (`rsi_divergence`) com confirmação de pivô sem repintura em `src/strategies/quantitative_indicators.py`.
- [ ] T011 [US2] Implementar gerador de sinal do Estocástico Lento em Extremos (`stochastic_extreme`) com cruzamento de %K e %D em sobrevenda/sobrecompra em `src/strategies/quantitative_indicators.py`.
- [ ] T012 [US2] Implementar gerador de sinal de MACD Histogram Momentum (`macd_momentum`) com inflexão de barras no histograma em `src/strategies/quantitative_indicators.py`.

---

## Phase 5: User Story 3 - Famílias de Volume/Fluxo Institucional e Volatilidade (Priority: P3)

**Goal**: Implementar as 3 estratégias de volume (Bandas de VWAP, MFI, Volume Clímax/VSA) e a estratégia de volatilidade (SuperTrend / ATR Trailing).

**Independent Test**: Executar `pytest tests/unit/test_quantitative_indicators.py -k "volume or vwap or mfi or vsa or supertrend"` validando cálculos ponderados por volume e bandas dinâmicas de ATR.

- [ ] T013 [P] [US3] Adicionar testes unitários para Bandas de VWAP, MFI, Volume Clímax/VSA e SuperTrend em `tests/unit/test_quantitative_indicators.py`.
- [ ] T014 [US3] Implementar estratégia de Bandas de VWAP (`vwap_bands`) com desvios padrão ponderados por volume em `src/strategies/quantitative_indicators.py`.
- [ ] T015 [US3] Implementar estratégia de Money Flow Index em Extremos (`mfi_extreme`) em `src/strategies/quantitative_indicators.py`.
- [ ] T016 [US3] Implementar estratégia de Volume Clímax & Absorção VSA (`volume_climax_vsa`) em `src/strategies/quantitative_indicators.py`.
- [ ] T017 [US3] Implementar estratégia de SuperTrend / ATR Trailing (`supertrend_trailing`) com máquina de estados $O(N)$ em `src/strategies/quantitative_indicators.py`.

---

## Phase 6: User Story 4 - Integração no StrategyCatalog, API e Frontend Web (Priority: P4)

**Goal**: Conectar o novo motor `QuantitativeIndicatorsEngine` ao catálogo unificado de estratégias, expor na API FastAPI e atualizar os seletores da SPA no frontend.

**Independent Test**: Abrir o navegador em `http://localhost:8000`, verificar que as 10 novas estratégias aparecem no Radar, Simulador Compra/Venda e que o Otimizador DCA ("Mais Lucrativa") rankeia os novos indicadores.

- [ ] T018 [US4] Integrar a classe `QuantitativeIndicatorsEngine` dentro de `src/strategies/__init__.py` no `StrategyCatalog`.
- [ ] T019 [US4] Atualizar o catálogo de estratégias exposto na API em `src/api/server.py` e schemas pydantic para incluir os 10 novos IDs e metadados.
- [ ] T020 [US4] Atualizar as listas e seletores suspensos no frontend `src/web/app.js` para organizar e exibir as novas estratégias no Radar e no Simulador.
- [ ] T021 [US4] Garantir que o otimizador clássico e o otimizador DCA em `src/evaluator/accumulation_simulator.py` e `src/evaluator/trade_simulator.py` suportem a avaliação dos novos IDs.

---

## Phase 7: Polish, Quality Gates & Verificação Global

**Purpose**: Verificação completa de conformidade com a Constituição, testes de regressão geral e documentação.

- [ ] T022 Executar a suíte de testes completa do projeto com `pytest tests/ -v` garantindo zero regressões.
- [ ] T023 Validar rigor de latência executando benchmark em `test_quantitative_indicators.py` garantindo tempo de execução < 50ms por ativo.
- [ ] T024 Atualizar checklist de requisitos em `specs/013-quantitative-indicators-package/checklists/requirements.md` e validar quickstart.md.
