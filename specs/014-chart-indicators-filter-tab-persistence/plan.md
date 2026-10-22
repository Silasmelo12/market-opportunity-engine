# Implementation Plan: Correção de Exibição dos Novos Indicadores na Aba Gráfico, Filtragem Inicial por Direção e Persistência de Aba Ativa ao Atualizar Página

**Branch**: `014-chart-indicators-filter-tab-persistence` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-chart-indicators-filter-tab-persistence/spec.md`

## Summary

Correção da experiência do usuário no frontend web (`src/web/index.html` e `src/web/app.js`):
1. Inclusão dos 10 novos indicadores quantitativos na barra lateral esquerda da aba Gráfico (`#tab-terminal`) com acordeões para Compra e Venda.
2. Aplicação imediata da filtragem por direção na barra lateral na inicialização da página e na navegação de abas (garantindo que se o botão "Compra" estiver selecionado, as estratégias de venda fiquem ocultas).
3. Persistência da aba ativa ao atualizar a página com F5 / recarregar o navegador através de roteamento reativo por URL hash (`#radar`, `#terminal`, `#simulator`, `#playbook`) e `localStorage`.

## Technical Context

**Language/Version**: JavaScript (ES6+ Vanilla), HTML5, Tailwind CSS
**Primary Dependencies**: TradingView Lightweight Charts, Plotly.js (frontend estático servido por FastAPI)
**Storage**: `window.location.hash` e `window.localStorage`
**Testing**: `pytest` para integridade da API e verificação manual em browser
**Target Platform**: Navegadores modernos (Desktop e Mobile)
**Project Type**: Web SPA (FastAPI Static Mount)
**Performance Goals**: Latência 0ms na alternância de abas e filtragem reativa no cliente
**Constraints**: Zero Look-Ahead Bias intacto; sem bibliotecas externas pesadas adicionais

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitetura Python (FastAPI) + Web SPA**: O frontend permanece estático em HTML/JS vanilla servido diretamente pelo FastAPI a partir de `src/web/`.
- [x] **II. Rigor Financeiro e Zero Look-Ahead Bias**: As estratégias exibidas e marcadas respeitam a execução estrita em $t+1$.
- [x] **III. Robustez Multi-Mercado**: Compatível com todos os ativos suportados no gráfico.
- [x] **IV. Modularidade Estrita**: Separação clara entre backend, API e Web SPA.
- [x] **Commit por Tarefa**: Cada tarefa de `tasks.md` gerará 1 commit atômico independente.

## Project Structure

### Documentation (this feature)

```text
specs/014-chart-indicators-filter-tab-persistence/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── navigation-and-sidebar-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code Layout

```text
src/
└── web/
    ├── index.html       # Adição dos blocos de acordeão dos indicadores na barra lateral
    └── app.js           # updateSidebarDirectionFilter(), STRATEGY_ALIASES, switchTab() com hash e localStorage
```
