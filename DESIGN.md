# DESIGN.md — Market Opportunity & Bottom Statistical Engine
*Diretrizes de Design System & Tokens Visuais (Identidade Quant-Executiva Unificada)*

<!-- impeccable:design-schema 1 -->

## 1. Visual World & Direction (Identidade Quant-Executiva)

O **Market Opportunity & Bottom Statistical Engine** combina o melhor de dois mundos:
1. **A Clareza Executiva do Investidor10:** Resumo patrimonial limpo, cartões respirados, métricas agregadas escaneáveis e foco nas decisões de alocação de capital (*Operate Mode*).
2. **O Rigor e Densidade do Terminal Quantitativo:** Superfícies profundas navy/grafite, acentos ciano e verde-azulado, tipografia monospaçada de alta legibilidade para séries de preços e indicadores estatísticos (*Bottom Detector 2x2*, *Z-Score*, *Timing*, *Win Rate*).

### Princípios Fundamentais de Design:
- **Bimodalidade Harmônica com Tokens Únicos:** Ambos os temas (Claro e Escuro) consomem exatamente a mesma nomenclatura semântica de tokens CSS (`--canvas`, `--surface`, `--border`, `--text`, `--primary`, `--success`, etc.). O tema claro oferece uma estética corporativa limpa (Investidor10 clean), enquanto o tema escuro oferece um terminal noturno de alta performance (Navy/Grafite Fintech).
- **Semântica Financeira Não Dependente Apenas de Cor:** Ganhos/Compras e Perdas/Vendas utilizam sempre reforço textual e ícones de direção (`▲`, `▼`, `↗`, `↘`) em conjunto com as cores de contraste auditadas (WCAG AA > 4.5:1).
- **Piso Tipográfico Estrito (Mínimo 11px):** Nenhum texto funcional, cabeçalho de tabela, label de formulário ou metadado renderiza abaixo de 11px. A classe `text-[10px]` é normalizada para `--font-size-floor` (11px) e os contratos unitários barram qualquer declaração menor.
- **Hierarquia Plana e Limpa:** Eliminação de cartões aninhados (*nested cards*) redundantes; agrupamento estruturado por espaçamento rítmico, divisórias sutis e tipografia bem balanceada.
- **Gráficos Integrados e Transparentes:** Plotly e TradingView utilizam fundos transparentes, herdando as cores de eixos, grid e tipografia diretamente dos tokens de tema ativos.

---

## 2. Design Tokens

### 🎨 Paleta de Cores e Superfícies (Color Tokens)

