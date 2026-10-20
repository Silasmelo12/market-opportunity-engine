# Quickstart Validation Guide: Market Opportunity & Bottom Statistical Engine

**Feature**: `001-market-opportunity-engine`
**Date**: 2026-10-19

## 1. Pré-Requisitos e Ambiente
- Python 3.10 ou superior.
- Dependências centrais instaladas:
  ```bash
  pip install streamlit yfinance pandas numpy plotly streamlit-lightweight-charts pyarrow
  ```

## 2. Teste Rápido de Ingestão e Cache
Valide o download de dados com cache local executando no console:
```bash
python -c "
from src.data_loader import DataLoader
s = DataLoader.load_asset_data('PETR4.SA', interval='1d', period='2y')
print(f'Carregado: {s.ticker} com {s.length} barras')
"
```
**Resultado Esperado**: Carregamento concluído em menos de 1 segundo e criação do arquivo em `.cache/data/PETR4.SA_1d.parquet`.

## 3. Teste Unitário da Máquina de Estados (Anti-Look-Ahead & Gap)
Valide se as regras matemáticas cravadas no FR-004 funcionam:
```bash
python -c "
from src.strategies.proprietary_reversal import ProprietaryReversalEngine
from src.data_loader import DataLoader
series = DataLoader.load_asset_data('AAPL', interval='1d', period='2y')
engine = ProprietaryReversalEngine(lookback_n=10, retest_window_m=5, tolerance_pct=0.01)
signals, lines = engine.generate_signals(series)
print(f'Total de sinais proprietários: {len(signals)}')
for sig in signals[:3]:
    print(sig)
"
```
**Resultado Esperado**:
- Sinais gerados com `execution_bar_index >= signal_bar_index`.
- Preço de gap respeitado quando `Open < Linha`.

## 4. Inicialização do Dashboard no Navegador
Para iniciar a aplicação web completa:
```bash
streamlit run src/app.py
```
**Resultado Esperado**:
- Interface abre no navegador em `http://localhost:8501`.
- Barra lateral permite alternar tickers multi-mercado e timeframes.
- Gráfico interativo com candles e linhas horizontais de negação.
- Painéis de Ranking de Win Rate e Scatter Plot Risco x Retorno atualizados instantaneamente.
