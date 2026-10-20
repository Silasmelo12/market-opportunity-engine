# Implementation Plan: Institutional UX/UI Design, Multi-Timeframe Intraday, Radar Scanner, Simulador de Acumulação e Guia de Estratégias

**Branch**: `002-institutional-ux-radar-simulator` | **Date**: 2026-10-20 | **Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/002-institutional-ux-radar-simulator/spec.md)

**Input**: Feature specification from `/specs/002-institutional-ux-radar-simulator/spec.md`

## Summary

Evolução de UX/UI institucional e ferramentas avançadas para a aplicação sem quebrar os motores matemáticos validados na Feature 001. A Feature 002 introduz:
1. Suporte a timeframes Intraday (`5m` a `12h`) com Resampling matemático OHLCV e controle de limites de dias da API.
2. Motor de Simulação de Acumulação Patrimonial (`accumulation_simulator.py`) e Semáforo de Timing ("*Comprei Atrasado?*").
3. Design System Dark FinTech (`src/ui/theme.py`) e Dicionário de Nomes Comerciais Amigáveis em português (`STRATEGY_LABELS_PT`).
4. Reestruturação da aplicação em 4 Abas principais no topo:
   - **Aba 1 (Radar)**: Scanner de oportunidades com semáforo de timing e navegação por clique.
   - **Aba 2 (Terminal)**: Análise completa do ativo com Ranking sem corte em 100%, Scatter Plot com Quadrante de Ouro e tabela estilizada.
   - **Aba 3 (Simulador)**: Simulação interativa com `@st.fragment` e curva de Patrimônio vs. Capital Desembolsado.
   - **Aba 4 (Playbook)**: Enciclopédia educacional detalhando conceitos e regras operacionais.

## Technical Context

**Language/Version**: Python 3.10+ (Single-Repo Streamlit)

**Primary Dependencies**:
- `streamlit>=1.37.0` (suporte nativo a `@st.fragment` e `st.column_config`)
- `plotly>=5.18.0` (visualizações dark interativas e scatter com quadrantes)
- `pandas>=2.1.0`, `numpy>=1.24.0` (resampling e simulação de cotas vetorizada)
- `yfinance>=0.2.36`, `pyarrow>=14.0.0` (ingestão e cache Parquet)
- `pytest>=8.0.0` (garantia de regressão zero)

**Target Platform**: Navegador web moderno via Streamlit Desktop/Local.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (100% Python & Otimização)**: Single-Repo, cache local Parquet, `@st.fragment` para evitar reloads lentos no navegador.
- [x] **Princípio II (Zero Look-Ahead Bias)**: Resampling estritamente causal em barras passadas fechadas, simulação de cotas usando o preço real de execução $P_{exec}$.
- [x] **Princípio III (Multi-Mercado & Fallback Quantitativo)**: Cesta do Radar cobrindo Ações EUA, Brasil, FIIs, Cripto e Commodities.
- [x] **Princípio IV (Modularidade & Contratos Padronizados)**: Preservação estrita de `OHLCVSeries`, `SignalRecord` e `StrategyStatsSummary`.

## Project Structure & Planned Modules

```text
src/
├── app.py                         # Ponto de entrada com abas no topo e controle de session_state
├── data_loader/
│   ├── fetcher.py                 # Suporte a timeframes intraday e limites de período
│   └── normalizer.py              # Resampling de 1h -> 2h, 4h, 12h e limpeza de NaN
├── evaluator/
│   ├── statistical_engine.py      # Mantido íntegro da Feature 001
│   ├── accumulation_simulator.py  # Novo: Simulação financeira de aportes fixos e patrimônio
│   └── timing_classifier.py       # Novo: Semáforo de Timing (Ideal, Cautela, Atrasado)
└── ui/
    ├── theme.py                   # Novo: CSS Dark Institucional, STRATEGY_LABELS_PT e KPI Cards
    ├── radar_tab.py               # Novo: Aba 1 (Scanner Macro & Tabela de Oportunidades)
    ├── main_chart.py              # Aba 2 (Candlestick e segmentos de linhas)
    ├── stats_panel.py             # Aba 2 (Ranking corrigido sem corte em 100% e Scatter de Quadrantes)
    ├── simulator_tab.py           # Novo: Aba 3 (Simulador financeiro com @st.fragment)
    └── guide_tab.py               # Novo: Aba 4 (Playbook educativo das 18 variações)

tests/
├── unit/
│   ├── test_resampler.py          # Novo: Validação matemática do Resampling OHLCV
│   ├── test_accumulation.py       # Novo: Validação das cotas e patrimônio simulado
│   └── test_timing_classifier.py  # Novo: Validação das faixas de semáforo de timing
```
