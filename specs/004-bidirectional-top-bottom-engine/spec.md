# Feature Specification: Bidirectional Market Opportunity & Top/Bottom Statistical Engine (Modos Compra, Venda e Ambos)

**Feature Branch**: `004-bidirectional-top-bottom-engine`  
**Created**: 2026-10-20  
**Status**: Ready for Planning  
**Input**: Solicitação do usuário para criar a Feature 004 ("Bidirectional Market Opportunity & Top/Bottom Statistical Engine - Modos Compra, Venda e Ambos"), expandindo todos os motores matemáticos, o avaliador estatístico, a API FastAPI e o Terminal Web 60fps para operar tanto na captura de Fundos (COMPRA / LONG) quanto na captura de Topos/Realização (VENDA / SHORT), com seletor global de direção na interface.

---

## User Scenarios & Testing

### User Story 1 - Controle Global de Direção Operacional na UI (Priority: P1)

Como investidor ou analista institucional, quero alternar com um clique entre os modos **🟢 Somente Compra (Fundos)**, **🔴 Somente Venda (Topos)** e **⚡ Compra e Venda (Bidirecional)** com filtragem client-side em 0ms, para que o gráfico TradingView, os painéis estatísticos Plotly, o Radar e as tabelas exibam exatamente os sinais da direção pretendida.

- **Why this priority**: É a porta de entrada da experiência bidirecional. Permite ao usuário focar em momentos de acumulação de fundos, momentos de proteção/realização de lucros em topos, ou na visão conjunta de reversões de mercado.
- **Independent Test**: Pode ser testado clicando no seletor segmentado de 3 estados na barra superior ou lateral da interface e verificando se os marcadores visíveis, linhas de referência, rankings Plotly e histórico filtram instantaneamente em memória JavaScript em < 10ms sem recarregar o navegador ou chamar a API.
- **Acceptance Scenarios**:
  1. **Given** um ativo carregado com sinais bidirecionais, **When** o usuário clica em `🔴 Venda`, **Then** o gráfico exibe apenas as setas vermelhas de topo (`aboveBar`, `arrowDown`, `#FF5252`), as linhas de resistência e os rankings de estratégias de venda.
  2. **Given** o modo `⚡ Compra e Venda`, **When** o gráfico renderiza, **Then** as setas verdes de compra (`belowBar`, `arrowUp`, `#00E676`) e as setas vermelhas de venda aparecem simultaneamente, ordenadas cronologicamente por timestamp.
  3. **Given** o modo `🟢 Compra`, **When** selecionado, **Then** apenas estratégias de fundo são visíveis, restaurando a visão clássica da Feature 003.

---

### User Story 2 - Espelhamento Simétrico dos Motores para Topos / VENDA (Priority: P1)

Como trader quantitativo, quero dispor de um catálogo simétrico de estratégias de venda/topo (Estratégia Proprietária de Topo 2x2, Price Action de Topo, Realização Estatística e 14 Padrões Bearish MQL5), rigorosamente alinhadas com o Princípio de Zero Look-Ahead Bias, para identificar exaustão compradora e pontos de saída/venda com base estatística comprovada.

- **Why this priority**: Sem a lógica matemática simétrica de venda, não é possível alimentar estatísticas confiáveis ou calcular a taxa de acerto de operações vendidas.
- **Independent Test**: Pode ser testado através de testes unitários em `tests/unit/` verificando:
  - Rompimentos de máxima seguidos de negação (fechamento abaixo da máxima rompida) na Estratégia Proprietária de Venda;
  - Execução no modo reteste com gap de alta preenchendo em `Open[t+k]`;
  - Padrões de vela bearish exigindo `Close > SMA(20)` e preenchendo em `Open[t+1]`.
