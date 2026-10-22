# Tasks: Refatoração da Tabela do Radar

**Input**: Design documents from `/specs/015-radar-table-ux-refactor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefa paralelizada
- **[Story]**: Mapeamento para a História de Usuário (US1, US2, US3)
- Conforme a Constituição, cada tarefa concluída DEVE gerar 1 commit git atômico no formato: `feat(015): <TaskID> <descrição>`

---

## Phase 1: Setup & Scaffolding

**Purpose**: Verificação do layout atual da tabela do radar e preparação das estruturas no frontend.

- [x] T001 Verificar a integridade das referências da tabela do radar em `src/web/index.html` e `src/web/app.js`.

---

## Phase 2: Foundational (Estrutura de Estado e Ordenação no Frontend)

**Purpose**: Adição do estado e métodos de ordenação na Single Page Application.

- [x] T002 Adicionar `radarSortField` e `radarSortOrder` ao `window.appState` em `src/web/app.js`.
- [x] T003 Implementar função auxiliar `sortRadarItems(items)` em `src/web/app.js` para ordenar por `historical_n` ou `historical_win_rate`.

---

## Phase 3: User Story 1 - Remoção de Colunas Redundantes (Priority: P1) 🎯 MVP

**Goal**: Remover as colunas "Categoria", "Preço Atual" e "Ação" do cabeçalho e do corpo da tabela do Radar.

**Independent Test**: Carregar a aba Radar no navegador e constatar que a tabela exibe apenas as colunas essenciais, e o clique no ativo continua navegando para o gráfico.

- [x] T004 [US1] Atualizar o `<thead>` da tabela em `src/web/index.html` removendo Categoria, Preço Atual e Ação (redução de 11 para 8 colunas).
- [x] T005 [US1] Atualizar `renderRadarTable()` em `src/web/app.js` removendo as células de Categoria, Preço Atual e botão Ação, ajustando o `colspan="8"` das mensagens vazias.

---

## Phase 4: User Story 2 - Semáforo Minimalista e Direção Compacta (Priority: P2)

**Goal**: Renderizar o semáforo de timing como bolinha colorida com tooltip e a direção com inicial compacta ("C" ou "V").

**Independent Test**: Observar as colunas Dir e Timing no Radar, verificando a bolinha colorida (com texto exibido no hover) e os badges compactos "C" e "V".

- [x] T006 [US2] Atualizar a renderização da coluna Direção em `renderRadarTable()` (`src/web/app.js`) para badge circular com inicial `"C"` ou `"V"` e tooltip descritivo.
- [x] T007 [US2] Atualizar a renderização da coluna Semáforo em `renderRadarTable()` (`src/web/app.js`) para círculo colorido minimalista de 12px com sombra suave e atributo `title` no hover.

---

## Phase 5: User Story 3 - Desmembramento do Histórico e Ordenação Interativa (Priority: P3)

**Goal**: Separar a métrica em "Qtd Sinais" e "Win Rate (%)" com cabeçalhos ordenáveis clicáveis.

**Independent Test**: Clicar nos cabeçalhos "Qtd Sinais" e "Win Rate (%)" alternando ordenação crescente e decrescente com feedback visual instantâneo.

- [x] T008 [US3] Adicionar IDs e indicadores de ordenação nos cabeçalhos `#th-sort-n` e `#th-sort-winrate` no `src/web/index.html`.
- [x] T009 [US3] Atualizar a renderização das linhas em `src/web/app.js` gerando duas células separadas: uma para `historical_n` e outra para `historical_win_rate`.
- [x] T010 [US3] Configurar listeners de clique nos cabeçalhos em `setupRadarTableSorting()` em `src/web/app.js` alternando `radarSortOrder` e atualizando os ícones.
- [x] T011 [US3] Integrar a ordenação antes da renderização das linhas em `renderRadarTable()` no `src/web/app.js`.

---

## Phase 6: Polish & Quality Gates

**Purpose**: Verificação de integridade, testes de regressão e validação.

- [x] T012 Executar suíte de testes completa com `python -m pytest tests/ -v` garantindo 100% de aprovação (82 testes).
- [x] T013 Atualizar checklist de requisitos em `specs/015-radar-table-ux-refactor/checklists/requirements.md` e validar quickstart.md.
