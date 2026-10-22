# Feature Specification: Correção de Exibição dos Novos Indicadores na Aba Gráfico, Filtragem Inicial por Direção e Persistência de Aba Ativa ao Atualizar Página

**Feature Branch**: `014-chart-indicators-filter-tab-persistence`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Correcao de Exibicao dos Novos Indicadores na Aba Grafico Filtragem Inicial por Direcao e Persistencia de Aba Ativa ao Atualizar Pagina com F5"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exibição Completa dos Novos Indicadores na Barra Lateral do Gráfico (Priority: P1)

Como analista técnico ou investidor, quero visualizar e poder ativar/desativar cada um dos 10 novos indicadores quantitativos na barra lateral esquerda da aba Gráfico (`#tab-terminal`), para que os sinais correspondentes sejam plotados diretamente sobre as velas do TradingView Lightweight Charts com marcadores visuais.

**Why this priority**: O usuário não consegue inspecionar graficamente os 10 novos indicadores entregues na feature anterior porque a barra lateral do gráfico não lista os checkboxes correspondentes.

**Independent Test**: Acessar a aba Gráfico (`#tab-terminal`) e verificar se os novos indicadores aparecem organizados em grupos de Compra e Venda na barra lateral, e que marcar o checkbox plota os respectivos marcadores nas velas do gráfico.

**Acceptance Scenarios**:
1. **Given** que o usuário está na aba Gráfico, **When** ele inspeciona a barra lateral de estratégias, **Then** ele encontra os blocos de "Indicadores Quantitativos" para Compra e Venda com os 10 indicadores (Bollinger Fechou Fora/Dentro, Keltner Squeeze, Z-Score, IFR/RSI, Estocástico, MACD, VWAP, MFI, Volume Clímax e SuperTrend).
2. **Given** a seleção de qualquer checkbox de indicador quantitativo, **When** a análise for executada/filtrada, **Then** as marcas e preços de execução aparecem no gráfico TradingView sem erros no console.

---

### User Story 2 - Filtragem Inicial Correta da Barra Lateral pela Direção Selecionada (Priority: P2)

Como investidor focado em operações de compra, quando eu clicar na aba Gráfico e o botão global de direção estiver em "Compra" (`BUY`), quero que a barra lateral exiba apenas os acordeões e estratégias de Compra (ocultando as estratégias de Venda), sem a necessidade de clicar novamente no botão de direção.

**Why this priority**: Evita ruído visual e inconsistência de estado na interface, garantindo que o que o botão de direção diz que está filtrando reflita imediatamente na lista de estratégias.

**Independent Test**: Carregar ou alternar para a aba Gráfico com o botão de Compra selecionado e verificar que todos os acordeões de estratégias de Venda (`data-direction="SELL"`) estão devidamente ocultados com a classe `hidden`.

**Acceptance Scenarios**:
1. **Given** que o botão de direção está em "Compra" (`BUY`), **When** o usuário abre a aba Gráfico, **Then** apenas os grupos com `data-direction="BUY"` estão visíveis e todos os grupos com `data-direction="SELL"` permanecem ocultos.
2. **Given** que o usuário troca a direção para "Venda" (`SELL`), **When** a alteração é feita, **Then** apenas os grupos de venda ficam visíveis.
3. **Given** que o usuário escolhe "Ambos" (`BOTH`), **When** ativado, **Then** todos os grupos de compra e venda ficam visíveis simultaneamente.

---

### User Story 3 - Persistência da Aba Ativa ao Recarregar a Página com F5 (Priority: P3)

Como usuário, quero que ao recarregar a página (F5 ou atualização do navegador) a aplicação continue exatamente na aba onde eu estava trabalhando (ex: Gráfico, Simulador ou Playbook), em vez de ser redirecionado forçadamente para a página inicial (Radar).

**Why this priority**: Melhora significativamente a experiência de uso (UX), permitindo recarregar a página para atualizar dados ou inspecionar sem perder o fluxo da tela de trabalho atual.

**Independent Test**: Navegar para a aba "Gráfico" (`tab-terminal`), pressionar F5/Recarregar no navegador e constatar que a aplicação reabre diretamente na aba "Gráfico". Fazer o mesmo teste para as abas "Simulador" (`tab-simulator`), "Playbook" (`tab-playbook`) e "Radar" (`tab-radar`).

**Acceptance Scenarios**:
1. **Given** que o usuário está na aba Simulador ou Gráfico, **When** a página for recarregada pelo navegador, **Then** a aplicação lê o estado persistido (via hash de URL `window.location.hash` e/ou `localStorage`) e reabre a mesma aba.
2. **Given** uma URL compartilhada ou acessada diretamente com `#terminal` ou `#simulator`, **When** carregada no navegador, **Then** a aplicação inicia diretamente na aba correspondente.

