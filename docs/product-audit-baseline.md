# Auditoria de Baseline — Produto, UI, Arquitetura e Integridade Financeira

**Data:** 2026-10-27  
**Branch de auditoria:** `audit/product-ui-baseline-20261027`  
**Commit-base:** `c0f0b782c5f0be921650ba38ce948a01d5af9dbb` (`docs(023): T067 auditar commits das tarefas`)  
**Modo:** somente leitura — nenhum código-fonte, configuração ou dependência foi alterado nesta fase.  
**Ambiente de execução:** Linux, Python 3.14.4 (`./venv`), FastAPI/Uvicorn em `http://127.0.0.1:8123`, Chromium via Playwright, viewports 1440×900 e 375×812.

---

## 1. Sumário executivo

A plataforma tem uma **base visual consistente e uma suíte de testes que passa**, mas ainda **não está pronta para decisões financeiras reais nem para exposição pública**. A auditoria encontrou problemas que afetam diretamente o dinheiro exibido ao usuário e a confiança nos backtests:

1. **A importação de planilhas B3 em `.xlsx` está quebrada no ambiente declarado** porque `openpyxl` não está em `requirements.txt`. O endpoint retorna HTTP 400 e o `sync-local` retorna HTTP 500.
2. **Após importar uma carteira B3, o sistema mantém R$ 10.000,00 de caixa fictício**, inflando o patrimônio total. Em reprodução controlada, uma posição de custo R$ 300,00 passou a exibir patrimônio de R$ 10.527,90.
3. **O simulador de acumulação (DCA) compra em sinais de VENDA** e conta esses sinais como aportes. Em reprodução, um cenário com 1 compra e 1 venda gerou 2 aportes e 18,3333 cotas, em vez de 1 aporte e 10 cotas.
4. **O filtro `end_date` não é respeitado na valuation do simulador de acumulação**: a equity final usa `close[-1]` da série inteira, incorporando preços futuros ao período solicitado. Em reprodução, um corte em 2024-01-03 retornou R$ 250,00 em vez de R$ 150,00.
5. **Não há conversão cambial**: ativos em BRL (B3) e em USD (EUA/cripto) são somados como se estivessem na mesma moeda, tornando patrimônio, pesos, retorno e alpha semanticamente inválidos em carteiras mistas.

Além disso, há **dados fabricados sem rótulo de demonstração** (série de proventos hardcoded e gráfico sintético de 12 meses), **KPIs de simulador fixos/enganosos** (drawdown sempre 0, alpha vs. DCA sempre 0), **controles de UI mortos**, **gráfico de ranking que não renderiza** e **postura de segurança inadequada para produção** (sem autenticação, CORS refletindo qualquer origem com credenciais, upload sem limite e CDN sem SRI).

### Veredito por dimensão

| Dimensão | Veredito | Comentário |
|---|---|---|
| Produto / onboarding | 🔴 Bloqueado | Importação B3 `.xlsx` quebrada e caixa fictício de R$ 10 mil. |
| UI / responsividade | 🟡 Bom baseline | 8 áreas sem overflow horizontal em 1440 e 375; temas e foco visível presentes. |
| Acessibilidade | 🟡 Parcial | Falta `role="tabpanel"`/`aria-labelledby`; apenas 8 de 72 botões têm `aria-label`. |
| Arquitetura | 🟡 Dívida relevante | `app.js` com 4.843 linhas; legado Streamlit ainda presente; código morto. |
| Integridade financeira | 🔴 Crítico | DCA compra em SELL, `end_date` ignorado, mistura BRL/USD e fallback para custo. |
| Testes | 🟡 Verde, mas com lacunas | 166 passed + 2 skipped; os 2 skips escondem justamente o caminho B3 `.xlsx`. |
| Segurança | 🔴 Não pronta para produção | Sem auth, CORS permissivo, upload sem limites, CDN sem SRI. |
| Spec Kit / governança | 🟡 Inconsistente | Drift report parou na spec 017; spec 023 segue “Draft” com 67 tarefas concluídas. |

### Contagem de achados

| Severidade | Quantidade | Significado |
|---|---:|---|
| **P0** | 5 | Bloqueia uso real, corrompe valores financeiros ou viola princípio não-negociável. |
| **P1** | 8 | Funcionalidade central incorreta/enganosa ou risco de segurança relevante. |
| **P2** | 8 | Dívida relevante, acessibilidade, governança e manutenibilidade. |
| **P3** | 5 | Polimento, documentação e higiene técnica. |

---

## 2. Escopo, método e limitações

### 2.1 Em escopo

- Produto: proposta, jornadas de onboarding, carteira, proventos, radar, gráfico, simulador e playbook.
- UX/UI: consistência visual, responsividade, estados vazios, controles e acessibilidade básica.
- Arquitetura: organização do frontend/backend, dependências, legado e acoplamentos.
- Integridade financeira: cálculo de patrimônio, preço médio, proventos, DCA, rebalanceamento, câmbio e janelas temporais.
- Testes: unitários, E2E, skips, mocks e lacunas de cobertura.
- Segurança: autenticação, CORS, upload, cadeia de suprimentos e exposição de erros.
- Spec Kit: constituição, spec ativa, tasks, drift report, integração e scripts.

### 2.2 Fora de escopo

- Correções, refatorações, redesign, instalação de dependências ou alteração de configuração.
- Teste de carga, penetração, SAST/DAST e auditoria de dependências com ferramentas externas.
- Validação de preços contra fontes de mercado em tempo real além das cotações retornadas pela própria API.
- Execução de ordens reais ou integração com corretora (a plataforma é analítica).
- Deploy em produção e validação no Render.

### 2.3 Método e evidências

1. Inspeção estática do código com `grep`/leitura de arquivos e coleta de `file:line`.
2. Execução da suíte existente com o `./venv` fornecido, sem instalar nada.
3. Sondagem dos endpoints com `curl` no servidor local.
4. Navegação real com Playwright nas 8 áreas, em desktop e mobile, com captura de screenshots e de console.
5. Reproduções controladas em scripts temporários fora do repositório (`/tmp/opencode/verify_*.py`).
6. Leitura dos artefatos Spec Kit (`.specify/`, `specs/023-professional-ui-layout/`).

**Artefatos visuais (fora do repositório):**
- Screenshots: `/tmp/opencode/audit-shots/` (16 imagens: 8 áreas × 2 viewports).
- Evidência estruturada: `/tmp/opencode/audit-visual.json`.

### 2.4 Limitações

