# Implementation Plan: B3 Spreadsheet Integration & Portfolio Tracking

**Branch**: `018-b3-spreadsheet-integration` | **Date**: 2026-10-22 | **Spec**: [specs/018-b3-spreadsheet-integration/spec.md](specs/018-b3-spreadsheet-integration/spec.md)

**Input**: Feature specification from `specs/018-b3-spreadsheet-integration/spec.md`

## Summary

Integrar a planilha oficial de movimentações exportada da B3 (`.xlsx`) como fonte primária de dados para a custódia do usuário, calculando cronologicamente posições líquidas, Preço Médio contábil ponderado e consolidação de proventos recebidos (dividendos, JCP, rendimentos). Os dados apurados alimentarão diretamente a aba **Visão Geral** (mantendo seu layout intacto), a aba **Carteira**, o **Radar de Mercado** e o **Terminal Gráfico**.

## Technical Context

**Language/Version**: Python 3.11+ / 3.13  
**Primary Dependencies**: FastAPI, Pydantic, pandas, openpyxl, TailwindCSS, TradingView Lightweight Charts, Plotly.js  
**Storage**: Arquivos em `B3/`, persistência no LocalStorage do navegador e memória do backend  
**Testing**: pytest (`tests/unit/test_b3_parser.py`)  
**Target Platform**: Navegador Web moderno (Chrome/Firefox/Edge) + Servidor local Uvicorn  
**Project Type**: Web Application (FastAPI + Vanilla JS SPA)  
**Performance Goals**: Leitura e cálculo de 1.000 movimentações em menos de 150ms  
**Constraints**: Zero look-ahead bias; conformidade estrita com a fórmula de preço médio da Receita Federal; preservação integral da aba Visão Geral  
**Scale/Scope**: 693 movimentações atuais, 22 ativos em custódia, R$ 683,39 em proventos  

## Constitution Check

- [x] **I. Arquitetura 100% Python (FastAPI) + Web SPA**: Implementação em `src/data_loader/b3_parser.py`, exposta via FastAPI em `src/api/` e consumida em `src/web/app.js`.
- [x] **II. Rigor Financeiro**: Cálculo rigorosamente cronológico do preço médio (sem viés de antecipação). Vendas não afetam o preço médio unitário das cotas remanescentes.
- [x] **III. Robustez Multi-Mercado**: Identificação e sufixação automática (`.SA`) para Ações, FIIs e BDRs.
- [x] **IV. Modularidade Estrita**: Parser isolado em `data_loader`, schemas em `api/schemas.py`, rotas em `api/server.py` e renderização em `src/web/`.

## Project Structure

### Documentation (this feature)

```text
specs/018-b3-spreadsheet-integration/
├── spec.md              # Especificação de requisitos
├── plan.md              # Este plano de implementação
├── research.md          # Análise da planilha da B3 e regras contábeis
├── data-model.md        # Modelos Pydantic e DTOs
└── tasks.md             # Tarefas de implementação (gerado via speckit-tasks)
```

### Source Code

```text
src/
├── data_loader/
│   └── b3_parser.py             # Parser e calculador de PM/custódia B3
├── api/
│   ├── schemas.py               # Adiciona B3Holding, B3ParseResult
│   └── server.py                # Endpoints GET /api/b3/sync-local e POST /api/b3/parse
src/web/
├── index.html                   # Botão de importação .xlsx da B3 e status de sincronização
├── app.js                       # Consumo dos dados da B3 na Visão Geral e Carteira
tests/
└── unit/
    └── test_b3_parser.py        # Testes unitários do cálculo de PM e proventos
```
