# Tasks: Redesign da Interface Web Estilo Investidor10

**Branch**: `021-investidor10-ui`
**Spec**: [specs/021-investidor10-ui-redesign/spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/021-investidor10-ui-redesign/spec.md)
**Plan**: [specs/021-investidor10-ui-redesign/plan.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/021-investidor10-ui-redesign/plan.md)
**Status**: Fase 1 Concluida | Fase 2A Pronta para Implementacao Incremental | Fase 2B Planejada

---

## Regras de Execucao & Condicoes de Parada
- Nenhuma tarefa da Fase 2A deve alterar a tela Visao Geral (`#tab-overview`) homologada na Fase 1.
- `src/app.py` e `src/ui/` permanecem **intocados**.
- Nao realizar redesign visual de tabelas ou componentes internos do Radar, Simulador ou Playbook.
- Cada tarefa so e considerada concluida quando seus criterios de validacao forem verificados via comando nao destrutivo.

---

## Lista Sequencial de Tarefas

### Bloco A a D: Fase 1 — Tela-Piloto Visao Geral (Concluida & Homologada)

- [x] **T001: Mapear Tokens Semanticos para Suporte Dual (Claro/Escuro)**
- [x] **T002: Estilizacao dos 4 Cards de KPI com Alinhamento Numerico**
- [x] **T003: Refatoracao Semantica e Atualizacao dos Rotulos dos 4 KPIs**
- [x] **T004: Implementacao do Card Hero de Boas-Vindas para Estado Vazio**
- [x] **T005: Tratamento de Proventos Parciais e Calculo de Media Dinamica**
- [x] **T006: Tratamento e Sinalizacao de Cotacoes Indisponiveis (Fallback)**
- [x] **T007: Adaptacao Dinamica dos Graficos Plotly para Temas Claro e Escuro**
- [x] **T008: Execucao da Suite E2E de Navegacao e Responsividade**
- [x] **T009: Execucao da Suite Completa de Testes Unitarios de Regressao**

---

### Bloco E: Fase 2A — Modelo de Rotas, Precedencia e Estado em `src/web/app.js`

- [ ] **T010: Implementar Mapeamento Unificado de Rotas e Precedencia de Navegacao**
  - *Arquivo*: `src/web/app.js`
  - *Acao*:
    1. Criar estrutura de configuracao de rotas mapeando ambientes (`carteira` e `quant`), subabas e IDs de painel de destino.
    2. Implementar a funcao `resolveCurrentRoute()` com a precedencia estrita:
       - 1º: `window.location.hash` se valido;
       - 2º: `localStorage.getItem('mo_active_route')` se nao houver hash;
       - 3º: Rota default `carteira/resumo`.
    3. Manter aliases para hashes legados (`#resumo`, `#posicoes`, `#radar`, etc.).
  - *Validacao*: `node --check src/web/app.js`.

- [ ] **T011: Implementar Sincronizacao Bidirecional de Historico (`popstate` / `hashchange`)**
  - *Arquivo*: `src/web/app.js`
  - *Acao*:
    1. Adicionar listeners para eventos `hashchange` e `popstate`.
    2. Garantir que a navegacao via botoes Voltar e Avancar do navegador atualiza simultaneamente o ambiente, a subnavegacao e o painel visivel.
    3. Ao trocar de aba por clique do usuario, atualizar a URL com `history.replaceState` ou hash correspondente sem provocar scroll jump.
  - *Validacao*: Teste interativo de recarregamento e historico via script de inspecao.

---

### Bloco F: Fase 2A — Estrutura HTML dos Dois Ambientes e Subnavegacao em `src/web/index.html`

- [ ] **T012: Inserir Seletor de Ambientes no Topo (`#global-pillar-selector`)**
  - *Arquivo*: `src/web/index.html`
  - *Acao*:
    1. Inserir no cabecalho ou logo abaixo dele a barra com 2 botoes de ambiente:
       - `#pillar-btn-carteira`: "Minha Carteira" (icone de carteira/briefcase);
       - `#pillar-btn-quant`: "Analise Quantitativa" (icone de terminal/grafico).
    2. Configurar atributos ARIA (`role="tab"`, `aria-selected`, `aria-controls`).
  - *Validacao*: Inspecao DOM: ambos os botoes presentes e acessiveis via teclado.