- A suíte E2E usa mocks de API em vários cenários; portanto, “33 passed” não prova integração real de todos os fluxos.
- Os 2 testes B3 foram pulados por nomes de fixture divergentes; o caminho real de `.xlsx` não foi exercitado.
- Não foi possível abrir os `.xlsx` locais porque `openpyxl` não está instalado no ambiente; a falha foi confirmada pela API.
- A análise de acessibilidade foi estática e comportamental básica; não houve execução de axe-core, leitor de tela ou teste com usuários.
- A análise de segurança não substitui um pentest; não houve teste de carga/DoS nem revisão de infraestrutura de deploy.
- Valores de mercado observados em reproduções vieram da API local/cache e podem variar; os defeitos apontados são de lógica, não de cotação.
- O relatório não altera nem valida as escolhas de produto (ex.: se “caixa não informado” deve ser 0 ou “—”).

---

## 3. Baseline do repositório e ambiente

### 3.1 Estado do Git

- Branch de trabalho: `audit/product-ui-baseline-20261027`, criada a partir de `feat/professional-ui-layout`.
- Commit-base: `c0f0b78`; `69` commits à frente de `origin/main`; `0` atrás.
- Nenhuma modificação rastreada no início da auditoria.
- Arquivos não rastreados pré-existentes preservados:
  - `B3/`
  - `graphify-out/`
  - `imagens modelo/`
  - `minha_carteira - Copia.csv`
  - `minha_carteira.csv`
  - `scratch/`
- Nenhum `git reset`, `clean`, `stash`, `push` ou `merge` foi executado.

### 3.2 Ambiente declarado vs. ambiente local

| Item | Declarado | Observado |
|---|---|---|
| Python | `render.yaml` → `3.11.9`; `README` → `3.11+` | `./venv` → `3.14.4` |
| Backend | FastAPI + Uvicorn | `GET /api/health` → `{"status":"ok","version":"4.0.0","cache_backend":"disk"}` |
| Planilhas B3 | `.xlsx`/`.xls`/`.csv` | `.xlsx` falha por ausência de `openpyxl` |
| Spec Kit | Integração `agy`, scripts PowerShell | `pwsh` não instalado |
| Testes | README “55 Passed”; PRODUCT “91+” | 166 passed + 2 skipped |

### 3.3 Baseline visual

As 8 áreas foram navegadas em `#carteira/visao-geral`, `#carteira/posicoes`, `#carteira/proventos`, `#carteira/patrimonio`, `#quant/radar`, `#quant/grafico`, `#quant/simulador` e `#quant/playbook`.

| Verificação | Resultado |
|---|---|
| Overflow horizontal em 1440×900 | Nenhum (`scrollWidth == clientWidth == 1440`) em todas as áreas. |
| Overflow horizontal em 375×812 | Nenhum (`scrollWidth == clientWidth == 375`) em todas as áreas. |
| Erros de página | Nenhum `pageerror`. |
| Console | 1 warning: `cdn.tailwindcss.com should not be used in production`. |
| Tema claro/escuro | Alternância funcional; tokens e foco visível presentes. |
| Navegação | Rotas canônicas funcionam; `#quant/tradingview` é alias de `#quant/grafico`, não uma 9ª área. |

**Ponto positivo:** a baseline visual é utilizável e consistente o suficiente para servir de referência de layout. Os problemas mais graves estão em dados, cálculos e segurança, não em overflow/responsividade.

---

## 4. Produto e jornadas

### 4.1 Onboarding B3: o caminho principal está bloqueado

O banner de primeiro uso convida o usuário a “Importar Extratos B3”, e o input aceita `.xlsx`, `.xls`, `.csv` e `.txt` (`src/web/index.html:1825`). Arquivos Excel são enviados ao backend (`src/web/app.js:3992-3998`), que chama `parse_b3_file` (`src/api/server.py:1857`).

**Achado P0-01 — Importação B3 `.xlsx` quebrada por dependência ausente.**

Evidências:

- `requirements.txt:1-13` não declara `openpyxl` nem `xlrd`.
- `src/api/server.py:1857` chama `parse_b3_file`, que usa `pd.read_excel` (`src/data_loader/b3_parser.py:535-537` e `:545-546`).
- Sondagem real:

```text
POST /api/b3/parse  -> HTTP 400
{"detail":"Erro ao processar planilhas B3: `Import openpyxl` failed. ..."}

GET /api/b3/sync-local -> HTTP 500
{"detail":"Erro ao processar planilha B3: `Import openpyxl` failed. ..."}
```

Impacto: o usuário não consegue importar o formato oficial mais comum da B3. O `render.yaml:7` instala apenas `requirements.txt`, então o deploy também sobe sem `openpyxl`.

Critério de aceite: em ambiente limpo, `pip install -r requirements.txt` seguido de `POST /api/b3/parse` com um `.xlsx` real retorna 200 e holdings coerentes; `GET /api/b3/sync-local` retorna 200; teste automatizado cobre o caminho `.xlsx`.

Dependências: decisão sobre suporte a `.xls` (exige `xlrd`), inclusão de fixture B3 no repositório/CI e pin de versão.

---

### 4.2 Onboarding B3: caixa fictício infla o patrimônio

**Achado P0-02 — R$ 10.000,00 de caixa padrão permanecem após a importação.**

Evidências:

- `src/web/app.js:3712` define `availableCash: 10000.0` no estado inicial.
- `applyB3ParsedResult` substitui holdings, renda e timeline, mas **não** define `availableCash` (`src/web/app.js:4048-4052`).
- O dashboard soma `cash + totalCurrentValue` (`src/web/app.js:1412-1416`).
- Reprodução controlada: após aplicar um resultado B3 com 10 PETR4 a preço médio R$ 30,00:

```text
cash: 10000
holdings: [{ticker: "PETR4.SA", shares: 10, average_buy_price: 30}]
equity: "R$ 10.527,90"
invested: "R$ 300,00"
```

Impacto: qualquer carteira importada exibe R$ 10 mil a mais de patrimônio, distorcendo rentabilidade, alocação, rebalanceamento e todos os KPIs derivados. O usuário pode não perceber, pois o campo de caixa fica em outra aba.

Critério de aceite: após importar uma carteira sem informação de caixa, o caixa deve ser `0` ou “não informado”, nunca R$ 10.000; o patrimônio deve refletir apenas os ativos importados; teste E2E importa fixture e compara equity com a soma das posições; UI solicita o caixa explicitamente.

Dependências: decisão de UX (caixa desconhecido vs. zero), fonte de cotação para valuation.

---

### 4.3 Estado vazio: dados fabricados sem rótulo

**Achado P1-02 — Série sintética de 12 meses e proventos hardcoded são exibidos como se fossem dados do usuário.**

Evidências:

- `src/web/app.js:1617-1625`: quando não há `b3Timeline`, o gráfico “Evolução do Patrimônio” gera 12 pontos artificiais (`11/25` a `10/26`) com `baseInv = max(100, totalInvested)`.
- `src/web/modules/proventos.js:48-50`: quando `b3MonthlyIncome` está vazio, o gráfico de proventos usa a série fixa `[35.20, 142.50, 38.00, 45.10, 180.20, 46.00, 52.30, 220.40, 58.10, 61.40, 245.90, 68.20]`.
- O estado vazio real (capturado em `/tmp/opencode/audit-visual.json`) mostra:
  - `Patrimônio total R$ 10.000,00`
  - `Valor investido: R$ 0,00`
  - gráfico com barras de R$ 0 a R$ 100
  - nenhum rótulo “demo”, “exemplo” ou “dados fictícios”.
