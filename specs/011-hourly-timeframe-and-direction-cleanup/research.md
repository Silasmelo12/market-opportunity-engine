# Research & Technical Decisions: Suporte ao Timeframe 1h e Ocultação do Seletor de Direção

**Feature**: `011-hourly-timeframe-and-direction-cleanup`  
**Date**: 2026-10-21  

---

## 1. Pesquisa 1: Resolução do Erro 400 no Timeframe Horário (`1h` / `60m`)

### Problema Identificado
Em `src/data_loader/fetcher.py`, o dicionário `MAX_PERIODS` continha a chave `"1h": "730d"`, mas omitia `"60m"`. Quando o usuário selecionava "60 Minutos (1 Hora)" no Simulador, o backend caía na regra padrão (`else: download_period = "5y"`). O Yahoo Finance rejeita downloads de 5 anos para candles de 60 minutos com erro `"1h data not available for range... must be within the last 730 days"`, resultando em um DataFrame vazio e disparando `HTTP 400` no endpoint `/api/simulate`.

### Decisão Técnica
1. **Adicionar `"60m": "730d"` em `MAX_PERIODS`** em `src/data_loader/fetcher.py`.
2. **Normalização de Intervalo**: Garantir que se `interval` for `"60m"` ou `"1h"`, o download utilize `"1h"` ou `"60m"` com teto de `"730d"` (ou menor, se solicitado).
3. **Limite em `server.py`**: No endpoint `/api/simulate/optimize` e `/api/simulate`, caso o intervalo seja horário (`1h` / `60m`) e o período seja superior a 730 dias (ex: `2y` ou `5y`), ajustar para `730d` automaticamente.

---

## 2. Pesquisa 2: Ocultação Contextual de `#global-direction-selector`

### Problema Identificado
O componente `#global-direction-selector` (botões segmentados "Compra", "Venda" e "Ambos") está localizado no cabeçalho global. Quando o usuário navega para a aba **Simulador** ou **Playbook**, os botões permanecem visíveis, gerando confusão de contexto e ruído visual desnecessário, já que o Simulador possui controles próprios de estratégia/modelo e o Playbook é apenas uma página de documentação.

### Decisão Técnica
1. Na função `switchTab(tabId)` em `src/web/app.js`:
   - Se `tabId === 'tab-simulator' || tabId === 'tab-playbook'`:
     Aplicar a classe `hidden` no elemento `#global-direction-selector`.
   - Se `tabId === 'tab-radar' || tabId === 'tab-terminal'`:
     Remover a classe `hidden` do elemento `#global-direction-selector`.
2. O estado de `state.activeDirection` permanece intacto na memória durante a alternância entre abas.
