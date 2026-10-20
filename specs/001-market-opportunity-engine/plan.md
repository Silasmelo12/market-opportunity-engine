# Implementation Plan: Market Opportunity & Bottom Statistical Engine

**Branch**: `001-market-opportunity-engine` | **Date**: 2026-10-19 | **Spec**: [spec.md](file:///c:/Users/silas/OneDrive/Documentos/Market%20Opportunity%20&%20Bottom%20Statistical%20Engine/specs/001-market-opportunity-engine/spec.md)

**Input**: Feature specification from `/specs/001-market-opportunity-engine/spec.md`

## Summary

Construção de uma aplicação web 100% Python via Streamlit que atua como Indicador Geral de Oportunidades de Mercado e Avaliador Estatístico de Fundos para perfil Holder/Acumulação. O sistema consome dados históricos do Yahoo Finance (`yfinance`) com cache persistente em Parquet/`st.cache_data`, processa 8 famílias de estratégias de compra (incluindo a Estratégia Proprietária de Negação de Rompimento 2x2 e 8 padrões CCandlePattern MQL5), e calcula métricas empíricas de acerto (`Win Rate %`), retorno futuro (`Forward Return %`) e calor suportado (`MAE %`) em horizontes de $X$ barras sem qualquer viés de antecipação (Zero Look-Ahead Bias). A visualização combina `streamlit-lightweight-charts` para o gráfico de velas com marcadores e linhas horizontais de negação e `plotly` para painéis analíticos comparativos.

## Technical Context

**Language/Version**: Python 3.10+ (Single-Repo)

**Primary Dependencies**:
- Web UI & Gráficos: `streamlit`, `streamlit-lightweight-charts`, `plotly`
- Dados & Vetorização: `yfinance`, `pandas`, `numpy`, `pyarrow` (Parquet)
- Performance de Loops Críticos (Opcional/Adicional): `numba` (se necessário para a máquina de estados)

**Storage**: Arquivos locais em formato Parquet (`.cache/data/{ticker}_{interval}.parquet`) gerenciados por `data_loader`.

**Testing**: `pytest` com testes unitários cobrindo anti-look-ahead bias, contratos de sinal e regras de reteste da máquina de estados.

**Target Platform**: Navegador web moderno via servidor Streamlit local/desktop.

**Project Type**: Single-repo Web Analytics Dashboard.

**Performance Goals**:
- Ingestão com cache: < 50ms para recargas.
- Cálculo da Máquina de Estados e das 8 estratégias: < 150ms para 1.000 barras.
- Carga completa do dashboard: < 2.5s.

**Constraints**:
- Proibição estrita de look-ahead bias nos motores de estratégia.
- Proibição de `DataFrame.iterrows()` em rotinas de sinal.
- Suporte multi-mercado nativo (EUA, Brasil, FIIs, Cripto, Commodities).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Princípio I (100% Python & Otimização)**: Streamlit Single-Repo, cache Parquet/st.cache_data, vetorização numpy/pandas, máquina de estados $O(N)$ em arrays numpy puros sem `iterrows()`.
- [x] **Princípio II (Rigor Financeiro & Zero Look-Ahead Bias)**: Sinais em $t$ executam estritamente em $t+1$ (ou no primeiro reteste em $t+k$ com $1 \le k \le M$). Módulo `statistical_evaluator` é o único com permissão de consultar $X$ barras futuras.
- [x] **Princípio III (Multi-Mercado & Fallback Quantitativo)**: Suporte a ações EUA, B3, FIIs, Cripto e Commodities com Fallback Quantitativo (DY Rolling + Desconto SMA200 e Mayer Multiple).
- [x] **Princípio IV (Modularidade & Contratos Padronizados)**: 4 módulos estritos (`data_loader`, `strategy_engines`, `statistical_evaluator`, `ui_dashboard`) e contrato obrigatório `SignalRecord`.

## Project Structure

### Documentation (this feature)

```text
specs/001-market-opportunity-engine/
├── spec.md              # Especificação de requisitos da feature
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas e trade-offs (Phase 0)
├── data-model.md        # Modelos de dados e contratos (Phase 1)
├── quickstart.md        # Guia de validação e execução (Phase 1)
├── contracts/           # Interfaces de módulos (Phase 1)
│   └── interfaces.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Tarefas de implementação (Phase 2 - /speckit-tasks)
```

### Source Code Layout

```text
src/
├── app.py                         # Ponto de entrada Streamlit principal
├── data_loader/
│   ├── __init__.py
│   ├── fetcher.py                 # Ingestão yfinance e cache local em Parquet
│   └── normalizer.py              # Ajustes de timezone e cálculo de DY Rolling
├── strategies/
│   ├── __init__.py
│   ├── base.py                    # Contrato SignalRecord e ReferenceLineSegment
│   ├── proprietary_reversal.py    # Máquina de Estados O(N) 2x2 (FR-004)
│   ├── mql5_candles.py            # Vetorização fiel ao Artigo 101 CCandlePattern
│   └── classic_engines.py         # DCA, Rebalanceamentos, Value Proxy, BOS, Spring
├── evaluator/
│   ├── __init__.py
│   └── statistical_engine.py      # Win Rate, Forward Return, MAE e Score sem viés
└── ui/
    ├── __init__.py
    ├── sidebar.py                 # Controles e filtros interativos
    ├── main_chart.py              # Lightweight Charts / Plotly com linhas e compras
    ├── stats_panel.py             # Ranking e Scatter Plot Risco x Retorno
    └── status_card.py             # Monitor de confluência e estado atual da barra

tests/
├── unit/
│   ├── test_data_loader.py
│   ├── test_proprietary_reversal.py # Validação de gap, reteste sequencial e bordas
│   ├── test_mql5_candles.py
│   ├── test_classic_engines.py
│   └── test_statistical_evaluator.py # Prova matemática de Zero Look-Ahead Bias
```