- O próprio E2E institucionaliza o fallback: `tests/e2e/test_proventos_layout.py:123` exige 12 barras e `:133-134,150` exigem os labels `11/25…10/26` quando não há dados.

Impacto: o primeiro contato do usuário mostra números que parecem reais. Isso é especialmente grave em produto financeiro e mina a confiança quando o usuário descobre que a série é sintética.

Critério de aceite: estados vazios exibem zeros, gráfico vazio e CTA (“Importe seus extratos”); a série hardcoded é removida ou explicitamente rotulada como demonstração; teste E2E garante que nenhum valor sintético aparece sem rótulo.

Dependências: decisão de produto sobre existência de “modo demo”.

---

### 4.4 Proventos: dados e agregação

Além da série hardcoded (P1-02), a lógica de agregação de proventos tem dois problemas de integridade:

**Achado P1-05 — Renda passiva é somada por arquivo, sem deduplicação, e vendas acima da posição são truncadas silenciosamente.**

Evidências:

- `src/data_loader/b3_parser.py:891`: `total_income = round(sum(item[3].total_income for item in loaded), 2)`.
- O comentário seguinte (`:893`) assume “Income is always additive across files”, mas não há deduplicação por evento/data/ticker.
- Reprodução com o mesmo CSV enviado duas vezes:

```text
1 file  -> total_income = 10.0
2 files -> total_income = 20.0
```

- `src/data_loader/b3_parser.py:770`: `new_qty = max(0.0, current["shares"] - qty)` — uma venda maior que a posição é truncada em zero, sem aviso.

Impacto: exportações B3 sobrepostas (ex.: um arquivo cumulative e um mensal) duplicam proventos; arquivos incompletos escondem inconsistências de custódia.

Critério de aceite: eventos de renda deduplicados por chave estável (data, ticker, tipo, valor) ou arquivos duplicados rejeitados com mensagem; venda acima da posição gera warning/erro explícito; testes cobrem duplicidade e oversell.

Dependências: metadados de período dos arquivos B3, decisão sobre tolerância a arquivos sobrepostos.

---

### 4.5 Radar: deck executivo sempre mostra 0,0% WR

**Achado P1-04 — O deck usa `win_rate`, mas a API entrega `historical_win_rate`.**

Evidências:

- `src/web/app.js:2215-2219` ordena e formata por `win_rate`.
- O schema do item de radar declara `historical_win_rate` (`src/api/schemas.py:127`) e o servidor preenche esse campo (`src/api/server.py:761,799,841,880`).
- Evidência visual real: o deck mostra `VALE3.SA — 0.0% WR`, enquanto a tabela logo abaixo mostra `VALE3.SA — 43,5%`.
- O mock E2E fornece **os dois campos** (`tests/e2e/test_dashboard_navigation.py:901-902`), mascarando o defeito.

Impacto: o “ativo de maior assimetria” é escolhido por um campo inexistente (ordem arbitrária) e o WR exibido é sempre 0,0%.

Critério de aceite: usar `historical_win_rate` com fallback explícito; remover `win_rate` dos mocks; teste E2E afirma que o deck mostra o mesmo WR da tabela (ex.: 43,5%).

Dependências: nenhuma.

---

### 4.6 Simulador: resultados materialmente incorretos

Os achados P0-03, P0-04 e P1-03 estão detalhados na seção 7. Em resumo:

- DCA compra em SELL.
- `end_date` não é respeitado na valuation.
- Drawdown, alpha vs. DCA e valor final do DCA são fixos/derivados de forma enganosa.

---

## 5. UX/UI, responsividade e acessibilidade

### 5.1 Pontos fortes

- 8 áreas com hierarquia visual consistente, tokens de tema e componentes reutilizáveis.
- Sem overflow horizontal nas duas larguras testadas.
- `:focus-visible` implementado para botões, links, inputs, selects, textareas, `[role="button"]`, `[role="tab"]` e `[tabindex]` (`src/web/styles.css:318-331`).
- `prefers-reduced-motion` respeitado (`src/web/styles.css:1394`).
- `lang="pt-BR"` e viewport corretos (`src/web/index.html:2-5`).
- Loading com `role="status"` e `aria-live="polite"` (`src/web/index.html:239`), toasts idem (`:2142`).

### 5.2 Controles mortos

**Achado P2-01 — Botões visíveis sem handler ou sem alvo no DOM.**

| Controle | Evidência | Situação |
|---|---|---|
| “Lançamento” no header | `src/web/index.html:182` | Nenhuma referência em `app.js`; clique não faz nada. |
| “12M” / “Tudo” | `src/web/index.html:348-349` | Sem `id`, sem handler; não alteram o gráfico. |
| “Expandir Todos” / “Recolher Todos” | `src/web/index.html:1702-1705` | Nenhuma referência em `app.js`. |
| Legenda do donut | `src/web/index.html:367` | Container existe, mas `app.js` procura `leg-pct-*` e `overview-top-asset-label`, que não existem no HTML. |
| Modal de Metas | `src/web/index.html:2156` | `setupOverviewMetasModal` exige `btn-edit-metas` (`src/web/app.js:1982`), ausente do HTML; o modal nunca abre. |
| Botões legados da visão geral | `src/web/app.js:163,183,190,219,243` | Referenciam `btn-overview-refresh`, `btn-overview-open-radar`, `btn-overview-apply-orders`, `btn-overview-import-csv`, `btn-overview-goto-radar`; nenhum existe no HTML. |

Impacto: o usuário percebe a interface como “quebrada” em pontos de ação óbvios. A legenda do donut fica permanentemente vazia.

Critério de aceite: cada controle visível tem handler e teste de clique, ou é removido; o modal de metas é acessível por um botão existente; a legenda do donut é preenchida por IDs existentes.

Dependências: decisão de produto sobre quais controles manter.

### 5.3 Acessibilidade

**Achado P2-02 — Semântica de abas incompleta e poucos rótulos acessíveis.**

Evidências:

- Os painéis (`#tab-overview`, `#tab-pane-radar`, `#tab-terminal`, etc.) não têm `role="tabpanel"` nem `aria-labelledby`; não há nenhum `role="tabpanel"` no HTML.
- As abas usam `role="tab"` e `aria-controls`, mas o painel correspondente não declara o papel.
- Há 72 elementos `<button>` e apenas 8 deles com `aria-label` (12 ocorrências de `aria-label` no HTML); parte dos botões é textual, mas ícones e ações compactas dependem de rótulo.
- O modal de metas não tem `role="dialog"`, `aria-modal="true"` ou foco inicial/trap.

