# UI Layout Contract: Layout Profissional e Unificado

**Feature**: 023-professional-ui-layout
**Date**: 2026-10-27
**Status**: Design contract
**Applies to**: `src/web/index.html`, `src/web/styles.css`, `src/web/app.js`, `src/web/modules/*`

Este contrato define os limites que a implementação visual deve respeitar. Ele não substitui os contratos de API existentes; complementa a spec com invariantes verificáveis de DOM, navegação, tema, acessibilidade e responsividade.

## 1. Non-Negotiable Compatibility Rules

1. Nenhuma API, schema Pydantic, cálculo financeiro ou regra de negócio pode ser alterada.
2. IDs, rotas, atributos de dados e funções globais listados neste contrato são **estáveis** e não podem ser renomeados ou removidos.
3. Deve existir exatamente um painel visível (`.tab-view:not(.hidden)`) em qualquer estado de navegação.
4. Nenhum ID pode aparecer duplicado no documento.
5. O comportamento de URL > `localStorage` > padrão deve ser preservado.
6. A troca de tema deve funcionar sem recarregar a página.
7. Nenhuma área, gráfico, tabela ou funcionalidade existente pode ser removida.
8. A aplicação deve continuar sendo uma SPA estática HTML/CSS/JS, sem novo framework ou bundler.

## 2. Environment and Route Contract

| Environment | Route | Panel ID | Subnav item |
|---|---|---|---|
| Minha Carteira | `#carteira/visao-geral` | `#tab-overview` | `[data-tab="resumo"]` |
| Minha Carteira | `#carteira/posicoes` | `#tab-portfolio` | `[data-tab="posicoes"]` |
| Minha Carteira | `#carteira/proventos` | `#tab-pane-proventos` | `[data-tab="proventos"]` |
| Minha Carteira | `#carteira/patrimonio` | `#tab-pane-patrimonio` | `[data-tab="patrimonio"]` |
| Análise Quantitativa | `#quant/radar` | `#tab-pane-radar` | `[data-tab="radar"]` |
| Análise Quantitativa | `#quant/grafico` | `#tab-terminal` | `[data-tab="tradingview"]` |
| Análise Quantitativa | `#quant/simulador` | `#tab-simulator` | `[data-tab="simulador"]` |
| Análise Quantitativa | `#quant/playbook` | `#tab-playbook` | `[data-tab="playbook"]` |

**Legacy compatibility**: rotas antigas (`#resumo`, `#posicoes`, `#proventos`, `#patrimonio`, `#radar`, `#terminal`, `#simulador`, `#playbook`) devem continuar resolvendo para a área correspondente quando já suportadas hoje.

## 3. Stable DOM Contract

### 3.1 Shell and navigation

- `#global-pillar-selector`
- `#pillar-btn-carteira`
- `#pillar-btn-quant`
- `#main-subnav-pills`
- `#subnav-group-carteira`
- `#subnav-group-quant`
- `[data-tab="resumo"]`, `[data-tab="posicoes"]`, `[data-tab="proventos"]`, `[data-tab="patrimonio"]`
- `[data-tab="radar"]`, `[data-tab="tradingview"]`, `[data-tab="simulador"]`, `[data-tab="playbook"]`
- `.tab-view`, `.tab-pane`, `.nav-tab.active`
- `#btn-theme-toggle`, `#theme-toggle-icon`
- `#btn-header-b3-status`, `#b3-import-label`, `#btn-header-add-trade`, `#b3-multi-file-input`
- `#loading-spinner`, `#loading-text`
- `#global-direction-selector`

### 3.2 Carteira

- `#tab-overview`, `#tab-portfolio`, `#tab-pane-proventos`, `#tab-pane-patrimonio`
- `#kpi-patrimonio-total`, `#kpi-lucro-total`, `#kpi-proventos-12m`, `#kpi-posicoes-lucro`
- `#overview-stacked-bar-chart`, `#overview-donut-chart`
- `#chart-proventos-detailed`, `#chart-patrimonio-detailed`
- `#investidor10-positions-categories`
- `#btn-proventos-view-mensal`, `#btn-proventos-view-anual`
- `#investidor10-welcome-banner` (condicional)
- `#link-overview-ver-patrimonio`

### 3.3 Quantitativo

- `#tab-pane-radar`, `#tab-terminal`, `#tab-simulator`, `#tab-playbook`
- `#radar-table-body`, `#radar-pagination-container`, `#radar-pagination-info`
- `#btn-radar-rescan`, `#btn-radar-prev`, `#btn-radar-next`
- `#radar-timeframe-buttons`, `#radar-category-pills`, `#radar-strategy-dropdown-wrapper`
- `#input-ticker`, `#select-period`, `#btn-load-analysis`, `#btn-refresh-data`
- `#sim-ticker`, `#sim-interval`, `#sim-mode`, `#sim-cycle-mode`
- `#sim-buy-strategy`, `#sim-sell-strategy`, `#btn-run-simulation`
- `#btn-optimize-combinations`, `#sim-optimizer-container`

