# Feature Specification: FastAPI High-Performance Engine + 60fps TradingView Web Terminal & Granular Strategy Controls

**Feature Branch**: `003-fastapi-tradingview-terminal`

**Created**: 2026-10-20

**Status**: Ready for Planning

**Input**: User description: "Criar a Feature 003 ('FastAPI High-Performance Engine + 60fps TradingView Web Terminal & Granular Strategy Controls'), substituindo a camada lenta do Streamlit por uma arquitetura desacoplada de altíssima performance (FastAPI Backend + Frontend SPA HTML5/JS nativo servidos na mesma porta), mantendo 100% dos motores matemáticos em `src/strategies/` e `src/evaluator/`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Terminal Gráfico 60fps TradingView com Filtragem Instantânea Client-Side (Priority: P1)

Como investidor técnico e analista institucional, quero carregar o gráfico do ativo uma única vez e marcar/desmarcar individualmente qualquer uma das 24 estratégias na barra lateral com resposta imediata a 60fps (0ms de latência), sem recarregar o gráfico ou fazer requisições lentas ao servidor a cada clique, para que minha análise seja fluida e ágil.

**Why this priority**: É o cerne da transição arquitetural. Elimina o engasgo e o re-render compulsivo do Streamlit, proporcionando uma experiência de nível TradingView/Koyfin real.

**Independent Test**: Pode ser testado abrindo o navegador no Terminal Web, ativando/desativando checkboxes individuais de estratégias e conferindo que os marcadores e as tabelas estatísticas atualizam instantaneamente em memória JavaScript sem disparar chamadas de rede adicionais.

**Acceptance Scenarios**:

1. **Given** um ativo carregado com 24 estratégias processadas, **When** o usuário desmarca ou marca uma estratégia específica (ex: "Negação Barra Anterior - Entrada Reteste"), **Then** os marcadores daquela estratégia no gráfico Canvas HTML5 e os painéis de ranking/tabela atualizam em menos de 16ms (60fps) via JavaScript sem nova chamada HTTP.
2. **Given** o gráfico TradingView Lightweight Charts, **When** o usuário aplica zoom, pan e scroll temporal, **Then** o canvas renderiza suavemente com as linhas de referência horizontais e marcadores de compra alinhados aos candles.

---

### User Story 2 - Controle Granular de 24 Estratégias e Expansão de Velas MQL5 (Priority: P2)

Como investidor quantitativo, quero ter controle individualizado sobre cada uma das 24 estratégias divididas em 4 grupos expansíveis (Estratégia Proprietária 2x2, Price Action, Alocação/Holder e 14 Padrões de Velas), com botões rápidos "Todos" e "Nenhum", para testar e combinar setups sem ficar refém de blocos travados.

**Why this priority**: A granularidade total capacita o usuário a isolar exatamente os padrões de maior convicção (ex: apenas Wyckoff Spring + Reteste Fundo N + Martelo Invertido).

**Independent Test**: Pode ser testado inspecionando os 4 accordions da barra lateral, clicando em "Nenhum" no grupo de velas, selecionando apenas "Vela: Martelo Invertido" e "Vela: Pinça de Fundo", e verificando a presença exclusiva desses sinais no gráfico e nas estatísticas.

**Acceptance Scenarios**:

1. **Given** a barra lateral do Terminal, **When** o usuário expande os 4 grupos, **Then** cada uma das 24 estratégias possui seu próprio checkbox com rótulo comercial em português e botões de atalho "Marcar Todos" / "Desmarcar Todos" por grupo.
2. **Given** a expansão de velas em `mql5_candles.py`, **When** os cálculos são executados, **Then** os 6 novos padrões (`inverted_hammer`, `tweezer_bottom`, `dragonfly_doji`, `abandoned_baby_bullish`, `bullish_kicker`, `climactic_pinbar`) são detectados com vetorização e execução rigorosa em `Open[t+1]`.

---

### User Story 3 - Radar de Mercado Multi-Ativos com Semáforo de Timing e 1-Click Navigation (Priority: P3)

