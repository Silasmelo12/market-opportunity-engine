# Feature Specification: Modularização Segura e Incremental do Frontend

**Feature Branch**: `022-codebase-modularization`  
**Created**: 2026-10-24  
**Last Updated**: 2026-10-24 (Reconciliação Exata da Baseline e Decomposição da Etapa 7)  
**Status**: Proposta Refinada para Revisão (Fase 4A — Planejamento)  
**Input**: Grafo de Dependências (`graphify-out/`), Auditoria de `src/web/app.js` (5.210 linhas), Reconciliação dos 130 testes (128 passed, 2 skipped), Auditoria de Execução no Navegador e Playwright.

---

## 1. Visão Geral e Justificativa

O frontend do **Market Opportunity & Bottom Statistical Engine** está concentrado em um único arquivo: `src/web/app.js` (5.210 linhas).

Embora a aplicação esteja estável e com 100% de sucesso nos testes vigentes, a manutenção tornou-se delicada devido ao acoplamento entre:
1. Dicionários e constantes de mapeamento (`TICKER_ALIASES`, `ASSET_NAMES`, rotas canônicas).
2. Funções puras de formatação monetária e manipulação de strings.
3. Cache e persistência em `localStorage`.
4. Roteamento hash com lógica de precedência (`URL Hash > LocalStorage > Default`).
5. Renderização de abas (`overview`, `carteira`, `proventos`, `radar`, `analise`, `simulador`).
6. Integração com CDNs globais (`Plotly`, `LightweightCharts`).

### Diretrizes de Engenharia e Princípios Inegociáveis
1. **Sem Redução Arbitrária de Linhas**: O objetivo da modularização é **coesão por responsabilidade, desacoplamento e testabilidade**, e **não** atingir uma cota fixa de linhas no arquivo raiz.
2. **Zero Nova Infraestrutura / Zero Bundlers**: Proibido adicionar Webpack, Vite, Rollup, Babel ou novos frameworks reativos (React/Vue/Svelte). A aplicação deve permanecer executável diretamente no navegador.
3. **Compatibilidade e Ordem de Carregamento**:
   - Atualmente, `index.html` carrega bibliotecas CDN síncronas (`tailwindcss`, `lightweight-charts`, `plotly`) no `<head>` e `app.js` no fim do `<body>` (L2186).
   - O objeto `elements` faz `document.getElementById(...)` no topo do arquivo (L146). No carregamento tradicional no fim do body, o DOM já foi parseado.
   - Os testes E2E executam chamadas como `page.evaluate("() => window.appState.radarActiveCategory")` e `page.evaluate("(t) => window.applyTheme(t, false)")`. Logo, **propriedades e métodos essenciais de teste devem obrigatoriamente permanecer acessíveis em `window`**.
   - Para evitar riscos de `defer` implícito ou escopo léxico isolado de `<script type="module">` antes do tempo, os primeiros passos adotam a estratégia mais simples e segura: **módulos isolados carregados via scripts complementares ou ES Modules avaliados estritamente por etapa**, garantindo que o escopo global não quebre os testes E2E.
4. **Backend Fora do Escopo Inicial**: `src/api/server.py` (1.872 linhas) está completamente estável e desacoplado do frontend via contrato HTTP/JSON. Ele permanece **fora do escopo inicial** e será avaliado separadamente apenas após o frontend estar modularizado e validado.
5. **Etapas Pequenas, Reversíveis e Testáveis**: Cada passo foca em uma responsabilidade atômica, começando por **constantes estáticas e funções puras**, adiando o estado compartilhado e o roteamento até que todas as dependências estejam mapeadas e isoladas.

---

## 2. Reconciliação Rigorosa da Baseline de Testes

### 2.1 Por que a contagem difere entre `tests/unit`, `tests/e2e` e `pytest tests/`?

