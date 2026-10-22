# Implementation Plan: Refatoração da Tabela do Radar com Ocultação de Colunas, Semáforo Minimalista, Direção Compacta e Ordenação de Histórico por Quantidade e Win Rate

**Branch**: `015-radar-table-ux-refactor` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/015-radar-table-ux-refactor/spec.md`

## Summary

Refatoração completa da tabela do Radar de Oportunidades em `src/web/index.html` e `src/web/app.js`:
1. Remoção das colunas redundantes "Categoria", "Preço Atual" e "Ação" (redução de 11 para 8 colunas).
2. Semáforo minimalista com bolinha circular colorida (verde, amarela, vermelha) e tooltip no hover.
3. Direção compacta com as iniciais "C" (Compra) e "V" (Venda).
4. Desmembramento da métrica histórica em "Qtd Sinais" e "Win Rate (%)" com ordenação interativa com latência 0ms nos cabeçalhos.

## Technical Context

**Language/Version**: JavaScript (ES6+ Vanilla), HTML5, Tailwind CSS
**Primary Dependencies**: Frontend estático servido por FastAPI
**Testing**: `pytest` para testes unitários e de integração
**Target Platform**: Navegadores modernos (Desktop e Mobile)
**Project Type**: Web SPA
**Performance Goals**: Ordenação e renderização em <10ms
**Constraints**: Zero Look-Ahead Bias intacto; sem novas bibliotecas externas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitetura Python + Web SPA**: Frontend estático servido pelo FastAPI em `src/web/`.
- [x] **II. Rigor Financeiro**: Dados históricos de sinais e win rate inalterados na lógica de cálculo.
- [x] **III. Robustez Multi-Mercado**: Compatível com todos os ativos do radar.
- [x] **IV. Modularidade Estrita**: Nenhuma lógica de negócio de estratégia movida para o frontend.
- [x] **Commit por Tarefa**: Cada tarefa de `tasks.md` gerará 1 commit atômico independente.

## Project Structure

### Documentation (this feature)

```text
specs/015-radar-table-ux-refactor/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── radar-table-layout.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code Layout

```text
src/
└── web/
    ├── index.html       # Atualização do <thead> com 8 colunas e ids para clique de ordenação
    └── app.js           # Estado de ordenação, listener de cliques e renderRadarTable() reformulado
```
