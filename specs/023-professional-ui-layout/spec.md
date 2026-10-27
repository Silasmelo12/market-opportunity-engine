# Feature Specification: Layout Profissional e Unificado da Interface Web

**Feature Branch**: `feat/professional-ui-layout`
**Created**: 2026-10-27
**Status**: Draft
**Input**: User description: "Melhorar o layout da interface web e deixá-lo mais profissional, unificando o visual das oito áreas da plataforma, corrigindo textos corrompidos, padronizando componentes, tipografia, temas claro/escuro, navegação e comportamento responsivo, sem alterar backend, APIs, contratos de dados ou funcionalidades existentes."

## 1. Contexto e Objetivo

A interface web do **Market Opportunity & Bottom Statistical Engine** evoluiu em duas linguagens visuais distintas:

1. As áreas de acompanhamento patrimonial (Resumo, Posições, Proventos e Evolução Patrimonial) seguem um padrão claro, executivo e respirado.
2. As áreas quantitativas (Radar, Gráfico, Simulador e Playbook) ainda carregam a estética escura original do terminal, com regras visuais de compensação para o tema claro.

Essa convivência gera inconsistência de contraste, espaçamento, tipografia e hierarquia, além de textos visivelmente corrompidos por codificação. O objetivo é entregar uma experiência única, profissional e coerente em todas as áreas, preservando integralmente o comportamento funcional existente.

### Princípios Norteadores

1. **Uma única linguagem visual**: todas as áreas compartilham a mesma hierarquia tipográfica, paleta semântica, espaçamento, bordas, sombras e padrões de componente.
2. **Clareza executiva e densidade quantitativa**: a interface deve parecer um produto financeiro profissional, legível para acompanhamento patrimonial e denso o suficiente para análise quantitativa.
3. **Semântica financeira preservada**: nenhum indicador, rótulo, cálculo ou significado de dado pode ser alterado por conveniência estética.
4. **Consistência entre temas**: claro e escuro são cidadãos de primeira classe em todas as oito áreas, sem telas que “quebrem” ao alternar o tema.
5. **Evolução segura**: nenhuma funcionalidade, rota, identificador de contrato ou integração pode ser removida ou ter seu comportamento alterado.

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Conteúdo legível e identidade visual consistente (Priority: P1)

Como investidor que usa a plataforma diariamente, quero que todos os textos, rótulos e números estejam legíveis e visualmente consistentes, para confiar na informação e enxergar o produto como uma ferramenta financeira profissional.

**Why this priority**: Textos corrompidos, tamanhos abaixo do mínimo legível e ícones inconsistentes afetam todas as telas e comprometem diretamente a credibilidade do produto. É a correção de maior impacto e menor dependência das demais.

**Independent Test**: Percorrer as oito áreas e verificar que não há caracteres corrompidos, que nenhum texto funcional está abaixo do tamanho mínimo definido e que ícones e tipografia seguem o mesmo padrão visual.

**Acceptance Scenarios**:

1. **Given** qualquer uma das oito áreas, **When** o usuário visualiza títulos, botões, tabelas e mensagens, **Then** todo o texto está em português correto, sem caracteres corrompidos ou símbolos substituídos.
2. **Given** uma tela com muitos dados, **When** o usuário lê rótulos, metadados e valores, **Then** nenhum texto funcional é exibido abaixo do piso tipográfico definido e valores financeiros usam algarismos tabulares.
3. **Given** qualquer ação representada por ícone, **When** o usuário a visualiza, **Then** o ícone pertence ao mesmo conjunto visual e não há emojis usados como ícones funcionais.

---

### User Story 2 - Navegação clara e previsível (Priority: P2)

Como usuário da plataforma, quero alternar entre os ambientes “Minha Carteira” e “Análise Quantitativa” e entre suas subáreas com clareza, para saber sempre onde estou e como chegar ao que preciso.

**Why this priority**: A navegação é o esqueleto de toda a experiência. Sem ela consistente, as demais melhorias visuais perdem coesão e o usuário se desorienta.

**Independent Test**: Alternar entre os dois ambientes, percorrer as oito subáreas, recarregar a página, usar voltar/avançar do navegador e verificar que ambiente, subnavegação, painel ativo e estado visual permanecem sincronizados.

**Acceptance Scenarios**:

