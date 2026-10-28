# Quickstart: Validação do Layout Profissional e Unificado

**Feature**: 023-professional-ui-layout
**Date**: 2026-10-27
**References**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/ui-layout-contract.md](./contracts/ui-layout-contract.md)

Este guia descreve como executar a aplicação e validar a feature de ponta a ponta. Ele não contém a implementação nem a suíte completa de testes.

## 1. Pré-requisitos

- Python 3.11+ (o repositório está validado em Python 3.14).
- Dependências de runtime e desenvolvimento instaladas.
- Navegador moderno para validação manual.
- Playwright com navegador Chromium para os testes E2E.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m playwright install chromium
```

## 2. Executar a aplicação

Opção A — entrypoint do projeto:

```bash
python run_server.py
```

Opção B — Uvicorn direto:

```bash
PYTHONPATH=. python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

Abrir: `http://127.0.0.1:8000`.

## 3. Validar contratos automatizados

### 3.1 Suíte unitária e de contratos

```bash
PYTHONPATH=. python -m pytest tests/unit -v
```

**Esperado**: todos os testes passam; nenhuma regressão nos contratos de UI/API.

### 3.2 Navegação e layout E2E

```bash
PYTHONPATH=. python -m pytest tests/e2e -v
```

**Esperado**: todos os cenários de navegação, tema, painel único, IDs e responsividade passam.

### 3.3 Suíte completa

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

**Esperado**: mesma linha de base ou melhor; zero falhas novas.

### 3.4 Garantia de que o backend não foi alterado

```bash
git diff --stat -- src/api
```

**Esperado**: saída vazia. Nenhum arquivo em `src/api/` deve aparecer no diff da feature.

## 4. Auditorias rápidas de conteúdo e tipografia

### 4.1 Artefatos de encoding

```bash
grep -nP "Ã|â†|â–|ð" src/web/index.html src/web/app.js src/web/modules/*.js
```

**Esperado**: nenhuma ocorrência.

### 4.2 Piso tipográfico

```bash
grep -n "text-\[10px\]" src/web/index.html
```

**Esperado**: nenhuma ocorrência em texto funcional. Casos decorativos, se existirem, devem ser justificados e não podem ser labels, botões ou metadados acionáveis.

### 4.3 IDs duplicados

```bash
grep -o 'id="[^"]*"' src/web/index.html | sort | uniq -d
```

**Esperado**: saída vazia.

## 5. Matriz de validação visual

Executar as 8 áreas nas 4 larguras e nos 2 temas: **64 verificações**.

| Área | 375px | 768px | 1366px | 1920px |
|---|---|---|---|---|
| Resumo | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Posições & Ativos | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Proventos | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Evolução Patrimonial | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Radar | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Gráfico | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Simulador | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |
| Playbook | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro | ☐ claro / ☐ escuro |

### Checklist por verificação

- Sem sobreposição, corte ou rolagem horizontal global.
- Tabelas largas rolam apenas no próprio contêiner, com indicativo.
- Tipografia legível; nenhum texto funcional abaixo de 11px.
- Contraste AA em texto, labels e controles.
- Cabeçalho, ambiente, subnav e ações utilizáveis.
- Estados ativo, hover, foco e desabilitado visíveis.
- Gráficos ocupam a largura do contêiner e não colapsam.
- Estado vazio/onboarding coerente com a presença ou ausência de dados.

## 6. Cenários funcionais obrigatórios

### 6.1 Navegação

1. Abrir `/#carteira/visao-geral` e confirmar ambiente “Minha Carteira” + subaba Resumo.
2. Alternar para “Análise Quantitativa” e percorrer as quatro subabas.
3. Recarregar a página e confirmar restauração da última área.
4. Usar voltar/avançar do navegador e confirmar sincronização.
5. Inserir hash inválido e confirmar fallback previsível.
6. Verificar que existe exatamente um painel visível e nenhum ID duplicado.

### 6.2 Tema