Impacto: leitores de tela podem não anunciar corretamente a relação aba/painel; navegação por teclado existe, mas a semântica fica incompleta.

Critério de aceite: cada aba tem `aria-controls` apontando para um painel com `role="tabpanel"` e `aria-labelledby`; botões somente-ícone têm `aria-label`; modal tem `role="dialog"`, `aria-modal` e gestão de foco; teste automatizado com axe ou checagem estática.

Dependências: nenhuma; pode ser feito junto com P2-01.

### 5.4 Polimento visual

**Achado P3-02 — Classe de backdrop inválida nos modais.**

- `src/web/index.html:2083` e `:2156` usam `surface-canvas/80`. `surface-canvas` é uma classe customizada (`.surface-canvas` em `src/web/styles.css:2398`), e o sufixo `/80` não gera utilitário Tailwind. O backdrop pode ficar sem cor/opacidade.
- Critério de aceite: usar `bg-slate-900/80` ou utilitário equivalente; validar visualmente.

---

## 6. Arquitetura e qualidade de código

### 6.1 Estrutura atual

- Backend: `src/api/` (FastAPI, schemas, cache), `src/data_loader/`, `src/evaluator/`, `src/strategies/`.
- Frontend: `src/web/` com `index.html` (2.191 linhas), `styles.css` (2.656 linhas), `app.js` (4.843 linhas) e 4 módulos pequenos (`constants.js`, `formatters.js`, `toast.js`, `proventos.js`).
- Legado: `src/app.py`, `src/ui/` (Streamlit) e dependências `streamlit`/`streamlit-lightweight-charts` em `requirements.txt:11-12`.

**Achado P2-07 — Monólito de frontend e código legado convivendo com a arquitetura declarada.**

Evidências:

- `app.js` concentra navegação, charts, radar, simulador, carteira, B3, modais e utilidades.
- A modularização da spec 022 extraiu apenas 4 módulos; o núcleo permanece monolítico.
- A constituição declara Streamlit como legado que “NÃO DEVE receber novas funcionalidades” (`.specify/memory/constitution.md`), mas ele continua no requirements de produção e em `src/ui/`.
- Há 40 IDs referenciados por `getElementById` em `app.js` que não existem no HTML estático (ex.: `overview-total-profit`, `overview-best-asset`, `meta-patrimonio-atual`); parte pode ser gerada dinamicamente, mas o conjunto indica código morto/legado de versões anteriores da visão geral.

Impacto: manutenção cara, risco de regressão em qualquer alteração e confusão sobre qual é o caminho oficial.

Critério de aceite: remover código morto e IDs órfãos; decidir formalmente o destino do Streamlit (remoção ou isolamento em `requirements-dev`/diretório legado); dividir `app.js` por domínio com contratos claros.

Dependências: decisão de produto/engenharia sobre o legado Streamlit; esforço de refatoração não trivial.

### 6.2 Dependências de produção

**Achado P2-08 — `pytest` e `streamlit` no requirements de produção.**

- `requirements.txt:10-12` inclui `pytest`, `streamlit` e `streamlit-lightweight-charts` no runtime.
- `requirements-dev.txt` já existe para Playwright, mas não separa o resto.
- Critério de aceite: `requirements.txt` apenas runtime; `requirements-dev.txt` com pytest/playwright; Streamlit removido ou movido para extra legado.

Dependências: P2-07.

### 6.3 Acoplamentos e contratos

- A API orquestra os motores, mas o frontend conhece muitos detalhes de resposta e mantém fallbacks próprios (ex.: `currentP = avgP` em `app.js:1371`), duplicando regras financeiras.
- `src/web/app.js` mistura dados de apresentação com cálculo de patrimônio, P&L e alocação.
- Critério de aceite: mover regras financeiras para o backend ou para um módulo único testável; frontend apenas renderiza contratos.

---

## 7. Integridade dos dados financeiros

Esta é a área de maior risco. Os achados abaixo foram confirmados por leitura de código e, quando indicado, por reprodução controlada.

### 7.1 DCA compra em sinais de venda

**Achado P0-03 — `simulate_accumulation` ignora a direção do sinal.**

Evidências:

- `src/evaluator/accumulation_simulator.py:476-482`: itera **todos** os sinais do agrupamento e adiciona cotas para cada `execution_price > 0`, sem filtrar `sig.direction == "BUY"`.
- `src/evaluator/accumulation_simulator.py:507`: `num_contributions=len(strat_signals)`, contando também sinais SELL e sinais sem execução válida.
- O endpoint `/api/simulate` no modo `accumulation` passa `signals` sem filtro de direção (`src/api/server.py:1176-1182`).

Reprodução:

```text
Série: [10, 12, 11]
Sinais: BUY @10 na barra 0; SELL @12 na barra 1
Aporte: R$ 100
Resultado observado: total_invested=200, total_shares=18.3333, num_contributions=2
Resultado esperado: total_invested=100, total_shares=10, num_contributions=1
```

Impacto: backtests de acumulação superestimam aportes e cotas sempre que a estratégia selecionada emite SELL; rankings de “melhor DCA” ficam inválidos.

Critério de aceite: somente sinais `BUY` geram aporte; `num_contributions` conta apenas aportes efetivos; teste unitário com BUY+SELL afirma 1 aporte/10 cotas/R$ 100; teste de API no modo accumulation.

Dependências: nenhuma.

### 7.2 `end_date` ignorado na valuation

**Achado P0-04 — Equity final usa o último close da série inteira, não o último close da janela.**

Evidências:

- `src/evaluator/accumulation_simulator.py:458`: `current_price = float(series.close[-1])`.
- `src/evaluator/accumulation_simulator.py:490`: `final_equity = total_shares * current_price`.
- `src/api/server.py:1242`: `current_market_price` também usa `series.close[-1]`.
- O mesmo padrão aparece em `optimize_strategy_pairs` (`src/evaluator/accumulation_simulator.py:559`).

Reprodução:

```text
Série: [10, 10, 15, 20, 25]
Sinal: BUY @10 na barra 1
end_date: 2024-01-03 (barra de close 15)
Resultado observado: current_price=25, current_equity=250
Resultado esperado: current_price=15, current_equity=150
```

Impacto: o simulador incorpora preços futuros ao período solicitado, violando o princípio de **Zero Look-Ahead Bias** da constituição (Princípio II) e inflando resultados históricos.

Critério de aceite: valuation usa `close_sliced[-1]` (último bar dentro da máscara); `current_market_price` idem; teste com `end_date` afirma R$ 150; teste anti-look-ahead garante que nenhum dado posterior ao corte influencia o resultado.

Dependências: nenhuma.

### 7.3 Mistura de moedas sem câmbio

**Achado P0-05 — BRL e USD são somados como se fossem a mesma unidade.**

Evidências:

- `src/evaluator/portfolio_simulator.py:972-974`: `inv = sum(h.shares * h.current_price ...)` e `return cash + inv`, sem moeda.
- `src/evaluator/portfolio_simulator.py:421`: `cur_p` vem do profile do ativo, sem normalização cambial.
- `advise_portfolio_rebalance` calcula `current_holdings_value` e `total_equity` com a mesma soma (`src/evaluator/portfolio_simulator.py:435-440`).
- Não há campo de moeda/FX nos schemas de holdings/profiles; `USDBRL=X` aparece apenas como ticker de forex (`src/api/server.py:618`), não como taxa de conversão.
- O universo do radar inclui B3 (BRL), EUA (USD), cripto (USD) e commodities (USD) no mesmo fluxo.

Impacto: uma carteira com PETR4 (R$) e AAPL (US$) tem patrimônio, pesos, retorno e alpha sem significado; o rebalanceamento pode sugerir compras/vendas com base em unidades incompatíveis.

Critério de aceite: definir moeda-base (BRL ou USD) e converter cada ativo com taxa explícita e data; ou rejeitar carteiras mistas com erro claro; exibir moeda e taxa na UI; testes com PETR4.SA + AAPL e com USDBRL=X.

Dependências: fonte de câmbio (yfinance `USDBRL=X`, BCB ou outra), decisão de produto sobre moeda-base e data de referência.

### 7.4 Fallback de cotação para o custo

**Achado P1-01 — Ausência de cotação vira “preço = custo”, escondendo perdas.**

Evidências:

- `src/web/app.js:1369-1386`: `currentP = avgP`; se não há quote nem recomendação, `hasValidMarketQuote = false`, mas `curVal = shares * currentP` continua usando o custo; o ativo entra no total e no P&L com 0%.
- `src/evaluator/portfolio_simulator.py:421`: `cur_p = prof.current_price if ... else avg_p`.
- O contador `missingQuotesCount` é exibido como aviso, mas o valor financeiro já foi contaminado.

Impacto: ativos sem cotação parecem “no zero a zero”, e o patrimônio é subestimado/estabilizado artificialmente; perdas reais ficam invisíveis.

Critério de aceite: ausência de cotação produz `null`/“sem cotação”, exclui o ativo de P&L e de pesos (ou usa último preço conhecido com flag explícita), sem fallback silencioso para custo; teste E2E com quote ausente afirma “—” e aviso.

Dependências: contrato de resposta de quotes, decisão de UX.

### 7.5 KPIs de simulador fixos ou enganosos

**Achado P1-03 — Drawdown, alpha vs. DCA e valor final do DCA não são calculados de fato.**

Evidências:

- `src/api/server.py:1237-1244` (modo accumulation):
  - `max_drawdown_pct: 0.0`
  - `dca_regular_final_value: round(final_equity, 2)`
  - `alpha_vs_dca_pct: 0.0`
  - `xirr_annualized_pct: None`
- `src/evaluator/accumulation_simulator.py:769-772` (ranking DCA): `max_drawdown_pct=0.0`, `win_rate_pct=100.0 if net_profit > 0 else 0.0`.
- A UI exibe esses campos (`src/web/app.js:3158-3167`).

Impacto: o usuário vê “drawdown 0%” e “alpha 0” como se fossem medições, quando são placeholders; a comparação “estratégia vs. DCA” é tautológica.

Critério de aceite: calcular drawdown a partir da `timeline_equity`; calcular um benchmark DCA real ou retornar `null` e ocultar o card; win rate baseado em trades fechados, não em sinal do P&L; testes com série volátil.

Dependências: definição do benchmark DCA e da janela de comparação.

### 7.6 Outros riscos financeiros

- **Preço médio em vendas parciais:** o parser zera o custo quando a posição chega a zero, mas não ajusta o custo realizado; não há P&L realizado no resultado B3. (P2)
- **Proventos e rendimentos:** a classificação por substring (`"dividendo"`, `"juros sobre capital"`, `"rendimento"`) pode capturar tipos ambíguos; não há validação de sinal/valor. (P2)
- **Timeline B3:** `_build_timeline_from_events` usa `max(0, cumulative + flow)` (`src/data_loader/b3_parser.py:816`), truncando fluxos negativos e podendo mascarar inconsistências. (P2)
- **Simulador de carteira:** usa `last_known_close` para ativos sem negociação no dia (`src/evaluator/portfolio_simulator.py:984-987`), o que é defensável, mas não há flag de “preço carregado” no resultado. (P3)

---

## 8. Backend, APIs e dados

### 8.1 Inventário

O backend expõe 12 rotas (11 de domínio + health):

| Rota | Uso |
|---|---|
| `GET /api/health` | Health check. |
| `GET /api/strategies` | Catálogo de estratégias. |
| `GET /api/analyze` | Análise de um ticker. |
| `GET /api/radar` | Varredura paginada. |
| `GET /api/tickers` | Universo de tickers. |
| `POST /api/simulate` | Backtest cycle/accumulation. |
| `POST /api/simulate/optimize` | Otimização de combinações. |
| `POST /api/portfolio/advise` | Plano de rebalanceamento. |
| `POST /api/portfolio/simulate` | Backtest multiassets. |
| `POST /api/portfolio/quotes` | Cotações com cache. |
| `GET /api/b3/sync-local` | Leitura de `B3/` local. |
| `POST /api/b3/parse` | Upload/parse B3. |

### 8.2 Cache e disponibilidade

- `GET /api/health` retorna `cache_backend: "disk"`, indicando fallback funcional sem Redis.
- O cache é usado em cotações e varreduras; não foi observado erro de indisponibilidade no baseline.
- Ponto positivo: a constituição exige fallback de cache e ele parece existir.

### 8.3 Erros e transparência

- `POST /api/b3/parse` retorna o texto cru da exceção (`src/api/server.py:1862`), incluindo nome de pacote e instrução de instalação. Isso é útil em dev, mas vaza detalhes em produção. (P2)
- `GET /api/b3/sync-local` não trata `ImportError` de forma amigável; devolve 500. (P2)

### 8.4 Dados e normalização

- O `data_loader` normaliza tickers e sufixos; não há evidência de conversão cambial.
- O parser B3 tem boa cobertura de tipos de planilha (`negociacao_detalhada`, `negociacao_resumo`, `movimentacao`, `csv_legado`), mas o caminho `.xlsx` não roda no ambiente.
- A leitura de `.xlsx` usa `pd.read_excel` sem `sheet_name`; se o arquivo B3 tiver múltiplas abas, apenas a primeira é lida (`src/data_loader/b3_parser.py:535-537` e `:545-546`). (P2, a confirmar com fixture)

---

## 9. Testes e critérios de aceite

### 9.1 Execução

Comandos executados com o `./venv` existente, sem instalar dependências:

```bash
./venv/bin/python -m pytest tests/unit -q
# 118 passed, 2 skipped

./venv/bin/python -m pytest tests/test_double_patterns.py tests/test_normalizer_suffix.py tests/test_radar_pagination.py -q
# 15 passed

./venv/bin/python -m pytest tests/e2e -q
# 33 passed in 140.09s
```

