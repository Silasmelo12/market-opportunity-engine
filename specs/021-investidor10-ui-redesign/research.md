# Research & Architecture Decisions: Redesign UI Estilo Investidor10

## 1. Technical Baseline
- **Backend**: FastAPI (`src/api/main.py`), servindo rotas REST `/api/...` e arquivos estáticos da SPA em `src/web/`.
- **Frontend Atual**: SPA em Vanilla JS + Tailwind CSS (`src/web/index.html`, `src/web/app.js`, `src/web/styles.css`).
- **Visualização Gráfica**:
  - TradingView Lightweight Charts já integrado para candlesticks.
  - Plotly.js / Chart.js para gráficos de dispersão e radar.
- **Armazenamento / Estado**:
  - `localStorage` para persistência de preferências do usuário (ex: aba ativa `mo_active_tab`).
  - Cache em memória e Parquet/JSON no backend para cotações e portfólio B3.

## 2. Decisões de Arquitetura Frontend

### D1: Modularização da UI por Abas no Frontend (SPA)
- **Problema**: O `index.html` atual possui 150KB com múltiplos painéis técnicos empilhados verticalmente, causando poluição visual e lentidão de navegação.
- **Solução**:
  - Criar um container principal com abas visuais no topo (*Resumo*, *Posições*, *Proventos*, *Patrimônio*, *Radar Estatístico*, *TradingView*).
  - Cada aba terá uma seção com classe `.tab-pane` e apenas a aba ativa (`.active`) ficará visível (`display: block` vs `display: none`).
  - As abas persistem o estado no `localStorage` sob a chave `mo_active_tab`.

### D2: Acordeões de Posições por Classe de Ativo
- **Problema**: Ações, FIIs e BDRs estavam misturados em uma única tabela sem distinção visual de tipo nem de peso ideal.
- **Solução**:
  - Agrupar os ativos retornados pela API `/api/portfolio` ou parseados da B3 por classe (`AÇÕES`, `FIIS`, `BDRS`, `OUTROS`).
  - Cada categoria é renderizada em um cartão independente com resumo no topo (Total investido, variação %, % na carteira vs % ideal) e botão retrátil com ícone chevron.

### D3: Gráficos de Proventos e Alocação
- **Solução**:
  - Proventos: Gráfico de barras mensais (12M) com alternador Mensal/Anual utilizando `Chart.js` ou `Plotly.js`.
  - Alocação: Gráfico de Donut com legenda estilizada indicando classe de ativo, percentual e valor financeiro total.

### D4: Preservação Estrita dos Endpoints FastAPI & Regra de Não-Regressão
- Nenhuma alteração de rota ou schema será feita em `src/api/`. Todas as APIs existentes (`/api/portfolio`, `/api/quotes`, `/api/radar`, `/api/b3/import`, `/api/evolution`) continuam idênticas.
- Testes automatizados em `tests/unit/test_ui_contracts.py` e `tests/unit/test_api_endpoints.py` garantirão a estabilidade dos contratos consumidos pelo frontend.