- [ ] **T013: Estruturar as Duas Barras de Subnavegacao Contextuais**
  - *Arquivo*: `src/web/index.html`
  - *Acao*:
    1. Substituir a subnav plana unica por dois contêineres contextuais:
       - `#subnav-pillar-carteira`: Botoes para "Visao Geral", "Posicoes & Custodia", "Proventos & Renda" e "Evolucao Patrimonial".
       - `#subnav-pillar-quant`: Botoes para "Radar de Mercado", "Grafico Interativo", "Simulador & Backtest" e "Playbook".
    2. Preservar atributos `data-tab` e `data-legacy-id` para compatibilidade com seletores existentes.
  - *Validacao*: Varredura DOM confirmando a existencia dos botoes contextuais e preservacao de IDs de painel.

- [ ] **T014: Garantir Unicidade de IDs e Preservacao dos Paineis Existentes**
  - *Arquivo*: `src/web/index.html`
  - *Acao*:
    1. Validar que nenhum ID foi duplicado (`#tab-overview`, `#tab-portfolio`, `#tab-pane-proventos`, `#tab-pane-patrimonio`, `#tab-pane-radar`, `#tab-terminal`, `#tab-simulator`, `#tab-playbook`).
    2. Garantir que o link "Ver posicoes" na Visao Geral aponte para a subaba de Posicoes do pilar Carteira.
    3. Adicionar link "Ver serie completa" no card de Aportes da Visao Geral direcionando para a subaba de Evolucao Patrimonial.
  - *Validacao*: `git diff --check` e script de contagem de IDs no DOM (zero IDs duplicados).

---

### Bloco G: Fase 2A — Estilizacao e Tokens Visuais em `src/web/styles.css`

- [ ] **T015: Estilos dos Ambientes e Subnavegacao nos Modos Claro e Escuro**
  - *Arquivo*: `src/web/styles.css`
  - *Acao*:
    1. Criar regras CSS para o seletor de pilares (`.pillar-nav-btn`) com indicador de estado ativo, hover suave e transicao.
    2. Estilizar as barras de subnavegacao contextuais (`.subnav-contextual-bar`) mantendo consistencia com o [DESIGN.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/DESIGN.md).
    3. Garantir contraste adequado em `:root` (fundo claro) e `[data-theme="dark"]` (fundo escuro).
  - *Validacao*: Inspecao visual e validacao de contraste WCAG AA.

- [ ] **T016: Estados de Foco e Acessibilidade por Teclado**
  - *Arquivo*: `src/web/styles.css`
  - *Acao*:
    1. Adicionar estilo de foco visivel (`:focus-visible`) para todos os botoes de pilar e subabas.
    2. Garantir que a navegacao por tabulacao (`Tab` / `Shift+Tab`) e ativacao por `Enter`/`Space` funcionem sem perda visual de foco.
  - *Validacao*: Teste automatizado via Playwright verificando foco visivel.

---

### Bloco H: Fase 2A — Handlers de Transicao e Redimensionamento em `src/web/app.js`

- [ ] **T017: Redimensionamento Automatico de Graficos na Alternancia de Painel**
  - *Arquivo*: `src/web/app.js`
  - *Acao*:
    1. Na funcao de exibicao de painel, ao ativar `#tab-terminal`, disparar `resizeChartResponsive()` e `state.chart.timeScale().fitContent()` em `setTimeout(..., 50)`.
    2. Ao ativar `#tab-overview`, `#tab-pane-proventos`, `#tab-pane-patrimonio` ou `#tab-simulator`, disparar `Plotly.relayout(container, { autosize: true })`.
  - *Validacao*: Teste E2E Playwright validando que os elementos `<svg>` ou canvas possuem largura > 0px e nao colapsam apos a troca de aba.

