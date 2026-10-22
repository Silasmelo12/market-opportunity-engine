# Tasks: B3 Multi-Spreadsheet Import & Production Cleanup

**Input**: Design documents from `specs/019-b3-multi-spreadsheet-import/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tarefas executáveis em paralelo (arquivos distintos, sem dependências diretas)
- **[Story]**: Mapeamento para história de usuário (`US1`, `US2`, `US3`)

---

## Phase 1: Foundational & Backend Parser Support

- [x] T001 [US2] Implementar parser específico para planilhas de `Negociação - Resumo` da B3 em `src/data_loader/b3_parser.py`
- [x] T002 [US1] Implementar função `parse_multiple_b3_files` em `src/data_loader/b3_parser.py` que mescla cronologicamente movimentações e consolida posições com negociações
- [x] T003 [US1] Atualizar endpoint `POST /api/b3/parse` em `src/api/server.py` para receber múltiplos arquivos (`files: List[UploadFile] = File(...)`)

---

## Phase 2: Frontend Multi-Upload & Production Cleanup

- [x] T004 [US3] Remover o botão "Sincronizar B3" (`btn-portfolio-sync-b3`) e referências locais de disco em `src/web/index.html` e `src/web/app.js`
- [x] T005 [US1] Adicionar atributo `multiple` ao input `#portfolio-csv-file-input` em `src/web/index.html`
- [x] T006 [US1] Atualizar função `uploadMultipleB3Spreadsheets(files)` em `src/web/app.js` para enviar todos os arquivos selecionados no mesmo FormData

---

## Phase 3: Testes e Validação Final

- [x] T007 [P] [US1] Criar testes unitários em `tests/unit/test_b3_parser.py` cobrindo o arquivo de negociação e o upload combinado de múltiplos arquivos
- [x] T008 Executar suite completa `python -m pytest tests/unit/test_b3_parser.py`
- [ ] T009 Commit final na branch `019-b3-multi-spreadsheet-import`