1. Confirmar tema claro como padrão em uma sessão sem preferência.
2. Alternar para escuro e confirmar atualização de todas as áreas e gráficos.
3. Recarregar e confirmar persistência.
4. Repetir a matriz visual nos dois temas.

### 6.3 Dados e estados

1. Testar com carteira vazia: banner de primeiro uso visível apenas nesse cenário.
2. Testar com carteira preenchida: banner não deve ocupar o espaço operacional.
3. Testar ticker/nome longo e valores extensos: sem sobreposição.
4. Testar falha/atraso de cotação: sinalizações de contingência visíveis.
5. Testar filtros, ordenação, paginação e simulação: comportamento preservado.

### 6.4 Acessibilidade

1. Percorrer a interface apenas com teclado.
2. Confirmar foco visível em todos os controles.
3. Confirmar ativação por Enter/Espaço nos controles aplicáveis.
4. Testar zoom de 200% sem perda de conteúdo.
5. Ativar preferência por movimento reduzido e confirmar supressão de animações não essenciais.
6. Verificar `aria-selected` nos controles de navegação.

## 7. Critérios de aceite

A feature é considerada validada quando:

- [ ] Suíte `pytest tests/` passa sem falhas novas.
- [ ] `src/api/` permanece sem alterações.
- [ ] Zero artefatos de encoding em textos visíveis.
- [ ] Zero IDs duplicados.
- [ ] Exatamente um painel visível por estado.
- [ ] 8/8 áreas aprovadas nos temas claro e escuro.
- [ ] 64/64 verificações visuais aprovadas.
- [ ] Nenhum texto funcional abaixo de 11px.
- [ ] Navegação por teclado e foco visível funcionando.
- [ ] Rotas, IDs e funções globais preservados.
- [ ] Nenhuma funcionalidade ou conteúdo removido.

## 8. Solução de problemas

- **Playwright não encontrado**: instalar `requirements-dev.txt` e executar `python -m playwright install chromium`.
- **Servidor não inicia**: verificar `PYTHONPATH=.` e a porta escolhida.
- **Gráfico não redimensiona**: confirmar que o contêiner tem largura/altura definidas e que o resize é chamado na abertura da área e na troca de tema.
- **Tema não persiste**: verificar a chave `terminal_theme` no `localStorage` e se `applyTheme` está acessível em `window`.
- **Rota não abre**: validar a precedência URL > `localStorage` > padrão e a existência do painel correspondente.

---

## 9. Diário de Execução da Implementação

### T001 — Baseline da suíte

- Branch: `feat/professional-ui-layout`
- Working tree inicial: apenas artefatos não rastreados de dados (`B3/`, `scratch/`, CSVs) e a própria pasta da spec.
- Baseline em 2026-10-27, com `venv/bin/python` (Python 3.14.4):
  - `PYTHONPATH=. python -m pytest tests/unit -q` → **95 passed, 2 skipped**.
  - `PYTHONPATH=. python -m pytest tests/e2e -q` → **18 passed**.
- Conclusão: linha de base verde; qualquer falha nova é regressão da feature.

### T002 — Baseline visual

- Captura automatizada das 8 áreas × 4 larguras (375/768/1366/1920) × 2 temas = **64 imagens**.
- Destino: `/tmp/023-ui-before/` (fora do repositório, conforme plano).
- Carteira sintética (PETR4.SA, TGAR11.SA, caixa e proventos) e respostas de `/api/radar`, `/api/analyze` e `/api/portfolio/quotes` mockadas para determinismo.

### T003 — Inventário de IDs, rotas e funções globais

- IDs do contrato presentes: todos, exceto `#b3-multi-file-input` (referenciado por `onclick` no banner de primeiro uso, porém ausente do DOM). **Lacuna registrada para correção.**
- Rotas canônicas e legadas: todas mapeadas em `src/web/modules/constants.js` (`CANONICAL_ROUTES` + `ROUTE_ALIASES`).
- Funções globais: `window.appState` explícito; `window.applyTheme` disponível por declaração de função de topo.
- IDs duplicados: nenhum (a checagem inicial por `grep 'id="'` gerou falsos positivos em `data-id`; a extração estrita de `id="..."` não encontrou duplicatas).

