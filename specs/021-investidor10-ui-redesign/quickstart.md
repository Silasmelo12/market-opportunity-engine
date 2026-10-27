# Quickstart: Como Testar e Executar o Novo Layout

1. **Iniciar o Servidor FastAPI**:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

2. **Acessar a Aplicação**:
   Abra no navegador: `http://localhost:8000`

3. **Verificação de Regressão e Testes**:
   ```bash
   pytest tests/unit/test_api_endpoints.py -v
   pytest tests/unit/ -v
   ```
