# Feature Specification: Refinamento de Padrões Duplos, Ajustes de UX e Performance do Radar

**Feature Branch**: `006-pattern-refinement-radar-performance`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Refinar Fundo Duplo + BOS (com filtros de tendência, posição relativa, RSI e profundidade), criar cópia como estratégia de venda; espelhar para Topo Duplo + BOS (cópia de compra); zoom/reset no gráfico; remover versão/FPS, 'Zona Ideal (Topo) 0,0%', 'S.A.' e título 'Terminal Quantitativo Gráfico'; radar inicia em Compra; ordem Compra/Venda/Ambos; paginação do radar; cache diário de cálculos; filtros de estratégia no radar iniciando desmarcados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fundo Duplo + BOS corrigido e confiável (Priority: P1)

Como analista, quero que o sinal de compra "Fundo Duplo + BOS" só apareça após uma queda real, para não comprar em topos ou no meio de ralis esticados.

**Why this priority**: O sinal atual marca mais topos que fundos, gerando compras erradas — é o maior problema de qualidade.

**Independent Test**: Rodar a estratégia em ativos com histórico conhecido e verificar que nenhum sinal de compra ocorre na máxima de 60 barras, acima da média, ou sem queda prévia mínima.

**Acceptance Scenarios**:

1. **Given** dois fundos B1 e B2 formados acima da SMA(50) e sem queda ≥ 6% desde a máxima recente, **When** ocorre rompimento da linha de pescoço, **Then** nenhum sinal de compra é gerado.
2. **Given** um rompimento cujo fechamento é ≥ máxima das últimas 60 barras, **When** o padrão é avaliado, **Then** o sinal é descartado.
3. **Given** RSI(14) não visitou < 45 durante B1/B2 ou RSI > 60 no rompimento, **When** avaliado, **Then** o sinal é descartado.
4. **Given** queda prévia ≥ 6%, fundos abaixo da SMA(50), RSI < 45 nos fundos e RSI ≤ 60 no rompimento, fechamento abaixo da máxima de 60 barras, **When** ocorre o rompimento, **Then** o sinal de compra é gerado.

---

### User Story 2 - Topo Duplo + BOS corrigido (espelho) (Priority: P1)

Como analista, quero que o sinal de venda "Topo Duplo + BOS" exija alta prévia real, de forma análoga ao fundo duplo.

**Independent Test**: Verificar que nenhum sinal de venda ocorre na mínima de 60 barras, abaixo da média ou sem alta prévia mínima.

**Acceptance Scenarios**:

1. **Given** topos T1/T2 abaixo da SMA(50) ou sem alta ≥ 6% desde a mínima recente, **When** há rompimento do suporte, **Then** nenhum sinal de venda.
2. **Given** fechamento do rompimento ≤ mínima das últimas 60 barras, **Then** sinal descartado.
3. **Given** RSI(14) não visitou > 55 em T1/T2 ou RSI < 40 no rompimento, **Then** sinal descartado.

---

### User Story 3 - Cópias invertidas como novas estratégias (Priority: P2)

Como analista, quero manter o comportamento antigo dos padrões como estratégias novas e com direção invertida: o antigo Fundo Duplo + BOS vira estratégia de **venda** e o antigo Topo Duplo + BOS vira estratégia de **compra**, pois empiricamente marcam a região oposta.

**Independent Test**: Comparar sinais da nova estratégia com os sinais da versão antiga: mesmas datas, direção invertida.

**Acceptance Scenarios**:

1. **Given** a lógica original do Fundo Duplo + BOS, **When** a nova estratégia "Fundo Duplo Invertido (Venda)" é executada, **Then** gera sinais de venda nas mesmas barras em que a lógica antiga gerava compra.
2. **Given** a lógica original do Topo Duplo + BOS, **When** a nova estratégia "Topo Duplo Invertido (Compra)" é executada, **Then** gera sinais de compra nas mesmas barras em que a lógica antiga gerava venda.
3. Ambas aparecem no radar, no simulador e na tabela comparativa com nomes distintos dos originais.

---

### User Story 4 - Radar rápido com paginação e cache diário (Priority: P1)

