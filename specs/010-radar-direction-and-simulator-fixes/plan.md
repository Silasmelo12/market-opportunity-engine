# Implementation Plan: Correção do Radar, Seletor de Modelo de Ciclo (1x vs Multi-Buy) e Alinhamento do Simulador

**Branch**: `010-radar-direction-and-simulator-fixes` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/010-radar-direction-and-simulator-fixes/spec.md`

---

## Summary

Esta feature resolve três necessidades críticas do terminal:
1. **Correção dos Seletores de Direção no Radar**: Conserta o ouvinte de clique dos botões Compra, Venda e Ambos, disparando a busca paginada e re-renderizando a tabela e o menu de estratégias.
2. **Seletor de Modelo de Entrada no Ciclo**: Permite ao usuário escolher livremente entre **"Compra Única (1x por Ciclo)"** (sem reentradas no mesmo trade) e **"Acumulação Multi-Buy (Nx por Ciclo)"** (com compras acumuladas e preço médio ponderado).
3. **Alinhamento Fiel entre Otimizador ("Mais Lucrativa") e Simulador ("Aplicar e Simular")**: Faz o Otimizador respeitar estritamente o tempo gráfico do simulador, o período intraday e o modelo de ciclo selecionado, garantindo 100% de convergência entre as métricas da combinação campeã e o resultado simulado.

---

## Technical Context

**Language/Version**: Python 3.11+ / HTML5 / JavaScript Vanilla (ES6+)  
**Primary Dependencies**: FastAPI, Pydantic, Pandas, NumPy, Lightweight Charts, Plotly.js, Tailwind CSS  
**Storage**: Cache em memória com TTL, disco Parquet/JSON e Redis opcional  
**Testing**: `pytest` com asserções formais unitárias e de integração  
**Target Platform**: Navegadores Web modernos (desktop e mobile)  
**Project Type**: Single-Repository Web Quant Terminal & Analytical API  
**Performance Goals**: Tempo de resposta do radar paginado < 200ms; otimização de pares em sub-segundo; visualização a 60fps  
**Constraints**: Zero look-ahead bias; conformidade estrita com a Constituição v2.0.0; commit atômico por tarefa  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **I. Arquitetura Python + Web SPA**: FastAPI gerencia schemas Pydantic e endpoints REST; Frontend SPA vanilla HTML/JS; sem acoplamento a frameworks legados.
- [X] **II. Zero Look-Ahead Bias**: As compras de 1x ou Multi-Buy e as vendas continuam operando estritamente em barras causais ($Open[t+1]$ ou reteste confirmado em $t+k$).
- [X] **III. Robustez Multi-Mercado**: Compatibilidade com ativos B3, EUA, Cripto e Commodities mantida.
- [X] **IV. Modularidade Estrita**: Divisão em `data_loader`, `strategy_engines`, `statistical_evaluator` e `api` + `web` preservada.
- [X] **Commit por Tarefa (OBRIGATÓRIO)**: Cada tarefa implementada no `tasks.md` gerará um commit atômico individual.

---

## Project Structure

### Documentation (this feature)

```text
specs/010-radar-direction-and-simulator-fixes/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Technical research and decisions
├── data-model.md        # Data entities, schemas and state modifications
├── quickstart.md        # End-to-end validation guide
├── contracts/           # API contracts (/api/simulate and /api/radar)
└── checklists/          # Requirements and quality checklists
```

### Source Code Impact

```text
src/
├── api/
│   ├── schemas.py                 # Adição de cycle_entry_mode em SimulateRequest e OptimizeCombinationsRequest
│   └── server.py                  # Repasse de cycle_entry_mode para simulador e otimizador
├── evaluator/
│   └── accumulation_simulator.py  # Suporte a single_buy vs multi_buy em simulate_cycle_trade e optimize_strategy_pairs
└── web/
    ├── index.html                 # Seletor visual de modelo de entrada (sim-cycle-mode) no painel do Simulador
    └── app.js                     # Correção de setupDirectionSelector (loadRadarData) e propagação em runOptimizer

tests/
└── unit/
    └── test_accumulation.py       # Testes unitários para cycle_entry_mode (single_buy vs multi_buy)
```

---

## Complexity Tracking

*Nenhuma violação constitucional detectada. Sem padrões complexos desnecessários adicionados.*
