# Research: Confiabilidade Crítica e Experiência Operacional

## Decisões confirmadas no código

### B3 `.xlsx`

`src/data_loader/b3_parser.py` usa `pd.read_excel` em `_read_b3_dataframe` (`:535-537` e `:545-546`). `requirements.txt` não declara `openpyxl` nem `xlrd`; o endpoint retorna 400/500 no ambiente declarado. A correção segura é declarar as duas dependências de leitura, mantendo o comportamento atual.

### Caixa após importação B3

`src/web/app.js:3712` inicializa `availableCash: 10000.0`; `applyB3ParsedResult` (`:4033-4052`) substitui holdings/renda/timeline, mas não o caixa. O caixa não faz parte do contrato de importação B3. A decisão segura é usar zero como default e resetar o caixa na importação, deixando o campo editável.

### DCA e `end_date`

`simulate_accumulation` agrupa sinais sem filtrar direção (`:476-482`) e usa `series.close[-1]` (`:458`, `:490`). `optimize_dca_strategies` já filtra BUY (`:734-739`), mas a função pública não. A correção deve ser feita na função pública para proteger todos os chamadores.

### Radar

O schema entrega `historical_win_rate` (`src/api/schemas.py:127`), mas o deck usa `win_rate` (`src/web/app.js:2215`). O mock E2E fornece os dois campos (`tests/e2e/test_dashboard_navigation.py:901-902`), mascarando o defeito.

### Ranking

`renderPlotlyRanking` usa `chartFontColor` e `chartGridColor` antes de defini-los e passa `[trace]` sem construir `trace` (`src/web/app.js:2657-2675`). O catch silencia o erro no console, deixando o container vazio.

### Dados sintéticos

`src/web/app.js:1617-1625` gera 12 pontos de evolução quando não há timeline; `src/web/modules/proventos.js:48-50` usa uma série fixa de proventos. O E2E de proventos exige 12 barras (`tests/e2e/test_proventos_layout.py:123,133-134,150`), institucionalizando o fallback. A correção é exibir estado vazio explícito e atualizar o teste.

### CORS e upload

`src/api/server.py:88-93` usa `allow_origins=["*"]` com credenciais. O endpoint `/api/b3/parse` lê o arquivo inteiro sem limite (`:1851`) e não valida extensão. A correção segura é allowlist por ambiente, limite de tamanho, extensões permitidas e limite de arquivos.

### Acessibilidade

Os painéis de aba não têm `role="tabpanel"` nem `aria-labelledby`; os controles de aba usam `aria-controls`. A correção é adicionar os atributos aos painéis existentes, sem alterar IDs/rotas.

## Decisões pendentes (não implementar agora)

- **Conversão cambial BRL/USD**: não há campo de moeda nem fonte/taxa definida. Implementar uma taxa inventada violaria a integridade financeira. Fica registrado como bloqueio de produto.
- **Autenticação**: não há modelo de usuário/deploy definido. Limitar CORS e uploads é seguro; inventar login/token quebraria o fluxo atual.
- **Benchmark DCA**: não há periodicidade/índice definido. Exibir `null`/“—” é mais honesto do que manter 0,0.
- **Oversell B3**: o parser trunca vendas acima da posição; a correção exige definir se deve ser erro, warning ou reconciliação. Não alterar sem requisito.