1. **Given** a plataforma aberta, **When** o usuário alterna o ambiente, **Then** a subnavegação exibe apenas as subáreas daquele ambiente e o estado ativo fica visualmente inequívoco.
2. **Given** uma rota explícita na URL, **When** a página é carregada, **Then** a rota da URL prevalece sobre a preferência armazenada e abre a área solicitada.
3. **Given** uma preferência previamente salva e ausência de rota explícita, **When** o usuário recarrega a página, **Then** a última área utilizada é restaurada.
4. **Given** navegação por voltar/avançar do navegador, **When** o histórico muda, **Then** ambiente, subnavegação e painel visível permanecem alinhados.
5. **Given** uso por teclado, **When** o usuário percorre a navegação com Tab e ativa com Enter/Espaço, **Then** todos os controles são alcançáveis e o foco é visível.

---

### User Story 3 - Áreas de carteira com padrão executivo uniforme (Priority: P3)

Como investidor acompanhando meu patrimônio, quero que Resumo, Posições, Proventos e Evolução Patrimonial compartilhem o mesmo padrão de cartões, tabelas, cabeçalhos e espaçamento, para comparar informações sem ruído visual.

**Why this priority**: Essas áreas concentram a operação patrimonial e já possuem uma base visual madura; padronizá-las consolida a identidade do produto e serve de referência para as áreas quantitativas.

**Independent Test**: Navegar pelas quatro áreas de carteira em tema claro e escuro e verificar que cabeçalhos, cartões, indicadores, gráficos, tabelas e acordeões seguem o mesmo padrão e alinhamento.

**Acceptance Scenarios**:

1. **Given** a área Resumo, **When** o usuário visualiza os indicadores principais, **Then** os cartões têm hierarquia, alinhamento, espaçamento e estados de variação consistentes entre si.
2. **Given** uma carteira com posições, **When** o usuário consulta Posições, **Then** cabeçalhos, tabelas, acordeões e ações por linha seguem o padrão único da plataforma.
3. **Given** uma carteira sem dados importados, **When** o usuário abre o Resumo, **Then** vê uma orientação clara de primeiro uso; com dados presentes, essa orientação não ocupa espaço indevido.
4. **Given** qualquer gráfico, **When** o tema é alternado, **Then** eixos, grades, legendas e cores semânticas permanecem legíveis e coerentes com o tema ativo.

---

### User Story 4 - Áreas quantitativas integradas à mesma identidade (Priority: P4)

Como analista quantitativo, quero que Radar, Gráfico, Simulador e Playbook tenham a mesma qualidade visual das áreas de carteira, para trabalhar por longos períodos com conforto e consistência.

**Why this priority**: São as áreas de maior densidade de dados e as que mais destoam hoje. A unificação completa depende da fundação visual e da navegação já estabelecidas.

**Independent Test**: Percorrer as quatro áreas quantitativas em ambos os temas e verificar que filtros, tabelas, formulários, gráficos, cartões e blocos de conteúdo seguem o mesmo padrão, sem resíduos da estética antiga.

**Acceptance Scenarios**:

1. **Given** o Radar, **When** o usuário aplica filtros e consulta a tabela, **Then** filtros, cabeçalhos, linhas, ordenação, paginação e estado vazio são visualmente consistentes com o restante da plataforma.
2. **Given** o Simulador, **When** o usuário configura parâmetros e executa uma simulação, **Then** formulários, seletores, botões e resultados seguem o padrão único e permanecem legíveis em ambos os temas.
3. **Given** o Gráfico, **When** o usuário alterna o tema ou redimensiona a janela, **Then** o gráfico se ajusta ao contêiner e mantém contraste e legibilidade.
4. **Given** o Playbook, **When** o usuário lê os grupos de estratégias, **Then** títulos, divisórias, blocos e destaques usam a mesma hierarquia visual das demais áreas.

---

### User Story 5 - Experiência responsiva e acessível (Priority: P5)

Como usuário em diferentes dispositivos, quero que a plataforma seja confortável em celular, tablet, notebook e monitor grande, e que pessoas com necessidades de acessibilidade consigam operá-la, para usar a ferramenta em qualquer contexto.

**Why this priority**: A responsividade e a acessibilidade são qualidades transversais que garantem que o novo padrão visual funcione de fato para todos os usuários e contextos.

**Independent Test**: Validar as oito áreas em 375px, 768px, 1366px e 1920px, em ambos os temas, incluindo navegação por teclado, zoom de 200% e preferência por movimento reduzido.

**Acceptance Scenarios**:

1. **Given** uma tela pequena, **When** o usuário navega entre áreas e consulta dados, **Then** não há sobreposição de conteúdo, quebra de layout ou rolagem horizontal involuntária.
2. **Given** uma tabela larga em tela pequena, **When** o usuário precisa ver mais colunas, **Then** há rolagem horizontal apenas na tabela e um indicativo visual de que ela é rolável.
3. **Given** qualquer elemento interativo, **When** o usuário o foca por teclado, **Then** há indicador de foco visível e ordem de tabulação lógica.
4. **Given** preferência do sistema por movimento reduzido, **When** a interface é utilizada, **Then** animações não essenciais são suprimidas.
5. **Given** zoom de 200%, **When** o usuário navega, **Then** conteúdo e controles continuam acessíveis e legíveis.