### T004 — Playwright e Chromium

- `requirements-dev.txt` instalado no `venv` do projeto (`playwright>=1.44.0`).
- `python -m playwright install chromium` concluído (Chrome Headless Shell 156).
- `pytest tests/e2e` executou de fato os cenários (sem `skip` por navegador ausente).

### T005 — Backend intocado

- `git diff --stat -- src/api` → saída vazia antes do início da implementação.

### T015–T016 — Reparo de encoding

- `src/web/index.html`: 399 sequências `cp1252 → UTF-8` reparadas.
- `src/web/app.js`: 139 sequências reparadas; `src/web/modules/*.js` sem artefatos.
- Reparo controlado por sequência UTF-8 válida, preservando acentos legítimos (ex.: `VISÃO`).
- Contratos ativados em `tests/unit/test_layout_contracts.py`: `test_index_html_has_no_encoding_artifacts` e `test_javascript_sources_have_no_encoding_artifacts`.
- `node --check` em `app.js` e módulos: OK.

### T017–T018 — Ícones lineares

- Emojis funcionais de `index.html` substituídos por `<use href="#icon-*">` do sprite (marca, ambientes, subnavegação, KPIs, importação, modais e toast).
- Templates dinâmicos de `app.js` e `toast.js` migrados para SVG (`categorias`, badges de ação, ordenação do Radar, toast e botões de remoção).
- Sprite ampliado com `icon-arrow-up`, `icon-arrow-down`, `icon-minus`, `icon-scale` e `icon-pause`.
- Contratos: `test_index_html_has_no_functional_emoji` e `test_javascript_sources_have_no_functional_emoji`.

### T019–T021 — Piso tipográfico e normalização

- `text-[10px]` eliminado das fontes: 93 ocorrências em `index.html` e 7 em `app.js` migradas para `text-[11px]`.
- Valores monetários e percentuais normalizados com `formatCurrency`, `formatNumber` e `formatPercent` (pt-BR, algarismos tabulares).
- Placeholders visuais padronizados como `--`.
- Contratos: `test_sources_do_not_declare_text_below_the_floor` e `test_typography_floor_contract_is_active`.

### T022 — Validação da US1 nas 8 áreas

- Data: 2026-10-27.
- `venv/bin/python -m pytest tests/e2e/test_ui_layout.py -q` → **6 passed**.
- `venv/bin/python -m pytest tests/unit/test_layout_contracts.py -q` → **18 passed**.
- Matriz capturada em `/tmp/023-ui-us1/`: **64/64 imagens** (8 áreas × 375/768/1366/1920 × claro/escuro).
- Verificação: zero artefatos de encoding, zero emojis funcionais, nenhum texto abaixo de 11px nas fontes, ícones consistentes.
- Observação: em 375px o título da marca é truncado e a subnavegação exige rolagem horizontal; ajuste previsto na US2 (T023–T030).

### T030 — Validação de rotas e navegação (US2)

- `venv/bin/python -m pytest tests/e2e/test_dashboard_navigation.py -q` → **16 passed**.
- Cobertura confirmada:
  - precedência URL > `localStorage` > padrão (`#quant/radar` sobre rota salva);
  - rotas canônicas e legadas (`#terminal`, `#resumo`, `#simulador`);
  - reload, `back` e `forward` sincronizando pilar, subnavegação e painel;
  - exatamente um `.tab-view` visível e zero IDs duplicados;
  - navegação por `Tab`/`Enter` e por setas (`ArrowLeft`/`ArrowRight`/`Home`/`End`);
  - offset sticky da subnavegação igual à altura real do header em 1600px e 768px;
  - seletor de direção visível apenas em Radar/Gráfico.
- Ajuste de expectativa: percentuais visíveis agora usam vírgula decimal pt-BR (`+6,25%`), coerente com T020.

### T040 — Validação das 4 áreas de carteira (US3)

