# Data Model: B3 Spreadsheet Integration

## Entidades & Esquemas Pydantic

### 1. `B3MovementRecord`
Representa uma movimentação individual da planilha oficial da B3.
```python
class B3MovementRecord(BaseModel):
    data: str
    entrada_saida: str  # "Credito" | "Debito"
    tipo: str           # "Compra", "Venda", "Rendimento", etc.
    ticker_raw: str
    ticker_clean: str   # Ex: "PETR4"
    ticker_sa: str      # Ex: "PETR4.SA"
    quantidade: float
    preco_unitario: float
    valor_operacao: float
    instituicao: Optional[str] = None
```

### 2. `B3Holding`
Posição em custódia calculada.
```python
class B3Holding(BaseModel):
    ticker: str             # "PETR4.SA"
    ticker_clean: str       # "PETR4"
    shares: float           # Quantidade de cotas em custódia
    average_buy_price: float # Preço Médio contábil ponderado (R$)
    total_invested: float   # shares * average_buy_price
    asset_class: str        # "Ações Brasil", "FIIs", "BDRs"
```

### 3. `B3MonthlyIncome`
Agrupamento mensal de proventos.
```python
class B3MonthlyIncome(BaseModel):
    month_year: str         # "2026-08"
    dividendos: float
    jcp: float
    rendimentos: float
    total: float
```

### 4. `B3ParseResult`
Resposta completa do backend para o frontend.
```python
class B3ParseResult(BaseModel):
    filename: str
    total_movements: int
    holdings: List[B3Holding]
    total_invested: float
    total_income: float
    monthly_income: List[B3MonthlyIncome]
```