---

### Edge Cases

- Carteira vazia, sem importações da B3: a orientação de primeiro uso deve ser útil e não deve competir com indicadores zerados.
- Carteira com muitos ativos, nomes longos de ticker/empresa e valores financeiros extensos: layout deve truncar ou quebrar linha sem sobrepor elementos.
- Cotações indisponíveis, desatualizadas ou estimadas: sinalizações de contingência devem permanecer visíveis e legíveis no novo padrão.
- Troca de tema com gráficos abertos: gráficos devem refletir o tema ativo sem exigir recarregamento.
- Recarregamento, voltar/avançar e URL com hash inválido: navegação deve cair no estado padrão de forma previsível.
- Preferência armazenada inválida ou corrompida: o sistema deve restaurar o estado padrão sem erro visível.
- Tabelas com muitas colunas em 375px: rolagem horizontal restrita ao contêiner da tabela.
- Uso com leitor de tela: nomes acessíveis, papéis e estados dos controles de navegação devem ser anunciados corretamente.
- Preferência por movimento reduzido ou zoom elevado: não deve haver perda de conteúdo ou funcionalidade.
- Alternância rápida de ambiente e subárea: deve haver exatamente um painel e um estado ativo por vez.

## 3. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Todas as oito áreas da interface DEVEM apresentar textos em português correto, sem caracteres corrompidos, símbolos substituídos ou artefatos de codificação.
- **FR-002**: A interface DEVE adotar uma única linguagem visual em todas as áreas, com a mesma hierarquia tipográfica, paleta semântica, espaçamento, bordas, sombras e raios de arredondamento.
- **FR-003**: Os temas claro e escuro DEVEM ser suportados integralmente nas oito áreas, sem resíduos de paleta, contraste insuficiente ou componentes que só funcionem em um tema.
- **FR-004**: O tema claro DEVE ser o padrão inicial; a preferência do usuário DEVE ser persistida e respeitada em visitas subsequentes.
- **FR-005**: O cabeçalho DEVE apresentar marca, alternador dos dois ambientes, ações principais e controle de tema de forma agrupada e hierarquicamente clara.
- **FR-006**: A subnavegação DEVE ser contextual ao ambiente ativo, exibindo apenas as quatro subáreas correspondentes.
- **FR-007**: O estado ativo de ambiente e subárea DEVE ser visualmente inequívoco e acessível por teclado.
- **FR-008**: A navegação DEVE preservar a precedência URL explícita > preferência armazenada > padrão do sistema, incluindo voltar/avançar e recarregamento.
- **FR-009**: DEVE existir exatamente um painel visível e um estado ativo por vez em qualquer combinação de ambiente e subárea.
- **FR-010**: Nenhum texto funcional, rótulo, cabeçalho de tabela ou metadado acionável DEVE ser exibido abaixo do piso tipográfico de 11px.
- **FR-011**: Valores financeiros, tickers e métricas quantitativas DEVEM usar algarismos tabulares e tipografia monoespaçada para facilitar comparação.
- **FR-012**: Ícones funcionais DEVEM pertencer a um conjunto visual único e consistente; emojis NÃO DEVEM ser usados como ícones de ação ou navegação.
- **FR-013**: Cartões, botões, campos de formulário, seletores, badges, tabelas e acordeões DEVEM seguir padrões únicos de tamanho, espaçamento, estados de hover, foco e desabilitado.
- **FR-014**: Cabeçalhos de área DEVEM apresentar título, contexto e ações de forma padronizada entre as oito áreas.
- **FR-015**: Tabelas de dados DEVEM usar alinhamento numérico consistente, cabeçalho legível, separação de linhas e estado de hover.
- **FR-016**: Gráficos DEVEM herdar as cores, grades, eixos e tipografia do tema ativo e ajustar-se ao contêiner ao abrir ou redimensionar.
- **FR-017**: A orientação de primeiro uso da área Resumo DEVE ser exibida apenas quando não houver dados de carteira/importação; com dados presentes, o espaço DEVE ser ocupado por conteúdo operacional.
- **FR-018**: A interface DEVE ser utilizável em larguras de 375px, 768px, 1366px e 1920px, sem sobreposição de conteúdo ou rolagem horizontal involuntária.
- **FR-019**: Tabelas mais largas que o contêiner DEVEM permitir rolagem horizontal restrita à tabela, com indicativo visual de rolagem.
- **FR-020**: Todos os controles interativos DEVEM ser alcançáveis por teclado, com foco visível e ordem de tabulação lógica.
- **FR-021**: Contraste de texto e elementos de interface DEVE atender ao nível AA das diretrizes WCAG.
- **FR-022**: A interface DEVE respeitar a preferência do sistema por movimento reduzido, suprimindo animações não essenciais.
- **FR-023**: A interface DEVE permanecer funcional com zoom de 200%, sem perda de conteúdo ou de controles.
- **FR-024**: Todos os identificadores de contrato, rotas, dados e comportamentos funcionais existentes DEVEM ser preservados; nenhuma API ou regra de negócio pode ser alterada.
- **FR-025**: Nenhuma área, funcionalidade, gráfico, tabela ou conteúdo informativo existente pode ser removido como parte da melhoria visual.
- **FR-026**: Mensagens de erro, carregamento, vazio e indisponibilidade DEVEM seguir o mesmo padrão visual e permanecer compreensíveis em ambos os temas.
- **FR-027**: A interface DEVE manter desempenho percebido equivalente ao atual, sem atraso adicional perceptível na troca de áreas, filtros ou temas.
- **FR-028**: A revisão visual DEVE cobrir as oito áreas nas quatro larguras de referência e nos dois temas, totalizando 64 verificações de tela.

