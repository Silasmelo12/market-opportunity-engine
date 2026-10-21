# Feature Specification: Correção do Radar, Seletor de Modelo de Ciclo (1x vs Multi-Buy) e Alinhamento do Simulador

**Feature Branch**: `010-radar-direction-and-simulator-fixes`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "crie a spec de correção" + "gostei das duas abordagens, gostaria que eu pudesse selecionar uma das duas para fazer o processo. então adicione isso na spec que acabei de criar."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtragem Reativa e Causal de Direção no Radar (Priority: P1)

Como um operador ou analista quantitativo no Terminal de Mercado,  
quero clicar nos botões de direção (**Compra**, **Venda** e **Ambos**) no cabeçalho ou no Radar,  
para que a tabela de oportunidades e o menu de estratégias atualizem instantaneamente com as oportunidades correspondentes à direção escolhida, sem comportamento inerte ou tabelas em branco.

**Why this priority**: É o defeito operacional primário relatado pelo usuário. Impede a visualização e varredura de sinais de topo (venda) e do universo consolidado bidirecional no Radar.

**Independent Test**: Pode ser testado de forma 100% isolada acessando a aba "Radar", clicando no botão "Venda" e verificando que a tabela carrega e lista oportunidades de venda/topo com os badges de timing corretos, alternando em seguida para "Ambos" e "Compra".

**Acceptance Scenarios**:

1. **Given** que o usuário está na aba Radar com a direção "Compra" ativa, **When** clica no botão "Venda", **Then** o sistema reseta a paginação para a página 1, busca/renderiza as oportunidades de venda no servidor e atualiza o menu de estratégias com filtros de venda.
2. **Given** que o usuário está na aba Radar, **When** clica no botão "Ambos", **Then** a tabela exibe oportunidades de compra e venda intercaladas por timing/prioridade.
3. **Given** que o usuário alternou a direção, **When** clica para navegar entre as páginas do radar (próxima/anterior), **Then** a direção selecionada é mantida e as páginas subsequentes refletem a mesma direção.

---

### User Story 2 - Seletor de Modelo de Entrada: Compra Única (1x) vs. Acumulação Multi-Buy (Priority: P2)

Como um investidor ou trader sistemático,  
quero poder selecionar explicitamente o modelo de execução por ciclo no Simulador entre **"Compra Única (1x por Ciclo)"** e **"Acumulação Multi-Buy (Nx por Ciclo)"**,  
para que eu possa tanto analisar operações simples com posição fixa de 1 entrada quanto testar estratégias de acumulação tática com reentradas e preço médio ponderado.

**Why this priority**: Dá ao usuário a liberdade de escolher entre as duas filosofias operacionais aprovadas (posição única estática vs. acumulação de cotas), eliminando qualquer confusão ou ambiguidade matemática.

**Independent Test**: Pode ser testado alternando o seletor entre "Compra Única (1x)" e "Acumulação Multi-Buy" no painel do Simulador e executando a simulação, verificando que:
- No modo "Compra Única (1x)": cada ciclo executa apenas 1 compra no primeiro sinal e ignora novos sinais até a venda, mantendo o capital investido fixo no valor inicial.
- No modo "Acumulação Multi-Buy": novos sinais de compra adicionam cotas e recalculam o preço médio ponderado, apurando o capital acumulado real.

**Acceptance Scenarios**:

1. **Given** que o usuário selecionou o modo "Compra Única (1x)", **When** executa a simulação ou otimização, **Then** apenas o primeiro sinal de compra após uma venda é executado, todas as compras subsequentes no ciclo são ignoradas, e as métricas refletem a alocação de cota única.
2. **Given** que o usuário selecionou o modo "Acumulação Multi-Buy", **When** executa a simulação ou otimização, **Then** cada sinal de compra confirmado compra cotas adicionais, recalcula o preço médio ponderado e liquida 100% no sinal de venda.
3. **Given** que o usuário altera a opção do seletor, **When** a interface atualiza, **Then** os rótulos e descrições dos KPIs explicitam com clareza o modelo ativo (ex: "Capital Investido: R$ 100 (1x)" vs "Capital Investido: R$ 3.700 (Nx acumulado)").

---

### User Story 3 - Sincronização Fiel entre Otimizador ("Mais Lucrativa") e Simulador ("Aplicar e Simular") (Priority: P3)

Como um analista quantitativo utilizando o Simulador de Ciclos de Trade,  
quero clicar em "Mais Lucrativa", visualizar a combinação campeã calculada sob o tempo gráfico e o modelo de ciclo selecionados e, ao clicar em "Aplicar e Simular",  
obter **exatamente o mesmo resultado de retorno, lucro líquido, número de trades e taxa de acerto** prometido no card campeão.

**Why this priority**: Garante que o Otimizador e o Simulador falem a mesma língua matemática, acabando com discrepâncias de tempo gráfico (ex.: 1d vs 5m) ou divergências de motor contábil.

**Independent Test**: Pode ser testado configurando um tempo gráfico (ex.: 5m) e um modo de ciclo (1x ou Multi-Buy), clicando em "Mais Lucrativa", conferindo as métricas do card campeão e clicando em "Aplicar e Simular", confirmando que os KPIs do simulador resultam em valores idênticos.

**Acceptance Scenarios**:

1. **Given** que o usuário configurou o Simulador com determinado tempo gráfico (`sim-interval`) e modelo de ciclo (1x ou Multi-Buy), **When** clica em "Mais Lucrativa", **Then** o algoritmo de otimização varre as combinações usando o mesmo tempo gráfico e o mesmo modelo de ciclo.
2. **Given** que o card da combinação campeã exibe $N$ trades, $R\%$ de retorno e $P$ de lucro líquido, **When** o usuário clica em "Aplicar e Simular", **Then** os cards principais de KPI e o histórico de trades apresentam rigorosamente os mesmos $N$ trades, $R\%$ de retorno e $P$ de lucro líquido.