---

### Edge Cases

- **Navegador sem Suporte a LocalStorage ou Cookies Bloqueados**: O sistema deve utilizar a hash da URL (`window.location.hash`) como canal primário ou fallback gracioso, garantindo que mesmo em modo anônimo a navegação seja restaurada.
- **Hash Inválida na URL (ex: `#aba-inexistente`)**: O sistema deve fazer fallback seguro para a aba padrão inicial (`tab-radar`) sem disparar exceções de JavaScript.
- **Redimensionamento do Gráfico ao Restaurar Diretamente na Aba Gráfico**: Ao iniciar a página já na aba Gráfico a partir de um reload, o container do TradingView Lightweight Charts deve calcular as dimensões corretas do canvas após o DOM estar visível, prevenindo que o gráfico fique colapsado com altura zero.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O layout da barra lateral da aba Gráfico (`src/web/index.html`) DEVE conter os grupos de acordeão "Indicadores Quantitativos - Compra" e "Indicadores Quantitativos - Venda", mapeados com a classe `.strategy-group-wrapper` e seus respectivos atributos `data-direction="BUY"` e `data-direction="SELL"`.
- **FR-002**: Cada um dos 10 novos indicadores quantitativos DEVE possuir seu checkbox `.strategy-cb` com `data-id` correspondente ao seu identificador técnico (`bollinger_close_in`, `keltner_squeeze`, `zscore_extreme`, `rsi_divergence`, `stochastic_extreme`, `macd_momentum`, `vwap_bands`, `mfi_extreme`, `volume_climax_vsa`, `supertrend_trailing`) e rótulo legível em português.
- **FR-003**: O arquivo `src/web/app.js` DEVE mapear os novos IDs no dicionário de aliases `STRATEGY_ALIASES` e no catálogo de filtros para sincronização bidirecional instantânea entre os checkboxes e o estado de plotagem do gráfico.
- **FR-004**: O sistema DEVE aplicar a filtragem de visibilidade dos acordeões da sidebar pela direção ativa logo na inicialização da página e sempre que a aba Gráfico for ativada na função `switchTab()`, garantindo que se o botão de Compra estiver ativo, nenhuma estratégia de venda fique visível.
- **FR-005**: A função `switchTab()` em `src/web/app.js` DEVE persistir a aba ativa tanto no `localStorage` (`activeTab`) quanto atualizar a hash da URL (`window.location.hash = '#' + tabId.replace('tab-', '')`).
- **FR-006**: Na inicialização do documento (`DOMContentLoaded`), a aplicação DEVE inspecionar primeiramente a hash da URL (`window.location.hash`) e secundariamente o `localStorage`, ativando a aba salva em vez de forçar sempre `tab-radar`.
- **FR-007**: Ao restaurar diretamente na aba Gráfico (`tab-terminal`), o sistema DEVE acionar a carga de análise e o ajuste responsivo de tamanho do gráfico (`resizeChartResponsive()` e `fitContent()`) garantindo visualização impecável.

### Key Entities

- **ActiveTabState**: Representação do identificador da aba aberta (`tab-radar`, `tab-terminal`, `tab-simulator`, `tab-playbook`) sincronizado entre hash de URL, `localStorage` e `state.activeTab`.
- **StrategySidebarGroup**: Elemento DOM `.strategy-group-wrapper` com atributo `data-direction` (`BUY` ou `SELL`) controlado reativamente pelo seletor global de direção.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos 10 novos indicadores quantitativos devem estar listados com checkboxes funcionais na barra lateral da aba Gráfico.
- **SC-002**: Ao selecionar "Compra" e entrar na aba Gráfico, exatamente 0 grupos de estratégias com `data-direction="SELL"` devem estar visíveis.
- **SC-003**: Ao pressionar F5/recarregar a página em qualquer uma das 4 abas (Radar, Gráfico, Simulador, Playbook), a aplicação deve reabrir na mesma aba em 100% dos testes.
- **SC-004**: Zero erros de JavaScript no console durante a navegação, recarregamento ou alternância de checkboxes.
- **SC-005**: Todos os 81 testes automatizados existentes continuam passando sem regressão.

---

## Assumptions

- O usuário utiliza navegadores modernos compatíveis com HTML5 History API / Location Hash e LocalStorage (Chrome, Edge, Firefox, Safari).
- Os seletores de classe `.strategy-group-wrapper` e `.strategy-cb` já possuem estutura de eventos consolidada em `src/web/app.js`.
