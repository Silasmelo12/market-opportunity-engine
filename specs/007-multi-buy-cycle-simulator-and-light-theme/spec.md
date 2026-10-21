# Feature Specification: Multi-Buy Cycle Trade, Light Theme & Enhanced Professional Simulator

**Feature Branch**: `007-multi-buy-cycle-simulator-and-light-theme`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "1. quero que no modo de compra e venda ele compre em absolutamente todos os sinais e acumule até o próximo sinal de venda e venda tudo. 2. adicionar tema do site claro. 3. melhore o simulador e deixe mais profissional e entendível. não esqueça de que a cada tarefa, faça commit e atualize o readme se necessário."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Buy Cycle Accumulation & Complete Exit (Priority: P1)

Como analista quantitativo ou investidor tático, quero que a simulação no modo "Trade (Compra -> Venda)" não ignore sinais de compra subsequentes ocorridos durante uma posição em aberto, mas sim compre em absolutamente todos os sinais de compra confirmados e acumule as cotas até que ocorra um sinal de venda, momento em que toda a posição acumulada é liquidada a mercado.

**Why this priority**: É a solicitação funcional primária. Atualmente, o simulador ignora todos os sinais de compra subsequentes se já estiver comprado, impedindo estratégias de acumulação de fundo em múltiplos pontos/escalonamento com realização unificada no topo.

**Independent Test**: Executar uma simulação com um ativo onde ocorrem 3 sinais de compra consecutivos seguidos por 1 sinal de venda. Verificar que foram executadas 3 entradas acumulando cotas e preço médio ponderado, e que a venda encerrou a totalidade das cotas com retorno consolidado correto.

**Acceptance Scenarios**:

1. **Given** um trade aberto após o primeiro sinal de compra em $t_1$, **When** novos sinais de compra confirmados ocorrerem em $t_2, t_3$ antes de qualquer sinal de venda, **Then** o simulador executa uma nova compra em cada um desses sinais, adicionando cotas à posição e atualizando o capital investido total e o preço médio ponderado de entrada.
2. **Given** uma posição com uma ou múltiplas compras acumuladas, **When** um sinal de venda confirmado for gerado, **Then** a totalidade das cotas acumuladas é vendida no preço de execução da venda (`Open[t_{sell}+1]` ou preço de reteste), apurando o PnL e retorno consolidado do ciclo completo.
3. **Given** um ciclo com múltiplas compras, **When** a tabela detalhada de trades for renderizada, **Then** o usuário consegue visualizar claramente todas as compras parciais pertencentes àquele ciclo (datas, preços individuais e preço médio) além dos dados consolidados de saída.
4. **Given** uma simulação que encerra com compras ativas sem sinal de venda subsequente até a última barra, **Then** o ciclo é marcado como "EM ABERTO", computando o valor de mercado atualizado com base no preço de fechamento da última barra.

---

### User Story 2 - Modo Visual Claro / Escuro (Theme Toggle) (Priority: P2)

Como usuário e trader que utiliza a plataforma em ambientes com iluminação variável, quero alternar entre o tema escuro (Dark Theme padrão institucional) e um tema claro (Light Theme elegante, com alto contraste e paleta fintech moderna), persistindo minha preferência no navegador.

**Why this priority**: Melhora significativa na usabilidade e acessibilidade, além de tornar as capturas de tela e demonstrações de portfólio muito mais versáteis e profissionais.

**Independent Test**: Clicar no botão seletor de tema (ícone Sol/Lua) no topo da interface e verificar se toda a paleta (fundo, cartões, tabelas, textos, inputs e gráficos do TradingView/Plotly) comuta instantaneamente sem quebra de contraste, mantendo-se ativa após recarregar a página.

**Acceptance Scenarios**:

1. **Given** a aplicação aberta, **When** o usuário clica no seletor de tema no cabeçalho, **Then** o tema comuta de Dark para Light (ou vice-versa) com transição fluida.
2. **Given** o tema Claro ativo, **Then** o gráfico TradingView e os gráficos analíticos Plotly atualizam suas cores de fundo, grades, eixos e tipografia para garantir contraste legível e estético.
3. **Given** uma preferência de tema selecionada, **When** o usuário atualiza a página ou reabre o navegador, **Then** a preferência salva em `localStorage` é respeitada imediatamente.

---

### User Story 3 - Simulador Visualmente Aprimorado, Didático e Profissional (Priority: P2)

Como analista que apresenta relatórios ou busca aprovação profissional, quero que o simulador apresente métricas financeiras mais claras, diagnósticos executivos intuitivos (ex.: Drawdown Máximo, Fator de Lucro, Taxa de Acerto, Preço Médio vs. Saída, Comparativo com Buy & Hold) e cards visuais de resumo que facilitem o entendimento imediato de qualquer stakeholder.

**Why this priority**: Transforma a ferramenta de um script de dados em um produto financeiro institucional compreensível tanto para analistas técnicos quanto para recrutadores e investidores.

**Independent Test**: Rodar uma simulação e verificar a presença de KPIs visuais destacados (Total Investido, Patrimônio Final, Retorno Acumulado %, Drawdown Máximo %, Win Rate %, Média de Dias por Ciclo, Saldo Lucro/Prejuízo em R$), gráfico de evolução de curva de capital com distinção visual de aportes/retiradas, e tabela com badges claros de status ("FECHADO - LUCRO", "FECHADO - PREJUÍZO", "EM ABERTO").

**Acceptance Scenarios**:

1. **Given** o resultado de uma simulação calculado, **Then** o topo exibe cartões KPI institucionais com cores semânticas (verde/vermelho), comparando diretamente o Retorno da Estratégia contra o *Buy & Hold* do ativo no mesmo período.
2. **Given** ciclos de trade com compras múltiplas, **Then** a tabela de histórico exibe um sumário expansível ou indicador claro de quantas entradas formaram aquele ciclo, o Preço Médio de Compra e o Preço de Venda.
3. **Given** o gráfico de curva de patrimônio, **Then** a visualização plota claramente o Capital Investido vs. Patrimônio Líquido ao longo do tempo.

---

### Edge Cases

- **Múltiplos sinais na mesma barra**: Se ocorrerem dois sinais de compra confirmados na mesma barra (ex.: de estratégias distintas), o simulador deve consolidar os aportes sem duplicar inconsistências de índice temporal.
- **Capital insuficiente para aporte fixo no ciclo de trade**: No modo de acúmulo de ciclo de trade, se o usuário configura um valor por aporte (ou divisão do capital inicial), o simulador deve tratar se o modelo de aporte é por cota fixa, valor monetário fixo por sinal, ou reinvestimento total/parcial.
- **Simulação com zero vendas**: Um ativo em forte tendência de alta que emite 5 compras e nenhuma venda até a data final deve apresentar o trade como aberto, com retorno flutuante (não realizado) baseado no preço atual.
- **Comutação de tema com gráfico aberto**: Ao alterar o tema, o TradingView Canvas não deve piscar ou perder a posição atual do zoom/escala.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O simulador no modo ciclo de trade MUST permitir e executar compras em **todos** os sinais de compra confirmados que ocorrerem enquanto a posição estiver aberta, acumulando as ações na carteira do ciclo.
- **FR-002**: Cada compra adicional no ciclo MUST acumular o número de cotas correspondente e recalcular o preço médio ponderado:
  $$\text{Preço Médio} = \frac{\sum (Q_i \times P_i)}{\sum Q_i}$$
- **FR-003**: Ao ocorrer um sinal de venda confirmado, o sistema MUST liquidar 100% das cotas acumuladas no ciclo, apurando o resultado consolidado e registrando o histórico de compras que compuseram o trade.
- **FR-004**: O sistema MUST suportar no endpoint `/api/simulate` e no frontend a definição do valor por sinal (ex.: aporte fixo por sinal de compra no ciclo ou fracionamento do capital).
- **FR-005**: O sistema MUST disponibilizar um seletor de tema (Dark / Light) acessível no cabeçalho global.
- **FR-006**: O tema Claro MUST possuir contraste acessível, fundos claros fintech elegantes (ex.: tons de cinza/ardósia neutros `#F8FAFC`, bordas `#E2E8F0`, tipografia escura `#0F172A`) e adaptar as cores do TradingView e Plotly dinamicamente.
- **FR-007**: A escolha de tema MUST ser salva em armazenamento local (`localStorage`) e aplicada antes do carregamento completo para evitar cintilação (*flash of unstyled theme*).
- **FR-008**: O simulador MUST apresentar métricas adicionais de robustez estatística: Fator de Lucro (*Profit Factor*), Máximo Rebaixamento (*Max Drawdown*), Retorno Anualizado, Média de Retorno por Ciclo e Comparativo com *Buy & Hold*.
- **FR-009**: A cada tarefa implementada nas fases seguintes, um commit git atômico MUST ser efetuado no formato padronizado pela governança.

### Key Entities

- **CycleTrade**: Representa um ciclo completo de operações, contendo:
  - `cycle_id`: Identificador sequencial.
  - `buy_entries`: Lista de compras parciais `[ { date, price, shares, capital, strategy_sub_id } ]`.
  - `total_shares`: Soma acumulada de cotas.
  - `total_invested`: Capital financeiro total empregado nas compras.
  - `average_buy_price`: Preço médio ponderado de entrada.
  - `sell_date`: Data da barra de liquidação total.
  - `sell_price`: Preço de saída executado.
  - `sell_strategy_sub_id`: Identificador da estratégia que disparou a venda.
  - `net_profit`: Lucro ou prejuízo líquido consolidado ($R\$$).
  - `return_pct`: Retorno percentual sobre o capital total investido.
  - `status`: `"FECHADO"` ou `"EM ABERTO"`.
- **ThemeConfig**: Identificador do tema ativo (`"dark"` ou `"light"`), mapa de cores de fundo, texto, bordas, velas e grades do gráfico.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No teste de múltiplos sinais de compra consecutivos, 100% dos sinais confirmados são executados e somados à posição antes do sinal de venda.
- **SC-002**: A divergência entre o preço médio calculado pelo simulador e o valor analítico formal é de $0.00\%$ (tolerância estritamente numérica).
- **SC-003**: A alternância entre tema claro e tema escuro ocorre em $\le 50\text{ms}$ no cliente, sem recarregar dados da API ou perder o estado do gráfico.
- **SC-004**: O simulador apresenta todos os 8 KPIs principais e tabela detalhada de trades em menos de 1 segundo para séries históricas de 2 anos.
- **SC-005**: 100% dos testes unitários novos e existentes passam na suíte de testes automatizados (`pytest`).

---

## Assumptions

- O valor alocado em cada sinal de compra adicional durante o ciclo pode ser configurado como um valor monetário fixo por sinal (ex.: R$ 1.000,00 por entrada) para permitir aportes acumulativos proporcionais e realistas.
- O tema claro será estilizado via classes utilitárias CSS / Tailwind compatíveis com a arquitetura SPA já existente.
- A cada tarefa concluída durante `/speckit-implement`, o agente executará o commit git individual correspondente, mantendo a integridade do histórico do repositório.