### Key Entities

- **Área da plataforma**: cada uma das oito subáreas navegáveis, distribuídas entre os ambientes “Minha Carteira” e “Análise Quantitativa”, com título, contexto, ações e conteúdo próprio.
- **Ambiente**: agrupamento superior que organiza as áreas em acompanhamento patrimonial ou análise quantitativa.
- **Tema visual**: variante clara ou escura que define superfícies, bordas, tipografia e cores semânticas de toda a interface.
- **Componente visual compartilhado**: elemento reutilizável como cartão, tabela, botão, campo, badge, acordeão ou gráfico, com estados e medidas padronizados.
- **Preferência de navegação/tema**: estado persistido que restaura a última área e o tema escolhido, sem sobrepor uma rota explícita.
- **Estado vazio/onboarding**: conteúdo exibido quando não há dados suficientes para a operação normal da área.

## 4. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das oito áreas exibem textos em português correto, com zero ocorrências de caracteres corrompidos ou artefatos de codificação em auditoria visual e automatizada.
- **SC-002**: 8 de 8 áreas apresentam a mesma linguagem visual, com zero telas contendo resíduos da paleta antiga ou estilos conflitantes.
- **SC-003**: 8 de 8 áreas funcionam integralmente nos temas claro e escuro, sem componentes ilegíveis ou com contraste abaixo de AA.
- **SC-004**: 100% dos textos funcionais respeitam o piso tipográfico de 11px em auditoria de todas as áreas.
- **SC-005**: As 64 verificações de tela (8 áreas × 4 larguras × 2 temas) são aprovadas sem sobreposição de conteúdo, corte de informação ou rolagem horizontal involuntária.
- **SC-006**: 100% dos controles interativos são alcançáveis por teclado, com foco visível e ordem lógica em todas as áreas.
- **SC-007**: Zero regressões funcionais nos testes automatizados existentes, com todas as rotas e identificadores de contrato preservados.
- **SC-008**: A preferência de tema e de última área é restaurada corretamente em 100% dos recarregamentos testados.
- **SC-009**: A troca entre áreas e entre temas não introduz atraso perceptível adicional em relação à linha de base atual.
- **SC-010**: A revisão de aceitação visual registra aprovação explícita em todas as 64 verificações de tela antes da entrega final.

## 5. Assumptions

- O escopo abrange as oito áreas existentes, sem criação de novas telas ou funcionalidades.
- O tema claro é o padrão inicial, alinhado às diretrizes de design vigentes; a preferência do usuário é persistida.
- A orientação de primeiro uso do Resumo é condicional à ausência de dados de carteira/importação.
- Ícones funcionais serão vetoriais e consistentes, substituindo emojis.
- Backend, APIs, cálculos financeiros, contratos de dados e regras de negócio permanecem inalterados.
- Os identificadores de contrato e as rotas existentes são preservados para não quebrar automações e integrações.
- A validação visual será feita nas larguras 375px, 768px, 1366px e 1920px, nos temas claro e escuro.
- A implementação será incremental, permitindo validação por blocos de tela sem bloquear a entrega global.
- A plataforma continuará sendo uma aplicação web estática servida pelo backend atual, sem introdução de novos frameworks ou infraestrutura de build.