```css
/* =========================================================================
   Tokens Semânticos Universais: Tema Claro (Padrão) vs. Tema Escuro
   ========================================================================= */

:root {
  color-scheme: light;

  /* Superfícies & Fundos */
  --canvas: #f8fafc;                 /* Fundo geral da aplicação (Slate 50) */
  --surface: #ffffff;                /* Superfície principal de cards e painéis */
  --surface-subtle: #f1f5f9;         /* Superfície elevada secundária (pílulas, header de tabela) */
  --surface-hover: #f8fafc;          /* Hover suave sobre linhas e botões secundários */
  --surface-overlay: rgba(15, 23, 42, 0.6); /* Backdrop para modais e popovers */

  /* Linhas e Bordas */
  --border: #e2e8f0;                 /* Borda padrão de cards e divisórias (Slate 200) */
  --border-strong: #cbd5e1;          /* Borda com maior ênfase e inputs (Slate 300) */
  --border-focus: #0284c7;           /* Borda e anel de foco acessível */

  /* Tipografia & Hierarquia de Contraste */
  --text-main: #0f172a;              /* Títulos, números grandes e textos de alta ênfase (Slate 900, >13:1) */
  --text-muted: #475569;             /* Labels, cabeçalhos de coluna e legendas (Slate 600, >6.5:1) */
  --text-subtle: #5b6b80;            /* Metadados, notas explicativas e placeholders (>5.4:1 sobre surface) */

  /* Cores Semânticas de Operação & Rentabilidade */
  --success: #047857;                /* Verde institucional para lucros e sinais de Compra (Fundo) */
  --success-soft: #ecfdf5;           /* Fundo suave para badges de Compra/Lucro */
  --success-border: #a7f3d0;         /* Borda de badge de sucesso */

  --danger: #be123c;                 /* Rose/Vermelho para prejuízos e sinais de Venda (Topo) */
  --danger-soft: #fff1f2;            /* Fundo suave para badges de Venda/Prejuízo */
  --danger-border: #fecdd3;          /* Borda de badge de perigo */

  --warning: #b45309;                /* Âmbar institucional para alertas e timing neutro */
  --warning-soft: #fef3c7;           /* Fundo suave para avisos */
  --warning-border: #fde68a;         /* Borda de aviso */

  /* Identidade & Acentos Quantitativos */
  --primary: #0369a1;                /* Azul institucional ciano (B3 / Ação Primária) */
  --primary-hover: #075985;          /* Hover de ação primária */
  --primary-soft: #e0f2fe;           /* Fundo suave de destaque e seleção de abas */
  --primary-text: #ffffff;           /* Texto sobre botões primários */

  --accent-teal: #0d9488;            /* Verde-azulado para estratégias quantitativas e timing */
  --accent-teal-soft: #ccfbf1;
  --purple: #7c3aed;                 /* Roxo para alocações globais/cripto */
  --purple-soft: #f3e8ff;

  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
}

[data-theme="dark"] {
  color-scheme: dark;

  /* Superfícies & Fundos Navy/Grafite */
  --canvas: #0a0e17;                 /* Fundo ultra escuro navy grafite */
  --surface: #111827;                /* Superfície de cards e painéis (Navy Slate) */
  --surface-subtle: #162032;         /* Superfície elevada secundária (pílulas, header de tabela) */
  --surface-hover: #1e293b;          /* Hover sobre linhas e botões */
  --surface-overlay: rgba(0, 0, 0, 0.75);

  /* Linhas e Bordas */
  --border: #1e293b;                 /* Borda sutil de painéis (Slate 800) */
  --border-strong: #334155;          /* Borda com maior ênfase (Slate 700) */
  --border-focus: #38bdf8;           /* Anel de foco ciano vibrante */

  /* Tipografia & Hierarquia de Contraste */
  --text-main: #f8fafc;              /* Títulos e valores primários (Slate 50, >14:1) */
  --text-muted: #94a3b8;             /* Labels e cabeçalhos de coluna (Slate 400, >7:1) */
  --text-subtle: #8b98a5;            /* Metadados e legendas (>6:1 sobre surface) */

  /* Cores Semânticas de Operação & Rentabilidade */
  --success: #10b981;                /* Esmeralda vibrante para Compra / Lucro */
  --success-soft: rgba(16, 185, 129, 0.14);
  --success-border: rgba(16, 185, 129, 0.35);

  --danger: #fb7185;                 /* Rose vibrante para Venda / Risco de reversão */
  --danger-soft: rgba(251, 113, 133, 0.14);
  --danger-border: rgba(251, 113, 133, 0.35);

  --warning: #f59e0b;                /* Âmbar para alertas e regime neutro */
  --warning-soft: rgba(245, 158, 11, 0.14);
  --warning-border: rgba(245, 158, 11, 0.35);

  /* Identidade & Acentos Quantitativos */
  --primary: #06b6d4;                /* Ciano vibrante para botões e seleção */
  --primary-hover: #22d3ee;
  --primary-soft: rgba(6, 182, 212, 0.14);
  --primary-text: #041019;           /* Texto escuro de alto contraste sobre ciano */

  --accent-teal: #14b8a6;            /* Verde-azulado técnico */
  --accent-teal-soft: rgba(20, 184, 166, 0.14);
  --purple: #a78bfa;                 /* Roxo suave para cripto */
  --purple-soft: rgba(167, 139, 250, 0.14);

  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 6px 16px -2px rgba(0, 0, 0, 0.6);
  --shadow-lg: 0 14px 28px -4px rgba(0, 0, 0, 0.7);
}
```