---

### Edge Cases

- **Ausência de Oportunidades na Direção**: Se uma categoria de ativos não possuir nenhum sinal confirmado na direção selecionada (ex: nenhuma venda em Commodities), a interface deve exibir mensagem semântica informativa ("Nenhuma oportunidade de venda encontrada nesta categoria"), mantendo os controles funcionais.
- **Transição Rápida de Direção**: Se o usuário alternar rapidamente entre "Compra", "Venda" e "Ambos", requisições assíncronas anteriores obsoletas não devem sobrescrever a resposta da direção mais recente.
- **Tempos Gráficos Intraday no Otimizador**: Ao otimizar pares em tempos de 5m ou 15m, o horizonte de dados deve ser limitado automaticamente ao período máximo permitido pela fonte de dados (ex: 60 dias) para evitar falhas de carregamento.
- **Ciclo Sem Sinais Adicionais no Multi-Buy**: Em trades onde ocorreu apenas 1 sinal de compra antes do sinal de venda, o comportamento de "Compra Única (1x)" e "Acumulação Multi-Buy" coincide naturalmente para aquele trade específico.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE atualizar os dados da tabela do Radar imediatamente ao acionar os seletores de direção "Compra", "Venda" ou "Ambos".
- **FR-002**: A troca de direção no Radar DEVE disparar a busca paginada correspondente (`loadRadarData`) utilizando a chave de cache e os parâmetros de direção corretos (`BUY`, `SELL`, `BOTH`).
- **FR-003**: A troca de direção DEVE redefinir a página ativa do radar para a primeira página (`page = 1`) para evitar inconsistências de paginação além dos limites.
- **FR-004**: O seletor de estratégias em dropdown do Radar (`renderRadarStratMenu`) DEVE ser re-renderizado ao alterar a direção para listar apenas estratégias pertinentes à direção selecionada (ou todas em caso de "Ambos").
- **FR-005**: O Simulador DEVE disponibilizar um controle interativo de **Modelo de Entrada no Ciclo** com duas opções mutuamente exclusivas:
  1. `single_buy`: **Compra Única (1x por Ciclo)**;
  2. `multi_buy`: **Acumulação Multi-Buy ($K$ Compras por Ciclo)**.
- **FR-006**: No modo `single_buy`, tanto a simulação quanto a otimização DEVEM executar estritamente a 1ª compra confirmada após a liquidação do ciclo anterior e descartar qualquer sinal de compra subsequente enquanto a posição estiver aberta.
- **FR-007**: No modo `multi_buy`, a simulação e a otimização DEVEM executar compras em todos os sinais de compra confirmados no ciclo, acumulando cotas e recalculando o preço médio ponderado.
- **FR-008**: A função de busca da combinação mais lucrativa (`runOptimizer` e `optimize_strategy_pairs`) DEVE extrair e utilizar o tempo gráfico selecionado no controle do próprio simulador (`sim-interval`), o horizonte de tempo adequado para intraday e o modelo de ciclo selecionado (`single_buy` vs `multi_buy`).
- **FR-009**: A ação "Aplicar e Simular" DEVE preencher os seletores de estratégia de compra e venda com a combinação campeã e disparar a simulação com os mesmos parâmetros que geraram aquela combinação, garantindo convergência exata entre o card da campeã e os cards de KPI do simulador.

---

### Key Entities

- **CycleEntryMode**: Enumeração representando a modalidade de entrada no ciclo de trade (`single_buy` | `multi_buy`).
- **RadarItem**: Registro de oportunidade do radar contendo ticker, categoria de ativo, direção (`BUY` ou `SELL`), estratégia, preço atual, timing (`IDEAL`, `EXTENDED`, `LATE`) e retorno prospectivo.
- **RadarPage**: Estrutura paginada que agrega itens de oportunidade, número da página, total de páginas e direção ativa.
- **StrategyPairRankItem**: Modelo de avaliação de par de estratégias contendo identificadores de compra/venda, retorno percentual, lucro líquido, taxa de acerto, número de trades fechados, drawdown máximo e modo de entrada avaliado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O clique em "Venda" ou "Ambos" no Radar atualiza a interface em menos de 1 segundo (usando cache local) ou no tempo padrão de varredura do servidor, exibindo as oportunidades correspondentes.
- **SC-002**: O usuário pode alternar livremente entre "Compra Única (1x)" e "Acumulação Multi-Buy" no Simulador, visualizando a atualização imediata dos resultados de acordo com o modelo selecionado.
- **SC-003**: As métricas de Retorno (%), Lucro Líquido, Total de Trades e Taxa de Acerto exibidas no card da combinação campeã do Otimizador e as métricas calculadas após clicar em "Aplicar e Simular" devem convergir com **100% de exatidão** para o modelo de ciclo e tempo gráfico configurados.
- **SC-004**: Zero regressões na suíte de testes unitários automatizados do projeto.

---

## Assumptions

- O endpoint `/api/radar` já possui suporte completo no backend aos parâmetros `direction=BUY`, `direction=SELL` e `direction=BOTH`.
- O dropdown de tempo gráfico do Simulador (`sim-interval`) e o seletor de modelo de ciclo (`cycle_entry_mode`) são as fontes de verdade para qualquer simulação ou otimização disparada dentro do simulador.
- Os testes unitários existentes continuarão cobrindo os cálculos estatísticos e contratos de dados da API.