- [ ] **T018: Garantir Visibilidade Exclusiva de Exatamente 1 Painel por Vez**
  - *Arquivo*: `src/web/app.js`
  - *Acao*:
    1. Assegurar que ao alternar de aba, todos os demais `.tab-view` e `.tab-pane` recebam a classe `hidden`.
    2. Evitar vazamento de conteudo ou multiplos paineis simultaneos no DOM.
  - *Validacao*: Teste de assertiva `document.querySelectorAll('.tab-view:not(.hidden)').length === 1`.

---

### Bloco I: Fase 2A — Suite de Testes Automatizados E2E e Validacao Final

- [ ] **T019: Atualizar e Expandir Testes E2E em `tests/e2e/test_dashboard_navigation.py`**
  - *Arquivo*: `tests/e2e/test_dashboard_navigation.py`
  - *Acao*:
    1. Atualizar o teste de navegacao para validar a alternancia entre os 2 pilares.
    2. Validar que as 8 subabas contextuais abrem seus respectivos paineis.
    3. Testar a precedencia de hash (navegando com hash explicitamente diferente da preferencia salva).
    4. Testar o comportamento do refresh (F5) e dos botoes Voltar/Avancar.
    5. Preservar o isolamento do baseline separado de `test_proventos_layout.py`.
  - *Validacao*: `python -m pytest tests/e2e/test_dashboard_navigation.py -v` (todos aprovados).

- [ ] **T020: Validacao de Regressao Geral da Aplicacao**
  - *Comando*:
    1. `node --check src/web/app.js`
    2. `git diff --check`
    3. `python -m pytest tests/unit -v` (95 aprovados, 2 skipped)
    4. `python -m pytest tests/e2e/test_dashboard_navigation.py -v` (todos aprovados)
  - *Validacao*: Zero regressoes em APIs, simulador, radar, b3_parser ou dashboard.

---

### Backlog Planejado: Fase 2B — Integracao Contextual entre Telas (Trabalho Separado)

- [x] **T021: Despacho Contextual de Ativo da Carteira para o Grafico (`openChartForHolding` / `navigateToRoute`)**
  - *Status*: Concluído na Etapa 1 da Fase 2B com banner contextual, ticker canônico e histórico resiliente.
- [x] **T022: Botao de Acao nos Acordeoes e Tabela de Custodia da Carteira**
  - *Status*: Concluído na Etapa 1 da Fase 2B na tabela de posições (`.btn-holding-open-chart`).
- [x] **T023: Botao de Acao Direta no Radar para o Grafico Interativo (`openChartFromRadar`)**
  - *Status*: Concluído na Etapa 2 da Fase 2B com coluna de Ação explícita (`.btn-radar-open-chart`), clique no ticker, banner `← Voltar para Radar`, scroll restaurado e isolamento estrito do simulador.
- [ ] **T024: Ancoras e Deep-linking para o Playbook**
  - *Dependencia*: Atribuir IDs unicos para cada uma das 48 estrategias em `tab-playbook`.
- [ ] **T025: Botoes de Ajuda Contextual `(?)` para Estrategias no Radar e no Grafico**
  - *Dependencia*: Conectar tags de padroes aos respectivos cards explicativos no Playbook.


---

### Bloco J: Fase 3A — Definição da Identidade Visual, Auditoria e Especificação de Tokens

- [x] **T026: Auditoria Técnica com Impeccable e Catalogação de Inconsistências Visuais**
  - *Arquivo*: `specs/021-investidor10-ui-redesign/spec.md`
  - *Ação*: Executar varredura técnica (`impeccable detect src/web`), catalogando os 96 anti-patterns identificados (dissonância de superfícies claras/escuras, 50+ textos com `10px` abaixo do piso de 11px, cartões aninhados, e botões sem anel de foco).
  - *Status*: Concluído na Fase 3A.

- [x] **T027: Definição dos Tokens Reutilizáveis de Design System em `DESIGN.md`**
  - *Arquivo*: `DESIGN.md`
  - *Ação*: Formalizar os tokens semânticos completos para Superfícies (`--canvas`, `--surface`, `--surface-subtle`), Bordas (`--border`, `--border-strong`), Tipografia (`--text-main`, `--text-muted`, `--text-subtle`), Acentos e Rentabilidade (`--primary`, `--success`, `--danger`, `--warning`), Raio e Sombras nos modos Claro e Escuro.
  - *Status*: Concluído na Fase 3A.

