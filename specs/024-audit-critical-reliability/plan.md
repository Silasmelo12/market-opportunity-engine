# Implementation Plan: Confiabilidade Crítica e Experiência Operacional

**Branch**: `spec/024-audit-critical-reliability` | **Date**: 2026-10-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/024-audit-critical-reliability/spec.md`

## Summary

Corrigir os defeitos P0/P1 confirmados na auditoria, em quatro incrementos independentes e cumulativos: (1) importação B3 confiável; (2) simulador de acumulação correto; (3) radar, gráficos e estados vazios honestos; (4) segurança e acessibilidade operacional. Cada incremento deve ser implementado em uma branch própria, com teste de regressão e revisão independente antes do commit.

## Technical Context

**Language/Version**: Python 3.11.9 (produção declarada); ambiente local 3.14.4

**Primary Dependencies**: FastAPI, pandas, numpy, pydantic, yfinance, Plotly.js, Tailwind CDN, Lightweight Charts; `openpyxl`/`xlrd` necessários para Excel

**Storage**: localStorage no navegador; cache em disco/JSON; sem banco de dados

**Testing**: pytest, FastAPI TestClient, Playwright/Chromium para E2E

**Target Platform**: Linux server (Render) + SPA estática servida pelo FastAPI

**Project Type**: Web application single-repository (backend Python + SPA vanilla)

**Performance Goals**: manter carregamento atual do dashboard; não introduzir processamento pesado no cliente

**Constraints**: Zero Look-Ahead Bias; preservar contratos/rotas/IDs; sem novas bibliotecas visuais; sem inventar regras financeiras; Python 3.11.9 em produção

**Scale/Scope**: 8 áreas da SPA, 12 rotas de API, 166 testes existentes + novos testes de regressão

## Constitution Check

| Princípio | Status | Observação |
|---|---|---|
| I. FastAPI + SPA, performance e cache | PASS | Nenhuma troca de stack; apenas dependências de leitura de Excel. |
| II. Rigor financeiro e Zero Look-Ahead Bias | PASS condicionado | A correção de `end_date` e o filtro BUY são requisitos diretos; FX permanece pendente e não será simulado. |
| III. Robustez multi-mercado | PASS | Não altera o universo; a mistura de moedas fica explicitamente fora de escopo até decisão. |
| IV. Modularidade e contratos | PASS condicionado | Mudanças ficam nos módulos existentes; campos opcionais de métricas devem ser refletidos nos schemas. |
| Quality Gates | PASS | Cada tarefa terá teste e commit; revisão independente antes do fechamento. |

## Project Structure

### Documentation (this feature)

```text
specs/024-audit-critical-reliability/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── api/                 # server.py, schemas.py, cache.py
├── data_loader/         # b3_parser.py, fetcher.py, normalizer.py
├── evaluator/           # accumulation_simulator.py, portfolio_simulator.py
├── strategies/          # motores existentes (não alterar sem requisito)
└── web/                 # index.html, app.js, styles.css, modules/

tests/
├── unit/
├── e2e/
└── fixtures...
```

**Structure Decision**: Single project. As mudanças de backend ficam em `src/api/`, `src/data_loader/` e `src/evaluator/`; as de interface em `src/web/`; os testes em `tests/`. Nenhum novo módulo de domínio é necessário.

## Phase 0: Research

- Confirmar que `pandas.read_excel` exige `openpyxl` para `.xlsx` e `xlrd` para `.xls`; declarar ambos no runtime.
- Confirmar que o caixa inicial é um valor de estado local, não um dado da B3; o default deve ser zero e a importação deve resetar o caixa para zero, com o usuário podendo informar manualmente.
- Confirmar que `simulate_accumulation` agrupa todos os sinais sem filtrar direção e usa `close[-1]`; corrigir com filtro explícito e `close_sliced[-1]`.
- Confirmar que `historical_win_rate` é o campo entregue pela API e que o deck usa `win_rate`; alinhar ao contrato real.
- Confirmar que `renderPlotlyRanking` referencia `chartFontColor` antes de defini-lo e que `trace` não é construído; corrigir com variáveis locais e trace explícito.
- Confirmar que o fallback de proventos e da evolução patrimonial é sintético; substituir por estado vazio explícito.
- Confirmar que CORS e upload não têm allowlist/limite; implementar configuração por ambiente e validação no endpoint.
- Confirmar que os painéis de aba não têm `role="tabpanel"`; adicionar semântica e nomes acessíveis.

## Phase 1: Design

### Contratos e decisões

- `SimulationMetricSummary.dca_regular_final_value` e `alpha_vs_dca_pct` passam a aceitar `null`; a UI exibe “—” quando não houver benchmark definido. Não será inventado um benchmark.
- `max_drawdown_pct` da acumulação será calculado a partir de `timeline_equity`.
- CORS usará `ALLOWED_ORIGINS` (lista separada por vírgula), com default local `http://localhost:8123,http://127.0.0.1:8123`; a SPA same-origin continua funcionando.
- Upload B3 aceitará `.xlsx`, `.xls`, `.csv` e `.txt`, com limite configurável `MAX_B3_UPLOAD_MB` (default 10 MB) e limite de 10 arquivos por requisição.
- Caixa: default zero; após importação B3, `availableCash = 0`; o usuário pode editar no formulário de carteira.
- Nenhuma alteração em fórmulas de retorno, preço médio ou alocação além das correções de janela/direção.

### Riscos

- `openpyxl`/`xlrd` aumentam o runtime; são necessários para o formato declarado.
- Resetar caixa pode surpreender quem já informou caixa manualmente; a UI deve deixar o campo visível e o toast deve explicar.
- `null` em métricas exige ajuste de schema e UI; testar contrato.
- CORS allowlist pode bloquear clientes legítimos; documentar `ALLOWED_ORIGINS`.
- A remoção de séries sintéticas pode quebrar E2E que as exigia; atualizar o teste para o comportamento correto.

## Phase 2: Tasks

Ver `tasks.md`.

## Complexity Tracking

Nenhuma violação constitucional prevista. A única decisão pendente é a conversão cambial, deliberadamente fora de escopo.
