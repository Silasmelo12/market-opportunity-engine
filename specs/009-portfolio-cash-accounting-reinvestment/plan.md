# Implementation Plan: Fluxo de Caixa Realista e Reinvestimento de Vendas no Simulador de Ciclo

**Branch**: `009-portfolio-cash-accounting-reinvestment` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

## Summary

Implementar a contabilidade realista de fluxo de caixa da carteira em `simulate_cycle_trade` (`src/evaluator/accumulation_simulator.py`):
1. **Caixa Líquido Dinâmico (`cash`)**: Começa com `initial_capital`. Cada compra debita do caixa disponível; se o caixa for insuficiente para cobrir o aporte (`cash < required_capital`), o valor faltante é injetado como capital novo do bolso (`cumulative_external_capital += required_capital - cash; cash = 0`).
2. **Reinvestimento Automático de Vendas**: Toda liquidação de posição em um sinal de venda soma integralmente `shares * sell_price` ao saldo de `cash`.
3. **Métrica "Capital Investido" e Curva Temporal**: Representa o dinheiro externo efetivamente desembolsado do bolso ao longo de toda a simulação (`cumulative_external_capital`), estabilizando quando novos ciclos são financiados pelos lucros das operações anteriores.
4. **Retorno Global da Estratégia**:
   $$\text{Retorno Global (\%)} = \frac{\text{Patrimônio Final} - \text{Capital do Bolso}}{\text{Capital do Bolso}} \times 100$$

---

## Technical Context

**Language/Version**: Python 3.11+, Vanilla JavaScript (ES6+), HTML5, Tailwind CSS  
**Primary Dependencies**: FastAPI, Pydantic, NumPy, Pandas, TradingView Lightweight Charts, Plotly.js  
**Testing**: pytest (`tests/unit/test_accumulation.py`)  
**Performance Goals**: < 50ms para simulação de 2 anos de histórico em passagem única $O(N)$.  
**Governance**: 1 commit atômico por tarefa implementada.

---

## Constitution Check

- [x] **Principle I (Python FastAPI + Web SPA)**: Lógica quantitativa no backend Python; SPA renderiza via API.
- [x] **Principle II (Zero Look-Ahead Bias)**: Cada débito e crédito no caixa ocorre estritamente na barra de execução causal (`execution_bar_index`).
- [x] **Principle IV (Modularidade)**: Alterações concentradas em `src/evaluator/accumulation_simulator.py` e refletidas na camada de contratos.
- [x] **Quality Gates (Commit por Tarefa OBRIGATÓRIO)**: Cada tarefa receberá commit imediato.

---

## Project Structure

```text
specs/009-portfolio-cash-accounting-reinvestment/
├── plan.md
├── spec.md
└── tasks.md

src/
├── evaluator/
│   └── accumulation_simulator.py   # Lógica do fluxo de caixa e reinvestimento
└── web/
    └── app.js                      # Sincronização visual de KPIs e curvas
tests/
└── unit/
    └── test_accumulation.py        # Teste unitário cobrindo múltiplos ciclos com reaproveitamento de caixa
```