**Total:** 166 passed, 2 skipped.  
**Tempo E2E:** ~140 s.  
**Warnings:** 3 (incluindo `on_event` deprecado do FastAPI).

### 9.2 Skips

Os 2 skips estão em `tests/unit/test_b3_parser.py`:

- `:69-71` espera `B3/movimentacao-2026-10-22-13-32-52.xlsx`.
- `:93-97` espera `B3/negociacao desde 04-08-2026.xlsx` e `B3/movimentacao desde 04-08-2026.xlsx`.

Os arquivos presentes são `B3/agosto 2026.xlsx`, `B3/julho 2026.xlsx`, `B3/junho.xlsx` e `B3/movimentacao.xlsx`. Ou seja, **o teste que validaria o caminho B3 real não roda**, e foi justamente por isso que P0-01 passou despercebido.

### 9.3 Lacunas de cobertura

| Lacuna | Evidência | Risco |
|---|---|---|
| DCA com sinal SELL | `tests/unit/test_accumulation.py:45-49` usa apenas BUY | P0-03 não detectado. |
| `end_date` na valuation | teste cita `end_date` no docstring, mas não cobre o corte (`tests/unit/test_accumulation.py:66-84`) | P0-04 não detectado. |
| Câmbio BRL/USD | nenhum teste com `currency`/`USDBRL` | P0-05 não detectado. |
| Exec deck vs. API real | mock fornece `win_rate` e `historical_win_rate` (`tests/e2e/test_dashboard_navigation.py:901-902`) | P1-04 mascarado. |
| Ranking Plotly | nenhum teste de `plot-ranking` | P1-07 não detectado. |
| B3 `.xlsx` real | skips por nome de fixture | P0-01 não detectado. |
| Proventos sem dados | `tests/e2e/test_proventos_layout.py:123,133-134,150` afirma 12 barras e os labels fixos `11/25…10/26` | P1-02 é institucionalizado pelo teste, não detectado. |
| Segurança/CORS/auth | nenhum teste de origem, auth ou limite de upload | P1-06 não detectado. |

### 9.4 Matriz de aceite dos P0/P1

| ID | Critério de aceite mínimo | Teste sugerido |
|---|---|---|
| P0-01 | `.xlsx` B3 importa em ambiente limpo | `POST /api/b3/parse` com fixture + assert 200/holdings. |
| P0-02 | Sem caixa fictício após import | E2E importa fixture e compara equity com soma das posições. |
| P0-03 | DCA só aporta em BUY | Unit com BUY+SELL: 1 aporte, 10 cotas, R$ 100. |
| P0-04 | Valuation usa último bar da janela | Unit com `end_date`: equity R$ 150, não R$ 250. |
| P0-05 | Carteira mista converte ou rejeita | Unit PETR4+AAPL com FX; assert moeda única. |
| P1-01 | Sem cotação ≠ custo | E2E com quote ausente: “—” e exclusão do P&L. |
| P1-02 | Sem dados sintéticos sem rótulo | E2E empty state: zeros + “sem dados”. |
| P1-03 | KPIs reais ou nulos | Unit com série volátil: drawdown > 0; alpha ≠ 0 quando aplicável. |
| P1-04 | Deck usa `historical_win_rate` | E2E assert 43,5% no deck e na tabela. |
| P1-05 | Renda deduplicada; oversell avisado | Unit com arquivo duplicado: total 10, não 20; oversell warning. |
| P1-06 | Auth/CORS/upload/SRI | Probes de origem, limite e headers; revisão de script tags. |
| P1-07 | Ranking renderiza | E2E assert `#plot-ranking` com dados e sem console error. |
| P1-08 | B3 `.xlsx` testado | Fixture com nome estável/glob; sem skip. |

---

## 10. Segurança e privacidade

### 10.1 Autenticação e autorização

**Achado P1-06 — Nenhuma rota exige autenticação.**

- Não há `Depends`, `APIKey`, `HTTPBearer` ou checagem de `Authorization` em `src/api/server.py`.
- Qualquer cliente que alcance a porta pode chamar `/api/analyze`, `/api/radar`, `/api/simulate`, `/api/portfolio/*` e `/api/b3/parse`.
- `render.yaml` publica o serviço (`type: web`, `startCommand: uvicorn ... --host 0.0.0.0`), sem camada de auth declarada.

Impacto: em deploy público, qualquer pessoa pode consumir a API, esgotar quota do yfinance, rodar varreduras caras e enviar arquivos; em localhost, qualquer site aberto no navegador pode chamar a API.

Critério de aceite: definir modelo de acesso (single-user local com bind `127.0.0.1`, token simples ou auth completa); proteger rotas caras; documentar no README.

### 10.2 CORS

- `src/api/server.py:88-93`: `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- Sondagem com `Origin: https://evil.example`:

```text
access-control-allow-origin: https://evil.example
access-control-allow-credentials: true
```

Impacto: o middleware reflete qualquer origem e permite credenciais; combinado com ausência de auth, amplia a superfície de ataque.

Critério de aceite: allowlist de origens (ex.: `http://localhost:8123`), `allow_credentials` apenas se necessário, métodos/headers mínimos; teste de preflight com origem não autorizada.

### 10.3 Upload

- `POST /api/b3/parse` lê o arquivo inteiro em memória (`await f.read()`, `src/api/server.py:1851`) sem limite de tamanho, tipo MIME ou número de arquivos.
- Não há validação de extensão no backend; o frontend aceita `.xlsx/.xls/.csv/.txt`, mas a API pode receber qualquer conteúdo.
- Impacto: DoS por arquivo gigante, parsing de formato inesperado e consumo de memória.

Critério de aceite: limite de tamanho (ex.: 10 MB), allowlist de extensões/MIME, limite de arquivos, rejeição precoce com 413/415.

### 10.4 Cadeia de suprimentos

- `src/web/index.html:19-23` carrega Tailwind, Lightweight Charts e Plotly de CDNs públicas **sem `integrity`/`crossorigin`**.
- O Tailwind CDN emite warning de produção.
- Impacto: comprometimento de CDN ou MITM pode injetar script na SPA; ausência de SRI impede verificação de integridade.

Critério de aceite: vendorizar os assets ou usar SRI com versões fixas; remover Tailwind CDN em produção (build estático).

### 10.5 Exposição de erros e segredos

- Erros de B3 retornam texto cru (`src/api/server.py:1862`).
- Não foram encontrados segredos, `.env`, chaves ou tokens no repositório (`grep` por `api_key|secret|password|token` em `src/` não retornou ocorrências).
- Ponto positivo: não há credenciais hardcoded evidentes.

Critério de aceite: mensagens de erro genéricas para o cliente, log detalhado no servidor; revisão periódica de segredos.

---

## 11. Spec Kit, governança e documentação