- [x] **T028: Especificação de Critérios de Aceitação e Arquitetura de Componentes**
  - *Arquivo*: `specs/021-investidor10-ui-redesign/spec.md` e `plan.md`
  - *Ação*: Integrar as diretrizes visuais aprovadas das referências *JSE Stock Radar* e *Market Insight*, formalizando critérios AC-3A-01 a AC-3A-07 e plano de migração top-down.
  - *Status*: Concluído na Fase 3A.

---

### Bloco K: Fase 3B — Planejamento Sequencial de Implementação do Redesign (Aguardando Aprovação)

> [!IMPORTANT]
> As tarefas abaixo compõem a execução técnica futura da Fase 3B. Nenhuma alteração de código ou estilo deve ser iniciada antes da revisão e autorização expressa do usuário.

- [x] **T029: [Prioridade 1 - Fundações] Saneamento de Tokens CSS Globais e Tailwind Config**
  - *Arquivos*: `src/web/styles.css`, `src/web/index.html`
  - *Ação*:
    1. Implementar o bloco completo de tokens CSS em `:root` e `[data-theme="dark"]` de acordo com o `DESIGN.md`.
    2. Atualizar o `tailwind.config` em `index.html` para consumir as variáveis CSS semânticas (`var(--canvas)`, `var(--surface)`, `var(--border)`, `var(--primary)`), eliminando hexadecimais estáticos dark-only.
  - *Validação*: `node --check src/web/app.js`, `git diff --check`, inspeção visual de herança de variáveis.

- [x] **T030: [Prioridade 1 - Componentes] Padronização de Cartões e Remoção de Aninhamentos (`nested-cards`)**
  - *Arquivos*: `src/web/styles.css`, `src/web/index.html`
  - *Ação*:
    1. Criar classe utilitária unificada `.card-surface` com fundo `var(--surface)`, borda `1px solid var(--border)` e raio `12px` (`--radius-lg`).
    2. Eliminar contêineres `.card-surface` aninhados dentro de outros cards nos painéis de Radar, Simulador e Playbook, substituindo por divisórias horizontais sutis e espaçamentos rítmicos.
  - *Validação*: Reexecução do `impeccable detect` confirmando eliminação dos apontamentos de `nested-cards`.

- [x] **T031: [Prioridade 1 - Componentes] Padronização de Tabelas e Aplicação do Piso Tipográfico de 11px**
  - *Arquivos*: `src/web/styles.css`, `src/web/index.html`, `src/web/app.js`
  - *Ação*:
    1. Padronizar `.table-standard` para as tabelas do Radar, Custódia, Simulador e Múltiplos.
    2. Elevar todos os cabeçalhos e metadados de `10px` (`text-[10px]`) para no mínimo `11px` (`text-[11px]` / `0.6875rem`) com peso `font-semibold` e `uppercase`.
    3. Garantir números tabulares em `font-mono` alinhados à direita e formatação `pt-BR`.
  - *Validação*: Reexecução do `impeccable detect` confirmando eliminação dos apontamentos de `undersized-ui-text`.

- [x] **T032: [Prioridade 1 - Acessibilidade] Padronização de Botões, Badges e Foco Visível (`:focus-visible`)**
  - *Arquivos*: `src/web/styles.css`, `src/web/index.html`
  - *Ação*:
    1. Padronizar `.btn-primary` (fundo ciano/azul com texto de alto contraste), `.btn-secondary` e `.btn-contextual`.
    2. Padronizar `.badge-pill` para timing, direção e estratégias com fundos suaves translúcidos e texto com contraste > 4.5:1.
    3. Garantir indicador de foco `:focus-visible` com anel ciano de 2px em todos os controles, formulários e abas.
  - *Validação*: Teste de acessibilidade via teclado (`Tab`/`Enter`) e contraste WCAG AA.

