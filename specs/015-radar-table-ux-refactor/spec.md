# Feature Specification: Refatoração da Tabela do Radar com Ocultação de Colunas, Semáforo Minimalista, Direção Compacta e Ordenação de Histórico por Quantidade e Win Rate

**Feature Branch**: `015-radar-table-ux-refactor`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Refatoracao da Tabela do Radar com Ocultacao de Colunas Semaforo Minimalista Direcao Compacta e Ordenacao de Historico por Quantidade e Win Rate"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tabela Simplificada e Limpa sem Colunas Redundantes (Priority: P1)

Como investidor ou analista, quero uma tabela no Radar de Oportunidades sem poluição visual desnecessária (sem as colunas "Categoria", "Preço Atual" e "Ação"), mantendo a largura e legibilidade confortáveis em monitores de qualquer resolução, com o clique no nome do ativo abrindo diretamente a análise.

**Why this priority**: A tabela atual possui 11 colunas com informações redundantes (como "Ação", visto que o próprio nome do ativo já é clicável, e "Categoria", já filtrada nas pílulas superiores). A limpeza visual é a base da usabilidade refinada.

**Independent Test**: Abrir o Radar e constatar que o cabeçalho e as linhas da tabela não contêm mais as colunas Categoria, Preço Atual e Ação, e que o clique no nome do ativo continua funcionando normalmente para navegar até a aba Gráfico.

**Acceptance Scenarios**:
1. **Given** a aba Radar aberta, **When** o usuário examina o cabeçalho da tabela, **Then** as colunas "Categoria", "Preço Atual" e "Ação" não estão presentes.
2. **Given** uma linha de ativo na tabela, **When** o usuário clica sobre o nome ou código do ativo, **Then** a aplicação abre a aba Gráfico com a análise carregada.

---

### User Story 2 - Semáforo de Timing Minimalista e Direção Compacta (Priority: P2)

Como usuário, quero visualizar o semáforo de timing através de uma bolinha colorida minimalista com tooltip informativo no hover e a direção representada apenas pelas iniciais estilizadas ("C" para Compra e "V" para Venda), permitindo leitura rápida e limpa dos sinais.

**Why this priority**: Substitui caixas de texto compridas por representações visuais compactas, economizando espaço horizontal e acelerando a identificação visual de oportunidades ideais.

**Independent Test**: Observar as colunas de "Direção" e "Semáforo" no Radar, verificando que a direção exibe um badge compacto com "C" (verde) ou "V" (vermelho), e o semáforo exibe uma bolinha colorida que revela a descrição textual ao passar o mouse.

**Acceptance Scenarios**:
1. **Given** um ativo com oportunidade de compra, **When** visualizado no Radar, **Then** a coluna de direção exibe um badge compacto com a letra "C" em verde esmeralda.
2. **Given** um ativo com oportunidade de venda, **When** visualizado no Radar, **Then** a coluna de direção exibe um badge compacto com a letra "V" em rosa/vermelho.
3. **Given** a coluna Semáforo, **When** o usuário passa o mouse sobre a bolinha verde, amarela ou vermelha, **Then** um tooltip nativo exibe o status de timing (ex: "Ideal / Reteste Válido", "Estendido", "Atrasado").

---

### User Story 3 - Separação da Coluna Histórico em Quantidade e Win Rate com Ordenação Interativa (Priority: P3)

Como analista quantitativo, quero ver o histórico separado em duas colunas distintas: "Qtd Sinais" (N) e "Win Rate (%)", com cabeçalhos clicáveis que permitam ordenar os ativos de forma crescente ou decrescente para priorizar estratégias com maior amostragem ou maior assertividade.

**Why this priority**: Permite ranquear instantaneamente na tabela quais oportunidades possuem os maiores índices de assertividade estatística ou a maior base histórica comprovada.

**Independent Test**: Clicar no cabeçalho "Qtd Sinais" e verificar a ordenação das linhas da tabela por quantidade de sinais. Clicar em "Win Rate (%)" e verificar a ordenação pela assertividade percentual, alternando entre ordem ascendente e descendente com ícone visual.

**Acceptance Scenarios**:
1. **Given** a tabela do Radar carregada, **When** o usuário visualiza as métricas históricas, **Then** elas estão separadas nas colunas "Qtd Sinais" e "Win Rate (%)".
2. **Given** um clique no cabeçalho "Win Rate (%)", **When** a ordenação é acionada, **Then** a tabela reordena instantaneamente as linhas em ordem decrescente de taxa de acerto (do maior para o menor win rate), exibindo uma seta $\blacktriangledown$.
3. **Given** um segundo clique no cabeçalho "Win Rate (%)", **When** acionado, **Then** a ordem inverte para crescente ($\blacktriangle$).
4. **Given** um clique no cabeçalho "Qtd Sinais", **When** acionado, **Then** as linhas são reordenadas pelo número de entradas históricas $N$.

