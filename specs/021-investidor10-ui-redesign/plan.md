# Implementation Plan: Redesign da Interface Web Estilo Investidor10

**Branch**: `021-investidor10-ui` | **Date**: 2026-10-24 | **Spec**: [specs/021-investidor10-ui-redesign/spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/021-investidor10-ui-redesign/spec.md)

---

## 1. Summary & Progresso das Fases

Este plano de implementacao detalha a evolucao incremental da interface web em etapas isoladas, seguras e verificaveis:
- **Fase 1 (Concluida & Homologada)**: Reestruturacao da Visao Geral (`#tab-overview`), com 4 KPIs auditados, graficos de Aportes Acumulados e Alocacao por Classe via Plotly, rigor semantico e contraste dual.
- **Fase 2A (Escopo Autorizado)**: Reorganizacao da Navegacao Global em 2 Ambientes Operacionais (Minha Carteira vs. Analise Quantitativa), subnavegacao contextual, precedencia estrita de rotas (URL Hash > LocalStorage > Default), sincronia com historico do navegador e redimensionamento de graficos.
- **Fase 2B (Trabalho Separado / Futuro)**: Integracoes contextuais profundas entre telas (Carteira -> Grafico com ticker pre-selecionado, Radar -> Simulador e busca contextual no Playbook).

---

## 2. Technical Context & Constraints

- **Linguagem / Stack**: Python 3.11+ (FastAPI), JavaScript Vanilla ES6+ (SPA sem bundler ou frameworks reativos), Tailwind CSS CDN, Plotly.js, TradingView Lightweight Charts.
- **Baseline de Testes**:
  - `tests/unit/`: 95 testes passando, 2 skipped (baseline intocavel).
  - `tests/e2e/test_dashboard_navigation.py`: 6 testes passando (expandir para cobrir Fase 2A).
  - `tests/e2e/test_proventos_layout.py`: 3 falhas conhecidas de layout herdadas de versoes antigas da aba proventos (baseline isolado; nao enfraquecer nem alterar).
- **Restricoes Rigidas de Escopo**:
  - Nao alterar `src/app.py` nem `src/ui/` (Streamlit 100% preservado).
  - Nao alterar a Visao Geral homologada da Fase 1.
  - Nao introduzir frameworks externos (React, Vue, Svelte, Vite).
  - Nao adicionar benchmarks (CDI, Ibov), projecoes de dividendos ou funcionalidades nao existentes na Fase 2A.
  - Nao realizar redesign visual das telas internas do Radar, Simulador, Posicoes ou Playbook na Fase 2A.
  - Preservar rigorosamente os IDs de contrato do DOM (`tab-overview`, `tab-portfolio`, `tab-terminal`, etc.).

---

## 3. Constitution & Safety Check

| Principio | Status | Justificativa de Conformidade |
| :--- | :--- | :--- |
| **I. Arquitetura FastAPI + SPA** | PASS | Servidor e rotas FastAPI intactos; SPA vanilla servida estaticamente. |
| **II. Rigor Financeiro e Zero Look-Ahead** | PASS | Nenhuma formula quantitativa ou de carteira e alterada. |
| **III. Semantica Financeira Precisa** | PASS | Mantida a semantica auditada da Fase 1. |
| **IV. Preservacao de IDs e Contratos** | PASS | Todos os IDs de paineis existentes sao preservados, evitando quebra de scripts ou testes. |
| **V. Precedencia de Rotas e Navegacao** | PASS | URL Hash tem prioridade sobre LocalStorage; navegacao Voltar/Avancar sincronizada. |
| **VI. Suporte Dual a Temas (Light & Dark)** | PASS | Novos componentes de navegacao usam tokens CSS semanticos de `styles.css`. |

---

## 4. Fases de Execucao Tecnica da Fase 2A