- Data: 2026-10-27.
- Matriz recapturada com espera determinística pelo fim do overlay e pela rede: `/tmp/023-ui-us3-validated/` (**64/64 imagens**).
- Verificações em claro e escuro (1366px e 375px, com conferência em 768/1920px):
  1. **Resumo/claro** — 4 KPIs, gráficos de evolução/alocação e acordeões de ativos renderizados sem placeholders residuais.
  2. **Resumo/escuro** — canvas integralmente escuro, títulos com contraste AA e gráficos legíveis.
  3. **Posições/claro** — cartão de categoria, formulário de rebalanceamento e tabela de posições sobre superfície clara.
  4. **Posições/escuro** — superfícies, bordas e texto hierarquizados corretamente no tema escuro.
  5. **Proventos/claro** — canvas claro e cartão do gráfico com controles Mensal/Anual visíveis.
  6. **Proventos/escuro** — cartão e eixo do gráfico legíveis, sem ilhas claras.
  7. **Patrimônio/claro** — canvas claro e estado vazio legível.
  8. **Patrimônio/escuro** — canvas escuro e estado vazio com contraste adequado.
- Correções aplicadas durante a validação:
  - `--bg` inexistente trocado por `--canvas` em `.area-posicoes/.area-proventos/.area-patrimonio`, restaurando o fundo claro em Proventos e Patrimônio.
  - Fundo do `#tab-overview` (que usa `bg-slate-50` no próprio elemento) remapeado para `--canvas` no tema escuro, eliminando a faixa clara e o título invisível.
  - Contêineres de gráficos do Resumo/Patrimônio limpos antes de `Plotly.newPlot`, removendo os textos "Carregando…" sobre gráficos já renderizados.
- Ajuste de teste: o E2E de importação agora valida o banner de primeiro uso no estado sem dados, coerente com a exibição condicional da T035.
- Suítes: `tests/unit/test_layout_contracts.py` + `tests/e2e/test_ui_layout.py` + `tests/e2e/test_dashboard_navigation.py` → **43 passed** (19 unitários + 8 de layout + 16 de navegação).

### T051 — Validação das 4 áreas quantitativas (US4)

- Data: 2026-10-27.
- Matriz capturada em `/tmp/023-ui-us4-validated/`: **64/64 imagens** (8 áreas × 375/768/1366/1920 × claro/escuro).
- Áreas quantitativas conferidas nos dois temas (1366px como referência, com checagem em 375/768/1920px):
  1. **Radar/claro** — KPIs executivos, filtros segmentados, tabela de oportunidades e paginação sobre superfícies claras.
  2. **Radar/escuro** — cartões, tabela e chips com hierarquia de tokens e contraste AA.
  3. **Gráfico/claro** — sidebar de estratégias, controles, banner de retorno contextual e área do Plotly coerentes com o restante do produto.
  4. **Gráfico/escuro** — sidebar, grupos de estratégia e gráfico legíveis, sem ilhas claras.
  5. **Simulador/claro** — formulários, grids de resultados, KPIs e tabela de trades usando `.card-surface`, `.input`, `.kpi-card` e `.table-standard`.
  6. **Simulador/escuro** — mesmos componentes com tokens escuros e séries dos gráficos legíveis.
  7. **Playbook/claro** — grupos, blocos e destaques com `.playbook-group-title`/`.playbook-block`.
  8. **Playbook/escuro** — blocos e destaques com contraste preservado.
- Migração concluída:
  - Radar, Gráfico, Simulador e Playbook passaram a usar `.quant-area`, `.card-surface`, `.chart-card`, `.kpi-card`, `.section-title`, `.segmented`, `.filter-chip`, `.input`, `.table-standard` e utilitários semânticos (`surface*`, `text-*`, `bg-*-soft`).
  - Renderizadores dinâmicos de `app.js` deixaram de emitir classes legadas (`fintech`/`gray`/`cyan`/`emerald`/`rose`/`amber`).
  - Bloco `[data-theme="light"]` de contra-tema das áreas legadas removido; `#tab-portfolio` retirado do remapeamento escuro da carteira.
  - Classes legadas residuais da cauda de Posições, do modal de metas, de Proventos e do toast migradas antes da remoção dos overrides.
