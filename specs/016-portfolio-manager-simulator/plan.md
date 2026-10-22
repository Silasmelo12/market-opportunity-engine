# Implementation Plan: Gestor, Consultor de Rebalanceamento e Simulador Multiativos de Carteira

**Branch**: `016-portfolio-manager-simulator` | **Date**: 2026-10-22 | **Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/016-portfolio-manager-simulator/spec.md)

**Input**: Feature specification from `/specs/016-portfolio-manager-simulator/spec.md`

---

## Summary

Implementar um módulo completo de **Gestão, Consultoria de Rebalanceamento e Simulação Histórica Multiativos de Carteira** integrado ao terminal quantitativo:
1. **Motor Quantitativo de Portfólio (`src/evaluator/portfolio_simulator.py`)**:
   - Identifica automaticamente o **Par de Estratégias Campeão** (Compra + Venda) de cada ativo do universo selecionado e calcula um **Score de Potencial (0–100)** combinando *Win Rate*, *Retorno Histórico*, *Max Drawdown* e *Timing* (`IDEAL` > `EXTENDED` > `LATE`).
   - Opera como **Consultor de Rebalanceamento Hoje** (`advise_portfolio_rebalance`), recebendo o caixa disponível (ex: R$ 10.000,00) e posições atuais do usuário para emitir ordens acionáveis (`COMPRAR`, `VENDER TOTAL`, `VENDER PARCIAL / REBALANCEAR`, `ROTACIONAR`, `MANTER`) com quantidade exata de cotas, valor em R$ e pesos atuais vs. alvo.
   - Opera como **Simulador Histórico Multiativos** (`simulate_portfolio_multi_asset`), executando backtest barra a barra (estritamente *Zero Look-Ahead Bias*) com alocação proporcional ao Score, limite máximo de concentração por ativo (ex: 25%) e as 3 regras de saída/rebalanceamento (Venda 100% no Topo, Venda Parcial acima do Teto + Banda e Rotação Tática por Custo de Oportunidade).
2. **Camada de API REST FastAPI (`src/api/schemas.py`, `src/api/server.py`)**:
   - Novos contratos Pydantic e endpoints `POST /api/portfolio/advise` e `POST /api/portfolio/simulate` com varredura paralela (`ThreadPoolExecutor`) e aproveitamento do cache diário/memória.
3. **Camada de Apresentação Web SPA (`src/web/index.html`, `src/web/app.js`, `src/web/styles.css`)**:
   - Nova 5ª aba principal **"Carteira"** (`tab-portfolio`) com persistência em `localStorage`, editor interativo de carteira atual + caixa, boleta de recomendações de rebalanceamento de hoje, 6 cards de KPIs institucionais, gráficos interativos Plotly.js (Curva de Evolução Patrimonial vs. Buy & Hold Equal-Weight da cesta e Composição de Alocação) compatíveis com Temas Claro e Escuro, e tabela histórica de operações.

---

## Technical Context

**Language/Version**: Python 3.11+ (Backend) / Vanilla JavaScript ES6+ + HTML5 + Tailwind CSS (Frontend SPA)

**Primary Dependencies**: FastAPI 0.110+, Uvicorn, Pydantic v2, NumPy, Pandas, Plotly.js 2.32.0

**Storage**: Cache local multi-camada existente (`.cache/data/*.parquet`, `.cache/radar_daily/*.json`, memória com TTL e Redis opcional) + `localStorage` no navegador para persistência da carteira do usuário (`market_engine_portfolio_v1`)

**Testing**: `pytest` (testes unitários de matemática de carteira, conservação de caixa, anti-look-ahead multiativos e testes de contrato dos endpoints FastAPI)

**Target Platform**: Web Application (Desktop & Mobile responsivo, servido via FastAPI/Uvicorn)

**Project Type**: Quantitative Trading Terminal & Portfolio Management Web Service (Single-Repository)

**Performance Goals**: Resposta dos endpoints `/api/portfolio/advise` e `/api/portfolio/simulate` em `< 3s` para cestas em cache (ex: Destaques com 14–17 ativos) usando `ThreadPoolExecutor`; renderização instantânea de gráficos no cliente

**Constraints**: Zero Look-Ahead Bias estrito em todas as decisões de compra, venda e rotação; conservação exata de caixa (`cash >= 0`); respeito rigoroso ao teto máximo percentual por ativo (`max_weight_pct`)

