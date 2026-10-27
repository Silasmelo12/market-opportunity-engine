# Tasks: Layout Profissional e Unificado da Interface Web

**Feature Branch**: `feat/professional-ui-layout`
**Input**: Design documents from `/specs/023-professional-ui-layout/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/ui-layout-contract.md](./contracts/ui-layout-contract.md), [quickstart.md](./quickstart.md)

**Tests**: As tarefas de contrato e E2E abaixo são tarefas de validação para tornar os critérios da spec verificáveis. Não há exigência de TDD; os testes podem ser escritos em paralelo à implementação, mas devem passar antes do fechamento da tarefa correspondente.

**Execution Rules**:
- Cada tarefa concluída deve gerar um commit próprio: `<tipo>(023): <TaskID> <descrição curta>`.
- Se um teste falhar, reverter a alteração antes de continuar.
- Não enfraquecer testes existentes para acomodar mudanças visuais.
- Nenhum arquivo em `src/api/` pode ser alterado.
- Preservar IDs, rotas e funções globais definidos no contrato de UI.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar baseline, ferramentas e contratos antes de tocar na interface.

- [X] T001 Confirmar branch `feat/professional-ui-layout`, working tree e baseline da suíte com `PYTHONPATH=. python -m pytest tests/ -v`; registrar o resultado em `specs/023-professional-ui-layout/quickstart.md`
- [X] T002 [P] Capturar baseline visual das 8 áreas em 375/768/1366/1920px e temas claro/escuro em `/tmp/023-ui-before/`
- [X] T003 [P] Inventariar IDs, rotas e funções globais estáveis contra `specs/023-professional-ui-layout/contracts/ui-layout-contract.md` e registrar lacunas
- [X] T004 [P] Verificar/instalar Playwright e Chromium conforme `tests/e2e/conftest.py` e `requirements-dev.txt`
- [X] T005 [P] Confirmar que `src/api/` está limpo com `git diff --stat -- src/api` antes do início

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar a fundação visual e o harness de validação compartilhado por todas as histórias.

**⚠️ CRITICAL**: Nenhuma user story deve começar antes desta fase.

- [X] T006 Consolidar tokens semânticos de superfícies, bordas, texto, estados financeiros, sombras, raios e espaçamento em `src/web/styles.css`
- [X] T007 Implementar a escala tipográfica e o piso de 11px, incluindo algarismos tabulares e hierarquia display/seção/card/corpo/label em `src/web/styles.css`
- [X] T008 Padronizar botões, campos, selects, badges e estados de foco/hover/disabled em `src/web/styles.css`
- [X] T009 Padronizar cartões, tabelas, acordeões, divisórias e estados vazio/erro/loading em `src/web/styles.css`
- [X] T010 [P] Expandir o sprite SVG de ícones lineares em `src/web/index.html`
- [X] T011 [P] Alterar o tema padrão para claro e preservar persistência/atualização de gráficos em `src/web/app.js`
- [X] T012 [P] Criar contratos de layout (encoding, tipografia, IDs, rotas, temas) em `tests/unit/test_layout_contracts.py`
- [X] T013 [P] Criar testes E2E de invariantes (painel único, temas, tabelas roláveis, teclado) em `tests/e2e/test_ui_layout.py`
- [ ] T014 [P] Atualizar `DESIGN.md` com o mapeamento consolidado de tokens e componentes visuais

**Checkpoint**: Fundação pronta; as histórias podem começar.

---

## Phase 3: User Story 1 - Conteúdo legível e identidade visual consistente (Priority: P1) 🎯 MVP

**Goal**: Eliminar textos corrompidos, aplicar o piso tipográfico e substituir emojis funcionais por ícones consistentes.

**Independent Test**: Percorrer as 8 áreas e verificar zero artefatos de encoding, nenhum texto funcional abaixo de 11px e ícones padronizados.

- [ ] T015 [P] [US1] Corrigir os artefatos de encoding em `src/web/index.html` com reparo controlado `cp1252 → UTF-8`
- [ ] T016 [P] [US1] Corrigir os artefatos de encoding em `src/web/app.js` e `src/web/modules/*.js`
- [ ] T017 [US1] Substituir emojis funcionais por referências ao sprite SVG em `src/web/index.html`
- [ ] T018 [US1] Substituir emojis e strings de ícone em templates dinâmicos de `src/web/app.js` e `src/web/modules/*.js`
- [ ] T019 [US1] Aplicar o piso tipográfico e algarismos tabulares aos textos visíveis de `src/web/index.html`
- [ ] T020 [US1] Normalizar rótulos, formatação numérica e strings visíveis em `src/web/app.js` e `src/web/modules/*.js`
- [ ] T021 [P] [US1] Ativar os contratos de encoding e tipografia em `tests/unit/test_layout_contracts.py`
- [ ] T022 [US1] Validar as 8 áreas nos dois temas e registrar evidências em `specs/023-professional-ui-layout/quickstart.md`

**Checkpoint**: US1 entregue e testável isoladamente (MVP de legibilidade e identidade).

---

## Phase 4: User Story 2 - Navegação clara e previsível (Priority: P2)

**Goal**: Reconstruir o shell com header e subnavegação contextuais, preservando rotas, IDs e histórico.

**Independent Test**: Alternar ambientes, percorrer as 8 subáreas, recarregar, usar voltar/avançar e navegar por teclado sem perder sincronia.

- [ ] T023 [US2] Reestruturar o header em `src/web/index.html`, preservando marca, seletor de ambientes, ações e tema
- [ ] T024 [US2] Reestruturar a subnavegação contextual em `src/web/index.html`, preservando `data-tab` e grupos por ambiente
- [ ] T025 [US2] Remover o header legado oculto de `src/web/index.html` após validar bindings e IDs
- [ ] T026 [P] [US2] Atualizar estilos do shell, offsets sticky, estados ativos e comportamento mobile em `src/web/styles.css`
- [ ] T027 [P] [US2] Ajustar a lógica de navegação e bindings preservados em `src/web/app.js`
- [ ] T028 [US2] Implementar foco visível, ordem de tabulação e ARIA nos controles de ambiente/subnav em `src/web/index.html` e `src/web/app.js`
- [ ] T029 [P] [US2] Adicionar/atualizar testes E2E de navegação em `tests/e2e/test_dashboard_navigation.py`
- [ ] T030 [US2] Validar rotas, precedência URL > storage > padrão, reload, voltar/avançar e painel único; registrar em `specs/023-professional-ui-layout/quickstart.md`

**Checkpoint**: US1 e US2 funcionam independentemente e em conjunto.

---

## Phase 5: User Story 3 - Áreas de carteira com padrão executivo uniforme (Priority: P3)

**Goal**: Unificar Resumo, Posições, Proventos e Evolução Patrimonial sob o mesmo padrão visual.

**Independent Test**: Navegar pelas 4 áreas de carteira nos dois temas e confirmar consistência de cartões, KPIs, gráficos, tabelas e acordeões.

- [ ] T031 [US3] Refatorar o markup de cabeçalho, KPIs, gráficos e acordeões do Resumo em `src/web/index.html`
- [ ] T032 [US3] Refatorar o markup de cabeçalho, tabelas e acordeões de Posições em `src/web/index.html`
- [ ] T033 [US3] Refatorar o markup de Proventos e Evolução Patrimonial em `src/web/index.html`
- [ ] T034 [P] [US3] Implementar estilos unificados das áreas de carteira em `src/web/styles.css`
- [ ] T035 [P] [US3] Implementar a exibição condicional do banner de primeiro uso em `src/web/app.js`
- [ ] T036 [US3] Ajustar renderização, classes e resize/tema dos gráficos do Resumo em `src/web/app.js`
- [ ] T037 [US3] Ajustar classes de renderização de Posições, Proventos e Patrimônio em `src/web/app.js` e `src/web/modules/proventos.js`
- [ ] T038 [P] [US3] Estender contratos de UI das áreas de carteira em `tests/unit/test_layout_contracts.py`
- [ ] T039 [P] [US3] Adicionar testes E2E das áreas de carteira em `tests/e2e/test_ui_layout.py`
- [ ] T040 [US3] Validar as 4 áreas de carteira nos dois temas e registrar evidências em `specs/023-professional-ui-layout/quickstart.md`

**Checkpoint**: As 4 áreas de carteira estão visualmente unificadas e testadas.

---

## Phase 6: User Story 4 - Áreas quantitativas integradas à mesma identidade (Priority: P4)

**Goal**: Migrar Radar, Gráfico, Simulador e Playbook para o mesmo sistema visual das áreas de carteira.

**Independent Test**: Percorrer as 4 áreas quantitativas nos dois temas e confirmar ausência de resíduos da estética escura legada.

- [ ] T041 [US4] Refatorar o markup do Radar (filtros, tabela, paginação, ações) em `src/web/index.html`
- [ ] T042 [US4] Refatorar o markup do Gráfico (sidebar, controles, retorno contextual) em `src/web/index.html`
- [ ] T043 [US4] Refatorar o markup do Simulador (formulários, grids, resultados) em `src/web/index.html`
- [ ] T044 [US4] Refatorar o markup do Playbook (grupos, blocos, destaques) em `src/web/index.html`
- [ ] T045 [P] [US4] Implementar estilos unificados das áreas quantitativas em `src/web/styles.css`
- [ ] T046 [P] [US4] Atualizar classes de renderização do Radar em `src/web/app.js`
- [ ] T047 [US4] Atualizar classes dos controles e do gráfico TradingView em `src/web/app.js`
- [ ] T048 [US4] Atualizar classes de renderização do Simulador e Playbook em `src/web/app.js`
- [ ] T049 [US4] Remover os blocos de override de tema legado de `src/web/styles.css` após a migração completa
- [ ] T050 [P] [US4] Adicionar testes E2E das áreas quantitativas em `tests/e2e/test_ui_layout.py`
- [ ] T051 [US4] Validar as 4 áreas quantitativas nos dois temas e registrar evidências em `specs/023-professional-ui-layout/quickstart.md`

**Checkpoint**: As 8 áreas compartilham a mesma identidade visual.

---

## Phase 7: User Story 5 - Experiência responsiva e acessível (Priority: P5)

**Goal**: Garantir usabilidade em 375/768/1366/1920px, teclado, zoom, contraste e movimento reduzido.

**Independent Test**: Executar a matriz de 64 verificações e os cenários de teclado, zoom e movimento reduzido sem falhas.

- [ ] T052 [US5] Adicionar wrappers roláveis e classes responsivas para tabelas/grids largos em `src/web/index.html`
- [ ] T053 [US5] Implementar breakpoints, gutters, grids e contenção de overflow em `src/web/styles.css`
- [ ] T054 [US5] Implementar foco visível, ARIA, contraste e `prefers-reduced-motion` em `src/web/index.html`, `src/web/styles.css` e `src/web/app.js`
- [ ] T055 [US5] Garantir resize de Plotly/TradingView na abertura de área, troca de tema e redimensionamento em `src/web/app.js`
- [ ] T056 [P] [US5] Adicionar testes E2E de teclado, foco e acessibilidade em `tests/e2e/test_ui_layout.py`
- [ ] T057 [P] [US5] Adicionar testes de responsividade estrutural e overflow em `tests/unit/test_layout_contracts.py`
- [ ] T058 [US5] Executar e registrar as 64 verificações visuais em `specs/023-professional-ui-layout/quickstart.md`
- [ ] T059 [US5] Validar zoom de 200% e movimento reduzido e registrar o resultado em `specs/023-professional-ui-layout/quickstart.md`

**Checkpoint**: As 8 áreas estão responsivas e acessíveis nos dois temas.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Auditoria final, limpeza e aprovação da entrega.

- [ ] T060 [P] Consolidar `DESIGN.md` com os padrões finais e remover referências obsoletas
- [ ] T061 [P] Confirmar que `src/api/` permanece intocado com `git diff --stat -- src/api`
- [ ] T062 [P] Auditar encoding, piso tipográfico e IDs duplicados em `src/web/index.html`, `src/web/app.js` e `src/web/modules/*.js`
- [ ] T063 Executar a suíte completa `PYTHONPATH=. python -m pytest tests/ -v` e registrar o resultado final em `specs/023-professional-ui-layout/quickstart.md`
- [ ] T064 Validar desempenho percebido em troca de área, troca de tema e resize de gráficos em `src/web/app.js` e `src/web/styles.css`
- [ ] T065 Revisar e aprovar as 64 verificações visuais finais em `specs/023-professional-ui-layout/quickstart.md`
- [ ] T066 Revisar o diff final de `src/web/`, remover CSS/classes mortas e executar `git diff --check`
- [ ] T067 Auditar que cada tarefa concluída gerou um commit próprio no formato `<tipo>(023): <TaskID> <descrição>` em `specs/023-professional-ui-layout/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; pode começar imediatamente.
- **Foundational (Phase 2)**: depende do Setup e **bloqueia todas as user stories**.
- **User Stories (Phases 3–7)**: dependem da Fundação.
  - US1 (P1) pode começar assim que a Fundação terminar.
  - US2 (P2) pode começar em paralelo com US1, pois atua principalmente no shell.
  - US3 (P3) e US4 (P4) dependem da Fundação e podem avançar em paralelo entre si.
  - US5 (P5) depende de US3 e US4 para validar a matriz completa das 8 áreas.
- **Polish (Phase 8)**: depende de todas as histórias concluídas.

### User Story Dependencies

- **US1 (P1)**: independente; entrega o MVP de legibilidade e identidade.
- **US2 (P2)**: independente de US1; integra-se ao shell.
- **US3 (P3)**: independente de US2; usa a Fundação e o shell existente.
- **US4 (P4)**: independente de US3; usa a Fundação e o shell existente.
- **US5 (P5)**: depende de US3 e US4 para cobrir as 8 áreas; pode adiantar contratos de teclado/responsividade.

### Within Each User Story

- Markup antes de estilos.
- Estilos antes de ajustes de renderização dinâmica.
- Implementação antes dos testes de contrato/E2E.
- Validação visual depois de testes automatizados.
- Cada tarefa deve ser commitada individualmente.

### Parallel Opportunities

- Setup: T002–T005 podem rodar em paralelo após T001.
- Fundação: T010–T014 podem rodar em paralelo com T006–T009 por atuarem em arquivos diferentes.
- US1: T015 e T016 podem rodar em paralelo (HTML e JS).
- US2: T026 e T027 podem rodar em paralelo após o markup do shell.
- US3: T034 e T035 podem rodar em paralelo após o markup das áreas de carteira.
- US3: T038 e T039 podem rodar em paralelo (unitário e E2E).
- US4: T045 e T046 podem rodar em paralelo após o markup do Radar.
- US5: T056 e T057 podem rodar em paralelo (E2E e unitário).
- Polish: T060, T061 e T062 podem rodar em paralelo.

---

## Parallel Example: User Story 1

```text
Task: "T015 Corrigir encoding em src/web/index.html"
Task: "T016 Corrigir encoding em src/web/app.js e src/web/modules/*.js"
```

## Parallel Example: User Story 2

```text
Task: "T026 Atualizar estilos do shell em src/web/styles.css"
Task: "T027 Ajustar navegação e bindings em src/web/app.js"
```

## Parallel Example: User Story 3

```text
Task: "T034 Implementar estilos das áreas de carteira em src/web/styles.css"
Task: "T035 Implementar banner condicional em src/web/app.js"
```

## Parallel Example: User Story 4

```text
Task: "T045 Implementar estilos quantitativos em src/web/styles.css"
Task: "T046 Atualizar classes de renderização do Radar em src/web/app.js"
```

## Parallel Example: User Story 5

```text
Task: "T056 Adicionar testes E2E de acessibilidade em tests/e2e/test_ui_layout.py"
Task: "T057 Adicionar testes de responsividade em tests/unit/test_layout_contracts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Setup).
2. Concluir Phase 2 (Foundational).
3. Concluir Phase 3 (US1).
4. **STOP e VALIDAR**: executar T021 e T022, confirmar zero encoding e piso tipográfico.
5. Demonstrar o MVP de legibilidade e identidade visual.

### Incremental Delivery

1. Fundação + US1 → validar MVP.
2. US2 → validar navegação e shell.
3. US3 → validar as áreas de carteira.
4. US4 → validar as áreas quantitativas.
5. US5 → validar responsividade e acessibilidade em todas as áreas.
6. Polish → auditoria final e aprovação da matriz de 64 verificações.

### Parallel Team Strategy

Com mais de um desenvolvedor:

1. Time conclui Setup + Fundação em conjunto.
2. Após a Fundação:
   - Dev A: US1 (conteúdo e identidade).
   - Dev B: US2 (shell e navegação).
   - Dev C: US3 (carteira).
   - Dev D: US4 (quantitativo).
3. US5 inicia após US3/US4 para cobrir a matriz completa.
4. Polish é executado em conjunto no final.

---

## Notes

- `[P]` indica tarefas paralelizáveis em arquivos diferentes, sem dependência de tarefa incompleta.
- `[USn]` mapeia a tarefa à user story correspondente.
- A matriz de 64 verificações é composta por 8 áreas × 4 larguras × 2 temas.
- Nenhuma tarefa pode alterar `src/api/`, cálculos financeiros, rotas existentes ou IDs estáveis.
- Commits por tarefa são obrigatórios pela constituição do projeto.
- Parar em cada checkpoint para validar a história de forma independente.