### 11.1 Drift report desatualizado

**Achado P2-03 — O relatório de drift cobre apenas as specs 001–017.**

Evidências:

- `.specify/sync/drift-report.md:3` gerado em `2026-10-22`.
- `:10` declara “Specs Analyzed 17 — Specs 001 a 017”.
- `:12-15` declara 100% alinhado e 0 drifted.
- Existem 22 diretórios em `specs/`, incluindo 018, 019, 021, 022 e 023.
- A spec ativa é 023 (`.specify/feature.json:2`), criada em 2026-10-27, depois do relatório.

Impacto: a governança afirma alinhamento total quando as specs mais recentes (incluindo a UI atual) não foram analisadas. O relatório não é confiável como gate.

Critério de aceite: regenerar o drift report incluindo 018–023; declarar lacunas; anexar data/commit; usar como gate de fechamento.

### 11.2 Status da spec 023

- `specs/023-professional-ui-layout/spec.md:5` → `Status: Draft`.
- `specs/023-professional-ui-layout/tasks.md` tem 67 tarefas marcadas `[X]` e 0 abertas, incluindo T067 de auditoria de commits.
- Impacto: o status não reflete o estado real; consumidores do Spec Kit podem tratar a feature como não implementada.

Critério de aceite: atualizar status para “Implemented”/“Done” após validação, ou reabrir tarefas se houver pendências; registrar decisão.

### 11.3 Integração e scripts

**Achado P2-04 — Integração `agy`/PowerShell incompatível com o ambiente.**

- `.specify/integration.json:4-14` declara integração `agy` e `script: "ps"`.
- `.specify/scripts/` contém apenas `powershell/*.ps1`.
- `pwsh` não está instalado no ambiente (`command -v pwsh` → vazio).
- Impacto: comandos do Spec Kit que dependem dos scripts não rodam neste ambiente; o fluxo fica dependente de Windows/PowerShell.

Critério de aceite: adicionar scripts Bash/portáveis ou documentar prerequisito `pwsh`; validar `check-prerequisites` no ambiente alvo.

### 11.4 Documentação e contagens

**Achado P2-06 — README/PRODUCT divergem da suíte real.**

- `README.md:10` → badge “Tests-55 Passed”.
- `PRODUCT.md:43` → “91+ testes”.
- Real: 166 passed + 2 skipped.
- `README.md:227` cita `test_frontend_text_has_no_mojibake` varrendo `src/web/*`; esse teste não existe (há apenas `test_no_mojibake_in_visible_text` em `tests/e2e/test_proventos_layout.py:155`).
- Impacto: métricas de qualidade e guardrails documentados não correspondem ao código.

Critério de aceite: atualizar contagens e remover/implementar a referência ao teste; gerar badge a partir da CI.

### 11.5 Versão de Python

**Achado P2-05 — Três versões conflitantes.**

- `render.yaml:11-12` → `3.11.9`.
- `README.md:6` → `3.11+`; `:158` → `3.10+`.
- `specs/023-professional-ui-layout/plan.md:15` → `Python 3.14`.
- `./venv` → `3.14.4`.
- Impacto: builds/testes podem divergir; dependências podem se comportar diferente.

Critério de aceite: definir matriz oficial (ex.: 3.11.9 em produção e CI), alinhar README/plan/render; testar na versão de produção.

---

## 12. Backlog priorizado, dependências e próximos passos

### 12.1 P0 — bloqueadores

| ID | Achado | Evidência | Critério de aceite | Dependência |
|---|---|---|---|---|
| **P0-01** | Importação B3 `.xlsx` quebrada | `requirements.txt:1-13`; `src/api/server.py:1857`; probe 400/500 | `.xlsx` importa em ambiente limpo; teste automatizado | `openpyxl` (+`xlrd` se `.xls`), fixture B3 |
| **P0-02** | Caixa fictício de R$ 10.000 após import | `src/web/app.js:3712,4048-4052,1412-1416`; repro equity R$ 10.527,90 | Caixa 0/“não informado”; equity = posições; E2E | Decisão de UX, quotes |
| **P0-03** | DCA aporta em SELL | `src/evaluator/accumulation_simulator.py:476-482,507`; repro 2 aportes/18,3333 cotas | Só BUY aporta; unit BUY+SELL = 1/10/R$100 | Nenhuma |
| **P0-04** | `end_date` ignorado na valuation | `src/evaluator/accumulation_simulator.py:458,490`; `src/api/server.py:1242`; repro 250 vs 150 | Usar `close_sliced[-1]`; teste end_date | Nenhuma |
| **P0-05** | BRL/USD somados sem câmbio | `src/evaluator/portfolio_simulator.py:421,972-974`; ausência de FX | Converter ou rejeitar carteira mista; teste PETR4+AAPL | Fonte FX, moeda-base |

### 12.2 P1 — correções de confiança

| ID | Achado | Evidência | Critério de aceite | Dependência |
|---|---|---|---|---|
| **P1-01** | Sem cotação → custo | `src/web/app.js:1369-1386`; `src/evaluator/portfolio_simulator.py:421` | `null`/“—”, fora do P&L; E2E | Contrato de quotes |
| **P1-02** | Dados sintéticos sem rótulo | `src/web/app.js:1617-1625`; `src/web/modules/proventos.js:48-50` | Empty state zerado; demo rotulado; E2E | Decisão de demo |
| **P1-03** | KPIs fixos (drawdown/alpha/DCA) | `src/api/server.py:1237-1244`; `src/evaluator/accumulation_simulator.py:769-772` | Cálculo real ou `null`; testes | Benchmark DCA |
| **P1-04** | Exec deck usa campo errado | `src/web/app.js:2215-2219`; `src/api/schemas.py:127`; visual 0,0% vs 43,5% | Usar `historical_win_rate`; E2E | Nenhuma |
| **P1-05** | Renda duplicada/oversell silencioso | `src/data_loader/b3_parser.py:891,770`; repro 10→20 | Dedupe/erro explícito; testes | Metadados B3 |
| **P1-06** | Sem auth, CORS `*`, upload sem limite, CDN sem SRI | `src/api/server.py:88-93,1851`; `src/web/index.html:19-23` | Auth/local-only, allowlist, limites, SRI | Modelo de deploy |
| **P1-07** | Ranking Plotly não renderiza | `src/web/app.js:2657-2675`; runtime `ReferenceError: chartFontColor` | Trace definido; E2E com dados | Nenhuma |
| **P1-08** | Testes B3 `.xlsx` pulados | `tests/unit/test_b3_parser.py:69-71,93-97` | Fixture estável; sem skip; CI | P0-01, fixtures |

### 12.3 P2 — dívida e governança