- **Acceptance Scenarios**:
  1. **Given** uma série OHLCV com tendência de alta e novo topo rompido, **When** um candle fecha abaixo da máxima rompida (`Close[t] < active_resistance_line`), **Then** a Negação de Topo é confirmada e uma venda é emitida em `Open[t+1]` (modo abertura) ou aguarda reteste da máxima até `M` barras (modo reteste).
  2. **Given** o modo reteste de topo na janela de `M` barras, **When** uma barra abre em Gap de Alta acima da linha (`Open[t+k] > active_resistance_line`), **Then** a venda executa no preço de abertura real daquela barra (`fill_type='retest_gap'`).
  3. **Given** os 14 padrões clássicos de velas de topo (Shooting Star, Hanging Man, Bearish Engulfing, Evening Star, Tweezer Top, etc.), **When** avaliados, **Then** todos exigem tendência prévia altista (`Close > SMA(20)`) e corpo calibrado por `SMA(abs(Close-Open), 12)`.
  4. **Given** o Price Action de Topo (`sell_double_top_bos` e `sell_wyckoff_upthrust`), **When** ocorrem dois topos ou perfuração de máxima com alto volume e rejeição imediata, **Then** o setup gera um sinal de venda em `Open[t+1]`.

---

### User Story 3 - Avaliador Estatístico Invertido para Venda e Semáforo de Timing de Topo (Priority: P2)

Como gestor de risco, quero que o Avaliador Estatístico compute adequadamente o retorno e o risco de vendas (onde ganho ocorre com queda do preço e o calor/MAE ocorre com novas altas), e que o Semáforo de Timing classifique se a oportunidade de topo está em Zona Ideal, Estendida ou Atrasada.

- **Why this priority**: Evita cálculos de retorno invertidos e garante consistência entre o modelo estatístico de alta e o de baixa.
- **Independent Test**: Pode ser testado passando sinais de venda para o avaliador e verificando se:
  - `Forward Return % = ((P_exec - Close[t_exec + X]) / P_exec) * 100` (positivo quando o ativo cai);
  - `MAE % = max(0, (max(High) - P_exec) / P_exec) * 100` (refletindo o calor sofrido contra novas altas);
  - Sinais em aberto (`t_exec + X >= len(close)`) continuam excluídos do Win Rate fechado.
- **Acceptance Scenarios**:
  1. **Given** uma venda executada a R$ 50,00 e preço após X barras a R$ 40,00, **When** o avaliador processa, **Then** `forward_return_pct = +20.0%` e `is_win = True`.
  2. **Given** uma venda executada a R$ 50,00 onde a máxima atingiu R$ 55,00 antes de cair, **When** o MAE é calculado, **Then** o calor adverso computado é de 10% (exibido como -10.0% no gráfico de dispersão).
  3. **Given** o preço atual próximo da resistência (`Close[-1] >= P_exec * 0.985`), **When** classificado, **Then** o Semáforo de Timing indica `🟢 ZONA IDEAL (TOPO)`. Se o preço já caiu mais de 4% do topo, classifica como `🔴 ATRASADO (JÁ DERRETEU)`.

---

### User Story 4 - Simulador de Acumulação e Giro de Lucro Bidirecional (Priority: P3)

Como investidor com foco em alocação patrimonial, quero que o Simulador Financeiro permita simular aportes na baixa e, quando no modo bidirecional, simular a realização parcial/venda no topo gerando caixa para rebalanceamento ou recompras mais baratas.

- **Why this priority**: Fecha o ciclo completo de acumulação e realização inteligente de lucros.
- **Independent Test**: Pode ser testado na Aba 3 selecionando modo Bidirecional e verificando se as vendas geram desinvestimento com caixa disponível somado à curva patrimonial.
- **Acceptance Scenarios**:
  1. **Given** sinais de compra seguidos por sinais de venda, **When** o simulador executa, **Then** as compras aumentam as cotas e as vendas realizam lucro/cotas injetando liquidez no caixa.
  2. **Given** a tabela comparativa do Terminal, **When** em modo `Venda` ou `Ambos`, **Then** exibe claramente quais estratégias de venda geraram melhor proteção de capital ou maior retorno absoluto na queda.

---

## Requirements & Scope

### Functional Requirements

- **FR-001 (Direction Contract)**: Todas as instâncias de `SignalRecord` devem conter o campo explícito `direction: str` com valores padronizados `"BUY"` ou `"SELL"`.
- **FR-002 (Proprietary Reversal Sell Machine)**: O módulo `src/strategies/proprietary_reversal.py` deve implementar a máquina de estados simétrica de topo:
  - Variantes: `sell_t1_open`, `sell_t1_retest`, `sell_t2_open`, `sell_t2_retest`.
  - Sobrescrita dinâmica da linha de resistência em caso de novos rompimentos de alta antes da negação.
  - Gatilho causal de negação quando `Close[t] < active_resistance_line`.
  - Janela de reteste sequencial de `M` barras com preenchimento em gap de alta no preço de `Open[t+k]`.