- Correções aplicadas durante a validação:
  - KPIs do Radar reorganizados (`flex-wrap` para ativo/score e empilhamento do regime no mobile), eliminando sobreposição em 375px e 768px.
  - Piso tipográfico mantido em 11px também nos KPIs do Radar (o contrato `test_sources_do_not_declare_text_below_the_floor` barra `text-[10px]`).
- Testes: `tests/unit/test_layout_contracts.py` + `tests/e2e/test_ui_layout.py` + `tests/e2e/test_dashboard_navigation.py` → **45 passed** (19 unitários + 10 de layout + 16 de navegação).
- Novos E2E: `test_quant_areas_use_shared_semantic_system` (presença dos componentes compartilhados e ausência de classes legadas nas 4 áreas) e `test_quant_areas_adapt_to_theme_tokens` (fundo do painel e dos cartões muda entre claro/escuro).

### T052–T057 — Responsividade, acessibilidade e resize (US5)

- Data: 2026-10-27.
- **T052** — wrappers padronizados como `.table-scroll touch-scroll` com dica visual em Radar, Simulador, Posições (3 tabelas) e modal de ordens; deck de KPIs do Radar em `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`; `touch-target` nas ações inline do Resumo.
- **T053** — contenção de overflow em `styles.css`: `min-width: 0` em `main`/painéis/grids, `.table-scroll > table { min-width: 100% }`, `scrollbar-gutter: stable`, alvos de toque (`.touch-target`, `.btn-remove-holding`, `.dir-seg-btn`), largura máxima do toast e de plots Plotly.
- **T054** — acessibilidade: regiões vivas (`#toast-notification`, `#loading-spinner`, `#radar-pagination-info`), `aria-pressed` em direção/timeframes/categorias, `aria-busy` no `body` durante carregamento, regiões roláveis focáveis (`tabindex="0"`) com anel de foco, contraste AA nos tokens (claro: `--primary #0369a1`, `--success #047857`, `--warning #b45309`, `--danger #be123c`, `--text-subtle #5b6b80`; escuro: `--text-subtle #8b98a5`, `--danger #fb7185`) e bloco `prefers-reduced-motion`.
- **T055** — `resizeAllCharts()` unificado (TradingView + 9 gráficos Plotly), listener global com `requestAnimationFrame`, remoção do listener duplicado e resize na abertura de área e na troca de tema.
- **T056** — 4 E2E: indicador de foco visível, rolagem de tabela por teclado, regiões vivas/nomes acessíveis e larguras de referência (sem overflow global e sem texto abaixo de 11px).
- **T057** — 4 contratos unitários: wrappers focáveis, breakpoints/overflow, grid de KPIs 1/2/4 colunas e contraste WCAG AA dos tokens.
- Testes: `test_layout_contracts.py` → **23 passed**; `test_ui_layout.py` → **14 passed**; `test_dashboard_navigation.py` → **16 passed**.

### T058 — 64 verificações visuais finais (US5)

- Data: 2026-10-27.
- Matriz capturada em `/tmp/023-ui-us5/`: **64/64 PNGs** (8 áreas × 375/768/1366/1920 × claro/escuro), todos com conteúdo.
- Auditoria automatizada sobre as 64 combinações:
  - `docOverflow = 0` em todas (sem rolagem horizontal global);
  - nenhum texto renderizado abaixo de 11px;
  - nenhum controle visível sem nome acessível;
  - 8 abas contextuais e exatamente 1 selecionada em todas as combinações;
  - todas as tabelas de conteúdo dentro de contêineres roláveis (o canvas interno do TradingView não é tabela e foi ignorado).
