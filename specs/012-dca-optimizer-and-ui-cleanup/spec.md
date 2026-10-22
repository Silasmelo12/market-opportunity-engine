# Feature Specification: Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA com Ranking de Estratégias de Compra e Ocultação de Venda no Frontend

**Feature Branch**: `012-dca-optimizer-and-ui-cleanup`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Suporte ao Otimizador 'Mais Lucrativa' para Acumulação DCA com Ranking de Estratégias de Compra e Ocultação de Venda no Frontend"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Busca da Estratégia de Acumulação DCA Mais Lucrativa (Priority: P1) 🎯 MVP

Como investidor quantitativo que utiliza a abordagem de acúmulo de patrimônio a longo prazo (DCA nos Fundos de Mercado), quero clicar no botão "Mais Lucrativa" quando estiver com o modo "Acumulação (DCA Fundos)" selecionado e receber o ranking das estratégias de compra com maior rentabilidade sobre o capital acumulado e maior patrimônio final gerado, para que eu possa identificar instantaneamente o melhor gatilho de aporte periódico para o ativo.

**Why this priority**: É o valor central do usuário. Hoje o otimizador só procura pares de Trade (Compra -> Venda), o que gera inconsistência conceitual ou resultados vazios/divergentes quando o usuário busca acumulação sem venda.

**Independent Test**: Selecionar um ativo (ex: PETR4.SA), definir o modo como "Acumulação (DCA Fundos)" e clicar em "Mais Lucrativa". O sistema deve retornar a lista de estratégias de compra rankeadas por retorno sobre o capital aportado, destacando a estratégia campeã sem exigir nem exibir estratégias de venda.

**Acceptance Scenarios**:

1. **Given** o usuário selecionou o modo "Acumulação (DCA Fundos)" e informou um valor de aporte periódico, **When** clica em "Mais Lucrativa", **Then** o sistema analisa todas as estratégias de compra de fundo aplicáveis ao histórico e exibe o card da Estratégia Campeã de DCA com seu retorno percentual, patrimônio final acumulado, preço médio e total de aportes realizados.
2. **Given** a lista de melhores estratégias de acumulação é exibida, **When** o usuário clica em "Aplicar e Simular" na campeã, **Then** a estratégia de compra correspondente é selecionada no simulador e a simulação de acumulação é executada imediatamente, convergindo 100% com os números apresentados no card.

---

### User Story 2 - Ergonomia Visual Contextual para o Modo de Acumulação (Priority: P2)

Como usuário do simulador, quero que a interface oculte automaticamente o seletor de "Estratégia de Venda (Saída / Topo)" e os campos de trades fechados (Win Rate, Trades) sempre que o modo "Acumulação (DCA Fundos)" estiver ativo, para evitar poluição visual e confusão conceitual, visto que a acumulação não realiza vendas.

**Why this priority**: Evita ruído visual e impede que o usuário tente configurar ou esperar saídas de venda em uma simulação puramente de acúmulo de cotas.

**Independent Test**: Alternar o seletor de "Modo de Operação" entre "Trade (Compra -> Venda)" e "Acumulação (DCA Fundos)" e verificar que o container de estratégia de venda é ocultado no modo DCA e reexibido no modo Trade.

**Acceptance Scenarios**:

1. **Given** o usuário está na aba Simulador e seleciona "Acumulação (DCA Fundos)", **When** a interface atualiza, **Then** o campo "Estratégia de Venda (Saída / Topo)" fica invisível, mantendo visível apenas a "Estratégia de Compra (Entrada)" e o valor do aporte.
2. **Given** o usuário alterna de volta para "Trade (Compra -> Venda)", **When** a interface atualiza, **Then** o seletor de "Estratégia de Venda" e o seletor de "Entradas no Ciclo" voltam a ficar visíveis normalmente.

---

### Edge Cases

- **Ativo com pouquíssimo histórico ou sem sinais de fundo suficientes**: O sistema deve apresentar mensagem amigável informando que não foram encontrados aportes suficientes para rankear as estratégias de compra no período.
- **Estratégias de compra com retornos empatados**: O desempate deve priorizar o menor preço médio ponderado de aquisição das cotas ou o maior patrimônio final acumulado.
- **Datas customizadas de início e fim**: A otimização de DCA deve respeitar rigorosamente o intervalo temporal definido pelo usuário na tela.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a busca da estratégia mais lucrativa no modo "Acumulação (DCA Fundos)", avaliando o desempenho individual de cada estratégia de compra disponível no catálogo.
- **FR-002**: O ranking de estratégias de DCA DEVE ordenar as estratégias candidatas de forma decrescente pelo Retorno sobre Capital Acumulado (%) e Patrimônio Final (R$).
- **FR-003**: A resposta de otimização no modo DCA DEVE informar o total de aportes realizados, o valor total investido, o patrimônio final apurado, o preço médio de aquisição das cotas e o retorno percentual total.
- **FR-004**: O card da Campeã exibido na interface DEVE adaptar-se semanticamente ao modo DCA, ocultando qualquer menção a "Estratégia de Venda", "Win Rate" ou "Fator de Lucro", e exibindo o Total de Aportes, Preço Médio e Patrimônio Final.
- **FR-005**: A ação "Aplicar e Simular" na campeã de DCA DEVE selecionar a estratégia de compra vencedora no simulador e disparar o backtest de acumulação, garantindo paridade exata de dados entre o card da campeã e o painel de KPIs do simulador.
- **FR-006**: A interface gráfica DEVE ocultar dinamicamente o dropdown de "Estratégia de Venda" sempre que o modo "Acumulação (DCA Fundos)" estiver selecionado.
- **FR-007**: No modo "Trade (Compra -> Venda)", o sistema DEVE preservar integralmente o comportamento existente de varredura combinatorial de pares (Compra + Venda) e o suporte aos modos de ciclo 1x e Multi-Buy.

### Key Entities

- **DCA Champion Strategy**: Representa a estratégia de compra de fundo mais lucrativa identificada no período para acumulação, contendo identificador, rótulo amigável, retorno acumulado (%), patrimônio final, total aportado, preço médio ponderado e número de aportes.
- **DCA Top Ranking Item**: Item individual da tabela de classificação de estratégias de compra avaliadas em regime de aportes periódicos.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo de resposta para a varredura e ordenação de todas as estratégias de compra no modo DCA deve ser inferior a 1 segundo para períodos de até 2 anos de histórico.
- **SC-002**: 100% de consistência matemática entre as métricas exibidas no card da Estratégia Campeã de DCA e as métricas calculadas na execução do simulador ao clicar em "Aplicar e Simular".
- **SC-003**: 0% de menções a conceitos de venda (Estratégia de Venda, Win Rate de trades) exibidos ao usuário durante a otimização de Acumulação DCA.

---

## Assumptions

- A acumulação DCA considera aportes de valor fixo (`contribution_amount`) a cada confirmação de sinal da estratégia de compra avaliada.
- Não há liquidação de posição durante a acumulação DCA (buy-and-hold contínuo baseado em gatilhos de fundo).
- O capital inicial é utilizado como o primeiro aporte na data de início ou o valor configurado no campo de aporte.