- **FR-003 (Classic & MQL5 Sell Engines)**:
  - Implementar em `src/strategies/` os equivalentes de venda: `sell_double_top_bos`, `sell_wyckoff_upthrust`, `sell_overbought_stat`, `sell_rebal_rv_rf`, `sell_rebal_relative_strength`, `sell_value_proxy`.
  - Implementar os 14 padrões clássicos de velas de topo (Shooting Star, Hanging Man, Bearish Engulfing, Dark Cloud Cover, Evening Star, Bearish Harami, Three Inside Down, Three Outside Down, Three Black Crows, Tweezer Top, Gravestone Doji, Abandoned Baby Bearish, Bearish Kicker, Climactic Bearish Pinbar) com filtro `Close > SMA(20)` e execução em `Open[t+1]`.
- **FR-004 (Directional Evaluator)**: O módulo `src/evaluator/statistical_engine.py` deve diferenciar a fórmula de retorno e calor baseando-se em `signal.direction`:
  - Se `BUY`: $R = \frac{C_{t+X} - P_{\text{exec}}}{P_{\text{exec}}}$, $\text{MAE} = \min(0, \frac{\min(Low) - P_{\text{exec}}}{P_{\text{exec}}})$.
  - Se `SELL`: $R = \frac{P_{\text{exec}} - C_{t+X}}{P_{\text{exec}}}$, $\text{MAE} = -\max(0, \frac{\max(High) - P_{\text{exec}}}{P_{\text{exec}}})$.
- **FR-005 (Directional Timing Classifier)**: O classificador de semáforo deve incorporar a lógica de distância percentual para topos:
  - `IDEAL`: Preço na resistência ou recuo $\le 1.5\%$.
  - `EXTENDED`: Queda entre $1.5\%$ e $4.0\%$ do ponto de venda.
  - `LATE`: Preço já caiu mais de $4.0\%$ abaixo do ponto de venda.
- **FR-006 (UI 3-Way Direction Segmented Control)**: A interface HTML5/JS deve renderizar um controle segmentado:
  - Botões: `🟢 Compra` | `🔴 Venda` | `⚡ Ambos`.
  - Filtragem client-side 0ms acionada por `switchDirection(dir)` sem recarga da API.
- **FR-007 (Lightweight Charts Multi-Direction Markers)**:
  - Sinais `BUY`: seta verde para cima (`shape: 'arrowUp'`, `color: '#00E676'`, `position: 'belowBar'`).
  - Sinais `SELL`: seta vermelha para baixo (`shape: 'arrowDown'`, `color: '#FF5252'`, `position: 'aboveBar'`).
  - Linhas de referência de suporte em verde/amarelo; linhas de resistência de topo em vermelho/magenta.

---

## Technical Constraints & Invariants

1. **Zero Look-Ahead Bias**:
   - Vendas em modo abertura executam obrigatoriamente no preço de abertura de $t+1$.
   - Vendas na última barra disponível ($t = N-1$) não podem emitir execução além dos limites do array e devem ser marcadas como pendentes (`AGUARDANDO_ABERTURA_T+1`).
2. **Backward Compatibility**:
   - Manter 100% dos testes existentes (32 testes) passando sem quebras.
   - Preservar os endpoints FastAPI (`/api/analyze`, `/api/radar`, `/api/simulate`) garantindo retrocompatibilidade com campos opcionais ou novos parâmetros `direction`.
3. **Desempenho 60fps**:
   - Alternância entre `Compra`, `Venda` e `Ambos` deve executar em $< 10\text{ms}$ no cliente, filtrando os sinais já pré-carregados na memória JavaScript.

---

## Key Metrics & Success Criteria

- **Catálogo de Estratégias**: 24 estratégias de Compra + 24 estratégias simétricas de Venda = 48 configurações operacionais completas.
- **Visualização**: Marcadores verdes e vermelhos renderizados no canvas com ordenação temporal estrita.
- **Acurácia Estatística**: Taxa de acerto de venda calculando lucro na desvalorização e prejuízo na alta do ativo.
- **Testes**: 100% dos testes unitários e de integração aprovados.