---

### 🔤 Tipografia & Escala de Tamanhos (Typography Tokens)

- **Família Primária (Interface & Executivo)**: `'Plus Jakarta Sans', system-ui, -apple-system, sans-serif`
- **Família Monospaçada (Valores, Tickers & Métricas Quant)**: `'JetBrains Mono', Consolas, monospace`

| Nível / Papel | Família | Tamanho (`px` / `rem`) | Peso (`font-weight`) | Line-height | Letter-spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Display / KPI** | `font-sans` | `24px` (`1.5rem`) | 800 (ExtraBold) | 1.15 | `-0.025em` |
| **Título de Seção (H2)** | `font-sans` | `18px` (`1.125rem`) | 700 (Bold) | 1.25 | `-0.015em` |
| **Título de Card (H3)** | `font-sans` | `15px` (`0.9375rem`) | 600 (SemiBold) | 1.3 | `-0.01em` |
| **Corpo / Parágrafo** | `font-sans` | `13px` (`0.8125rem`) | 400 / 500 (Regular/Medium) | 1.5 | `normal` |
| **Preços & Tickers** | `font-mono` | `12px - 13px` | 600 (SemiBold) | 1.2 | `0.01em` |
| **Headers de Tabela** | `font-sans` | `11px` (`0.6875rem`) *(Piso mínimo)* | 600 (SemiBold) | 1.2 | `0.04em` (Uppercase) |
| **Badges & Tags Quant** | `font-mono` | `11px` (`0.6875rem`) *(Piso mínimo)* | 700 (Bold) | 1.2 | `0.02em` |

> [!IMPORTANT]
> **Piso Mínimo de 11px:** É estritamente proibido o uso de `text-[10px]` para qualquer elemento de texto funcional, cabeçalho de coluna, botão de navegação ou metadado acionável.

---

### 📐 Espaçamento, Bordas e Raio (Spatial Tokens)

```css
:root {
  /* Escala Modular de Espaçamento Base 4px */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* Raio de Arredondamento */
  --radius-xs: 4px;                  /* Pequenos seletores internos */
  --radius-sm: 6px;                  /* Badges, tags e pílulas */
  --radius-md: 8px;                  /* Botões, inputs e dropdowns */
  --radius-lg: 12px;                 /* Cards, painéis e contêineres principais */
  --radius-xl: 16px;                 /* Diálogos executivos e modais */
}
```

---

## 3. Padrões de Componentes Compartilhados (Shared Components)

### 3.1 Cartões Executivos & Painéis (`.card-surface`, `.metric-card`)
- **Container**: `background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-sm);`
- **Hierarquia de Cabeçalho**: Label em `var(--text-muted)` (11px uppercase) seguido por valor em destaque `var(--text-main)` (18px-24px).
- **Sem Aninhamento de Cartões**: Não aninhar cartões com bordas e sombras dentro de cartões existentes. Usar divisórias horizontais sutis (`border-b: 1px solid var(--border)`) ou fundo elevado `var(--surface-subtle)`.

### 3.2 Tabelas Institucionais (`.table-standard`)
- **Cabeçalho (`thead`)**:
  - `background: var(--surface-subtle);`
  - `color: var(--text-muted); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;`
  - `padding: 10px 14px; border-bottom: 1px solid var(--border);`
- **Linhas de Dados (`tbody tr`)**:
  - `border-bottom: 1px solid var(--border); transition: background 0.15s ease; font-size: 12px;`
  - `hover: background: var(--surface-hover);`
  - Padding de célula: `8px 14px;`
- **Células Numéricas e Financeiras**:
  - Alinhamento à direita com `font-mono`, tabular numbers e formatação estrita `pt-BR` (ex: `R$ 1.234,56`).
