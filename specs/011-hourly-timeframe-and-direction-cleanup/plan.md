# Implementation Plan: Suporte ao Timeframe 1h sem Erro 400 e Ocultação do Seletor de Direção no Simulador e Playbook

**Branch**: `011-hourly-timeframe-and-direction-cleanup` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/011-hourly-timeframe-and-direction-cleanup/spec.md`

---

## Summary

Esta feature contempla duas entregas essenciais:
1. **Resolução do Erro 400 no Timeframe de 1h**: Mapeamento de `"60m"` como equivalente a `"1h"` em `MAX_PERIODS` no `DataLoader`, aplicando o teto de 730 dias do Yahoo Finance e garantindo execução com sucesso no simulador e otimizador.
2. **Ocultação Contextual do Seletor de Direção**: Atualização de `switchTab` para ocultar o componente `#global-direction-selector` nas abas Simulador e Playbook, exibindo-o apenas no Radar e Gráfico.

---

## Technical Context

**Language/Version**: Python 3.11+ / HTML5 / JavaScript Vanilla (ES6+)  
**Primary Dependencies**: FastAPI, Pydantic, Pandas, NumPy, yfinance, Lightweight Charts  
**Storage**: Cache em disco Parquet (`.cache/data/`) e memória  
**Testing**: `pytest` com asserções formais unitárias  
**Target Platform**: Navegadores Web modernos (desktop e mobile)  
**Project Type**: Single-Repository Web Quant Terminal & Analytical API  
**Performance Goals**: Carregamento horário em cache Parquet em < 100ms; transição visual instantânea (0ms)  
**Constraints**: Zero look-ahead bias; conformidade estrita com a Constituição v2.0.0; commit atômico por tarefa  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **I. Arquitetura Python + Web SPA**: FastAPI gerencia endpoints REST; Frontend SPA vanilla HTML/JS.
- [X] **II. Zero Look-Ahead Bias**: Causalidade temporal inalterada.
- [X] **III. Robustez Multi-Mercado**: Compatibilidade com ativos horários mantida.
- [X] **IV. Modularidade Estrita**: Divisão desacoplada preservada.
- [X] **Commit por Tarefa (OBRIGATÓRIO)**: Cada tarefa implementada no `tasks.md` gerará um commit atômico individual.

---

## Project Structure

### Documentation (this feature)

```text
specs/011-hourly-timeframe-and-direction-cleanup/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Technical research and decisions
├── data-model.md        # Data entities, schemas and state modifications
├── quickstart.md        # End-to-end validation guide
└── checklists/          # Requirements and quality checklists
```

### Source Code Impact

```text
src/
├── data_loader/
│   └── fetcher.py       # Inclusão de "60m": "730d" em MAX_PERIODS e normalização horária
├── api/
│   └── server.py        # Limite de período em 730d para 1h/60m no endpoint de otimização/simulação
└── web/
    └── app.js           # Ocultação/exibição condicional de #global-direction-selector em switchTab

tests/
└── unit/
    └── test_resampler.py # Teste de carregamento e normalização com 60m / 1h
```

---

## Complexity Tracking

*Nenhuma violação constitucional. Sem padrões complexos desnecessários adicionados.*