- [x] **T033: [Prioridade 2 - Telas Quantitativas] Harmonização Visual do Radar de Mercado (Dados Reais)**
  - *Arquivos*: `src/web/index.html`, `src/web/styles.css`
  - *Ação*:
    1. Aplicar os tokens de cartões `.card-surface` e tipografia nos 4 KPIs existentes do deck superior (`#exec-kpi-buys`, `#exec-kpi-sells`, `#exec-kpi-top-asset`, `#exec-kpi-market-regime`), mantendo os dados reais sem inventar medidores ou barras não suportadas.
    2. Estilizar pílulas de categorias (`#radar-category-pills`) e seletores de tempo (`#radar-timeframe-buttons`) com estilos semânticos de alto contraste.
    3. Aplicar o padrão `.table-standard` na tabela de oportunidades do Radar (`#radar-table-body`), garantindo alinhamento e contraste em ambos os temas.
  - *Validação*: Testes E2E de preservação de estado e navegação contextual do Radar aprovados.

- [x] **T034: [Prioridade 2 - Telas Quantitativas] Harmonização Visual do Gráfico Interativo e Terminal**
  - *Arquivos*: `src/web/index.html`, `src/web/styles.css`, `src/web/app.js`
  - *Ação*:
    1. Aplicar a paleta unificada de superfícies no cabeçalho do ativo, controles de timeframe e barra de retorno contextual.
    2. Configurar o layout dos gráficos inferiores Plotly (`#plot-ranking`, `#plot-scatter`) para consumir os tokens semânticos de texto e grid sem quebra de contraste.
    3. Manter estritamente os dados reais do ativo ativo sem adicionar componentes de cotações externas ou boletas fictícias.
  - *Validação*: `node --check src/web/app.js`, `git diff --check`, 9 testes de contratos de UI aprovados e 6 testes E2E específicos de navegação contextual, estado e renderização do Gráfico Interativo aprovados (100% de sucesso).
  - *Status*: Concluído na Fase 3B.

- [x] **T035: [Prioridade 3 - Telas de Apoio] Harmonização do Simulador, Playbook e Custódia**
  - *Arquivos*: `src/web/index.html`, `src/web/styles.css`
  - *Ação*:
    1. Unificar o formulário do Simulador com inputs em grid equilibrado, labels em `var(--text-muted)` e botões padronizados.
    2. Organizar o Playbook em cards modulares com âncoras por estratégia e badges de setup legíveis.
    3. Harmonizar o bloco inferior de custódia (`#tab-portfolio`) eliminando a dissonância entre o cabeçalho Investidor10 e os cards de parâmetros.
  - *Validação*: `node --check src/web/app.js`, `git diff --check`, 95 testes unitários (incluindo contratos de UI) aprovados e 4 testes E2E específicos de navegação, responsividade e contraste dual-theme aprovados (100% de sucesso).
  - *Status*: Concluído na Fase 3B.

- [x] **T036: [Prioridade 4 - Quality Gate] Verificação Visual Dual Theme, A11y e Testes Automatizados**
  - *Ação*:
    1. Executar `node --check src/web/app.js` e `git diff --check`.
    2. Executar auditoria visual Impeccable detect (`.agents/skills/impeccable/scripts/impeccable.cmd detect src/web`).
    3. Executar `python -m pytest tests/unit -v` (95 passed, 2 skipped em planilhas B3 opcionais).
    4. Executar suíte completa de testes E2E (`python -m pytest tests/e2e -v`, 18 passed: 15 em navegação/contraste/responsividade/roteamento e 3 em layout e alternância de Proventos).
    5. Capturar 24 screenshots de comprovação visual cobrindo as 6 telas principais (Visão Geral, Radar, Gráfico Interativo, Simulador, Playbook e Custódia) em 1600px desktop e 768px tablet nos modos Claro e Escuro.
  - *Validação*: 100% dos testes unitários e E2E aprovados (95 unitários + 18 E2E = 113 testes automatizados). Conformidade estrita com o `DESIGN.md`.
  - *Status*: Concluído na Fase 3B.