- Revisão visual por área nos dois temas (1366px como referência, com checagem em 375/768/1920px): Resumo, Posições, Proventos, Patrimônio, Radar, Gráfico, Simulador e Playbook.
- Correções aplicadas durante a revisão:
  - **Radar** — o rótulo de regime não é mais truncado: `updateRadarExecutiveDeck` deixou de aplicar `truncate` e usa `leading-tight`, exibindo “Sobrevendido (Alta Assimetria)” por inteiro em 375px e 1366px.
  - **Cabeçalho** — em 768–1023px o selo “Quantitative Pro” espremia o nome da marca até largura zero. O selo agora só aparece a partir de 1280px e quando o seletor de direção não está visível (`:has`), o bloco da marca tem largura mínima de 196px acima de 480px e, entre 1024–1279px, os rótulos secundários (B3/Lançamento) viram ícones com `aria-label`. Resultado: marca legível em 375/768/1024/1280/1366/1920, sem sobreposição.
- Alvos pequenos remanescentes: apenas ações de texto inline da sidebar do Gráfico em desktop (48×17, 31×17, 36×17) e checkbox 13×13 com rótulo clicável — cobertos pela exceção de texto inline da WCAG 2.5.8; em 375/768 não há alvos pequenos.
- Testes após as correções: `test_layout_contracts.py` → **23 passed**; `test_ui_layout.py` + `test_dashboard_navigation.py` → **30 passed**.

### T059 — Zoom de 200% e movimento reduzido (US5)

- Data: 2026-10-27.
- **Zoom de 200%** — simulado pelo viewport CSS efetivo (1366→683px e 1920→960px, com `device_scale_factor=2`), nas 8 áreas em tema claro:
  - `docOverflow = 0` em **16/16** combinações;
  - nenhum texto abaixo de 11px;
  - exatamente 1 painel `.tab-view` visível, com cabeçalho e subnavegação presentes.
- **Teclado em 200%** (683px, Radar): 16 controles alcançados por `Tab`, todos com indicador de foco visível e totalmente dentro do viewport (`left ≥ 0`, `right ≤ 683`), sem controles cortados.
- **Movimento reduzido** (`reduced_motion="reduce"`, tema escuro, 8 áreas): `transition-duration` e `animation-duration` ≤ 0,001s em header, abas, botão de tema, cartões, KPIs, toast e subnavegação; `scroll-behavior: auto`. **8/8 áreas OK**, zero falhas.
- Script de apoio: `/tmp/opencode/validate_zoom_motion.py`.

### T060 — Consolidação do DESIGN.md

- Data: 2026-10-27.
- Tokens do `DESIGN.md` sincronizados com `src/web/styles.css`: **31 tokens no tema claro + 31 no escuro, 0 divergências** (script de paridade sobre os blocos `:root` e `[data-theme="dark"]`).
- Valores atualizados para o padrão final: `--primary #0369a1`, `--success #047857`, `--warning #b45309`, `--danger #be123c`, `--text-subtle #5b6b80` (claro); `--text-subtle #8b98a5`, `--danger #fb7185` (escuro).
- Seção 4 documenta as relações reais de contraste (17,85:1 / 7,58:1 / 5,44:1 no claro; 16,96:1 / 6,92:1 / 6,03:1 no escuro).
- Seção 6.7 atualizada com o comportamento responsivo final do header (480/1024/1279/1280px), alvos de toque, regiões roláveis focáveis, zoom de 200% e movimento reduzido.
- Referências obsoletas removidas: classes legadas `fintech-*`, `gray-*`, `cyan-*`, `emerald-*`, `rose-*`, `amber-*` e overrides de tema em runtime agora estão explicitamente marcados como removidos pela Feature 023.

### T061 — Backend intocado

- Data: 2026-10-27.
- `git diff --stat -- src/api` (working tree) → vazio.
- `git diff --stat 4fd3ad5^..HEAD -- src/api` (toda a Feature 023) → vazio; `git diff --name-only 4fd3ad5^..HEAD -- src/api | wc -l` → **0 arquivos**.
- Último commit que tocou `src/api/`: `b5a9707` (anterior à Feature 023).
- Rotas, contratos de dados e cálculos financeiros permanecem inalterados.