Como gestor de carteira, quero abrir a Aba 1 ("🌐 Radar de Oportunidades") e ver uma varredura multi-ativos processada em paralelo pelo backend FastAPI, exibindo o Semáforo de Timing ("*Comprei Atrasado?*"), e navegar para o ativo no gráfico com um único clique.

**Why this priority**: Permite triar instantaneamente o mercado antes de abrir os gráficos individuais.

**Independent Test**: Pode ser testado acessando o Radar, conferindo o tempo de resposta em paralelo via `GET /api/radar` e clicando no botão "Abrir no Gráfico" para alternar para a Aba 2 com o ticker já carregado.

**Acceptance Scenarios**:

1. **Given** a requisição `GET /api/radar`, **When** o backend processa a cesta de ativos via pool concorrente e cache em memória, **Then** o payload JSON retorna em menos de 1.5 segundo com o Semáforo (Verde, Amarelo, Vermelho) e distância percentual da entrada recomendada.
2. **Given** a tabela do Radar, **When** o usuário clica em "Abrir no Gráfico", **Then** a aplicação transiciona instantaneamente para a Aba 2 com o ticker carregado e pronto para inspeção.

---

### User Story 4 - Simulador de Acumulação e Playbook Didático Interativo (Priority: P4)

Como investidor holder, quero simular na Aba 3 o patrimônio acumulado investindo R$ X por entrada em cada sinal e consultar na Aba 4 o Playbook completo das 24 estratégias (com distinção explícita entre Wyckoff Spring e Fundo Duplo + BOS).

**Why this priority**: Conclui a experiência institucional de ponta a ponta (diagnóstico, validação gráfica, projeção de riqueza e educação técnica).

**Independent Test**: Pode ser testado alterando o valor do aporte na Aba 3 com atualização em milissegundos e lendo os cards comparativos na Aba 4.

**Acceptance Scenarios**:

1. **Given** a Aba 3 (Simulador), **When** o usuário altera o valor de aporte ou o intervalo de datas, **Then** a curva patrimonial vs. desembolso e o ranking financeiro recalculam instantaneamente.
2. **Given** a Aba 4 (Playbook), **When** o usuário consulta as estratégias, **Then** cards didáticos explicam a lógica, a fórmula de entrada, a psicologia e a diferenciação entre Wyckoff Spring (sweep na mínima) e Fundo Duplo + BOS (rompimento no topo intermediário).

---

### Edge Cases

- **Execução na mesma porta sem Node.js**: O FastAPI deve servir o frontend estático SPA (`index.html`, `app.js`, `styles.css`) diretamente pela rota raiz `/`, eliminando a necessidade de ferramentas de build como npm/Vite.
- **Conflito de concorrência no cache de dados**: O cache em memória LRU/TTL do backend deve ser thread-safe para requisições simultâneas ao mesmo ticker.
- **Timeframes intraday com limite de histórico**: A seleção de `5m` a `30m` deve manter a restrição de 60 dias da API, e `2h`, `4h`, `12h` devem usar o Resampling da base de 1h validado na Feature 002.
- **Série com 0 sinais na estratégia selecionada**: A interface client-side deve tratar graciosamente a desmarcação de todos os checkboxes exibindo estado vazio sem quebrar o canvas do TradingView.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE desacoplar a camada de apresentação criando um backend de alta performance em `FastAPI` (`src/api/server.py`) servindo o frontend estático SPA na raiz `/` na mesma porta via `StaticFiles`.
- **FR-002**: O backend DEVE disponibilizar os endpoints JSON:
  - `GET /api/analyze`: entrega em payload único candles OHLCV, 24 estratégias, linhas de referência, métricas estatísticas, estado atual e timing status;
  - `GET /api/radar`: processa em paralelo via `ThreadPoolExecutor` a cesta monitorada com cache em memória;
  - `POST /api/simulate`: executa a simulação financeira de aportes com histórico de evolução patrimonial.
