# Implementation Plan: Pacote de Estratégias Quantitativas com Indicadores Técnicos

**Branch**: `013-quantitative-indicators-package` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-quantitative-indicators-package/spec.md`

## Summary

Implementação de um pacote robusto e modular contendo 10 estratégias quantitativas organizadas em 4 famílias operacionais (Reversão à Média, Osciladores & Divergências, Volume & Fluxo Institucional e Volatilidade/Tendência Dinâmica). Todas as estratégias respeitam rigorosamente a cláusula inegociável de Zero Look-Ahead Bias (sinal gerado na barra $t$ com dados até o fechamento de $t$, e execução na barra $t+1$ ao preço $Open[t+1]$), vetorização pura com NumPy/Pandas e integração bidirecional (compra e venda) no Radar, Simulador de Trades e Simulador DCA.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Uvicorn, NumPy, Pandas, Pydantic v2
**Storage**: Cache em memória (TTL) e Parquet/JSON local
**Testing**: `pytest`
**Target Platform**: Servidor local FastAPI / Web SPA
**Project Type**: Web Service / Quantitative Analysis Engine
**Performance Goals**: Varredura de 500 barras em <50ms por estratégia; otimização multi-estratégia em <3s
**Constraints**: Zero Look-Ahead Bias estrito; Proibido `DataFrame.iterrows()` ou iterações lentas em caminhos críticos
**Scale/Scope**: 10 novas estratégias, 4 famílias, suportando Radar, Simulador e Otimizador DCA

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitetura Python + Web SPA & Otimização de Performance**: Todas as estratégias implementadas em Python puro vetorizado (`numpy`/`pandas`), sem `iterrows()`.
- [x] **II. Rigor Financeiro e Zero Look-Ahead Bias (NON-NEGOTIABLE)**: Todo sinal $t$ tem execução strictly em $t+1$ ao preço de abertura (`Open[t+1]`). Sem filtros com dados futuros.
- [x] **III. Robustez Multi-Mercado & Fallback Quantitativo**: Compatível com B3 (`.SA`), EUA, Cripto (`-USD`) e Commodities (`=F`) em `1d`, `1wk` e `60m`.
- [x] **IV. Modularidade Estrita e Contratos Padronizados**: Retorno estruturado no contrato padrão `SignalRecord` contendo os 5 campos obrigatórios (`signal_bar_index`, `execution_bar_index`, `execution_price`, `reference_line_price`, `strategy_sub_id`).
- [x] **Commit por Tarefa**: Cada tarefa em `tasks.md` receberá um commit atômico independente.

## Project Structure

### Documentation (this feature)

```text
specs/013-quantitative-indicators-package/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── strategies-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code Layout

```text
src/
├── strategies/
│   ├── base.py                     # Dataclasses de contratos (SignalRecord, OHLCVSeries)
│   ├── quantitative_indicators.py  # NOVO: Motor vetorizado dos 10 indicadores (4 famílias)
│   ├── classic_engines.py          # Estratégias clássicas existentes
│   ├── mql5_candles.py             # Padrões de vela existentes
│   ├── proprietary_reversal.py     # Negação de rompimento existente
│   └── __init__.py                 # Catálogo unificado com registro dos novos motores
├── evaluator/
│   ├── trade_simulator.py          # Simulador de pares compra/venda
│   └── accumulation_simulator.py   # Simulador e otimizador DCA
├── api/
│   ├── server.py                   # Endpoints (/api/strategies, /api/radar/scan, /api/simulate/*)
│   └── schemas.py                  # Schemas pydantic
└── web/
    ├── app.js                      # UI controllers, seletores dinâmicos e renders
    └── index.html                  # Interface SPA

tests/
├── unit/
│   ├── test_quantitative_indicators.py # NOVO: Testes unitários vetorizados e anti-lookahead
│   └── ...
```