- **Ações na Linha**:
  - Botão contextual com área de toque mínima de 28px de altura, rótulo claro e contraste assegurado.

### 3.3 Botões & Controles Interativos (`.btn-primary`, `.btn-secondary`, `.btn-contextual`)
- **Botão Primário (`.btn-primary`)**:
  - Fundo: `var(--primary)` com texto `var(--primary-text)`.
  - Raio: `var(--radius-md)` (8px). Altura: `32px` a `36px`.
  - Hover: `var(--primary-hover)` com leve transição de escala/brilho.
- **Botão Secundário / Outline (`.btn-secondary`)**:
  - Fundo: `var(--surface)`. Borda: `1px solid var(--border)`. Texto: `var(--text-main)`.
  - Hover: `background: var(--surface-subtle); border-color: var(--border-strong);`
- **Botão Contextual de Tabela (`.btn-contextual`)**:
  - Fundo translúcido `var(--primary-soft)`, borda `1px solid var(--primary)`, texto `var(--primary)`.
  - Hover: elevação de opacidade com preservação rigorosa de legibilidade.
- **Foco por Teclado (`:focus-visible`)**:
  - `outline: 2px solid var(--border-focus); outline-offset: 2px;` obrigatório em todos os botões e links.

### 3.4 Badges Quantitativos & Indicadores de Timing (`.badge-pill`)
- **Estrutura**: Altura `22px`, padding horizontal `8px`, `border-radius: var(--radius-sm)`, tipografia `font-mono` 11px negrito.
- **Compra / Setup Fundo**: Fundo `var(--success-soft)`, borda `1px solid var(--success-border)`, texto `var(--success)`. Prefixo `▲` ou `●`.
- **Venda / Topo Alerta**: Fundo `var(--danger-soft)`, borda `1px solid var(--danger-border)`, texto `var(--danger)`. Prefixo `▼` ou `●`.
- **Neutro / Timing Estendido**: Fundo `var(--warning-soft)`, borda `1px solid var(--warning-border)`, texto `var(--warning)`.

---

## 4. Diretrizes de Acessibilidade & Contraste (a11y)

1. **Relação de Contraste Auditada (WCAG AA):**
   - Textos primários: `17.85:1` (claro) e `16.96:1` (escuro) sobre `--surface`.
   - Textos secundários (`--text-muted`): `7.58:1` (claro) e `6.92:1` (escuro) sobre `--surface`.
   - Textos terciários (`--text-subtle`): `5.44:1` (claro) e `6.03:1` (escuro) sobre `--surface`; mínimo de `4.97:1`/`5.54:1` sobre `--surface-subtle`.
   - Badges e textos coloridos (verde, vermelho, âmbar, ciano) mantêm ≥ `4.5:1` sobre `--surface`, `--canvas` e `--surface-subtle`. O contrato `test_theme_tokens_meet_wcag_aa_contrast` audita os pares nos dois temas.
2. **Dupla Codificação Semântica:**
   - Todo indicador de variação percentual ou direção é acompanhado de texto explícito ou glifo (`▲` / `▼`).
3. **Navegabilidade por Teclado:**
   - Navegação completa por tabulação (`Tab` / `Shift+Tab`) com foco visível sem interrupções.
   - Ativação de abas, acordeões e modais via teclas `Enter` e `Space`.

---

## 5. Diretrizes de Visualização de Gráficos (Plotly & TradingView)

1. **Fundo Transparente:**
   - Sempre definir `paper_bgcolor: 'rgba(0,0,0,0)'` e `plot_bgcolor: 'rgba(0,0,0,0)'`.
2. **Cores dos Eixos e Gridlines Dinâmicas:**
   - Eixos e rótulos consomem cor de texto do tema: `#0F172A` (claro) / `#F8FAFC` (escuro).
   - Gridlines utilizam cor de borda atenuada: `rgba(203, 213, 225, 0.5)` (claro) / `rgba(51, 65, 85, 0.4)` (escuro).
