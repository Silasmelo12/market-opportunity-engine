# Data Model: Suporte ao Timeframe 1h e Ocultação do Seletor de Direção

**Feature**: `011-hourly-timeframe-and-direction-cleanup`  
**Date**: 2026-10-21  

---

## 1. Mapeamento de Timeframes no `DataLoader`

```python
MAX_PERIODS = {
    "5m": "60d",
    "15m": "60d",
    "30m": "60d",
    "60m": "730d",     # Adicionado para suportar 60m
    "1h": "730d",      # 730 dias corridos (~2 anos)
    "2h": "730d",
    "4h": "730d",
    "12h": "730d",
}
```

---

## 2. Visibilidade da Interface

| Elemento DOM | Abas Visíveis | Abas Ocultas |
|---|---|---|
| `#global-direction-selector` | `tab-radar` (Radar), `tab-terminal` (Gráfico) | `tab-simulator` (Simulador), `tab-playbook` (Playbook) |
