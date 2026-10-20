# Contracts: Feature 003

## Endpoints REST FastAPI

### 1. `GET /api/analyze`
**Query Parameters**:
- `ticker`: str (default: "PETR4.SA")
- `interval`: str (default: "1d")
- `period`: str (default: "2y")
- `lookback_n`: int (default: 10)
- `retest_m`: int (default: 5)
- `retest_tol`: float (default: 0.005)
- `horizon_x`: int (default: 60)

**Output**: JSON formatado conforme `AnalyzeResponse` em `data-model.md`.

---

### 2. `GET /api/radar`
**Query Parameters**:
- `tickers`: Optional[str] (lista separada por vírgula, default cesta institucional)
- `interval`: str (default: "1d")
- `horizon_x`: int (default: 60)

**Output**: Array de `RadarItem` ordenados por prioridade de oportunidade.

---

### 3. `POST /api/simulate`
**Body JSON**:
```json
{
  "ticker": "PETR4.SA",
  "interval": "1d",
  "period": "2y",
  "contribution_amount": 100.0,
  "start_date": "2023-01-01",
  "end_date": "2024-10-01",
  "selected_strategies": ["t1_retest", "wyckoff_spring"]
}
```
**Output**: Dicionário de `SimulationResult` contendo séries de patrimônio acumulado e capital investido.

---

### 4. `GET /` e Arquivos Estáticos
- `GET /` -> Serve `src/web/index.html`
- `GET /static/*` -> Serve `src/web/*` (CSS, JS, assets)
