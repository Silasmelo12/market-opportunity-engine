# Tasks: Correção da Aba Gráfico, Filtragem Inicial por Direção e Persistência de Abas

**Input**: Design documents from `/specs/014-chart-indicators-filter-tab-persistence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefa paralelizada
- **[Story]**: Mapeamento para a História de Usuário (US1, US2, US3)
- Conforme a Constituição, cada tarefa concluída DEVE gerar 1 commit git atômico no formato: `feat(014): <TaskID> <descrição>`

---

## Phase 1: Setup & Scaffolding

**Purpose**: Preparação e verificação do ambiente para testes de UI e integridade.

- [x] T001 Verificar a integridade dos arquivos `src/web/index.html` e `src/web/app.js` antes das alterações.

---

## Phase 2: Foundational (Funções Auxiliares de Roteamento e Filtragem)

**Purpose**: Criação de helpers centrais compartilhados no frontend para roteamento de hash e filtragem de direção.

- [ ] T002 Implementar função `updateSidebarDirectionFilter()` em `src/web/app.js` para ocultar ou exibir `.strategy-group-wrapper` de acordo com `state.activeDirection`.
- [ ] T003 Implementar helpers de mapeamento de abas e hash de URL (`getTabFromHash()`, `getHashFromTab()`) com suporte a `localStorage` em `src/web/app.js`.

---

## Phase 3: User Story 1 - Exibição dos Novos Indicadores na Barra Lateral do Gráfico (Priority: P1) 🎯 MVP

**Goal**: Adicionar os blocos de acordeão de Compra e Venda para os 10 novos indicadores quantitativos na barra lateral esquerda da aba Gráfico (`#tab-terminal`).

**Independent Test**: Abrir a aba Gráfico no navegador e constatar que os blocos "Indicadores Quantitativos de Fundo" e "Indicadores Quantitativos de Topo" estão presentes com todos os 10 checkboxes funcionais.

- [ ] T004 [US1] Adicionar os acordeões `acc-quant-buy` e `acc-quant-sell` com os 10 checkboxes `.strategy-cb` em `src/web/index.html` no container `#strategy-accordion-container`.
- [ ] T005 [US1] Mapear os 10 novos identificadores técnicos no objeto `STRATEGY_ALIASES` em `src/web/app.js` para ativação reativa de plotagem nas velas.

---

## Phase 4: User Story 2 - Filtragem Inicial Correta da Barra Lateral por Direção (Priority: P2)

**Goal**: Garantir que, com o botão "Compra" selecionado, apenas estratégias de compra fiquem visíveis na barra lateral do gráfico na abertura inicial e ao alternar de aba.

**Independent Test**: Carregar a página e clicar na aba Gráfico mantendo "Compra" ativo; verificar que todas as seções de venda estão com a classe `hidden`.

- [ ] T006 [US2] Chamar `updateSidebarDirectionFilter()` dentro de `DOMContentLoaded` em `src/web/app.js` para aplicar o filtro logo no primeiro render.
- [ ] T007 [US2] Chamar `updateSidebarDirectionFilter()` dentro de `switchTab(tabId)` em `src/web/app.js` sempre que a aba Gráfico for ativada.
- [ ] T008 [US2] Conectar `updateSidebarDirectionFilter()` aos cliques dos botões de direção no `#global-direction-selector` em `src/web/app.js`.

---

## Phase 5: User Story 3 - Persistência da Aba Ativa ao Recarregar a Página com F5 (Priority: P3)

**Goal**: Permitir que ao pressionar F5 / recarregar a página, o usuário permaneça exatamente na aba atual (Radar, Gráfico, Simulador ou Playbook).

**Independent Test**: Navegar para `#terminal` ou `#simulator`, pressionar F5 e constatar que a aplicação reabre diretamente na aba selecionada com gráfico ajustado e sem erros.

- [ ] T009 [US3] Atualizar a função `switchTab()` em `src/web/app.js` para gravar o hash correspondente na URL (`window.location.hash`) e persistir no `localStorage`.
- [ ] T010 [US3] Atualizar a inicialização em `DOMContentLoaded` em `src/web/app.js` para ler a hash inicial da URL ou `localStorage` e invocar `switchTab()`.
- [ ] T011 [US3] Adicionar listener de evento `window.addEventListener('hashchange')` em `src/web/app.js` para suporte nativo ao botão Voltar/Avançar do navegador.
- [ ] T012 [US3] Garantir o redimensionamento responsivo do gráfico (`resizeChartResponsive()` e `fitContent()`) com `requestAnimationFrame` quando a página iniciar diretamente na aba Gráfico.

---

## Phase 6: Polish & Quality Gates

**Purpose**: Verificação completa de conformidade com a Constituição, testes de regressão geral e documentação.

- [ ] T013 Executar a suíte de testes automatizados com `python -m pytest tests/ -v` garantindo zero regressões (81 testes passando).
- [ ] T014 Atualizar checklist de requisitos em `specs/014-chart-indicators-filter-tab-persistence/checklists/requirements.md` e validar quickstart.md.