**Scale/Scope**: Suporte a todas as categorias de ativos do terminal (Destaques, Ações Brasil, FIIs Brasil, Ações EUA, Commodities, Forex, Criptomoedas e cestas personalizadas) nos tempos gráficos suportados (`1d`, `1wk`, `1h`, `15m`, `5m`)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate Evaluation (Pre-Research & Post-Design) | Status |
|---|---|---|
| **I. Arquitetura Python (FastAPI) + Web SPA & Otimização de Performance** | 100% Python/FastAPI no backend + Vanilla JS/HTML/Tailwind em `src/web/`. Sem uso de Streamlit legado. Processamento numérico em arrays NumPy/Pandas e paralelismo com `ThreadPoolExecutor`. Gráficos analíticos de carteira renderizados via Plotly.js. | ✅ PASS |
| **II. Rigor Financeiro e Zero Look-Ahead Bias (NON-NEGOTIABLE)** | No backtest multiativos (`simulate_portfolio_multi_asset`), cada barra $t$ na linha do tempo consome apenas sinais cuja barra de confirmação ocorreu em $< t$ e executa pelo `execution_price` causal na barra $t$. Nenhuma informação de $t+1$ vaza para o cálculo de pesos ou rotações em $t$. | ✅ PASS |
| **III. Robustez Multi-Mercado & Fallback Quantitativo** | Suporta carteiras de Ações B3 (`.SA` com lotes inteiros), FIIs (`.SA`), Ações EUA, Commodities (`=F`) e Cripto (`-USD` com cotas fracionárias), alinhando calendários distintos via *forward-fill* causal de preços de fechamento para marcação a mercado. | ✅ PASS |
| **IV. Modularidade Estrita e Contratos de Dados Padronizados** | Mantém a separação exata nos 4 domínios: `data_loader` (inalterado), `strategies` (inalterado), `evaluator` (novo `src/evaluator/portfolio_simulator.py` consumindo os contratos padrão `SignalRecord` e `OHLCVSeries`) e `api` + `web` (`src/api/schemas.py`, `src/api/server.py`, `src/web/`). | ✅ PASS |
| **Quality Gates & Commit por Tarefa** | Contratos documentados em `contracts/portfolio-api.md`, testes unitários anti-look-ahead e de conservação contábil previstos, e cada tarefa de `tasks.md` gerará um commit individual durante `/speckit-implement`. | ✅ PASS |

---

## Project Structure

### Documentation (this feature)

```text
specs/016-portfolio-manager-simulator/
├── plan.md              # Este arquivo (Plano de Implementação)
├── research.md          # Phase 0 output (Score de Potencial, Sizing, 3 Regras de Rebalanceamento)
├── data-model.md        # Phase 1 output (Entidades, campos, validações e transições de estado)
├── quickstart.md        # Phase 1 output (Guia de execução e validação E2E)
├── contracts/
│   └── portfolio-api.md # Phase 1 output (Contratos REST FastAPI e UI SPA)
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação
└── tasks.md             # Phase 2 output (será gerado por /speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── data_loader/
│   ├── fetcher.py                  # Carregamento OHLCV com cache Parquet (reutilizado)
│   └── normalizer.py               # Normalização de tickers e sufixos (reutilizado)
├── strategies/
│   └── ...                         # Catálogo de 50 estratégias (reutilizado)
├── evaluator/
│   ├── __init__.py                 # Exportará funções e classes de portfolio_simulator.py
│   ├── accumulation_simulator.py   # Reutilizado (optimize_strategy_pairs)
│   ├── statistical_engine.py       # Reutilizado (evaluate_all_strategies)
│   ├── timing_classifier.py        # Reutilizado (classify_timing_status)
│   └── portfolio_simulator.py      # [NOVO] Motor de Score de Potencial, Consultor Hoje e Simulador Multiativos
├── api/
│   ├── schemas.py                  # [MODIFICADO] Schemas Pydantic para /api/portfolio/advise e /api/portfolio/simulate
│   └── server.py                   # [MODIFICADO] Endpoints POST /api/portfolio/advise e POST /api/portfolio/simulate
└── web/
    ├── index.html                  # [MODIFICADO] 5ª Aba "Carteira" (#tab-portfolio) e layout completo
    ├── app.js                      # [MODIFICADO] Estado localStorage, chamadas de API, tabelas e gráficos Plotly da Carteira
    └── styles.css                  # [MODIFICADO] Estilos de badges de ordens, barras de score e adaptação Light/Dark

tests/
└── unit/
    ├── test_portfolio_simulator.py # [NOVO] Testes unitários de Score, Rebalanceamento, Rotação, Caixa e Anti-Look-Ahead
    └── test_api_endpoints.py       # [MODIFICADO] Testes de contrato para /api/portfolio/advise e /api/portfolio/simulate
```

**Structure Decision**: Arquitetura Single-Repository modular existente preservando os 4 domínios da Constituição (`data_loader`, `strategies`, `evaluator`, `api` + `web`). A lógica matemática e de máquina de estados da carteira fica isolada em `src/evaluator/portfolio_simulator.py`, enquanto `src/api/server.py` apenas orquestra o carregamento paralelo e serializa os schemas Pydantic para a SPA em `src/web/`.

---

## Complexity Tracking

> Nenhuma violação da Constituição foi introduzida. Todos os gates passaram integralmente.