1. **P2-01 Controles mortos** — `index.html:182,348-349,1702-1705,2156`; remover ou implementar. **Aceite:** cada controle visível tem handler e teste de clique, ou é removido. **Dependência:** decisão de produto.
2. **P2-02 Acessibilidade** — `role="tabpanel"`/`aria-labelledby` ausentes; 8 de 72 botões com `aria-label`; modal sem `role="dialog"`. **Aceite:** abas/painéis com semântica ARIA, botões-ícone rotulados, modal com foco gerenciado; checagem axe. **Dependência:** nenhuma.
3. **P2-03 Drift report desatualizado** — `.specify/sync/drift-report.md:3,10`; regenerar 018–023. **Aceite:** relatório cobre todas as specs e declara lacunas. **Dependência:** nenhuma.
4. **P2-04 `agy`/PowerShell** — `.specify/integration.json:4-14`; `pwsh` ausente. **Aceite:** scripts portáveis ou prerequisito documentado e validado. **Dependência:** decisão de tooling.
5. **P2-05 Python drift** — `render.yaml:11-12` vs `plan.md:15` vs `venv` 3.14.4. **Aceite:** matriz única de versão em produção/CI/docs. **Dependência:** decisão de plataforma.
6. **P2-06 Docs/contagens** — `README.md:10,227`; `PRODUCT.md:43`. **Aceite:** contagens e referências de teste corretas. **Dependência:** nenhuma.
7. **P2-07 Monólito/legado** — `app.js` 4.843 linhas; 40 IDs referenciados fora do HTML estático; Streamlit em `requirements.txt:11-12`. **Aceite:** código morto removido, `app.js` dividido por domínio e destino do Streamlit decidido. **Dependência:** esforço de refatoração.
8. **P2-08 Dependências de produção** — `pytest`/`streamlit` no runtime. **Aceite:** runtime enxuto e dev separado. **Dependência:** P2-07.

### 12.4 P3 — polimento

1. **P3-01 Tailwind CDN em produção** — `index.html:19`; warning real. **Aceite:** build estático sem CDN. **Dependência:** pipeline de build.
2. **P3-02 Backdrop inválido** — `surface-canvas/80` em `index.html:2083,2156`. **Aceite:** utilitário válido e backdrop visível. **Dependência:** nenhuma.
3. **P3-03 FastAPI `on_event` deprecado** — warnings da suíte. **Aceite:** migrar para `lifespan` sem warning. **Dependência:** nenhuma.
4. **P3-04 Comentário divergente** — `portfolio_simulator.py:633-640` fala `>= 50`, código usa `>= 45`. **Aceite:** comentário e código alinhados. **Dependência:** decisão do limiar.
5. **P3-05 `num_contributions` semântica** — já coberto por P0-03. **Aceite:** nome/contrato refletem apenas aportes efetivos. **Dependência:** P0-03.

### 12.5 Sequência recomendada

1. **Semana 1 — destravar onboarding e dinheiro:** P0-01, P0-02, P1-01, P1-02.
2. **Semana 1-2 — corrigir simulador:** P0-03, P0-04, P1-03, P1-07, P1-04.
3. **Semana 2 — câmbio e B3:** P0-05, P1-05, P1-08.
4. **Semana 2-3 — segurança:** P1-06, P2-08, SRI/vendorização, auth/local-only.
5. **Semana 3 — UX/acessibilidade/governança:** P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07.
6. **Contínuo:** P3 e regeneração do drift report a cada fechamento de spec.

### 12.6 Próximas tarefas concretas

- [ ] Adicionar `openpyxl` (e `xlrd`, se `.xls` for suportado) e um teste com fixture B3 `.xlsx`.
- [ ] Corrigir `applyB3ParsedResult` para não herdar `availableCash=10000`; decidir e documentar o comportamento de caixa desconhecido.
- [ ] Filtrar `direction == "BUY"` em `simulate_accumulation` e corrigir `num_contributions`.
- [ ] Usar `close_sliced[-1]` em `simulate_accumulation`/`optimize_strategy_pairs` e adicionar teste de `end_date`.
- [ ] Definir moeda-base e implementar conversão FX (ou rejeitar carteiras mistas).
- [ ] Remover fallback `currentP = avgP` e propagar “sem cotação”.
- [ ] Remover séries hardcoded de proventos/evolução ou rotulá-las como demo.
- [ ] Corrigir `renderPlotlyRanking` (`trace`, cores) e adicionar E2E do gráfico.
- [ ] Corrigir deck do radar para `historical_win_rate` e remover `win_rate` dos mocks.
- [ ] Deduplicar renda B3 e avisar oversell.
- [ ] Implementar auth/local-only, allowlist CORS, limites de upload e SRI.
- [ ] Regenerar drift report 018–023 e atualizar status da spec 023.
- [ ] Atualizar README/PRODUCT e alinhar versão de Python.

---

## Apêndice A — Reproduções controladas

Scripts temporários usados (fora do repositório, não versionados):

| Script | Objetivo | Resultado |
|---|---|---|
| `/tmp/opencode/verify_dca.py` | DCA com BUY+SELL | `total_invested=200`, `total_shares=18.3333`, `num_contributions=2` |
| `/tmp/opencode/verify_enddate.py` | `end_date` na valuation | `current_price=25`, `current_equity=250` (esperado 15/150) |
| `/tmp/opencode/verify_phantom_cash.py` | Caixa após B3 | `cash=10000`, `equity=R$ 10.527,90`, `invested=R$ 300,00` |
| `/tmp/opencode/verify_ranking3.py` | Ranking Plotly | `plot children: 0`; `ReferenceError: chartFontColor is not defined` |
| `/tmp/opencode/verify_b3_income.py` | Renda duplicada | 1 arquivo = 10,0; 2 arquivos = 20,0 |
| `curl` | B3 `.xlsx` | `POST /api/b3/parse` 400; `GET /api/b3/sync-local` 500 |

## Apêndice B — Evidências visuais

- `/tmp/opencode/audit-shots/desktop_*.png` — 8 áreas em 1440×900.
- `/tmp/opencode/audit-shots/mobile_*.png` — 8 áreas em 375×812.
- `/tmp/opencode/audit-visual.json` — títulos, headings, botões, texto, `scrollWidth`/`clientWidth`, erros de console.
- Destaques:
  - Estado vazio com `R$ 10.000,00` e série sintética.
  - Radar com `0.0% WR` no deck e `43,5%` na tabela para o mesmo ativo.
  - Nenhum overflow horizontal; apenas warning de Tailwind CDN.

## Apêndice C — Arquivos não rastreados preservados

Os itens abaixo já existiam antes da auditoria e **não** foram modificados, movidos ou removidos:

- `B3/`
- `graphify-out/`
- `imagens modelo/`
- `minha_carteira - Copia.csv`
- `minha_carteira.csv`
- `scratch/`

---

**Conclusão:** a baseline visual e a suíte existente são um bom ponto de partida, mas os P0 precisam ser resolvidos antes de qualquer uso com dados reais. O relatório é deliberadamente somente leitura: nenhuma correção foi aplicada nesta fase.