Como usuário, quero que o radar abra rapidamente, carregando por páginas e reaproveitando cálculos já feitos no dia.

**Independent Test**: Abrir o radar duas vezes no mesmo dia; a segunda abertura deve ser quase instantânea; navegar entre páginas.

**Acceptance Scenarios**:

1. **Given** o radar aberto, **When** carregado, **Then** apenas a primeira página (padrão 20 ativos) é calculada/exibida, com controles anterior/próxima e indicação da página atual/total.
2. **Given** cálculos já realizados hoje para um ativo/estratégia, **When** o radar é aberto novamente, **Then** os resultados são servidos do cache sem recalcular.
3. **Given** a virada do dia (novo pregão/novos dados), **Then** o cache do dia anterior é invalidado e recalculado sob demanda.
4. **Given** o serviço de cache indisponível, **Then** o sistema continua funcionando calculando diretamente (sem erro para o usuário).

---

### User Story 5 - Filtros e defaults do radar (Priority: P2)

Como usuário, quero que o radar inicie em "Compra", com os botões na ordem Compra, Venda, Ambos, e com filtro de estratégias (todas desmarcadas inicialmente).

**Acceptance Scenarios**:

1. **Given** o radar aberto pela primeira vez, **Then** o modo selecionado é "Compra" e os botões aparecem na ordem Compra → Venda → Ambos.
2. **Given** o radar aberto, **Then** existe um filtro de estratégias com todas as opções desmarcadas.
3. **Given** nenhuma estratégia marcada, **Then** o radar mostra oportunidades de todas as estratégias da direção selecionada (desmarcado = sem filtro).
4. **Given** uma ou mais estratégias marcadas, **Then** o radar mostra apenas oportunidades dessas estratégias, e a paginação considera o resultado filtrado.

---

### User Story 6 - Zoom no gráfico e limpeza visual (Priority: P3)

Como usuário, quero botões de zoom (+/−) e reset no gráfico, e uma interface limpa sem textos desnecessários.

**Acceptance Scenarios**:

1. **Given** o gráfico exibido, **When** clico em "+", "−" ou "Reset", **Then** o gráfico aproxima, afasta ou volta à visualização padrão.
2. **Given** qualquer tela, **Then** não aparecem: o nome/versão do sistema, o contador de FPS, o texto "Zona Ideal (Topo) 0,0%" e o título "Terminal Quantitativo Gráfico".
3. **Given** ativos brasileiros listados, **Then** os nomes aparecem sem o sufixo "S.A." (ex.: "Petrobras" em vez de "Petrobras S.A.").

### Edge Cases

- Ativo com menos de 60 barras de histórico: filtros de posição relativa/SMA(50) não podem ser avaliados → sinal descartado.
- RSI indisponível no início da série (primeiras 14 barras) → sinal descartado.
- Nome de ativo contendo "S.A." em variações ("S/A", "SA" final) → remover apenas o sufixo societário, sem alterar o restante do nome.
- Filtro de estratégia que resulta em zero oportunidades → mensagem "Nenhuma oportunidade encontrada" e paginação oculta.
- Troca de direção (Compra/Venda/Ambos) com estratégias marcadas que não pertencem à nova direção → essas marcações são ignoradas no filtro.
- Zoom no limite máximo/mínimo → botão não produz efeito, sem erro.

## Requirements *(mandatory)*

### Functional Requirements

**Fundo Duplo + BOS (compra, corrigido)**
- **FR-001**: Os fundos B1 e B2 MUST estar abaixo da SMA(50) (contexto de tendência de baixa) OU vir de uma queda ≥ 6% em relação à máxima recente.
- **FR-002**: O sinal MUST ser descartado se Close[t] do rompimento ≥ máxima de High das últimas 60 barras.
- **FR-003**: O RSI(14) MUST ter ficado < 45 em algum momento durante a formação de B1 ou B2, e MUST ser ≤ 60 na barra de rompimento.
- **FR-004**: Antes de B1 MUST ter ocorrido queda mínima de 6% a partir da máxima anterior na janela de análise.
- **FR-005**: Todos os limiares (período da média, % de queda, janela de máximas, níveis de RSI) MUST ser parâmetros configuráveis com os defaults acima.

