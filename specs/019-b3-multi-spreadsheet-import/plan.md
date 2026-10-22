# Implementation Plan: B3 Multi-Spreadsheet Import & Production Cleanup

**Branch**: `019-b3-multi-spreadsheet-import` | **Date**: 2026-10-22 | **Spec**: [specs/019-b3-multi-spreadsheet-import/spec.md](specs/019-b3-multi-spreadsheet-import/spec.md)

**Input**: Feature specification from `specs/019-b3-multi-spreadsheet-import/spec.md`

## Summary

Expandir o motor de parsing da B3 (`b3_parser.py`) para suportar tanto planilhas de **Movimentação** quanto de **Negociação - Resumo**, permitindo o upload simultâneo de múltiplos arquivos através de um único botão na interface web com consolidação automática de custódia e proventos. Remover elementos de sincronização local de servidor (`Sincronizar B3`) preparando a aplicação para deploy em produção.

## Technical Context

**Language/Version**: Python 3.11+ / 3.13  
**Primary Dependencies**: FastAPI, Pydantic, pandas, openpyxl, TailwindCSS  
**Testing**: pytest (`tests/unit/test_b3_parser.py`)  
**Target Platform**: Navegador Web moderno + Servidor Web em produção  
**Performance Goals**: Leitura combinada de múltiplos arquivos (< 1.5s total)  
**Constraints**: Zero look-ahead bias; conformidade contábil; idempotência na mesclagem de arquivos.  

## Constitution Check

- [x] **I. Arquitetura Python (FastAPI) + Web SPA**: Backend em FastAPI com processamento assíncrono de lista de arquivos; frontend SPA vanilla responsivo.
- [x] **II. Rigor Financeiro**: Tratamento adequado de quantidades líquidas e preços médios informados oficialmente pela B3.
- [x] **III. Robustez Multi-Mercado**: Normalização de tickers fracionários (`AZTE3F` -> `AZTE3.SA`) e sufixação `.SA`.
- [x] **IV. Modularidade Estrita**: Parser isolado em `data_loader`, DTOs em `schemas.py`, endpoint em `server.py`.

## Project Structure

### Documentation (this feature)

```text
specs/019-b3-multi-spreadsheet-import/
├── spec.md
├── plan.md
├── research.md
└── tasks.md
```

### Source Code

```text
src/
├── data_loader/
│   └── b3_parser.py             # Suporte a Negociação - Resumo e parse_multiple_b3_files
├── api/
│   └── server.py                # Endpoint POST /api/b3/parse aceitando List[UploadFile]
src/web/
├── index.html                   # Remoção do botão de sync local e adição de multiple no file input
└── app.js                       # Upload de múltiplos arquivos com FormData
tests/
└── unit/
    └── test_b3_parser.py        # Testes de negociação e combinação múltipla
```