3. **Paleta Semântica das Séries:**
   - Rentabilidade Positiva / Aportes: `var(--success)`.
   - Venda / Prejuízo / Drawdown: `var(--danger)`.
   - Patrimônio / Valor de Mercado: `var(--primary)`.
   - Comparadores / Benchmarks: `var(--accent-teal)` e `var(--purple)`.

---

## 6. Mapeamento Consolidado de Tokens e Componentes (Feature 023)

Esta seção é a referência única para implementar qualquer área da SPA. Toda
tela deve consumir os tokens abaixo, sem cores hardcoded fora de `:root` e
`[data-theme="dark"]`.

Desde a Feature 023, as áreas não usam mais as classes legadas
`fintech-*`, `gray-*`, `cyan-*`, `emerald-*`, `rose-*` ou `amber-*`, nem os
blocos de override de tema em tempo de execução. A migração é verificada por
`test_quant_areas_use_shared_semantic_system`.

### 6.1 Tokens semânticos

| Papel | Token | Uso |
| :--- | :--- | :--- |
| Fundo da aplicação | `--canvas` | `<body>`, painéis de área, páginas |
| Superfície principal | `--surface` | Cards, tabelas, header, subnav, modais |
| Superfície secundária | `--surface-subtle` | Cabeçalho de tabela, pílulas, estados vazios |
| Hover | `--surface-hover` | Linhas de tabela, botões secundários |
| Borda padrão | `--border` | Cards, divisórias, tabelas |
| Borda forte | `--border-strong` | Inputs, selects, contornos de ênfase |
| Borda sutil | `--border-subtle` | Divisórias internas e cartões aninhados |
| Texto principal | `--text-main` | Títulos, valores, células |
| Texto secundário | `--text-muted` | Labels, cabeçalhos de coluna |
| Texto terciário | `--text-subtle` | Metadados, notas, placeholders |
| Ação primária | `--primary` / `--primary-hover` / `--primary-soft` | Botões, seleção, links |
| Ganho / Compra | `--success` / `--success-soft` / `--success-border` | Variações positivas, badges de compra |
| Perda / Venda | `--danger` / `--danger-soft` / `--danger-border` | Variações negativas, badges de venda |
| Alerta / Neutro | `--warning` / `--warning-soft` / `--warning-border` | Timing estendido, avisos |
| Foco | `--border-focus` / `--focus-ring` | `:focus-visible` e anel de foco |
| Superfície inversa | `--inverse-surface` / `--inverse-text` | Botões escuros no tema claro e vice-versa |
| Estados | `--state-loading`, `--state-empty`, `--state-error`, `--state-success` | Mensagens de estado |

### 6.2 Escala tipográfica

| Nível | Classe utilitária | Token | Tamanho |
| :--- | :--- | :--- | :--- |
| Display / Hero | `.type-display` | `--font-size-display` | 28px |
| Seção | `.type-section` | `--font-size-section` | 18px |
| Card | `.type-card` | `--font-size-card` | 14px |
| Corpo | `.type-body` | `--font-size-body` | 13px |
| Label | `.type-label` | `--font-size-label` | 12px |
| Metadado | `.type-meta` | `--font-size-meta` | 11px |
| Piso absoluto | `.text-\[10px\]` (clamp) | `--font-size-floor` | 11px |

Valores financeiros, tickers e métricas quantitativas usam
`.financial-value`, `.font-mono`, `.kpi-value` ou `[data-financial]` com
`font-variant-numeric: tabular-nums`.

### 6.3 Componentes compartilhados