**Topo Duplo + BOS (venda, corrigido — espelho)**
- **FR-006**: T1 e T2 MUST estar acima da SMA(50) OU vir de alta ≥ 6% desde a mínima recente.
- **FR-007**: Sinal descartado se Close[t] ≤ mínima de Low das últimas 60 barras.
- **FR-008**: RSI(14) MUST ter ficado > 55 durante T1 ou T2 e MUST ser ≥ 40 no rompimento.
- **FR-009**: Antes de T1 MUST ter ocorrido alta mínima de 6% a partir da mínima anterior.

**Novas estratégias invertidas**
- **FR-010**: O sistema MUST oferecer a estratégia "Fundo Duplo Invertido (Venda)" que reproduz exatamente a lógica original (pré-correção) do Fundo Duplo + BOS, emitindo sinal de venda.
- **FR-011**: O sistema MUST oferecer a estratégia "Topo Duplo Invertido (Compra)" que reproduz a lógica original do Topo Duplo + BOS, emitindo sinal de compra.
- **FR-012**: As novas estratégias MUST estar disponíveis em radar, simulador/backtest e comparativos.

**Radar**
- **FR-013**: O radar MUST iniciar no modo "Compra".
- **FR-014**: Os botões de direção MUST seguir a ordem Compra, Venda, Ambos.
- **FR-015**: O radar MUST ser paginado (20 ativos por página por padrão), calculando apenas os ativos da página solicitada quando não houver cache.
- **FR-016**: O radar MUST ter filtro multi-seleção de estratégias, iniciando com todas desmarcadas; nenhuma marcada equivale a "todas".
- **FR-017**: Resultados de cálculo diários (por ativo, estratégia e data) MUST ser armazenados em cache persistente compartilhado e reutilizados durante o mesmo dia.
- **FR-018**: Na indisponibilidade do cache, o sistema MUST calcular normalmente sem falhar.

**Gráfico e UI**
- **FR-019**: O gráfico MUST ter botões de zoom in, zoom out e reset.
- **FR-020**: MUST ser removidos da interface: indicador de versão, contador de FPS, texto "Zona Ideal (Topo) 0,0%" e título "Terminal Quantitativo Gráfico".
- **FR-021**: Nomes de ativos brasileiros MUST ser exibidos sem o sufixo "S.A." (e variações "S/A").

### Key Entities

- **Estratégia**: id, nome exibido, direção (compra/venda), parâmetros configuráveis.
- **Sinal/Oportunidade**: ativo, estratégia, direção, data, preço de referência.
- **Resultado em cache**: chave (ativo, estratégia, data de pregão), resultado calculado, validade até a virada do dia.
- **Página do radar**: número da página, tamanho, total de itens, filtros aplicados (direção, estratégias).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0% dos sinais de compra do Fundo Duplo + BOS ocorrem na máxima de 60 barras ou com RSI > 60 no rompimento (verificado em backtest do universo atual).
- **SC-002**: 0% dos sinais de venda do Topo Duplo + BOS ocorrem na mínima de 60 barras ou com RSI < 40.
- **SC-003**: A primeira página do radar aparece em ≤ 3 segundos sem cache e ≤ 1 segundo com cache do dia.
- **SC-004**: Navegar entre páginas com cache leva ≤ 1 segundo.
- **SC-005**: 100% dos itens visuais listados no FR-020 e sufixos "S.A." ausentes em todas as telas.
- **SC-006**: As estratégias invertidas reproduzem 100% das datas de sinal da lógica original.

## Assumptions

- Defaults escolhidos dentro das faixas informadas: SMA(50), queda/alta prévia de 6% (faixa 5–8%), janela de 60 barras, RSI < 45 / ≤ 60 (compra) e simétricos > 55 / ≥ 40 (venda).
- O usuário indicou explicitamente Redis como tecnologia de cache diário; a decisão final fica para o plano.
- "Dia" do cache = data do último pregão disponível nos dados.
- Tamanho de página padrão 20 ativos.
- Os nomes das novas estratégias são provisórios e podem ser renomeados no plano.
- O item 11 não foi informado na solicitação original e não faz parte do escopo.
