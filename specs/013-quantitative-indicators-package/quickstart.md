# Quickstart & Verification Guide: Pacote de Estratégias Quantitativas

Este guia descreve como verificar e validar o funcionamento das novas 10 estratégias quantitativas.

## 1. Pré-Requisitos
- Ambiente Python com dependências instaladas (`uvicorn`, `fastapi`, `numpy`, `pandas`, `yfinance`, `pytest`).
- Conexão local ativa para testes automatizados.

---

## 2. Execução dos Testes Automatizados

Executar a nova suíte de testes unitários dedicada aos novos indicadores:
```powershell
pytest tests/unit/test_quantitative_indicators.py -v
```

Verificar a integridade de regressão com toda a suíte existente (mais de 55 testes):
```powershell
pytest tests/ -v
```

---

## 3. Verificação Manual via API

1. Iniciar o servidor de desenvolvimento:
   ```powershell
   python -m uvicorn src.api.server:app --reload --port 8000
   ```

2. Validar se o catálogo expõe as 10 novas estratégias:
   ```powershell
   curl http://localhost:8000/api/strategies
   ```
   *Resultado esperado*: JSON contendo as novas estratégias com IDs `bollinger_close_in`, `keltner_squeeze`, `zscore_extreme`, etc.

3. Testar simulação com o novo par Bollinger Fechou Fora/Dentro (Compra) e SuperTrend (Venda):
   ```powershell
   curl -X POST http://localhost:8000/api/simulate/run `
     -H "Content-Type: application/json" `
     -d '{"ticker":"PETR4.SA","timeframe":"1d","period":"2y","buy_strategy":"bollinger_close_in","sell_strategy":"supertrend_trailing","initial_capital":10000}'
   ```

4. Testar o Otimizador de Acumulação DCA com os novos indicadores:
   ```powershell
   curl -X POST http://localhost:8000/api/simulate/optimize `
     -H "Content-Type: application/json" `
     -d '{"ticker":"BBAS3.SA","timeframe":"1d","period":"2y","simulation_mode":"accumulation","contribution_amount":500}'
   ```
   *Resultado esperado*: Lista de ranking contendo os novos indicadores avaliados como estratégias de aporte em fundos estatísticos.