| Componente | Classes | Estados obrigatórios |
| :--- | :--- | :--- |
| Cartão | `.card`, `.card-header`, `.card-title`, `.card-subtitle`, `.card-body`, `.card-surface`, `.metric-card`, `.kpi-card` | default, hover (quando interativo) |
| Botões | `.btn-primary`, `.btn-secondary`, `.btn-contextual`, `.btn-danger`, `.btn-ghost`, `.btn-icon` | default, hover, focus-visible, active, disabled, loading |
| Campos | `.input`, `.select`, `.field-label`, `.field-help`, `.field-error` | default, focus, invalid, disabled |
| Badges | `.badge`, `.badge-pill`, `.badge-success`, `.badge-danger`, `.badge-warning`, `.badge-info` | semânticos por tema |
| Tabelas | `.table-standard`, `.table-scroll`, `.table-scroll-hint` | hover de linha, cabeçalho sticky, rolagem contida |
| Acordeões | `.accordion`, `.accordion-header`, `.accordion-body` | default, hover, aberto/fechado |
| Estados | `.state-empty`, `.state-error`, `.state-loading` | vazio, erro, carregando |

### 6.4 Navegação e shell

- Header: marca, seletor de ambientes (`#global-pillar-selector`), ações
  (`#btn-header-b3-status`, `#btn-header-add-trade`) e tema (`#btn-theme-toggle`).
- Subnavegação contextual: `#main-subnav-pills` com `#subnav-group-carteira`
  e `#subnav-group-quant`; `[data-tab]` e `aria-selected` são estáveis.
- Rotas canônicas: `#carteira/visao-geral`, `#carteira/posicoes`,
  `#carteira/proventos`, `#carteira/patrimonio`, `#quant/radar`,
  `#quant/grafico`, `#quant/simulador`, `#quant/playbook`.
- Precedência: URL explícita > `localStorage` > `carteira/visao-geral`.
- Exatamente um `.tab-view:not(.hidden)` e um `aria-selected="true"` por ambiente.

### 6.5 Ícones

O sprite inline em `src/web/index.html` é a única fonte de ícones funcionais.
Ícones disponíveis: `icon-sun`, `icon-moon`, `icon-chart`, `icon-wallet`,
`icon-coins`, `icon-trending-up`, `icon-target`, `icon-candlestick`,
`icon-bolt`, `icon-book`, `icon-refresh`, `icon-check`, `icon-x`,
`icon-warning`, `icon-import`, `icon-plus`, `icon-arrow-left`,
`icon-arrow-right`, `icon-sort`, `icon-building`, `icon-globe`, `icon-coin`,
`icon-layers`.

Uso: `<svg class="icon" aria-hidden="true"><use href="#icon-target"></use></svg>`.
Emojis não são permitidos como ícones de ação ou navegação.

### 6.6 Temas

- Padrão inicial: `light`.
- Persistência: `localStorage['terminal_theme']` (`light` | `dark`).
- Valor inválido ou ausente: `light`, sem erro visível.
- Atributo: `document.documentElement.dataset.theme`.
- Troca de tema atualiza gráficos Plotly/TradingView sem recarregar.
- As oito áreas devem ser legíveis nos dois temas; nenhuma tela pode depender
  de conversão de paleta em tempo de execução.

### 6.7 Responsividade e acessibilidade

- Larguras de referência: 375, 390, 768, 1024, 1366, 1600 e 1920px.
- Navegação móvel inferior (`#mobile-bottom-nav`): exibida automaticamente abaixo de 768px (`md:hidden`) para acesso imediato a **Resumo**, **Carteira**, **Radar** e **Gráfico** (Penpot Screens 11, 12 e 13).
- Grid de KPIs: 1 coluna em mobile, 2 em tablet e 4 em desktop (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).

---

## 7. Mapeamento das 13 Telas do Penpot (`Market Opportunity — Complete System Redesign`)

O arquivo Penpot `bfddaaba-4180-81d4-8008-db61527024e2` (página `01 · Design System & Telas`, `bfddaaba-4180-81d4-8008-db61527024e3`) especifica 13 pranchas oficiais implementadas na SPA:

| # | Prancha Penpot | Dimensão Ref. | Seção / Elemento DOM | Módulo JS Responsável |
| :--- | :--- | :--- | :--- | :--- |
| **01** | `01 · Minha Carteira — Visão Geral` | `1600×1020` | `#tab-overview` (`#investidor10-hero-kpis`, `#overview-stacked-bar-chart`, `#overview-donut-chart`, `#overview-highlights-card`) | `app.js` + `modules/modals.js` |
| **02** | `02 · Minha Carteira — Posições & Custódia` | `1600×1020` | `#tab-portfolio` (`#custody-kpis-grid`, `#custody-category-pills`, `#investidor10-positions-categories`) | `modules/modals.js` + `app.js` |
| **03** | `03 · Minha Carteira — Proventos` | `1600×980` | `#tab-pane-proventos` (`#proventos-kpis-grid`, `#chart-proventos-detailed`, `#prov-composition-list`, `#prov-history-tbody`) | `modules/proventos.js` |
| **04** | `04 · Minha Carteira — Evolução Patrimonial` | `1600×980` | `#tab-pane-patrimonio` (`#chart-patrimonio-detailed`, `#pat-summary-final`, `#pat-history-tbody`) | `modules/evolution.js` |
| **05** | `05 · Quant — Radar de Oportunidades (Fundo 2x2)` | `1600×1020` | `#tab-pane-radar` (`#radar-executive-deck`, `#radar-category-pills`, `#radar-table-body`) | `app.js` |
| **06** | `06 · Quant — Gráfico TradingView & Sinais` | `1600×1060` | `#tab-terminal` (`#tv-chart-container`, `#plot-ranking`, `#plot-scatter`, `#signals-table-body`) | `app.js` |
| **07** | `07 · Quant — Simulador & Backtest` | `1600×1060` | `#tab-simulator` (`#sim-kpi-container`, `#plot-simulation-curve`, `#sim-trades-table-body`) | `app.js` |
| **08** | `08 · Quant — Playbook de Estratégias` | `1600×980` | `#tab-playbook` (`#playbook-search-input`, `#playbook-filter-pills`, `#playbook-cards-grid`) | `modules/playbook.js` |
| **09** | `09 · Modal — Importação de Extratos B3` | `760×640` | `#modal-b3-import` (`#modal-b3-dropzone`, `#modal-b3-files-list`, `#btn-modal-b3-process`) | `modules/modals.js` |
| **10** | `10 · Modal — Novo Lançamento Manual` | `760×640` | `#modal-new-trade` (`.modal-trade-type-btn`, `#modal-trade-ticker`, `#modal-trade-total-preview`) | `modules/modals.js` |
| **11** | `11 · Mobile — Visão Geral` | `390×844` | `#tab-overview` + `#mobile-bottom-nav` | `app.js` + `modules/modals.js` |
| **12** | `12 · Mobile — Posições & Custódia` | `390×844` | `#tab-portfolio` + `#mobile-bottom-nav` | `modules/modals.js` |
| **13** | `13 · Mobile — Radar Quant` | `390×844` | `#tab-pane-radar` + `#mobile-bottom-nav` | `app.js` + `modules/modals.js` |
- Header responsivo:
  - abaixo de 480px a marca pode truncar com reticências e as ações quebram em linhas próprias;
  - a partir de 480px o bloco da marca tem largura mínima de 196px e as ações quebram em vez de espremê-la;
  - até 1023px o seletor de direção ocupa uma linha própria;
  - entre 1024px e 1279px os rótulos secundários (B3/Lançamento) viram ícones com `aria-label`;
  - o selo “Quantitative Pro” só aparece a partir de 1280px e fica oculto quando o seletor de direção está visível (Radar/Gráfico).
- Tabelas largas usam `.table-scroll` (com `tabindex="0"` e dica visual em mobile); a página nunca rola horizontalmente.
- Alvos de toque: 32px para ações inline e 28px para ações de linha de tabela.
- Foco visível em todos os controles, incluindo regiões roláveis; ativação por Enter/Espaço.
- `prefers-reduced-motion: reduce` suprime animações e transições não essenciais (`≤ 0.001s`) e força `scroll-behavior: auto`.
- Zoom de 200% preserva conteúdo, controles e navegação por teclado (validado nas 8 áreas).
