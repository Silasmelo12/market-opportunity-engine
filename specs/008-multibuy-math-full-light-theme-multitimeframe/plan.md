# Implementation Plan: Matemática Multi-Buy Genérica, Tema Claro Global & Multi-Timeframe 5m

**Branch**: `008-multibuy-math-full-light-theme-multitimeframe` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

## Summary

Esta feature resolve três pilares cruciais:
1. **Rigor Matemático Genérico para K Compras**: Em `simulate_cycle_trade`, contabilizar como Capital Investido a soma real de todos os aportes realizados nas $K$ compras de todos os ciclos ($\text{Investido Real} = \sum C_i$), e derivar o retorno da estratégia sobre este montante desembolsado.
2. **Tema Claro Global e Coerente**: Atualizar o CSS para cobrir todas as classes do Tailwind (`bg-fintech-surface`, `bg-gray-800`, `bg-gray-900`, `card-surface`, headers, modais e bordas), garantindo um tema fintech claro 100% harmonioso e sem blocos escuros residuais.
3. **Simulação e Análise Multi-Timeframe (5m, 15m, 60m)**: Expandir o seletor do simulador e da API para suportar intervalos intradiários (`5m`, `15m`, `60m`, `1d`, `1wk`).

---

## Technical Context

**Language/Version**: Python 3.11+, Vanilla ES6 JavaScript, Tailwind CSS  
**Dependencies**: FastAPI, NumPy, Pandas, Uvicorn, TradingView Lightweight Charts  
**Storage**: Cache em memória + Disco (.cache)  
**Testing**: pytest  
**Governance**: 1 commit por tarefa concluída  

---

## Constitution Check

- [x] Principle I (FastAPI + Web SPA): Lógica matemática no backend Python, visual na SPA.
- [x] Principle II (Zero Look-Ahead): As $K$ compras e a liquidação da venda respeitam estritamente a ordem cronológica causal.
- [x] Commit por tarefa: Cada tarefa implementada receberá commit git imediato.
