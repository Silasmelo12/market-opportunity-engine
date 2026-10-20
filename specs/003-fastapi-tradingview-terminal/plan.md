# Implementation Plan: Feature 003

**Branch**: `003-fastapi-tradingview-terminal` | **Date**: 2026-10-20 | **Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/003-fastapi-tradingview-terminal/spec.md)

## Summary

Substituição da camada lenta do Streamlit por uma arquitetura desacoplada de altíssima performance:
1. **Backend FastAPI (`src/api/server.py`)**:
   - Cache em memória TTL/LRU e execução concorrente via `ThreadPoolExecutor` para o Radar.
   - Servidor FastAPI servindo o frontend estático SPA na mesma porta (porta `8000`).
   - Endpoints `/api/analyze`, `/api/radar` e `/api/simulate` entregando JSONs estruturados em milissegundos.
2. **Expansão de Velas para 24 Estratégias Totais (`src/strategies/mql5_candles.py`)**:
   - Adicionados 6 novos padrões de reversão de fundo de alta probabilidade (`inverted_hammer`, `tweezer_bottom`, `dragonfly_doji`, `abandoned_baby_bullish`, `bullish_kicker`, `climactic_pinbar`), totalizando 14 velas e 24 estratégias completas.
3. **Frontend SPA Web Terminal 60fps (`src/web/index.html`, `styles.css`, `app.js`)**:
   - TradingView Lightweight Charts nativo em Canvas HTML5 a 60fps com zoom/pan responsivo.
   - Barra lateral com 4 accordions e controle granular individual para cada uma das 24 estratégias, com atalhos "Todos" e "Nenhum".
   - **Filtragem Client-Side Instantânea (0ms)**: Marcar/desmarcar qualquer estratégia atualiza os marcadores e tabelas na memória do navegador a 60fps sem requisições de rede adicionais.
   - 4 Abas: `🌐 Radar de Oportunidades`, `📈 Terminal de Análise`, `💰 Simulador de Patrimônio` e `📘 Playbook & Guia`.

## Technical Context

**Language/Version**: Python 3.10+ (Backend FastAPI) + JavaScript ES6 / Canvas HTML5 (Frontend SPA)

**Primary Dependencies**:
- Backend: `fastapi>=0.110.0`, `uvicorn>=0.30.0`, `pydantic>=2.0.0`
- Frontend: Tailwind CSS (via CDN), TradingView Lightweight Charts 4.1+ (via CDN standalone), Plotly.js 2.30+ (via CDN)
- Motores Matemáticos: `numpy`, `pandas`, `yfinance`, `pyarrow` (100% preservados)

## Constitution Check

- [x] **Princípio I (100% Python & Otimização)**: FastAPI Single-Repo, cache local Parquet + cache em memória TTL, frontend SPA estático sem compilação Node.js.
- [x] **Princípio II (Zero Look-Ahead Bias)**: Todos os 24 motores executam estritamente em `Open[t+1]` ou reteste sequencial em $M$ barras.
- [x] **Princípio III (Multi-Mercado)**: Suporte completo preservado a Ações EUA, B3, FIIs, Cripto e Commodities em todos os timeframes (`5m` a `1wk`).
- [x] **Princípio IV (Modularidade)**: Separação estrita `src/data_loader/`, `src/strategies/`, `src/evaluator/`, `src/api/` e `src/web/`.

## Project Structure & Planned Modules

```text
src/
├── api/
│   ├── __init__.py
│   ├── server.py              # FastAPI app, endpoints REST, cache e StaticFiles mount
│   └── schemas.py             # Modelos Pydantic para validação e serialização rápida
├── strategies/
│   ├── base.py                # Contratos imutáveis existentes
│   ├── proprietary_reversal.py# 4 variantes existentes
│   ├── classic_engines.py     # 6 estratégias clássicas existentes
│   └── mql5_candles.py        # Expandido: 8 existentes + 6 novos padrões de fundo (14 totais)
├── evaluator/
│   ├── statistical_engine.py  # Avaliador estatístico existente
│   ├── accumulation_simulator.py # Simulador financeiro existente
│   └── timing_classifier.py   # Semáforo de timing existente
├── web/
│   ├── index.html             # Shell da SPA com 4 abas, barra lateral e canvas
│   ├── styles.css             # Tema FinTech Dark, layouts flex/grid e accordions
│   └── app.js                 # Lógica reativa: TradingView Canvas, filtragem 0ms, Plotly.js e simulação
└── main.py                    # Ponto de entrada Uvicorn para inicialização simples

tests/
├── unit/
│   ├── test_mql5_expansion.py # Novo: Teste dos 6 novos padrões de vela
│   └── test_api_endpoints.py  # Novo: Teste dos endpoints FastAPI
```
