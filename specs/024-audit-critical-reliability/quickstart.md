# Quickstart: Confiabilidade Crítica e Experiência Operacional

## Pré-requisitos

```bash
python -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/python -m playwright install chromium
```

## Executar a suíte

```bash
./venv/bin/python -m pytest tests/unit -q
./venv/bin/python -m pytest tests/test_double_patterns.py tests/test_normalizer_suffix.py tests/test_radar_pagination.py -q
./venv/bin/python -m pytest tests/e2e -q
```

## Subir a aplicação

```bash
./venv/bin/python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8123
```

Abrir `http://127.0.0.1:8123`.

## Verificações manuais

1. Importar um `.xlsx` B3 e conferir que o caixa não é R$ 10.000.
2. Importar o mesmo arquivo duas vezes e conferir que a renda não duplica.
3. Simular acumulação com BUY+SELL e conferir 1 aporte.
4. Simular com `end_date` e conferir o preço final da janela.
5. Abrir o radar e comparar o deck com a tabela.
6. Abrir o gráfico de ranking e conferir barras.
7. Abrir carteira vazia e conferir ausência de séries sintéticas.
8. Testar CORS/upload inválido e navegação por teclado.

## Observações

- `ALLOWED_ORIGINS` e `MAX_B3_UPLOAD_MB` são configuráveis por ambiente.
- O caixa é manual; a B3 não informa caixa.
- Métricas sem benchmark aparecem como “—”.