---

### Edge Cases

- **Ativos com Zero Sinais Históricos ou Win Rate Nulo**: Se um ativo tiver $N=0$ ou taxa de acerto indefinida, a ordenação deve tratá-lo graciosamente, colocando-o no final da lista decrescente sem gerar erros de JavaScript.
- **Paginação do Radar e Troca de Categorias**: Ao alternar de página ou trocar a pílula de categoria (ex: Ações, FIIs, Cripto), a ordenação selecionada pelo usuário pelo cabeçalho deve ser preservada ou aplicada aos novos itens exibidos.
- **Alinhamento Numérico**: Os valores numéricos das colunas ordenáveis (Qtd Sinais e Win Rate) devem estar alinhados de forma consistente com fontes tabulares/mono para facilitar a comparação visual rápida.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O cabeçalho da tabela do Radar (`src/web/index.html`) e o template de linhas (`src/web/app.js`) DEVEM remover integralmente as colunas "Categoria", "Preço Atual" e "Ação".
- **FR-002**: A coluna "Direção" DEVE exibir um badge compacto contendo exclusivamente a letra `"C"` para compras (`BUY`) e a letra `"V"` para vendas (`SELL`), acompanhado de tooltip descritivo ("Compra" ou "Venda") no atributo `title`.
- **FR-003**: A coluna "Semáforo de Timing" DEVE renderizar exclusivamente um indicador circular minimalista (`w-3 h-3 rounded-full`) centralizado, com cores institucionais reativas:
  - Verde (`bg-emerald-400` / `ring-2 ring-emerald-500/30`) para `IDEAL`;
  - Amarelo (`bg-amber-400` / `ring-2 ring-amber-500/30`) para `EXTENDED`;
  - Vermelho (`bg-rose-400` / `ring-2 ring-rose-500/30`) para `LATE` ou outros.
  - O elemento DEVE conter o atributo `title` preenchido com a descrição textual do timing (`item.timing_label`).
- **FR-004**: A métrica histórica DEVE ser desmembrada em duas colunas independentes no cabeçalho e no corpo da tabela:
  1. `"Qtd Sinais"` (valor numérico inteiro, ex: `14`);
  2. `"Win Rate"` (valor percentual formatado, ex: `74.5%`).
- **FR-005**: Os cabeçalhos das colunas "Qtd Sinais" e "Win Rate" DEVEM ser interativos (com cursor pointer e ícone de seta de ordenação), permitindo alternar a ordenação entre decrescente ($\blacktriangledown$) e crescente ($\blacktriangle$).
- **FR-006**: O estado de ordenação (`radarSortField` e `radarSortOrder`) DEVE ser mantido no estado do cliente (`state`), executando a ordenação das linhas com latência de 0ms sem necessidade de recarregar a API.
- **FR-007**: A mensagem de fallback ("Nenhuma oportunidade encontrada") DEVE atualizar seu `colspan` para refletir exatamente o novo número total de colunas da tabela (8 colunas no total).

### Key Entities

- **RadarTableColumnLayout**: Nova estrutura de 8 colunas da tabela:
  1. `Ativo` (Nome amigável + Ticker);
  2. `Direção` (`C` ou `V`);
  3. `Estratégia Confirmada`;
  4. `Status do Setup`;
  5. `Semáforo` (Bolinha colorida com tooltip);
  6. `Distância (%)`;
  7. `Qtd Sinais` (Ordenável por $N$);
  8. `Win Rate` (Ordenável por %).
- **RadarSortState**: Estado com `field` (`"historical_n"` ou `"historical_win_rate"`) e `direction` (`"desc"` ou `"asc"`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Redução do número total de colunas da tabela de 11 para exatamente 8 colunas, eliminando 100% dos elementos das colunas Categoria, Preço Atual e Ação.
- **SC-002**: A direção deve ocupar menos de 40px de largura horizontal com as letras compactas "C" ou "V".
- **SC-003**: O semáforo deve ser visualmente representado por um círculo de 12px de diâmetro, exibindo o texto do timing exclusivamente ao passar o cursor do mouse.
- **SC-004**: Clicar nos cabeçalhos "Qtd Sinais" ou "Win Rate" deve ordenar a lista de itens da página atual em menos de 10ms.
- **SC-005**: 100% dos 82 testes automatizados continuam passando sem falhas.

---

## Assumptions

- O clique sobre o bloco do ativo (Nome + Ticker) continua disparando a ação de navegação para a aba Gráfico com o ativo e estratégia selecionados.
- A ordenação das colunas opera sobre os itens da página corrente ou conjunto carregado no cliente, mantendo total responsividade e performance instantânea.