- **FR-003**: O frontend DEVE ser implementado como SPA HTML5/JS nativo com TradingView Lightweight Charts (Canvas 60fps) e Plotly.js para os gráficos estatísticos.
- **FR-004**: O frontend DEVE realizar a filtragem de estratégias de forma 100% client-side em JavaScript: marcar ou desmarcar checkboxes deve atualizar marcadores e tabelas instantaneamente (0ms) sem requisições HTTP adicionais.
- **FR-005**: A barra lateral DEVE apresentar 4 grupos expansíveis com checkboxes individuais para as 24 estratégias e botões de atalho "Marcar Todos" / "Desmarcar Todos" por grupo:
  - Grupo 1: 4 variantes da Negação Proprietária 2x2;
  - Grupo 2: Price Action Institucional (Fundo Duplo + BOS e Wyckoff Spring separados);
  - Grupo 3: Alocação & Holder (DCA Dinâmico, Value Proxy, Rebal RFxRV e Força Relativa);
  - Grupo 4: 14 Padrões de Velas (os 8 atuais + 6 novos adicionados em `mql5_candles.py`: `inverted_hammer`, `tweezer_bottom`, `dragonfly_doji`, `abandoned_baby_bullish`, `bullish_kicker`, `climactic_pinbar`).
- **FR-006**: O sistema DEVE disponibilizar barra de seleção de timeframes no topo do gráfico: `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d`, `1wk`.
- **FR-007**: A interface DEVE ser estruturada em 4 abas instantâneas:
  - `🌐 Radar de Oportunidades`: com Semáforo de Timing e botão de navegação com 1 clique;
  - `📈 Terminal de Análise`: TradingView Canvas + Ranking Plotly até 118% com `N entradas` + Scatter Risco x Retorno com Quadrante de Ouro;
  - `💰 Simulador de Patrimônio & Aportes`: simulação interativa de aportes fixos;
  - `📘 Playbook & Guia de Estratégias`: enciclopédia educacional detalhando todas as 24 estratégias.
- **FR-008**: O sistema DEVE preservar rigorosamente todos os motores matemáticos, regras anti-lookahead e testes unitários das Features 001 e 002.

### Key Entities

- **AnalysisPayload (JSON)**: Payload unificado contendo série OHLCV, array de sinais das 24 estratégias, segmentos de linhas de referência, resumos estatísticos por estratégia e status de timing atual.
- **StrategyRegistryItem**: Descritor de estratégia contendo `id`, `sub_id`, `group_id`, `label_pt` e `default_active`.
- **RadarBasketItem**: Item do scanner contendo métricas resumidas, preço recomendado, preço atual e badge de timing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A filtragem interativa de estratégias no navegador (marcar/desmarcar) deve atualizar o gráfico Canvas e as tabelas em menos de 16 milissegundos (60fps) sem chamadas de rede.
- **SC-002**: O endpoint `GET /api/analyze` deve responder em menos de 400 milissegundos para ativos com 2 anos de histórico em cache.
- **SC-003**: O endpoint `GET /api/radar` para 8 ativos concorrentes deve responder em menos de 1.2 segundo no primeiro carregamento e menos de 100 milissegundos em requisições em cache.
- **SC-004**: 100% dos 23 testes unitários existentes continuam passando, com adição de testes para os 6 novos padrões de vela e para os endpoints da API FastAPI.
- **SC-005**: Zero dependência de Node.js, npm ou bundlers externos para execução da aplicação.

## Assumptions

- O servidor FastAPI + Uvicorn será executado via Python nativo na porta padrão `8000` (ou `8501`), servindo tanto a API REST JSON quanto o bundle de arquivos estáticos HTML/CSS/JS.
- As bibliotecas TradingView Lightweight Charts (`lightweight-charts.standalone.production.js`) e Plotly.js (`plotly-latest.min.js`) serão carregadas via CDN ou empacotadas estaticamente para funcionamento offline.
- A experiência de zoom e pan no canvas HTML5 utiliza a aceleração de hardware nativa do navegador.