### 3.4 Global JavaScript contract

Devem permanecer acessíveis em `window`:

- `window.appState`
- `window.applyTheme`

Outras funções consumidas por testes existentes devem ser inventariadas antes de qualquer refatoração e preservadas ou migradas com alias compatível.

## 4. Theme Contract

- Atributo de tema: `document.documentElement.dataset.theme` / `data-theme` com valores `light` ou `dark`.
- Chave de persistência: `terminal_theme`.
- Padrão inicial: `light`.
- Valor inválido/ausente: `light`, sem erro visível.
- Alternância: atualiza atributo, persiste e chama a atualização de gráficos.
- Todas as oito áreas devem ser legíveis e funcionalmente equivalentes nos dois temas.
- Cores semânticas de ganho/perda devem manter contraste AA e não depender apenas de cor.
- Nenhuma área pode depender de overrides que convertam uma paleta escura em clara em tempo de execução.

## 5. Visual System Contract

### 5.1 Typography

- Piso absoluto: 11px para qualquer texto funcional, label, metadado acionável ou cabeçalho de tabela.
- Valores financeiros, tickers e métricas: fonte monoespaçada/tabular.
- Hierarquia: display, título de seção, título de card, corpo, label, metadado.
- Não usar emojis como ícones funcionais.

### 5.2 Components

- Cartões, botões, campos, selects, badges, tabelas e acordeões devem compartilhar medidas, raios, bordas, sombras e estados.
- Estados obrigatórios: default, hover, focus-visible, active, disabled, loading, empty, error.
- Não aninhar cartões com borda/sombra redundantes.
- Ações destrutivas devem ser visualmente distintas e confirmadas quando já houver confirmação no fluxo atual.

### 5.3 Layout

- Largura máxima de conteúdo consistente entre as áreas.
- Gutter horizontal consistente em desktop e mobile.
- Grid de KPIs: 4 colunas em desktop, 2 em tablet, 1 em mobile.
- Cabeçalhos de área com título, contexto e ações no mesmo padrão.
- Tabelas largas: rolagem horizontal restrita ao contêiner, com indicativo visual.
- Nenhuma rolagem horizontal global involuntária.

## 6. Accessibility Contract

- Controles de navegação: `role="tab"`/`role="tablist"` quando aplicável, `aria-selected` sincronizado.
- Todo controle interativo alcançável por Tab e ativável por Enter/Espaço quando aplicável.
- Foco visível com contraste adequado.
- Contraste mínimo AA (4.5:1 para texto normal).
- Zoom de 200% sem perda de conteúdo/controle.
- `prefers-reduced-motion`: animações não essenciais suprimidas.
- Nomes acessíveis para botões icônicos.
- Mensagens de erro/carregamento/vazio anunciáveis e visualmente consistentes.

## 7. Content Contract

- Todo texto visível em português correto, sem artefatos de encoding.
- Rótulos financeiros mantêm o significado atual; nenhuma métrica pode ser renomeada de forma enganosa.
- Notas de contingência de cotação e latência permanecem visíveis.
- Nenhuma informação é removida por razões estéticas.

## 8. Responsive Contract

Larguras de referência: **375px, 768px, 1366px, 1920px**.

Em cada largura:

- O shell permanece utilizável (marca, ambiente, ações e tema acessíveis).
- A subnavegação ativa permanece visível e alcançável.
- Conteúdo não se sobrepõe nem é cortado.
- Tabelas largas rolam apenas dentro do próprio contêiner.
- Gráficos ajustam-se ao contêiner sem colapsar para largura zero.
- Áreas de toque têm tamanho adequado em telas pequenas.

## 9. Verification Matrix

| Verificação | Método | Critério |
|---|---|---|
| Encoding | Auditoria automatizada + inspeção | Zero artefatos em textos visíveis |
| Um painel ativo | Playwright/DOM | `document.querySelectorAll('.tab-view:not(.hidden)').length === 1` |
| IDs únicos | Playwright/DOM | Nenhum ID duplicado |
| Rotas | Playwright | Hash, storage, default, voltar/avançar e reload consistentes |
| Temas | Playwright + inspeção | 8/8 áreas em `light` e `dark` |
| Tipografia | Auditoria de classes/estilos | Nenhum texto funcional < 11px |
| Contraste | Ferramenta de contraste + inspeção | AA em texto e controles |
| Teclado | Playwright | Navegação e ativação por teclado |
| Responsividade | Matriz visual | 64/64 aprovadas |
| Regressão funcional | pytest | Suíte existente sem falhas novas |
| APIs | Inspeção de diff | Nenhuma alteração em `src/api/` |

## 10. Change Control

- Qualquer necessidade de renomear um ID estável exige justificativa, alias de compatibilidade e atualização explícita dos testes.
- Qualquer alteração de rota exige suporte à rota legada e atualização do contrato.
- Qualquer alteração visual que afete um teste existente deve ser resolvida no código, não enfraquecendo o teste.
- A aprovação final exige evidência das 64 verificações visuais e da suíte automatizada.