Ao rodar apenas subdiretórios específicos, o pytest coleta apenas os arquivos contidos naquelas pastas:
- `pytest tests/unit`: Coleta **97 testes** (95 aprovados, **2 ignorados** em `test_b3_parser.py` devido a fixtures opcionais locais).
- `pytest tests/e2e`: Coleta **18 testes** (15 em `test_dashboard_navigation.py` e 3 em `test_proventos_layout.py`, todos aprovados).
- **Testes Raiz (fora de `unit/` e `e2e/`)**: Na pasta raiz `tests/` existem **3 arquivos adicionais** que contêm exatamente **15 testes**:
  1. `tests/test_double_patterns.py`: **9 testes** (padrões de reversão Double Bottom / Double Top e validação de lookahead zero).
  2. `tests/test_normalizer_suffix.py`: **1 teste** (validação de `strip_corporate_suffix`).
  3. `tests/test_radar_pagination.py`: **5 testes** (paginação de radar, filtro direcional, resiliência de cache e health-check).

### Reconciliação Aritmética Completa:
$$\text{Total Coletado} = 97\ (\text{unit}) + 18\ (\text{e2e}) + 15\ (\text{raiz}) = \mathbf{130\ \text{testes}}$$
$$\text{Resultado Global} = \mathbf{128\ \text{PASSED}} + \mathbf{2\ \text{SKIPPED}} + \mathbf{0\ \text{FAILED}}$$

### 2.2 Comando Canônico de Validação
O comando canônico e oficial que deve ser executado para validação plena de qualquer etapa é:
```powershell
$env:PYTHONPATH="."; pytest tests/ -v
```
*Tempo típico de execução*: ~2 min e 13 seg (inclui automação Chromium/Playwright nos 18 testes E2E).

---

## 3. Divisão Segura por Responsabilidade e Sequenciamento

A decomposição é organizada em etapas estritamente sequenciais e reversíveis:

1. **Etapa 1: Constantes Estáticas e Dicionários** (`TICKER_ALIASES`, `ASSET_NAMES`, rotas).
2. **Etapa 2: Funções Puras e Formatadores** (`formatPrice`, `stripCorporateSuffix`, `resolveTicker`, `sanitizeTickerParam`, `getAssetName`).
3. **Etapa 3: Notificações Visuais e Helpers de DOM** (`showToastNotification`, `showLoading`).
4. **Etapa 4: Módulo Isolado de Proventos** (`renderProventosTabChart`, `setupProventosControls`).
5. **Etapa 5: Auditoria de Consumidores do Estado Global** (`window.appState`, persistência).
6. **Etapa 6: Motor de Roteamento e Navegação Hash** (`parseHashRoute`, precedência Hash > Storage > Default).
7. **Etapa 7: Telas de Domínio Específico (Decompostas em Tarefas Independentes)**:
   - **7.1 Módulo Overview (Visão Geral)**: KPIs patrimoniais, metas e gráficos Plotly de aportes/alocação.
   - **7.2 Módulo Custódia & Portfólio (Posições & B3)**: Editor de posições, importação B3, propostas pré-flight de ordens.
   - **7.3 Módulo Radar Quantitativo**: Tabela de radar, filtros de categorias/estratégias, paginação e ordenação.
   - **7.4 Módulo Gráfico Interativo**: Integração TradingView Lightweight Charts, linha de preço médio e linhas de reteste.
   - **7.5 Módulo Simulador & Análise**: Gráficos de ranking/dispersão Plotly, simulação de ciclo trade/DCA e otimizador de estratégias.

---

## 4. Critérios de Aceite e Salvaguardas

1. **Critério de Aceite Inflexível**: A execução do comando canônico deve sempre reportar exatamente **128 passed, 2 skipped, 0 failed**.
2. **Condição de Aborto / Reversão Imediata**: Qualquer falha em teste unitário, de contrato ou E2E cancela imediatamente a etapa e dispara reversão via checkout do arquivo afetado.
3. **Preservação de Escopo Global**: Nenhuma variável (`window.appState`) ou função (`window.applyTheme`) consumida pelo Playwright pode se tornar inacessível.
