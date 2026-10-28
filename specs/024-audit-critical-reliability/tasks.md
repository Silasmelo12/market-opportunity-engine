# Tasks: Confiabilidade Crítica e Experiência Operacional

**Input**: Design documents from `/specs/024-audit-critical-reliability/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`

**Tests**: Obrigatórios para cada correção P0/P1 e para os estados de borda.

**Organização**: Cada fase é uma branch cumulativa independente. O agente principal executa Git, testes e integração; implementadores atuam com escopo restrito.

## Phase 1: Setup e baseline

- [ ] T001 Confirmar branch base e estado do Git; registrar testes de baseline.
- [ ] T002 Confirmar os defeitos P0/P1 no código atual e congelar o escopo em `spec.md`.
- [ ] T003 Registrar decisões pendentes (FX, auth, benchmark DCA) em `research.md`.

## Phase 2: User Story 1 — Importação B3 confiável (P1)

**Goal**: `.xlsx` funciona em ambiente limpo, caixa fictício é removido e arquivos idênticos não duplicam renda.

**Independent Test**: importar fixture `.xlsx`; repetir o mesmo arquivo; verificar holdings, caixa e renda.

- [ ] T004 [US1] Adicionar `openpyxl` e `xlrd` ao `requirements.txt` com justificativa.
- [ ] T005 [US1] Alterar o default de `availableCash` para 0 e resetar o caixa em `applyB3ParsedResult` (`src/web/app.js`).
- [ ] T006 [US1] Deduplicar arquivos B3 idênticos por conteúdo em `parse_multiple_b3_files` (`src/data_loader/b3_parser.py`).
- [ ] T007 [US1] Atualizar a UI/toast para explicar que o caixa não veio da B3 e pode ser informado manualmente.
- [ ] T008 [US1] Adicionar testes de importação `.xlsx`, caixa zero e deduplicação de arquivo idêntico.
- [ ] T009 [US1] Executar testes unitários/E2E afetados e revisar o diff.

**Checkpoint**: importação B3 confiável e testada.

## Phase 3: User Story 2 — Simulador de acumulação correto (P1)

**Goal**: somente BUY aporta; `end_date` limita a valuation; drawdown é real e métricas sem benchmark são nulas.

**Independent Test**: cenário BUY+SELL = 1 aporte/10 cotas/R$100; `end_date` = R$150, não R$250.

- [ ] T010 [US2] Filtrar `direction == "BUY"` em `simulate_accumulation` e corrigir `num_contributions`.
- [ ] T011 [US2] Usar `close_sliced[-1]` na valuation e retornar vazio quando a janela não tiver barras.
- [ ] T012 [US2] Calcular `max_drawdown_pct` a partir da curva e tornar `dca_regular_final_value`/`alpha_vs_dca_pct` opcionais.
- [ ] T013 [US2] Alinhar `src/api/server.py` (`current_market_price`) e a UI para métricas nulas (“—”).
- [ ] T014 [US2] Adicionar testes unitários BUY+SELL, `end_date` e drawdown; testar contrato da API.
- [ ] T015 [US2] Executar testes e revisar o diff.

**Checkpoint**: simulador sem look-ahead e sem compra em venda.

## Phase 4: User Story 3 — Radar, gráficos e estados vazios honestos (P1)

**Goal**: deck/tabela coerentes, ranking renderiza e não há séries sintéticas não rotuladas.

**Independent Test**: deck 43,5% = tabela; `#plot-ranking` com barras; carteira vazia sem série de 12 meses.

- [ ] T016 [US3] Trocar `win_rate` por `historical_win_rate` no deck (`src/web/app.js`) e remover o campo extra do mock E2E.
- [ ] T017 [US3] Corrigir `renderPlotlyRanking` (variáveis de tema e trace) e adicionar fallback de erro legível.
- [ ] T018 [US3] Remover as séries sintéticas de evolução e proventos; renderizar estado vazio explícito.
- [ ] T019 [US3] Atualizar testes E2E que exigiam as 12 barras sintéticas e adicionar teste do deck/ranking.
- [ ] T020 [US3] Executar testes e revisar o diff.

**Checkpoint**: dados apresentados de forma consistente e honesta.

## Phase 5: User Story 4 — Segurança, acessibilidade e controles (P2)

**Goal**: CORS/upload limitados, abas acessíveis e controles mortos removidos/implementados.

**Independent Test**: preflight não autorizado rejeitado; upload inválido 4xx; painéis `tabpanel`; sem botões mortos.

- [ ] T021 [US4] Implementar allowlist CORS por `ALLOWED_ORIGINS` e limitar uploads por tamanho/extensão/quantidade.
- [ ] T022 [US4] Adicionar `role="tabpanel"`/`aria-labelledby` aos painéis e nomes acessíveis aos botões de ícone.
- [ ] T023 [US4] Implementar ou remover os controles mortos (Lançamento, 12M/Tudo, Expandir/Recolher, legenda do donut, modal de metas).
- [ ] T024 [US4] Adicionar testes de CORS/upload e checagens estáticas de acessibilidade/controles.
- [ ] T025 [US4] Executar testes e revisar o diff.

**Checkpoint**: operação mais segura e interface previsível.

## Phase 6: Polish e entrega

- [ ] T026 Atualizar documentação de execução em `docs/audit-execution-report.md`.
- [ ] T027 Atualizar contagens/README apenas se os números mudarem e houver evidência.
- [ ] T028 Executar suíte completa, inspeção visual e revisão final do diff.
- [ ] T029 Confirmar estado do Git, branches e commits; não fazer push/merge.

## Dependencies & Execution Order

- T004–T009 dependem de T001–T003.
- T010–T015 dependem de T009 (branch cumulativa).
- T016–T020 dependem de T015.
- T021–T025 dependem de T020.
- T026–T029 dependem de T025.
- Nenhum implementador com escrita atua em paralelo sobre os mesmos arquivos.
- Revisão independente é obrigatória antes de cada commit.

## Out of Scope

- Conversão cambial, autenticação corporativa, redesenho amplo e remoção do Streamlit.