### Etapa 1: Motor de Roteamento, Precedencia e Sincronizacao em `src/web/app.js`
- **Mapeamento de Rotas e Ambientes**:
  ```javascript
  const ROUTE_CONFIG = {
    'carteira/resumo':     { pillar: 'carteira', tab: 'resumo', paneId: 'tab-overview' },
    'carteira/posicoes':   { pillar: 'carteira', tab: 'posicoes', paneId: 'tab-portfolio' },
    'carteira/proventos':  { pillar: 'carteira', tab: 'proventos', paneId: 'tab-pane-proventos' },
    'carteira/patrimonio': { pillar: 'carteira', tab: 'patrimonio', paneId: 'tab-pane-patrimonio' },
    'quant/radar':         { pillar: 'quant', tab: 'radar', paneId: 'tab-pane-radar' },
    'quant/grafico':       { pillar: 'quant', tab: 'tradingview', paneId: 'tab-terminal' },
    'quant/simulador':     { pillar: 'quant', tab: 'simulador', paneId: 'tab-simulator' },
    'quant/playbook':      { pillar: 'quant', tab: 'playbook', paneId: 'tab-playbook' }
  };
  // Aliases retrocompativeis para hashes legados:
  // '#resumo' -> 'carteira/resumo', '#posicoes' -> 'carteira/posicoes', etc.
  ```
- **Precedencia Rigorosa**:
  1. `window.location.hash`: se presente e valido, resolve a rota e ativa o destino.
  2. `localStorage.getItem('mo_active_route')` / `mo_active_tab`: fallback somente quando nao houver hash.
  3. Default absoluto: `carteira/resumo`.
- **Sincronizacao Bidirecional**:
  - `window.addEventListener('hashchange', () => resolveCurrentRoute());`
  - `window.addEventListener('popstate', () => resolveCurrentRoute());`
  - A ativacao da rota atualiza o hash sem adicionar entradas espurias no historico via `history.replaceState` quando conveniente.

### Etapa 2: Estrutura HTML do Seletor de Ambientes e Subnavegacao em `src/web/index.html`
- **Seletor de Ambientes no Topo**:
  - Barra superior de navegacao com dois botoes de pilar:
    - `#pillar-btn-carteira` ("Minha Carteira")
    - `#pillar-btn-quant` ("Analise Quantitativa")
- **Barras de Subnavegacao Contextuais**:
  - `#subnav-pillar-carteira`: Botoes para Visao Geral, Posicoes & Custodia, Proventos & Renda, Evolucao Patrimonial.
  - `#subnav-pillar-quant`: Botoes para Radar de Mercado, Grafico Interativo, Simulador & Backtest, Playbook.
  - O pilar ativo remove a classe `hidden` da sua respectiva barra de subnavegacao e oculta a outra.
- **Preservacao de IDs de Painel e Acessibilidade**:
  - Manter rigorosamente `tab-overview`, `tab-portfolio`, `tab-pane-proventos`, `tab-pane-patrimonio`, `tab-pane-radar`, `tab-terminal`, `tab-simulator`, `tab-playbook`.
  - Atributos `role="tab"`, `aria-selected` e `aria-controls` devidamente sincronizados.

### Etapa 3: Estilos e Tokens Visuais em `src/web/styles.css`
- Definir classes semanticas para o alternador de ambientes e subnavegações.
- Garantir contraste adequado em ambos os temas (`:root` claro e `[data-theme="dark"]`).
- Indicador visual claro de ambiente e subaba ativa (borda inferior de destaque ou pílula ativa com transição suave).
- Foco via teclado com anel de foco visível (`outline: 2px solid var(--primary)`).

### Etapa 4: Gerenciamento de Visibilidade e Redimensionamento de Graficos em `src/web/app.js`
- Ao ativar a subaba `tradingview` (`#tab-terminal`):
  - Disparar `updateSidebarDirectionFilter()`.
  - Disparar `resizeChartResponsive()`.
  - Disparar `state.chart.timeScale().fitContent()` em `setTimeout(..., 50)`.
- Ao ativar subabas com graficos Plotly (`tab-overview`, `tab-pane-proventos`, `tab-pane-patrimonio`, `tab-simulator`):
  - Disparar `Plotly.relayout(container, { autosize: true })` para garantir que graficos abertos em background recalculam a largura do container.

### Etapa 5: Expansao e Execucao da Suite de Testes E2E da Fase 2A
- Atualizar `tests/e2e/test_dashboard_navigation.py` para validar:
  - Alternancia entre Minha Carteira e Analise Quantitativa.
  - Subnavegacoes contextuais correspondentes.
  - Acessibilidade e visibilidade unica de cada um dos 8 paineis.
  - Precedencia de rota: URL Hash prevalece sobre localStorage.
  - Recarregamento da pagina (refresh/F5) e botoes Voltar/Avancar mantem sincronia.
  - Ausencia de IDs duplicados no DOM.
  - Toggle de tema nos dois ambientes.

---

## 5. Planejamento da Fase 2B (Trabalho Separado / Backlog)

A ser executada somente apos a homologacao completa da Fase 2A:
1. **Atalho Carteira -> Grafico**:
   - Adicionar botao de acao contextual nas linhas de custodia (`#investidor10-positions-categories`).
   - Implementar funcao de despacho `navigateToChart(ticker, { returnRoute: 'carteira/posicoes' })`.
   - Adicionar barra/pilula de retorno no topo do terminal ("Voltar para Custodia").
2. **Atalho Radar -> Grafico e Simulador**:
   - Acoes rapidas no Radar para abrir ativo no grafico com timeframes sincronizados ou no Simulador com o par campeao.
3. **Playbook Contextual**:
   - Atribuir IDs de ancora a cada uma das 48 estrategias em `tab-playbook`.
   - Inserir micro-botoes de ajuda `(?)` ao lado das tags de padroes no Radar e Grafico.


---

## 6. Fase 3A & 3B — Plano de Arquitetura de Componentes, Tokens e Transição Visual

### 6.1 Estratégia de Priorização Top-Down (Fundações e Componentes Existentes)
Para garantir consistência visual sem desvio de escopo funcional, o redesign segue estritamente a sequência arquitetural:
1. **Nível 1: Fundações Globais e Tokens de Design (Fase 3A / T026-T028)**:
   - Centralizar todas as cores, tipografia, raios e sombras em variáveis CSS semânticas em `src/web/styles.css`.
   - Atualizar a definição de `tailwind.config` em `src/web/index.html` para refletir as variáveis de tokens semânticos, permitindo suporte dual theme automático.
   - Definir classes de utilidade compartilhadas (`.card-surface`, `.table-standard`, `.btn-primary`, `.btn-secondary`, `.badge-pill`, etc.).
2. **Nível 2: Saneamento dos Componentes Compartilhados (Fase 3B.1 / T029-T032)**:
   - Padronizar cartões, eliminando aninhamentos excessivos (`nested-cards`) e unificando cantos arredondados (`--radius-lg` = 12px) e sombras.
   - Padronizar tabelas com piso tipográfico de 11px em cabeçalhos, números tabulares monospaçados e botões contextuais.
   - Padronizar botões primários, secundários e badges de timing/direção com dupla codificação.
3. **Nível 3: Harmonização Visual das Telas com Dados Reais Existentes (Fase 3B.2 / T033-T036)**:
   - **Radar de Mercado**: Estilização do Command Deck de 4 KPIs já existentes (Compras, Vendas, Maior Assimetria, Regime) e da tabela de oportunidades com base na estética de cartões e tabelas compartilhadas. **Sem criação de medidores ou barras de breadth fictícios**.
   - **Gráfico Interativo**: Harmonização do cabeçalho do ativo, timeframe e gráficos inferiores Plotly com a paleta de superfícies grafite/navy e acentos ciano. **Sem criação de carrossel de cotações externo não alimentado**.
   - **Simulador & Backtest**: Harmonização do formulário de parâmetros, cards de métricas de trade/acumulação e curva de capital existente.
   - **Playbook**: Organização em grid limpo sem aninhamentos profundos e badges de setup legíveis.
   - **Posições & Custódia**: Unificação do bloco inferior (simulador de carteira) com a estética de cartões e tabelas compartilhadas.

### 6.2 Critérios de Não-Regressão e Preservação de Contratos
- Todos os identificadores de painéis (`tab-overview`, `tab-portfolio`, `tab-pane-radar`, etc.) e IDs de formulários/gráficos permanecem intactos.
- Nenhuma fórmula de cálculo, endpoint ou lógica financeira é alterada.
- Novos elementos visuais só são aplicados onde houver dado real fornecido pelo backend existente.
- Todos os testes unitários (95 passed) e E2E (15 passed) devem continuar passando a cada incremento.
